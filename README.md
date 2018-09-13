# pyqt-sf-plotter
First working version. README to be finished.

Plotter for stopped-flow (SF) spectroscopy data. Written in PyQt.

Dependencies (under which this app is written): Qt 5.7.1, Python 3.5.3, PyQt 5.7, Numpy 1.12.1, Matplotlib 2.0.0.

To run the program (Linux):

    python3 pyqtsfplotter_app.py
    
To run on Window$, first put a Python3 python.exe in PATH, and run:

    python pyqtsfplotter_app.py

Don't modify pyqtsfplotter_gui.py. Rather, use Qt Designer to edit pyqtsfplotter_gui.ui and run

    pyuic5 pyqtsfplotter_gui.ui -o pyqtsfplotter_gui.py


