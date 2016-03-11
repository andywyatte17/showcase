#!/bin/python

from PySide import QtCore
from tabstype import TabsType

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

def MsBuildTask(parent, tabsType, tabs_ix, sln, configuration):
    '''
        tabsType is 'TabsType' - edit/label/textread/lastlines
        ...
    '''
    proc = QtCore.QProcess(parent)
    line_flush = 10
    proc.readyReadStandardOutput.connect( lambda: parent.write_process_output(proc, False, line_flush, tabs_ix) )
    proc.readyReadStandardError.connect( lambda: parent.write_process_output(proc, False, line_flush, tabs_ix) )
    proc.finished.connect( lambda x : parent.write_process_output(proc, True, line_flush, tabs_ix) )
    proc.start("msbuild",
            [sln,
            "/t:Rebuild",
            "/p:Configuration={}".format(configuration)])
    return proc

def PythonPrimesTask(parent, tabsType, tabs_ix):
    '''
       ...
    '''
    proc = QtCore.QProcess(parent)
    line_flush = 10
    proc.readyReadStandardOutput.connect( lambda: parent.write_process_output(proc, False, line_flush, tabs_ix) )
    proc.readyReadStandardError.connect( lambda: parent.write_process_output(proc, False, line_flush, tabs_ix) )
    proc.finished.connect( lambda x : parent.write_process_output(proc, True, line_flush, tabs_ix) )
    proc.start("python", ["-", str(10000)])
    proc.waitForStarted()
    proc.write(_PY_SCRIPT_PRIMES_TO_N)
    proc.closeWriteChannel()
    return proc
