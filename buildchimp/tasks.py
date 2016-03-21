#!/bin/python

from PySide import QtCore
from tabstype import TabsType
from PySide.QtCore import QTemporaryFile
import os

_PY_SCRIPT_PRIMES_TO_N = R'''
import sys
n = int(sys.argv[1])
print("Primes to {}".format(n))
p = 2
while p <= n:
        for i in range(2, p):
                if p%i == 0:
                        p=p+1 
        print("%s" % p)
        p=p+1
print("Done")
'''

def Finished(exitcode, parent, process, line_flush, tabs_ix, finished_action):
    print("FinishTask")
    parent.write_process_output(process, True, line_flush, tabs_ix)
    finished_action(exitcode)

def ApplyEnvironment(qprocess, environment):
    # Push environment into python environment - this should ensure that os.path.expandvars
    #   works correctly when there are vars within vars
    old_os_environ = os.environ
    try:
        for var,val in environment:
            os.environ[var] = val
        if environment:
            env = QtCore.QProcessEnvironment.systemEnvironment()
            for var,val in environment:
                env.insert(var, os.path.expandvars(val))
            qprocess.setProcessEnvironment(env)
    except:
        pass
    # Revert os.env
    os.environ = old_os_environ

def WinCommandTask(parent, cmd_source, line_flush, tabsType, tabs_ix, finished_action, environment=None):
    '''
       environment - list of tuples (EnvVarName, Value)
       Launch a task switch is effectively a windows bat file.
    '''
    f = QTemporaryFile()
    f.setFileTemplate( f.fileTemplate() + ".bat" )
    f.open()
    f.write(cmd_source)
    f.flush()
    f.close()
    f.setAutoRemove(False)
    process = QtCore.QProcess(parent)
    ApplyEnvironment(process, environment)
    process.readyReadStandardOutput.connect( lambda parent=parent, process=process, line_flush=line_flush, tabs_ix=tabs_ix :
                                                  parent.write_process_output(process, False, line_flush, tabs_ix) )
    process.readyReadStandardError.connect( lambda parent=parent, process=process, line_flush=line_flush, tabs_ix=tabs_ix :
                                                  parent.write_process_output(process, False, line_flush, tabs_ix) )
    process.finished.connect( lambda exitcode, finished_action=finished_action, parent=parent, process=process,
                                      line_flush=line_flush, tabs_ix=tabs_ix :
                                          Finished(exitcode, parent, process, line_flush, tabs_ix, finished_action) )
    process.start("cmd.exe", ["/c", f.fileName()])
    return process

def BashCommandTask(parent, term_source, line_flush, tabsType, tabs_ix, finished_action, environment=None):
    '''
       environment - list of tuples (EnvVarName, Value)
       Launch a task switch is effectively a windows bat file.
    '''
    f = QTemporaryFile()
    f.setFileTemplate( f.fileTemplate() )
    f.open()
    f.write(term_source)
    f.flush()
    f.close()
    f.setAutoRemove(False)
    process = QtCore.QProcess(parent)
    ApplyEnvironment(process, environment)
    process.readyReadStandardOutput.connect( lambda parent=parent, process=process, line_flush=line_flush, tabs_ix=tabs_ix :
                                                  parent.write_process_output(process, False, line_flush, tabs_ix) )
    process.readyReadStandardError.connect( lambda parent=parent, process=process, line_flush=line_flush, tabs_ix=tabs_ix :
                                                  parent.write_process_output(process, False, line_flush, tabs_ix) )
    process.finished.connect( lambda exitcode, finished_action=finished_action, parent=parent, process=process,
                                      line_flush=line_flush, tabs_ix=tabs_ix :
                                          Finished(exitcode, parent, process, line_flush, tabs_ix, finished_action) )
    process.start("bash", [f.fileName()])
    return process

def PythonTask(parent, pysource, line_flush, tabsType, tabs_ix, finished_action, environment=None, pyargs=None):
    '''
       Launch a task based on some python source code.
    '''
    process = QtCore.QProcess(parent)
    ApplyEnvironment(process, environment)
    process.readyReadStandardOutput.connect( lambda parent=parent, process=process, line_flush=line_flush, tabs_ix=tabs_ix :
                                                  parent.write_process_output(process, False, line_flush, tabs_ix) )
    process.readyReadStandardError.connect( lambda parent=parent, process=process, line_flush=line_flush, tabs_ix=tabs_ix :
                                                  parent.write_process_output(process, False, line_flush, tabs_ix) )
    process.finished.connect( lambda exitcode, finished_action=finished_action, parent=parent, process=process,
                                      line_flush=line_flush, tabs_ix=tabs_ix :
                                          Finished(exitcode, parent, process, line_flush, tabs_ix, finished_action) )
    args = ["-"]
    if pyargs:
        args = args + pyargs
    process.start("python", args)
    process.waitForStarted()
    process.write(pysource)
    process.closeWriteChannel()
    return process
    

def MsBuildTask(parent, tabsType, tabs_ix, sln, configuration):
    src = R'''msbuild "{}" /t:Rebuild /p:Configuration="{}"'''.format(sln, configuration)
    return WinCommandTask(parent, src, tabsType, tabs_ix)
    
        
def PythonPrimesTask(parent, tabsType, tabs_ix):
    '''
       ...
    '''
    return PythonTask(parent, _PY_SCRIPT_PRIMES_TO_N, 10, tabsType, tabs_ix, ["10000"])
