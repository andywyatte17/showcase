#!/bin/python

from PySide import QtCore
from tabstype import TabsType
from PySide.QtCore import QTemporaryFile
import os


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
    os.environ = old_os_environ  # Revert os.environ


def WinCommandTask(taskmanager, cmd_source, task, environment=None):
    '''
       environment - list of tuples (EnvVarName, Value)
       Launch a task which is effectively a windows bat file.
    '''
    f = QTemporaryFile()
    f.setFileTemplate( f.fileTemplate() + ".bat" )
    f.open()
    f.write(cmd_source)
    f.flush()
    f.close()
    f.setAutoRemove(False)
    process = QtCore.QProcess()
    ApplyEnvironment(process, environment)
    process.readyReadStandardOutput.connect( lambda taskmanager=taskmanager, process=process, task=task :
                                                 taskmanager.write_process_output(process, False, task) )
    process.readyReadStandardError.connect( lambda taskmanager=taskmanager, process=process, task=task :
                                                taskmanager.write_process_output(process, False, task) )
    process.finished.connect( lambda exitcode, taskmanager=taskmanager, process=process, task=task :
                                  taskmanager.finished(exitcode, task, process) )
    process.start("cmd.exe", ["/c", f.fileName()])
    return process


def BashCommandTask(taskmanager, term_source, task, environment=None):
    '''
       environment - list of tuples (EnvVarName, Value)
       Launch a task which is effectively a bash script.
    '''
    f = QTemporaryFile()
    f.setFileTemplate( f.fileTemplate() )
    f.open()
    f.write(term_source)
    f.flush()
    f.close()
    f.setAutoRemove(False)
    process = QtCore.QProcess()
    ApplyEnvironment(process, environment)
    process.readyReadStandardOutput.connect( lambda taskmanager=taskmanager, process=process, task=task :
                                                 taskmanager.write_process_output(process, False, task) )
    process.readyReadStandardError.connect( lambda taskmanager=taskmanager, process=process, task=task :
                                                taskmanager.write_process_output(process, False, task) )
    process.finished.connect( lambda exitcode, taskmanager=taskmanager, process=process, task=task :
                                  taskmanager.finished(exitcode, task, process) )
    process.start("bash", [f.fileName()])
    return process


def PythonTask(taskmanager, pysource, task, environment=None, pyargs=None):
    '''
       Launch a task based on some python source code.
    '''
    process = QtCore.QProcess()
    ApplyEnvironment(process, environment)
    process.readyReadStandardOutput.connect( lambda taskmanager=taskmanager, process=process, task=task :
                                                 taskmanager.write_process_output(process, False, task) )
    process.readyReadStandardError.connect( lambda taskmanager=taskmanager, process=process, task=task :
                                                taskmanager.write_process_output(process, False, task) )
    process.finished.connect( lambda exitcode, taskmanager=taskmanager, process=process, task=task :
                                  taskmanager.finished(exitcode, task, process) )
    args = ["-"]
    if pyargs:
        args = args + pyargs
    process.start("python", args)
    process.waitForStarted()
    process.write(pysource)
    process.closeWriteChannel()
    return process

