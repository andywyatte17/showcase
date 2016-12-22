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
from PySide import QtGui
from PySide.QtCore import Qt

NOT_STARTED=0
RUNNING=1
DONE=2

color_type = namedtuple("color_type", ["htmlCol", "qbrush"])

tasks_tuple = namedtuple("tasks", ["dict", "status", "dependencies", "id",
                                   "timein", "timeend", "parent_tree_item", "is_optional",
                                   "will_run_task", "error_code", "line_flush", "tabs_ix",
                                   "time_tree_item"])

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
    

def can_task_be_started(task, all_tasks):
    # A task can be started if the task has all dependencies met
    if task.status!=NOT_STARTED: return False
    if not task.will_run_task : return False
    for id in ([] if not task.dependencies else task.dependencies):
        for others in [x for x in all_tasks if x!=id]:
            if id==others.id and not DoneOrWontRun(others):
                return False
    return True

def all_tasks_done(all_tasks):
    return len(all_tasks) == sum(1 if DoneOrWontRun(x) else 0 for x in all_tasks)


class TaskDependencyFault:
    pass


def merge_two_dicts(a, b, level=0):
    '''
       merges dict-of-dicts 'b' into dict-of-dicts 'a'
    '''
    for kb in b:
        vb = b[kb]
        if isinstance(vb, dict):
            if not kb in a:
                a[kb] = {}
            elif not isinstance(a[kb], dict):
                raise Exception("dict / non-dict conflict.")
            merge_two_dicts(a[kb], b[kb], level+1)
        else:
            if kb in a and isinstance(a[kb], dict):
                raise Exception("dict / non-dict conflict.")
            a[kb] = b[kb]
    return a


class TaskManager:
    def __init__(self, yaml_text, yaml_user_text, mainwnd, yaml_path):
        self.yaml_path = yaml_path
        self.config_dict = yaml.load(yaml_text)
        config_user_dict = None
        if yaml_user_text:
            config_user_dict = yaml.load(yaml_user_text)
        if config_user_dict:
            self.config_dict = merge_two_dicts(self.config_dict, config_user_dict)
        self.environment = None
        self.stopping = False
        if "globals" in self.config_dict:
            g = self.config_dict["globals"]
            if "environment" in g:
                self.environment = list()
                env = g["environment"]
                for k in env.keys():
                    self.environment.append( (k,env[k]) )
        self.tasks = []
        self.mainwnd = mainwnd
        validate_yaml(self.config_dict)
        # Setup tasks
        for step in self.config_dict['buildsteps']:
            self.tasks.append( tasks_tuple(dict=step, status=NOT_STARTED,
                                            dependencies=step["dependencies"],
                                            id=step["id"], timein=None, timeend=None, parent_tree_item=None,
                                            is_optional=("optional" in step and step["optional"]),
                                            will_run_task=True, error_code=0,
                                            tabs_ix=0, line_flush=10,
                                            time_tree_item=QStandardItem("time:") ) )

        # Add Tree Items
        tree_items = self.mainwnd.enqueueTreeBuildTasks( [(x.dict['title'], x.dict['description']) for x in self.tasks] )
        an_item = None
        for i in range(0, len(self.tasks)):
            self.tasks[i] = self.tasks[i]._replace(parent_tree_item=tree_items[i][1])
            self.tasks[i].parent_tree_item.appendRow( [ self.tasks[i].time_tree_item ] )
            if self.tasks[i].is_optional:
                parent = self.tasks[i].parent_tree_item
                an_item = parent
                parent.setCheckable(True)
                parent.setCheckState(QtCore.Qt.Checked)
        if an_item:
            an_item.model().itemChanged.connect( self.TreeItemChanged )
        self.mainwnd.treeView.expandAll()
    
    def TreeItemChanged(self, dunno):
        for i in range(0, len(self.tasks)):
            task = self.tasks[i]
            parent_tree_item = task.parent_tree_item
            self.tasks[i] = task._replace(will_run_task=is_checked(parent_tree_item))
            task = self.tasks[i] 
            parent_tree_item.setForeground(ForegroundForTask(task))
        
    def launch_task(self, task_index):
        self.tasks[task_index].parent_tree_item.setForeground(ForegroundForTask(self.tasks[task_index]))
        self.tasks[task_index] = self.tasks[task_index]._replace(timein=time.time())
        
        if "inline_script_py" in self.tasks[task_index].dict:
            tab_ix = self.mainwnd.enqueue_tab(self.tasks[task_index].dict["title"])
            self.tasks[task_index] = self.tasks[task_index]._replace(tabs_ix=tab_ix, line_flush=10)
            tt = self.mainwnd.tabs[tab_ix]
            proc = PythonTask(self, self.tasks[task_index].dict["inline_script_py"], self.tasks[task_index],
                              environment = self.environment)
            self.mainwnd.tabs[tab_ix] = self.mainwnd.tabs[tab_ix]._replace(qprocess=proc)
            # ...
        elif "inline_script_sh" in self.tasks[task_index].dict:
            tab_ix = self.mainwnd.enqueue_tab(self.tasks[task_index].dict["title"])
            self.tasks[task_index] = self.tasks[task_index]._replace(tabs_ix=tab_ix, line_flush=10)
            tt = self.mainwnd.tabs[tab_ix]
            proc = BashCommandTask(self, self.tasks[task_index].dict["inline_script_sh"], self.tasks[task_index],
                                  environment = self.environment)
            self.mainwnd.tabs[tab_ix] = self.mainwnd.tabs[tab_ix]._replace(qprocess=proc)
            # ...
        elif "inline_script_bat" in self.tasks[task_index].dict:
            tab_ix = self.mainwnd.enqueue_tab(self.tasks[task_index].dict["title"])
            self.tasks[task_index] = self.tasks[task_index]._replace(tabs_ix=tab_ix, line_flush=10)
            tt = self.mainwnd.tabs[tab_ix]
            proc = WinCommandTask(self, self.tasks[task_index].dict["inline_script_bat"], self.tasks[task_index],
                                   workingDir = self.yaml_path, environment = self.environment)
            self.mainwnd.tabs[tab_ix] = self.mainwnd.tabs[tab_ix]._replace(qprocess=proc)
            # ...
        elif "message" in self.tasks[task_index].dict:
            tab_ix = self.mainwnd.enqueue_tab(self.tasks[task_index].dict["title"])
            # Show the message
            m = QtGui.QMessageBox(self.mainwnd)
            m.setText(self.tasks[task_index].dict["message"])
            m.setWindowModality(Qt.WindowModal)
            m.exec_()
            # ...
            self.tasks[task_index] = self.tasks[task_index]._replace(tabs_ix=tab_ix, line_flush=10)
            tt = self.mainwnd.tabs[tab_ix]
            proc = PythonTask(self, "print('The user was shown the message.')", self.tasks[task_index],
                                   environment = self.environment)
            self.mainwnd.tabs[tab_ix] = self.mainwnd.tabs[tab_ix]._replace(qprocess=proc)
    
    def finished_task(self, exitcode, task_index):
        task = self.tasks[task_index]._replace(status=DONE, timeend=time.time())
        if exitcode!=0:
            task = task._replace(error_code = exitcode)
        self.tasks[task_index] = task
        time_delta = task.timeend-task.timein
        time_delta = dt.datetime.utcfromtimestamp(time_delta)
        time_delta = "time: " + time_delta.strftime('%H:%M:%S')
        task.time_tree_item.setText( time_delta )
        task.parent_tree_item.setForeground( ForegroundForTask(task) )
        if exitcode==0:
            self.run_loop()
        
    def run_loop_init(self):
        self.stopping = False
        for i in range(0, len(self.tasks)):
            self.tasks[i] = self.tasks[i]._replace(status=NOT_STARTED)
            if not self.tasks[i].will_run_task:
                self.tasks[i] = self.tasks[i]._replace(status=DONE)
            
    def run_loop(self):
        TASKS_BEGIN = -1
        if all_tasks_done(self.tasks):
            return
        if not self.stopping:
            result = self.start_another_task_if_possible()
    
    def stop(self):
        self.stopping = True
        for tab_ix in range(0, len(self.mainwnd.tabs)):
            qp = self.mainwnd.tabs[tab_ix].qprocess
            if qp:
                qp.terminate()
                if not qp.waitForFinished(msecs=10000):
                    qp.kill()
            self.mainwnd.tabs[tab_ix] = self.mainwnd.tabs[tab_ix]._replace(qprocess=None)

    def start_another_task_if_possible(self):
        # Count number of running tasks
        tasks_running = 0
        for x in self.tasks:
            if x.status==RUNNING: tasks_running+=1
        
        # Try to find an unstarted task with dependencies fulfilled - if so, start it
        for i in range(0,len(self.tasks)):
            if can_task_be_started(self.tasks[i], self.tasks):
                self.tasks[i] = self.tasks[i]._replace(status=RUNNING)
                self.launch_task(i)
                return True
        if tasks_running==0:
            raise TaskDependencyFault()
        return False

    def write_process_output(self, process, is_finished, task):
        time_delta = time.time()-task.timein
        time_delta = dt.datetime.utcfromtimestamp(time_delta)
        time_delta = "time: " + time_delta.strftime('%H:%M:%S')
        task.time_tree_item.setText( time_delta )
        self.mainwnd.write_process_output(process, is_finished, task.line_flush, task.tabs_ix)

    def finished(self, exitcode, task, process):
        self.mainwnd.write_process_output(process, True, task.line_flush, task.tabs_ix)
        task_index = self.tasks.index(task)
        self.finished_task( exitcode, task_index)
