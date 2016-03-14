#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""

import sys
import os

def main():
    from mainwnd import MainWnd
    from PySide import QtGui
    app = QtGui.QApplication(sys.argv)
    ex = MainWnd()
    sys.exit(app.exec_())

if __name__ == '__main__':
    # OSX DYLD_LIBRARY_PATH=~/Library/Python/2.7/lib/python/site-packages/PySide python buildchimp.py
    main()
