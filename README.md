# pyqt-sf-plotter

Cross-platform GUI plotter for stopped-flow (SF) spectroscopy data written in PyQt.

![ScreenShot](/exampleData/screenshot-xfce.png)

## Installing and Running

* Just clone this repo to install to a computer. Make sure the following dependencies exist on the computer: 
  * Qt
  * Python 
  * PyQt 
  * Numpy 
  * Matplotlib
 
   Typically most Python and Qt distributions will suffice.

* To run the program on Linux:

  ```python3 pyqtsfplotter_app.py```
    
  or
  
  ```
  chmod +x pyqtsfplotter_app.py
  ./pyqtsfplotter_app.py
  ```

This program is never actually tested on MacOS, but should run fine just like on Linux.

* To run on Windows, first put a Python3's `python.exe` in `PATH`, and run:

    python pyqtsfplotter_app.py
    
## Notes on Modifying This Program

* To change the GUI, don't modify `pyqtsfplotter_gui.py` directly. Rather, use Qt Designer to edit `pyqtsfplotter_gui.ui` and run

    pyuic5 pyqtsfplotter_gui.ui -o pyqtsfplotter_gui.py

* The main window is set to have a size of at least 1280 x 960 pixels. This limit can be reduced if changes are made to the UI, but the program is not guaranteed to run properly. 
