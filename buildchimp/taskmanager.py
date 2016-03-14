#!/bin/python

import yaml
from collections import namedtuple
from pprint import pprint
import threading, time
from lib import ScopeGuard
from tasks import *
from  PySide.QtCore import QProcess

NOT_STARTED=0
RUNNING=1
DONE=2

tasks_tuple = namedtuple("tasks", ["dict", "status", "dependencies", "id"])

def validate_yaml(yaml_dict):
    # TODO: ...
    return

def can_task_be_started(nt, all_tasks):
    # A task can be started if the task has all dependencies met
    if nt.status!=NOT_STARTED: return False
    for id in ([] if not nt.dependencies else nt.dependencies):
        for others in [x for x in all_tasks if x!=id]:
            if id==others.id and others.status!=DONE:
                return False
    return True

def all_tasks_done(all_tasks):
    return len(all_tasks) == sum(1 if x.status==DONE else 0 for x in all_tasks)

class TaskDependencyFault:
    pass

class TaskManager:
    def __init__(self, yaml_text, main_wnd):
        self.config_dict = yaml.load(yaml_text)
        self.tasks = []
        self.main_wnd = main_wnd
        validate_yaml(self.config_dict)
        # Setup tasks
        for step in self.config_dict['buildsteps']:
            self.tasks.append( tasks_tuple(dict=step, status=NOT_STARTED,
                                            dependencies=step["dependencies"],
                                            id=step["id"]) )
    
    def launch_task(self, task_index):
        task = self.tasks[task_index]
        print("\nlaunch_task")
        print(task)
        print("\n")
        if "inline_script_py" in task.dict:
            tab_ix = self.main_wnd.enqueue_tab(task.dict["title"])
            tt = self.main_wnd.tabs[tab_ix]
            proc = PythonTask(self.main_wnd, task.dict["inline_script_py"], 10, tt, tab_ix,
                                  lambda exitcode, self=self, task_index=task_index : self.finished_task(task_index))
            self.main_wnd.tabs[tab_ix] = self.main_wnd.tabs[tab_ix]._replace(qprocess=proc)
        elif "inline_script_sh" in task.dict:
            pass # TODO: ...
        elif "inline_script_bat" in task.dict:
            tab_ix = self.main_wnd.enqueue_tab(task.dict["title"])
            tt = self.main_wnd.tabs[tab_ix]
            proc = WinCommandTask(self.main_wnd, task.dict["inline_script_bat"], 10, tt, tab_ix,
                                  lambda exitcode, self=self, task_index=task_index : self.finished_task(task_index))
            self.main_wnd.tabs[tab_ix] = self.main_wnd.tabs[tab_ix]._replace(qprocess=proc)
    
    def finished_task(self, task_index):
        self.tasks[task_index] = self.tasks[task_index]._replace(status=DONE)
        self.run_loop()
        
    def run_loop(self):
        print("run_loop")
        TASKS_BEGIN = -1
        if all_tasks_done(self.tasks):
            print("run_loop: all_tasks_done")
            return
        result = self.start_another_task_if_possible()
        print("run_loop: start_another_task_if_possible = {}".format(result))
    
    def start_another_task_if_possible(self):
        # Count number of running tasks
        tasks_running = 0
        for x in self.tasks:
            if x.status==RUNNING: tasks_running+=1

        print("\n\nstart_another_task_if_possible")
        for task in self.tasks: pprint(task)
        print("\n")
        
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
