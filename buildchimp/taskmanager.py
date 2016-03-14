#!/bin/python

import yaml
from collections import namedtuple
from pprint import pprint
import threading, time
from lib import ScopeGuard
from tasks import *
from  PySide.QtCore import QProcess
import time
import datetime as dt
from PySide.QtGui import QStandardItem, QBrush, QColor

NOT_STARTED=0
RUNNING=1
DONE=2

color_type = namedtuple("color_type", ["htmlCol", "qbrush"])

tasks_tuple = namedtuple("tasks", ["dict", "status", "dependencies", "id",
                                   "timein", "timeend", "parent_tree_item", "is_optional",
                                   "will_run_task", "error_code"])

class Color:
    def Black(self):
        return color_type(htmlCol="#000", qbrush=QBrush(QColor.fromRgb(0,0,0)))

    def Red(self):
        return color_type(htmlCol="#000",qbrush=QBrush(QColor.fromRgb(0xff,0,0)))

    def Green(self):
        return color_type(htmlCol="#070",qbrush=QBrush(QColor.fromRgb(0,0x77,0)))

    def Blue(self):
        return color_type(htmlCol="#00f",qbrush=QBrush(QColor.fromRgb(0,0,0xff)))

    def Gray(self):
        return color_type(htmlCol="#777",qbrush=QBrush(QColor.fromRgb(0x77,0x77,0x77)))

def ForegroundForTask(task):
    if task.status==DONE and task.error_code!=0: return Color().Red().qbrush
    if task.status==DONE: return Color().Blue().qbrush
    if not task.will_run_task : return Color().Gray().qbrush
    if task.status==RUNNING : return Color().Green().qbrush
    return Color().Black().qbrush
    
def validate_yaml(yaml_dict):
    pass # TODO: ...

def DoneOrWontRun(x):
    return x.status==DONE or x.will_run_task==False
    
def is_checked(q_standard_item):
    if not q_standard_item.isCheckable() : return True
    return q_standard_item.checkState()==QtCore.Qt.Checked
    
def can_task_be_started(nt, all_tasks):
    # A task can be started if the task has all dependencies met
    if nt.status!=NOT_STARTED: return False
    for id in ([] if not nt.dependencies else nt.dependencies):
        for others in [x for x in all_tasks if x!=id]:
            if id==others.id and not DoneOrWontRun(others):
                return False
    return True

def all_tasks_done(all_tasks):
    return len(all_tasks) == sum(1 if DoneOrWontRun(x) else 0 for x in all_tasks)

class TaskDependencyFault:
    pass

class TaskManager:
    def __init__(self, yaml_text, main_wnd):
        self.config_dict = yaml.load(yaml_text)
        self.environment = None
        if "globals" in self.config_dict:
            g = self.config_dict["globals"]
            if "environment" in g:
                self.environment = list()
                env = g["environment"]
                for k in env.keys():
                    self.environment.append( (k,env[k]) )
        self.tasks = []
        self.main_wnd = main_wnd
        validate_yaml(self.config_dict)
        # Setup tasks
        for step in self.config_dict['buildsteps']:
            self.tasks.append( tasks_tuple(dict=step, status=NOT_STARTED,
                                            dependencies=step["dependencies"],
                                            id=step["id"], timein=None, timeend=None, parent_tree_item=None,
                                            is_optional=("optional" in step and step["optional"]),
                                            will_run_task=True, error_code=0 ) )
        # Add Tree Items
        tree_items = self.main_wnd.enqueueTreeBuildTasks( [(x.dict['title'], x.dict['description']) for x in self.tasks] )
        an_item = None
        for i in range(0, len(self.tasks)):
            self.tasks[i] = self.tasks[i]._replace(parent_tree_item=tree_items[i][1])
            if self.tasks[i].is_optional:
                parent = self.tasks[i].parent_tree_item
                an_item = parent
                parent.setCheckable(True)
                parent.setCheckState(QtCore.Qt.Checked)
        if an_item:
            an_item.model().itemChanged.connect( self.TreeItemChanged )
    
    def TreeItemChanged(self, dunno):
        for i in range(0, len(self.tasks)):
            task = self.tasks[i]
            parent_tree_item = task.parent_tree_item
            self.tasks[i] = task._replace(will_run_task=is_checked(parent_tree_item))
            task = self.tasks[i] 
            parent_tree_item.setForeground(ForegroundForTask(task))
        
    def launch_task(self, task_index):
        task = self.tasks[task_index]
        task.parent_tree_item.setForeground(ForegroundForTask(task))
        self.tasks[task_index] = self.tasks[task_index]._replace(timein=time.time())
        if "inline_script_py" in task.dict:
            tab_ix = self.main_wnd.enqueue_tab(task.dict["title"])
            tt = self.main_wnd.tabs[tab_ix]
            proc = PythonTask(self.main_wnd, task.dict["inline_script_py"], 10, tt, tab_ix,
                              lambda exitcode, self=self, task_index=task_index : self.finished_task(exitcode, task_index),
                              environment = self.environment)
            self.main_wnd.tabs[tab_ix] = self.main_wnd.tabs[tab_ix]._replace(qprocess=proc)

        elif "inline_script_sh" in task.dict:
            tab_ix = self.main_wnd.enqueue_tab(task.dict["title"])
            tt = self.main_wnd.tabs[tab_ix]
            proc = BashCommandTask(self.main_wnd, task.dict["inline_script_sh"], 10, tt, tab_ix,
                                  lambda exitcode, self=self, task_index=task_index : self.finished_task(exitcode, task_index),
                                  environment = self.environment)
            self.main_wnd.tabs[tab_ix] = self.main_wnd.tabs[tab_ix]._replace(qprocess=proc)

        elif "inline_script_bat" in task.dict:
            tab_ix = self.main_wnd.enqueue_tab(task.dict["title"])
            tt = self.main_wnd.tabs[tab_ix]
            proc = WinCommandTask(self.main_wnd, task.dict["inline_script_bat"], 10, tt, tab_ix,
                                  lambda exitcode, self=self, task_index=task_index : self.finished_task(exitcode, task_index),
                                  environment = self.environment)
            self.main_wnd.tabs[tab_ix] = self.main_wnd.tabs[tab_ix]._replace(qprocess=proc)
    
    def finished_task(self, exitcode, task_index):
        task = self.tasks[task_index]._replace(status=DONE, timeend=time.time())
        if exitcode!=0:
            task = task._replace(error_code = exitcode)
        self.tasks[task_index] = task
        time_delta = task.timeend-task.timein
        time_delta = dt.datetime.utcfromtimestamp(time_delta)
        time_delta = "time: " + time_delta.strftime('%H:%M:%S')
        task.parent_tree_item.appendRow( [QStandardItem(time_delta)] )
        task.parent_tree_item.setForeground( ForegroundForTask(task) )
        if exitcode==0:
            self.run_loop()
        
    def run_loop_init(self):
        for i in range(0, len(self.tasks)):
            self.tasks[i] = self.tasks[i]._replace(status=NOT_STARTED)
            
    def run_loop(self):
        TASKS_BEGIN = -1
        if all_tasks_done(self.tasks):
            return
        result = self.start_another_task_if_possible()
    
    def start_another_task_if_possible(self):
        # Count number of running tasks
        tasks_running = 0
        for x in self.tasks:
            if x.status==RUNNING: tasks_running+=1
        
        # Try to find an unstarted task with dependencies fulfilled - if so, start it
        for i in range(0,len(self.tasks)):
            task = self.tasks[i]
            if can_task_be_started(task, self.tasks):
                self.tasks[i] = task._replace(status=RUNNING)
                self.launch_task(i)
                return True
        if tasks_running==0:
            raise TaskDependencyFault()
        return False
