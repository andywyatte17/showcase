#!/bin/python

from PySide import QtGui
from PySide import QtCore
from PySide.QtCore import QProcess
from PySide.QtCore import Qt
from threading import Lock, Thread
from PySide.QtGui import QStandardItem, QStandardItemModel
import tasks
from tabstype import *
import taskmanager
from lib import *
from taskmanager import Color
import time
import config
import sys
from webserver import Webserver

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
        self.filter_model = None
        self.settings = QtCore.QSettings()
        self.openRecentMenu = None
        self.initUI()
        self.qtimer = QtCore.QTimer()
        self.qtimer.timeout.connect( self.make_screenshot )
        self.qtimer.start( 5*1000 )
        self.webserver = None
        RestoreGeom(self)

    def make_screenshot(self):
        if self.webserver:
            pngPath = self.webserver.pngPath
            if pngPath:
                widget = self.centralWidget()
                r = widget.rect()
                pixmap = QtGui.QPixmap( r.size() )
                widget.render( pixmap, QtCore.QPoint(), QtGui.QRegion(r) )
                file = QtCore.QFile(pngPath)
                file.open(QtCore.QIODevice.WriteOnly)
                pixmap.save(file, "PNG")

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

        btn = QtGui.QPushButton("Run")
        btn.pressed.connect( self.run_yaml )
        top.addWidget( btn )

        btn = QtGui.QPushButton("Stop")
        btn.pressed.connect( self.stop_yaml )
        top.addWidget( btn )

        top.addWidget( QtGui.QLabel("Filters:") )
        
        model = QStandardItemModel()
        combo = QtGui.QComboBox()
        combo.setModel(model)
        self.filter_model = model

        ix = 0
        for label,str in config.FILTERS:
            item = QStandardItem(label)
            model.appendRow(item)
            combo.setItemData(ix, str)
            ix += 1

        combo.currentIndexChanged.connect( lambda ix, combo=combo : self.filter_combo_changed(ix, combo) )
        top.addWidget(combo)
        
        return top

    def makeBottomLeftLayout(self):
        bottom_left = QtGui.QVBoxLayout()
        self.treeView = QtGui.QTreeView()
        tv = self.treeView
        self.treeViewModel = QStandardItemModel()
        tvm = self.treeViewModel
        tvm.setHorizontalHeaderLabels (["Build Tasks"])
        tv.setSizePolicy( QtGui.QSizePolicy( QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding ) )
        tv.setModel(tvm)
        bottom_left.addWidget(tv)
        color_key = QtGui.QTextEdit()
        color_key.setFrameStyle( QtGui.QFrame.NoFrame )
        color_key.setReadOnly(True)
        color_key.setHtml('''
<b>Key:</b>
<p>
<ul>
  <li><span style="color:{blue}">Blue Items - Task is completed.</span></li>
  <li><span style="color:{gray}">Gray Items - Optional task is disabled.</span></li>
  <li><span style="color:{green}">Green Items - Task is running.</span></li>
  <li><span style="color:{black}">Black Items - Task is still to be run.</span></li>
</ul>
</p>
        '''.format(red=Color().Red().htmlCol, black=Color().Black().htmlCol, 
                   gray=Color().Gray().htmlCol, green=Color().Green().htmlCol,
                   blue=Color().Blue().htmlCol))
        color_key.setSizePolicy( QtGui.QSizePolicy( QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed ) )
        color_key.setFixedHeight(100)
        bottom_left.addWidget(color_key)
        return bottom_left
        
    def updateRecentFileList(self):
        menu = self.openRecentMenu
        menu.clear()
        paths = self.settings.value("recentPaths", [])
        if paths:
            for path in paths:
                action = QtGui.QAction(path, self)
                action.triggered.connect(lambda self=self, path=path : self.open_yaml_from_path(path))
                menu.addAction(action) 

    def makeBottomLayout(self):
        bottom = QtGui.QHBoxLayout()
        bottom.addLayout(self.makeBottomLeftLayout())
        # self.enqueueTreeBuildTasks( [("Build CC Debug", "Build..."), ("Build CC Release", "Build...")] )
        return bottom

    def enqueueTreeBuildTasks(self, listOfTasksAndDescriptions):
        '''
           returns list( (taskLabel, parent QStandardItem) )
        '''
        tvm = self.treeViewModel
        tvm.clear()
        tvm.setHorizontalHeaderLabels (["Build Tasks"])
        results = []
        for label,description in listOfTasksAndDescriptions:
            parent = QStandardItem(label)
            parent.appendRow([QStandardItem(description)])
            tvm.appendRow(parent)
            results.append( (label, parent) )
        return results

    def enqueue_tab(self, label):
        '''
           returns tab_ix - integer index of tab generated
        '''
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
        SEPARATOR = "separator"
        OPEN_RECENT_PLACEHOLDER = "OpenRecentPlaceholder"
        for x in ( ("Open YAML task file...", "Ctrl+O", self.open_yaml_task),
                    OPEN_RECENT_PLACEHOLDER,
                    SEPARATOR,
                    ("Run YAML tasks", "Ctrl+R", self.run_yaml),
                    ("Stop YAML tasks", "Ctrl+Shift+R", self.stop_yaml),
                    SEPARATOR,
                    ("Start Webserver", "", self.start_webserver),
                    ("Stop Webserver", "", self.stop_webserver),
                    SEPARATOR,
                    ("Exit", "Ctrl+Q", self.close)
                 ):
            if x==SEPARATOR:
                action = QtGui.QAction("", self)
                action.setSeparator(True)
                actions.append(action)
            elif x==OPEN_RECENT_PLACEHOLDER:
                actions.append(OPEN_RECENT_PLACEHOLDER)
            else:
                label, cut, action_fn = x
                action = QtGui.QAction(label, self)
                action.setShortcut(cut)
                action.triggered.connect(action_fn)
                actions.append(action)
        
        sb = self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        for act in actions:
            if act==OPEN_RECENT_PLACEHOLDER:
                self.openRecentMenu = QtGui.QMenu(title="Open Recent")
                fileMenu.addMenu(self.openRecentMenu)
                self.updateRecentFileList()
            else:
                fileMenu.addAction(act)
        
        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('BuildChimp')    
        self.show()        

    def toggle_paused(self):
        self.paused = not self.paused
        if not self.paused:
            self.filter_change_filter( self.filter )   # Bump a change in texts
        
    def filter_combo_changed(self, ix, combo):
        data = combo.itemData(ix)
        self.filter_change_filter( data )

    def filter_change_filter(self, filter):
        self.text_change_mutex.acquire()
        with ScopeGuard(self.text_change_mutex.release) as sg:
            self.filter = filter
            for x in self.tabs:
                edit = x.edit
                text = x.textread
                edit.setText( self.apply_filter(text, self.filter) )

    def apply_filter(self, text, filter):
        def colorize(str, filter):
            # TODO: We can add <span...>...</span>... around text.
            return str
        if not filter: return text
        x = text.decode("utf-8").split("\n")
        return "\n".join( [colorize(y,filter) for y in x if filter in y.lower()] )
    
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
            Returns True - user wants quit, False - user cancelled (doesn't want quit).
        '''
        res = QtGui.QMessageBox.warning(self, "Closing",
            "Processes are still running - do you want to quit?",
            QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
        if res==QtGui.QMessageBox.Ok:
            if self.taskmanager:
                self.taskmanager.stop()
            return True
        return False

    def add_load_path(self, path):
        path_list = self.settings.value("recentPaths", [])
        path_list = [path] + path_list
        def filter_dups_stable(seq):
            seen = set()
            seen_add = seen.add
            return [x for x in seq if not (x in seen or seen_add(x))]
        path_list = filter_dups_stable(path_list)
        path_list_items = set(path_list)
        self.settings.setValue("recentPaths", path_list)
        self.updateRecentFileList()

    def open_yaml_task(self):
        file = QtGui.QFileDialog.getOpenFileName(filter="YAML buildchimp files (*.yaml)")
        if file:
            self.open_yaml_from_path(file[0])
            
    def open_yaml_from_path(self, path):
        self.taskManager = taskmanager.TaskManager( open(path).read(), self )
        self.add_load_path(path)

    def run_yaml(self):
        if self.taskManager:
            self.taskManager.run_loop_init()
            self.tabs = []
            self.tabCtrl.clear()
            self.taskManager.run_loop()

    def stop_yaml(self):
        if self.taskManager:
            self.taskManager.stop()
          
    def closeEvent(self, event):
        SaveGeom(self)
        self.settings.sync()
        
        stop_webserver = (lambda ws=self.webserver : ws.stop()) if self.webserver else lambda : None

        if not self.tabs or len(self.tabs)==0:
            stop_webserver()
            return self.close()
        for x in self.tabs:
            print(x.qprocess.state())
            if x.qprocess and x.qprocess.state()!=QtCore.QProcess.NotRunning:
                if not self.warn_fn(): return
        stop_webserver()

    def start_webserver(self):
        if self.webserver: return
        if sys.platform=="darwin":
            try:
                self.webserver = Webserver()
                self.webserver.start()
            except:
                self.webserver = None

    def stop_webserver(self):
        if self.webserver:
            self.webserver.stop()
            self.webserver = None

