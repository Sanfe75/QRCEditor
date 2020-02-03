# QRCEditor

A simple GUI to create and compile .qrc files to .py resources.

The program follows the Qt Resource System as described in:
https://doc.qt.io/qt-5/resources.html

I'm learning Qt for python and I don't use Qt Designer so I created
my own program to create the .qrc file. It is also a BASIC frontend
for pyside2-rcc.exe, you can setup some basic options and run the
compiler from QRC Editor.

The program uses python 3.8 (I really had to try the walrus operator)
and PySide2 5.14.

The idea of the program is based on an example from:
Rapid GUI Programming with Python and Qt ( ww.qtrac.eu/pyqtbook.html)

Also my thanks to https://icons8.com for the icons.