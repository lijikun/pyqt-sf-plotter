# pyqt-sf-plotter

Cross-platform GUI plotter for stopped-flow (SF) spectroscopy data, written in Python 3 with PyQt 5.

![ScreenShot](/exampleData/screenshot-xfce.png)

## Installing and Running

* Just clone this repo to install to a computer. 

  ```
  cd [your directory]
  git clone https://github.com/lijikun/pyqt-sf-plotter/
  cd pyqt-sf-plotter
  ```

  Make sure the following dependencies exist on the computer, with indicated or newer versions: 
  * Qt 5.7
  * Python 3.5
  * PyQt 5.7
  * Numpy 1.12.1
  * Matplotlib 2.0.0
 
   Typically most Python and Qt distributions will suffice.

* To run the program on Linux:

  ```
  python3 pyqtsfplotter_app.py
  ```
    
  or
  
  ```
  chmod +x pyqtsfplotter_app.py
  ./pyqtsfplotter_app.py
  ```
  This program is never actually tested on MacOS, but should run fine just like on Linux.

* To run on Windows, first put a Python3's `python.exe` in `PATH`, and run:

  ```
  python pyqtsfplotter_app.py
  ```
    
## Notes on Modifying This Program

* To modify the GUI, don't edit `pyqtsfplotter_gui.py` directly. Rather, use Qt Designer to edit `pyqtsfplotter_gui.ui` and run `pyuic5` to generate it automatically. You need the `pyqt5-dev-tools` package installed.

  ```
  pyuic5 pyqtsfplotter_gui.ui -o pyqtsfplotter_gui.py
  ```

* The minimum size of the main window is set 1280 x 960 pixels. This limit can be lifted if changes are made to the UI, but the program is not guaranteed to run properly. 
