# pygubu-tcpclient-example

This is an example application based on the python module [pygubu](https://github.com/alejandroautalan/pygubu).

Tcpclientk is two things: a TCP client and a GUI based on [python3](https://www.python.org/), [pygubu](https://github.com/alejandroautalan/pygubu) and [Tkinter](https://wiki.python.org/moin/TkInter).

Previously, writing portable simple GUIs was a difficult task, now thanks
to [pygubu](https://github.com/alejandroautalan/pygubu), almost everybody can do it.

Anyway, [pygubu](https://github.com/alejandroautalan/pygubu) deserves more example code, this is why I've started to
write this example.

# Packaging this example for Windows with pyinstaller

This procedure was tested on Windows 7 and Python 3.6.1, it is still experimental but it works:

  1. In Windows, install [python3](https://www.python.org/)

  2. Open a command shell and type:

     `pip install pygubu`

  3. Then, type:

     `pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip`

  4. In the pygubu-tcpclient-example directory, type:

     `pyi-makespec --onefile`

     This will produce a file called `onefile.spec`

  5. Edit the `.spec` file to add some more data tuples, like this:

     `datas=[('tcpclientk.png', '.'), ('tcpclientk.ui','.'), ('tcpclientk_about_dialog.ui', '.')],`

     These files will be automatically copied to the bundle directory. There is some code
     in `tcpclientk` to detect if it is run from a bundle and adapt the PATH accordingly, see NOTES below

  6. Run `pyinsaller onefile.spec`, this will produce one single `.exe`file under the `dist`
     directory. This file contains all dependencies that are needed to run the example

NOTES:

  * I needed to install a development version of [pyinstaller](https://github.com/pyinstaller/pyinstaller), because I have
had problems with the latest release. But maybe you don't need to do that anymore since these
changes have been added to the latest release?

  * Add `from pygubu.builder import ttkstdwidgets` to your source
to avoid the error: `ModuleNotFoundError: No module named 'pygubu.builder.ttkstdwidgets'`

  * To detect if the code runs in a bundle or not:

```
import sys
FILE_PATH = None  # To be set in __main__

if getattr( sys, 'frozen', False ) :
    # running in a bundle
    bundle_dir = sys._MEIPASS
else :
    # running live in a normal Pyton environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

FILE_PATH = bundle_dir

# Then refer to all files from datas like this from your code:
os.path.join(FILE_PATH, "tcpclientk.ui"), etc...
```
