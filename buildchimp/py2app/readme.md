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
