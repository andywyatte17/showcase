#!/bin/python

from PySide import QtCore

class ScopeGuard:
    '''
    ScopeGuard / ScopeExit-like object - use keyword 'with' to ensure a method is called at scope
      exit, even if an exception is thrown.
      
    Example:
    def fn():
        ... do some setup requiring unsetup(...) ...
        with ScopeGuard( lambda : unsetup(...) ) as sg:
          DoSomeStuff()
    '''
    def __init__(self, exit_action):
        self.exit_action = exit_action
    def __enter__(self):
        return self
    def __exit__(self, x_type, x_value, x_traceback ):
        self.exit_action()

class Enum(object): 
    '''
    Enum - Simple Enum type.
    Example DIRECTION = Enum(("UP", "DOWN"))

    Found at: http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
    '''
    def __init__(self, tupleList):
            self.tupleList = tupleList

    def __getattr__(self, name):
            return self.tupleList.index(name)
            
def RestoreGeom(q_main_window):
    '''
        Restore the location of a QMainWindow object.
    '''
    g = q_main_window.settings.value("geometry")
    ws = None
    if g:
        ws = q_main_window.settings.value("windowState")
    if g and ws:
        q_main_window.restoreGeometry(g)
        q_main_window.restoreState(ws)

def SaveGeom(q_main_window):
    '''
        Save the location of a QMainWindow object.
    '''
    q_main_window.settings.setValue("geometry", q_main_window.saveGeometry())
    q_main_window.settings.setValue("windowState", q_main_window.saveState())
        
