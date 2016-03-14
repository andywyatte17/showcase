#!/bin/python

class ScopeGuard:
    def __init__(self, exit_action):
        self.exit_action = exit_action
    def __enter__(self):
        return self
    def __exit__(self, x_type, x_value, x_traceback ):
        self.exit_action()
