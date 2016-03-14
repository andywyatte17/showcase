#!/bin/python

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
            