#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PySide tutorial 

This program creates a skeleton of
a classic GUI application with a menubar,
toolbar, statusbar and a central widget. 

author: Jan Bodnar
website: zetcode.com 
last edited: August 2011
"""

import sys
from PySide import QtGui
from PySide import QtCore
from PySide.QtCore import QProcess

class Example(QtGui.QMainWindow):
    
    def __init__(self):
        super(Example, self).__init__()
        self.tabs = None
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
            rv.setStyle('{ font: "Courier New" }')
            return rv
        
        self.tabs = [(StyledTextEdit(), "1", "", -1), (StyledTextEdit(), "2", "", -1)]
        mdiArea.addTab( self.tabs[0][0], self.tabs[0][1] )
        mdiArea.addTab( self.tabs[1][0], self.tabs[1][1] )

        exitAction = QtGui.QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        runAction = QtGui.QAction('Run', self)
        runAction.setShortcut('Ctrl+R')
        runAction.triggered.connect(self.run)

        sb = self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        fileMenu.addAction(runAction)

        #toolbar = self.addToolBar('Exit')
        #toolbar.addAction(exitAction)
        
        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Main window')    
        self.show()        

    def run(self):
        p = QtCore.QProcess(self)
        self.processes.append(p)
        p.readyReadStandardOutput.connect( lambda: self.write_process_output(p, False) )
        p.finished.connect( lambda x : self.write_process_output(p, True) )
        #p.start("find", ["/home/andy/dev"])
        #p.start("find", ["/home/andy"])
        p.start("msbuild", [R"""D:\Projects\Vemnet068\7d\trunk\CommonCode\BuildAll\WinProj\BuildCommonCode.sln""", "/t:Build", "/p:Configuration=Release"])

    def write_process_output(self, process, finish):
        t = str( process.readAllStandardOutput() )
        old = self.tabs[0]
        newText = old[2] + t
        nLines = newText.count("\n") / 100
        self.tabs[0] = (old[0], old[1], newText, nLines)
        if old[3] != nLines or finish:
            old[0].append( t )
            print("spew")

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

