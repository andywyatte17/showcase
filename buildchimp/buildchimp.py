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
from mainwnd import MainWnd
from PySide import QtGui

def main():
    app = QtGui.QApplication(sys.argv)
    ex = MainWnd()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

