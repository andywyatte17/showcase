#!/bin/sh

rm -rf build dist

python setup.py py2app

install_name_tool -add_rpath @executable_path/../Frameworks dist/buildchimp.app/Contents/MacOS/buildchimp

for qt in "QtCore" "QtGui" "QtNetwork"
do
  usr_local_lib="/usr/local/lib/$qt.framework/Versions/4/$qt"
  echo $usr_local_lib
  for so in dist/buildchimp.app/Contents/Resources/lib/python2.7/lib-dynload/PySide/Qt*.so
  do
    install_name_tool -change /usr/local/lib/$qt.framework/Versions/4/$qt \
      @executable_path/../Frameworks/$qt.framework/Versions/4/$qt \
         $so
  done
done
