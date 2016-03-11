#!/bin/python

from PySide import QtGui
from PySide import QtCore
from PySide.QtCore import QProcess
from test_scripts import PY_SCRIPT_PRIMES_TO_N
from collections import namedtuple

tabs_type = namedtuple("tabs_type", ['edit', 'label', 'textread', 'lastlines'])

class MainWnd(QtGui.QMainWindow):
    
    def __init__(self):
        super(MainWnd, self).__init__()
        self.tabs = None    # list of tabs_type namedtuples
        self.processes = []
        self.initUI()

    def initUI(self):
        widget = QtGui.QWidget()
        hb = QtGui.QHBoxLayout()
        tv = QtGui.QTreeView()
        self.initTreeView(tv)
        hb.addWidget(tv)
        self.initUI2(hb)
        widget.setLayout(hb)
        self.setCentralWidget(widget)

    def initTreeView(self, tv):
        from PySide.QtGui import QStandardItem, QStandardItemModel
        tv.setSizePolicy( QtGui.QSizePolicy( QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding ) )
        tvm = QStandardItemModel()
        parent = QStandardItem("A")
        parent.appendRow([QStandardItem("B1")])
        parent.appendRow([QStandardItem("B2")])
        tvm.appendRow(parent)
        parent = QStandardItem("C")
        parent.appendRow([QStandardItem("D1")])
        tvm.appendRow(parent)
        tv.setModel(tvm)
    
    def initUI2(self, hb):
        mdiArea = QtGui.QTabWidget()
        hb.addWidget(mdiArea);

        def StyledTextEdit():
            rv = QtGui.QTextEdit()
            # rv.setStyle('{ font: "Courier New" }')
            return rv
        
        self.tabs = [tabs_type(edit=StyledTextEdit(), label="1", textread="", lastlines=-1), \
                      tabs_type(edit=StyledTextEdit(), label="2", textread="", lastlines=-1)]
        mdiArea.addTab( self.tabs[0].edit, self.tabs[0].label)
        mdiArea.addTab( self.tabs[1].edit, self.tabs[1].label )

        exitAction = QtGui.QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        runAction = QtGui.QAction('Run', self)
        runAction.setShortcut('Ctrl+R')
        runAction.triggered.connect(self.run)

        runActionPy = QtGui.QAction('Run Python', self)
        runActionPy.setShortcut('Ctrl+P')
        runActionPy.triggered.connect(self.run_python)
        
        sb = self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        fileMenu.addAction(runAction)
        fileMenu.addAction(runActionPy)

        #toolbar = self.addToolBar('Exit')
        #toolbar.addAction(exitAction)
        
        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Main window')    
        self.show()        

    def run(self):
        p = QtCore.QProcess(self)
        self.processes.append(p)
        p.readyReadStandardOutput.connect( lambda: self.write_process_output(p, False, 100) )
        p.finished.connect( lambda x : self.write_process_output(p, True, 100) )
        #p.start("find", ["/home/andy/dev"])
        #p.start("find", ["/home/andy"])
        p.start("msbuild", [R"""D:\Projects\Vemnet068\7d\trunk\CommonCode\BuildAll\WinProj\BuildCommonCode.sln""", "/t:Build", "/p:Configuration=Release"])

    def run_python(self):
        p = QtCore.QProcess(self)
        self.processes.append(p)
        p.readyReadStandardOutput.connect( lambda: self.write_process_output(p, False, 10) )
        p.readyReadStandardError.connect( lambda: self.write_process_output(p, False, 10) )
        p.finished.connect( lambda x : self.write_process_output(p, True, 10) )
        p.start("python", ["-", str(10000)])
        p.waitForStarted()
        p.write(PY_SCRIPT_PRIMES_TO_N)
        p.closeWriteChannel()
    
    def write_process_output(self, process, finish, line_flush):
        print("Process exit-code = {}".format(process.exitCode()))
        t = str( process.readAllStandardOutput() )
        old = self.tabs[0]
        newText = old.textread + t
        nLines = newText.count("\n") / line_flush
        self.tabs[0] = tabs_type(edit=old.edit, label=old.label, textread=newText, lastlines=nLines)
        if old.lastlines != nLines or finish:
            old[0].append( t )
