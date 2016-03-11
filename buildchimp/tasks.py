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

def WinCommandTask(parent, cmd_source, tabsType, tabs_ix):
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
    proc = QtCore.QProcess(parent)
    line_flush = 10
    proc.readyReadStandardOutput.connect( lambda: parent.write_process_output(proc, False, line_flush, tabs_ix) )
    proc.readyReadStandardError.connect( lambda: parent.write_process_output(proc, False, line_flush, tabs_ix) )
    proc.finished.connect( lambda x : parent.write_process_output(proc, True, line_flush, tabs_ix) )
    proc.start("cmd.exe", ["/c", f.fileName()])
    return proc

    
def MsBuildTask(parent, tabsType, tabs_ix, sln, configuration):
    src = R'''msbuild "{}" /t:Rebuild /p:Configuration="{}"'''.format(sln, configuration)
    return WinCommandTask(parent, src, tabsType, tabs_ix)
    
    
def PythonTask(parent, pysource, line_flush, tabsType, tabs_ix, pyargs=None):
    '''
       Launch a task based on some python source code.
    '''
    proc = QtCore.QProcess(parent)
    proc.readyReadStandardOutput.connect( lambda: parent.write_process_output(proc, False, line_flush, tabs_ix) )
    proc.readyReadStandardError.connect( lambda: parent.write_process_output(proc, False, line_flush, tabs_ix) )
    proc.finished.connect( lambda x : parent.write_process_output(proc, True, line_flush, tabs_ix) )
    args = ["-"]
    if pyargs:
        args = args + pyargs
    proc.start("python", args)
    proc.waitForStarted()
    proc.write(pysource)
    proc.closeWriteChannel()
    return proc
    
    
def PythonPrimesTask(parent, tabsType, tabs_ix):
    '''
       ...
    '''
    return PythonTask(parent, _PY_SCRIPT_PRIMES_TO_N, 10, tabsType, tabs_ix, ["10000"])
