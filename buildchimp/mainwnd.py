#!/bin/python

from PySide import QtGui
from PySide import QtCore
from PySide.QtCore import QProcess
from PySide.QtCore import Qt
from test_scripts import PY_SCRIPT_PRIMES_TO_N
from threading import Lock
from PySide.QtGui import QStandardItem, QStandardItemModel
import testtasks
from tabstype import *

class MainWnd(QtGui.QMainWindow):
    
    def __init__(self):
        super(MainWnd, self).__init__()
        self.tabs = []    # list of TabsType objects (namedtuples)
        self.processes = []
        self.filter = None
        self.treeView, self.treeViewModel = None,None
        self.text_change_mutex = Lock()
        self.paused = False
        self.tabCtrl = None
        self.initUI()

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
                            ("building","building"), ("Warning:", "Warning:"),
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
        self.initTreeViewModel(tvm)
        tv.setSizePolicy( QtGui.QSizePolicy( QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding ) )
        tv.setModel(tvm)
        bottom.addWidget(tv)
        return bottom

    def initTreeViewModel(self, tvm):
        parent = QStandardItem("A")
        parent.appendRow([QStandardItem("B1")])
        parent.appendRow([QStandardItem("B2")])
        tvm.appendRow(parent)
        parent = QStandardItem("C")
        parent.appendRow([QStandardItem("D1")])
        tvm.appendRow(parent)

    def enqueue_tab(self, label):
        def StyledTextEdit():
            rv = QtGui.QTextEdit()
            rv.setStyleSheet('font-family: "Andale Mono", "Courier New", "Lucida Console", Monaco, monospace;' +
                             'font-size: 10px;')
            return rv

        tt = TabsType(edit=StyledTextEdit(), label=label, textread="", lastlines=-1)
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
                                     ("MsBuild Debug", "Ctrl+1", self.run_msbuild_debug),
                                     ("MsBuild Release", "Ctrl+2", self.run_msbuild_release),
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

    def run_msbuild_debug(self):
        tabs_ix = self.enqueue_tab("MsBuild_Debug")
        self.tabs[tabs_ix] = ClearText(self.tabs[tabs_ix])
        proc = testtasks.MsBuildTask(self, self.tabs[tabs_ix], tabs_ix, "Debug")
        self.processes.append(proc)

    def run_msbuild_release(self):
        tabs_ix = self.enqueue_tab("MsBuild_Release")
        self.tabs[tabs_ix] = ClearText(self.tabs[tabs_ix])
        proc = testtasks.MsBuildTask(self, self.tabs[tabs_ix], tabs_ix, "Release")
        self.processes.append(proc)
        
    def run_python(self):
        tabs_ix = self.enqueue_tab("Python Primes")
        self.tabs[tabs_ix] = ClearText(self.tabs[tabs_ix])
        proc = testtasks.PythonPrimesTask(self, self.tabs[tabs_ix], tabs_ix)
        self.processes.append(proc)

    def toggle_paused(self):
        self.paused = not self.paused
        if not self.paused:
            self.filter_fn( self.filter )   # Bump a change in texts
        
    def filter_fn(self, filter):
        self.text_change_mutex.acquire()
        try:
            self.filter = filter
            for x in self.tabs:
                edit = x.edit
                text = x.textread
                edit.setText( self.apply_filter(text, self.filter) )
        finally:
            self.text_change_mutex.release()

    def apply_filter(self, text, filter):
        if not filter: return text
        x = text.split("\n")
        return "\n".join( [y for y in x if filter in y.lower()] )
    
    def write_process_output(self, process, finish, line_flush, tabs_ix):
        self.text_change_mutex.acquire()
        try:
            t = str( process.readAllStandardOutput() )
            if finish:
                t = t + "\n" + "Process exit-code = {}".format(process.exitCode())
            old = self.tabs[tabs_ix]
            newText = old.textread + t
            nLines = newText.count("\n") / line_flush
            self.tabs[tabs_ix] = old._replace(textread=newText, lastlines=nLines)
            if not self.paused and old.lastlines != nLines or finish:
                old.edit.setText( self.apply_filter(newText, self.filter) )
        finally:
            self.text_change_mutex.release()
