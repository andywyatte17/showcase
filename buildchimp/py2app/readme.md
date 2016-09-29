## py2app - Turning the program into a Mac app (bundle)

### Prerequisites

(From https://pythonhosted.org/py2app/install.html#installing-with-pip)
* Install py2app - ```sudo pip install -U py2app```

### Create setup.py

* py2applet --make-setup ../buildchimp.py
* Adjust setup.py to include PySide
  * ```OPTIONS = { ..., 'includes': ['PySide.QtCore', 'PySide.QtGui'], ... }```
* Adjust setup.py to include an icon
  * ```OPTIONS = { ..., 'iconfile':'chimp.icns', ... }```

### To Build

* Clean up build dirs - ```rm -rf build dist```
* Build for deploy - ```python setup.py py2app```

If you try to run it with DYLD_LIBRARY_PATH set to nothing, you'll get a problem:

* Run it - ```DYLD_LIBRARY_PATH="" dist/buildchimp.app/Contents/MacOS/buildchimp```

To fix this by added buildchimp.app/.../Frameworks to @rpath, do the following:

* ```install_name_tool -add_rpath @executable_path/../Frameworks dist/buildchimp.app/Contents/MacOS/buildchimp```

Try it again:

* Run it - ```DYLD_LIBRARY_PATH="" dist/buildchimp.app/Contents/MacOS/buildchimp```
  * Hopefully this will run successfully.

There's also another problem with dylib/so loading that occurs on other machines with different setups. Diagnosis:

* ```otool -L dist/buildchimp.app/Contents/Resources/lib/python2.7/lib-dynload/PySide/Qt*.so```
  * Notice the paths /usr/local/lib/Qt... - these need to be picked from @rpath.

To fix this:

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

### build.sh

All the above details are found in build.sh
