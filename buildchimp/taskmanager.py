#!/bin/python

import yaml
from collections import namedtuple
from pprint import pprint
import threading, time

NOT_STARTED=0
RUNNING=1
DONE_ERROR=2
DONE_OK=3

def validate_yaml(yaml_dict):
    # TODO: ...
    return

def can_task_be_started(nt, all_tasks):
    # A task can be started if the task has all dependencies met
    if nt.status!=NOT_STARTED: return False
    for id in ([] if not nt.dependencies else nt.dependencies):
        for others in [x for x in all_tasks if x!=id]:
            if id==others.id and others.status!=DONE_OK:
                return False
    return True

def all_tasks_done(all_tasks):
    return len(all_tasks) == sum(1 if x.status==DONE_OK else 0 for x in all_tasks)

class TaskManager:
    def __init__(self, yaml_text, mainWnd):
        self.config_dict = yaml.load(yaml_text)
        self.mainWnd = mainWnd
        validate_yaml(self.config_dict)
    
    def launch_task(self, task_index, tasks):
        task = tasks[task_index]
        print(task)
        time.sleep(10)
        tasks[task_index] = task._replace(status=DONE_OK)
        # TODO: ...
        
    def run(self):
        nt = namedtuple("tasks", ["dict", "status", "dependencies", "id"])
        tasks = []
        for step in self.config_dict['buildsteps']:
            tasks.append( nt(dict=step, status=NOT_STARTED,
                             dependencies=step["dependencies"],
                             id=step["id"]) )
        while True:
            # Look for a task with status 0 to start
            if all_tasks_done(tasks):
                break
            for i in range(0,len(tasks)):
                task = tasks[i]
                if can_task_be_started(task, tasks):
                    tasks[i] = task._replace(status=RUNNING)
                    self.launch_task(i, tasks)
                    break
            time.sleep(2)
                    