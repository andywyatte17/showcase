#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
buildchimp.py
    A program written using PySide (Qt 4) for automating build processes, ie small scripts
    that build source copy and (possibly) copy files after etc. Configuration of these
    build processes is made using YAML files.
'''

import sys
import os

def main():
    from mainwnd import MainWnd
    from PySide import QtGui
    from PySide import QtCore
    QtCore.QCoreApplication.setApplicationName("buildchimp")
    QtCore.QCoreApplication.setOrganizationName("ghuisoft")
    QtCore.QCoreApplication.setOrganizationDomain("ghuisoft.net")
    app = QtGui.QApplication(sys.argv)
    ex = MainWnd()
    sys.exit(app.exec_())

if __name__ == '__main__':
    '''
      On OSX after python -m pip install --user PySide buildchimp.py gives an ImportError
      exception. My fix:
         ~/.bash_profile += export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:$HOME/Library/Python/2.7/lib/python/site-packages/PySide
    '''
    main()
