#!/bin/python

from PySide import QtGui
from PySide import QtCore
from PySide.QtCore import QProcess
from PySide.QtCore import Qt
from test_scripts import PY_SCRIPT_PRIMES_TO_N
from threading import Lock, Thread
from PySide.QtGui import QStandardItem, QStandardItemModel
import tasks
from tabstype import *
import taskmanager
#import quickxpm

class ScopeGuard:
    def __init__(self, exit_action):
        self.exit_action = exit_action
    def __enter__(self):
        return self
    def __exit__(self, x_type, x_value, x_traceback ):
        self.exit_action()

def RestoreGeom(some_obj):
    some_obj.settings = QtCore.QSettings("net.ghuisoft", "buildchimp")
    g = some_obj.settings.value("geometry")
    ws = None
    if g:
        ws = some_obj.settings.value("windowState")
    if g and ws:
        some_obj.restoreGeometry(g)
        some_obj.restoreState(ws)

def SaveGeom(some_obj):
    some_obj.settings.setValue("geometry", some_obj.saveGeometry())
    some_obj.settings.setValue("windowState", some_obj.saveState())
        
class MainWnd(QtGui.QMainWindow):
    
    def __init__(self):
        super(MainWnd, self).__init__()
        self.tabs = []    # list of TabsType objects (namedtuples)
        self.filter = None
        self.treeView, self.treeViewModel = None,None
        self.text_change_mutex = Lock()
        self.paused = False
        self.tabCtrl = None
        self.proc_terminated = False
        self.taskManager = None
        self.threads = []
        self.initUI()
        RestoreGeom(self)

    def initUI(self):
        widget = QtGui.QWidget()
        total_layout = QtGui.QVBoxLayout()
        top = self.makeTopLayout()
        bottom = self.makeBottomLayout()
        self.initUI2(bottom)
        total_layout.addLayout(top)
        total_layout.addLayout(bottom)
        widget.setLayout(total_layout)
        self.setCentralWidget(widget)

    def makeTopLayout(self):
        """Make a QHBoxLayout containing clickable buttons like 'Pause', and filters ('errors', 'warnings'...)"""
        top = QtGui.QHBoxLayout()
        top.setAlignment( Qt.AlignLeft )

        btn = QtGui.QPushButton("Pause")
        btn.setCheckable(True)
        btn.pressed.connect( self.toggle_paused )
        top.addWidget( btn )
        
        for label,str in ( ("error(s)","error(s)"), ("warning(s)","warning(s)"),
                            ("building","building"), (" vs warning ", "warning "),
                            ("{}",None) ):
            btn = QtGui.QPushButton(label)
            btn.setMaximumWidth(100)
            btn.setMaximumHeight(30)
            btn.released.connect( lambda self=self, str=str: self.filter_fn(str) )
            top.addWidget( btn )

        return top
        
    def makeBottomLayout(self):
        bottom = QtGui.QHBoxLayout()
        self.treeView = QtGui.QTreeView()
        tv = self.treeView
        self.treeViewModel = QStandardItemModel()
        tvm = self.treeViewModel
        tvm.setHorizontalHeaderLabels (["Build Tasks"])
        tv.setSizePolicy( QtGui.QSizePolicy( QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding ) )
        tv.setModel(tvm)
        bottom.addWidget(tv)
        self.enqueueTreeBuildTasks( [("Build CC Debug", "Build..."), ("Build CC Release", "Build...")] )
        return bottom

    def enqueueTreeBuildTasks(self, listOfTasksAndDescriptions):
        '''
           returns list( (taskLabel, parent QStandardItem) )
        '''
        tvm = self.treeViewModel
        tvm.clear()
        results = []
        for label,description in listOfTasksAndDescriptions:
            parent = QStandardItem(label)
            parent.appendRow([QStandardItem(description)])
            tvm.appendRow(parent)
            results.append( (label, parent) )
        return results

    def enqueue_tab(self, label):
        def StyledTextEdit():
            rv = QtGui.QTextEdit()
            rv.setStyleSheet('font-family: "Andale Mono", "Courier New", "Lucida Console", Monaco, monospace;' +
                             'font-size: 10px;')
            return rv

        tt = TabsType(edit=StyledTextEdit(), label=label, textread="", lastlines=-1, qprocess=None)
        self.tabs.append(tt)
        tab_ix = len(self.tabs)-1
        self.tabCtrl.addTab( tt.edit, tt.label)
        self.tabCtrl.setCurrentIndex(tab_ix)
        return tab_ix
   
    def initUI2(self, hb):
        tabCtrl = QtGui.QTabWidget()
        self.tabCtrl = tabCtrl
        hb.addWidget(tabCtrl);

        actions = []
        for label, cut, action_fn in (
                                     ("Open YAML task file...", "Ctrl+O", self.open_yaml_task),
                                     ("MsBuild CommonCode - Debug", "Ctrl+1", self.run_msbuild_cc_dbx),
                                     ("MsBuild AllExes - Debug", "Ctrl+2", self.run_msbuild_exes_dbx),
                                     ("Python Primes", "Ctrl+3", self.run_python),
                                     ("Exit", "Ctrl+Q", self.close)
                                   ):
            action = QtGui.QAction(label, self)
            action.setShortcut(cut)
            action.triggered.connect(action_fn)
            actions.append(action)
        
        sb = self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        for act in actions:
            fileMenu.addAction(act)
        
        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('BuildChimp')    
        self.show()        

    def run_msbuild_cc_dbx(self):
        sln = R"""D:\Projects\Vemnet068\7d\trunk\CommonCode\BuildAll\WinProj\BuildCommonCode.sln"""
        tabs_ix = self.enqueue_tab("MsBuild CC Dbx")
        self.tabs[tabs_ix] = ClearText(self.tabs[tabs_ix])
        proc = tasks.MsBuildTask(self, self.tabs[tabs_ix], tabs_ix, sln, "Debug")
        self.tabs[tabs_ix] = self.tabs[tabs_ix]._replace(qprocess=proc)

    def run_msbuild_exes_dbx(self):
        sln = R"""D:\Projects\Vemnet068\7d\trunk\Applications\AllExes\AllExes.sln"""
        tabs_ix = self.enqueue_tab("MsBuild Exes Dbx")
        self.tabs[tabs_ix] = ClearText(self.tabs[tabs_ix])
        proc = tasks.MsBuildTask(self, self.tabs[tabs_ix], tabs_ix, sln, "Debug")
        self.tabs[tabs_ix] = self.tabs[tabs_ix]._replace(qprocess=proc)
        
    def run_python(self):
        tabs_ix = self.enqueue_tab("Python Primes")
        self.tabs[tabs_ix] = ClearText(self.tabs[tabs_ix])
        proc = tasks.PythonPrimesTask(self, self.tabs[tabs_ix], tabs_ix)
        self.tabs[tabs_ix] = self.tabs[tabs_ix]._replace(qprocess=proc)

    def toggle_paused(self):
        self.paused = not self.paused
        if not self.paused:
            self.filter_fn( self.filter )   # Bump a change in texts
        
    def filter_fn(self, filter):
        self.text_change_mutex.acquire()
        with ScopeGuard(self.text_change_mutex.release) as sg:
            self.filter = filter
            for x in self.tabs:
                edit = x.edit
                text = x.textread
                edit.setText( self.apply_filter(text, self.filter) )

    def apply_filter(self, text, filter):
        if not filter: return text
        x = text.split("\n")
        return "\n".join( [y for y in x if filter in y.lower()] )
    
    def write_process_output(self, process, finish, line_flush, tabs_ix):
        if self.proc_terminated:
            return
        self.text_change_mutex.acquire()
        with ScopeGuard(self.text_change_mutex.release) as sg:
            t = str( process.readAllStandardOutput() )
            t += str( process.readAllStandardError() )
            if finish:
                t = t + "\n" + "Process exit-code = {}".format(process.exitCode())
            old = self.tabs[tabs_ix]
            newText = old.textread + t
            nLines = newText.count("\n") / line_flush
            self.tabs[tabs_ix] = old._replace(textread=newText, lastlines=nLines)
            if not self.paused and old.lastlines != nLines or finish:
                old.edit.setText( self.apply_filter(newText, self.filter) )

    def warn_fn(self):
        '''
            Yes = user clicked 'Ok', No - user clicked 'Cancel'
        '''
        res = QtGui.QMessageBox.warning(self, "Closing",
            "Processes are still running - do you want to quit?",
            QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
        if res==QtGui.QMessageBox.Ok:
            for x in self.tabs:
                if x.qprocess:
                    x.qprocess.kill()
            return 
            
    def open_yaml_task(self):
        file = QtGui.QFileDialog.getOpenFileName(filter="YAML buildchimp files (*.yaml)")
        if file:
            self.taskManager = taskmanager.TaskManager( open(file[0]).read(), self )
            thread = Thread(target = self.taskManager.run())
            thread.start()
          
    def closeEvent(self, event):
        SaveGeom(self)
        print("event={}".format(event))
    
        if not self.tabs or len(self.tabs)==0:
            return self.close()
        for x in self.tabs:
            print(x.qprocess.state())
            if x.qprocess and x.qprocess.state()!=QtCore.QProcess.NotRunning:
                return self.warn_fn()
                
        self.proc_terminated = True
        for x in self.tabs:
            proc = x.qprocess
            if proc and proc.state()!=QtCore.QProcess.NotRunning:
                print("Killing {}", proc)
                proc.terminate()
