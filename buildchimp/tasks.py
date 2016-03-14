#!/bin/python

from PySide import QtCore
from tabstype import TabsType
from PySide.QtCore import QTemporaryFile

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
    
def WinCommandTask(parent, cmd_source, line_flush, tabsType, tabs_ix, finished_action):
    '''
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
    process.readyReadStandardOutput.connect( lambda parent=parent, process=process, line_flush=line_flush, tabs_ix=tabs_ix :
                                                  parent.write_process_output(process, False, line_flush, tabs_ix) )
    process.readyReadStandardError.connect( lambda parent=parent, process=process, line_flush=line_flush, tabs_ix=tabs_ix :
                                                  parent.write_process_output(process, False, line_flush, tabs_ix) )
    process.finished.connect( lambda exitcode, finished_action=finished_action, parent=parent, process=process,
                                      line_flush=line_flush, tabs_ix=tabs_ix :
                                          Finished(exitcode, parent, process, line_flush, tabs_ix, finished_action) )
    process.start("cmd.exe", ["/c", f.fileName()])
    return process

    
def MsBuildTask(parent, tabsType, tabs_ix, sln, configuration):
    src = R'''msbuild "{}" /t:Rebuild /p:Configuration="{}"'''.format(sln, configuration)
    return WinCommandTask(parent, src, tabsType, tabs_ix)
    
    
def PythonTask(parent, pysource, line_flush, tabsType, tabs_ix, finished_action, pyargs=None):
    '''
       Launch a task based on some python source code.
    '''
    process = QtCore.QProcess(parent)
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
    
    
def PythonPrimesTask(parent, tabsType, tabs_ix):
    '''
       ...
    '''
    return PythonTask(parent, _PY_SCRIPT_PRIMES_TO_N, 10, tabsType, tabs_ix, ["10000"])
