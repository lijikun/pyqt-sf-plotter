#!/usr/bin/python3
# Models and object definitions for MVC-style programming.
# Still needs QtGui because of popup messages for warnings and errors in data.

import copy
from os import path

from PyQt5 import QtCore, QtGui, QtWidgets
import numpy
from matplotlib import cm as mpl_cm
from matplotlib import colors as mpl_colors
       
class DataFileObject(object):    
    def __init__(self, fileName):
        super().__init__()
        self.fName = fileName
        self.z, self.w, self.t = self.importRawFile(fileName)
        self.__model = None
        
    def importRawFile(self, fileName):
        extension = path.splitext(fileName)[1]
        z = []
        t = []
        w = []
        flag_wt = False        
        with open(fileName, mode='r') as f1: 
            validFile = True
            # Searches for and reads header line.
            if extension == '.csv':
                while True: # two possible formats in input file
                    line1 = f1.readline()
                    if 'Time,Wavelength' in line1:
                        line1 = f1.readline()
                        try:
                            w = [float(x) for x in line1.split(sep=',')[1:-1]]
                        except ValueError:
                            validFile = False
                        break
                    if 'Wavelength,Time' in line1:
                        line1 = f1.readline()
                        try:
                            t = [float(x) for x in line1.split(sep=',')[1:-1]]
                        except ValueError: 
                            validFile = False
                        flag_wt = True
                        break
                    if not line1: # error: detects end of file prematurely
                        break
            elif extension == '.txt':
                line1 = f1.readline()
                line1Items = line1.split()
                if line1Items[0] == 'Time' and len(line1Items) > 1:
                    w = line1Items[1:]
            # Reads the rest of the data, if any.        
            if w:
                sepString = ',' if extension == '.csv' else None
                while True:
                    line1 = f1.readline()
                    if line1.strip():
                        try:
                            line1_Numbers = [float(x) for x in line1.split(sep=sepString)]
                        except ValueError: 
                            validFile = False
                        if len(line1_Numbers) == 1 + len(w):
                            t.append(line1_Numbers[0])
                            z.append(line1_Numbers[1:])
                        else:
                            break
                    else:
                        break
            elif t:
                while True:
                    line1 = f1.readline()
                    if line1.strip():
                        try:
                            line1_Numbers = [float(x) for x in line1.split(sep=',')] 
                        except ValueError: 
                            validFile = False
                        if len(line1_Numbers) == 1 + len(t):
                            w.append(line1_Numbers[0])
                            z.append(line1_Numbers[1:])
                        else:
                            break
                    else:
                        break
            f1.close()
            print(fileName, ': ', sum(len(x) for x in z), '=', len(w), '*', len(t))
            if not (len(w) > 0 and len(t) > 0 and validFile):
                QtWidgets.QMessageBox.question(None, 'Invalid Raw Data File', \
                    'File ' + fileName + ' contains no valid data. Skipped.', \
                    QtWidgets.QMessageBox.Ok)
        return (z if flag_wt else list(map(list, zip(*z)))), w, t  
     
    # Lazy evaluation and caching for models.
    def genModel(self, whatType):
        if self.__model == None:
            self.__model = DataInSingleFileListModel(self, whatType)
        else:
            self.__model.setType(whatType)
        return self.__model
        
    def isValid(self):
        return (True if (self.z and self.w and self.t) else False)

class DataInSingleFileListModel(QtCore.QAbstractListModel):
    def __init__(self, dataFileObject, whatType):
        super().__init__()
        self.__z = copy.copy(dataFileObject.z)
        self.__w = copy.copy(dataFileObject.w)
        self.__t = copy.copy(dataFileObject.t)
        # Boolean, True if timetraces, False if spectra
        self.__whatType = whatType
        
    def setType(self, whatType):
        self.layoutAboutToBeChanged.emit()
        self.__whatType = whatType
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), 0))
        self.layoutChanged.emit()
        
    def getType(self):
        return self.__whatType
        
    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self.__w) if self.__whatType else len(self.__t)
    
    def flags(self, index):
        if index.isValid() and index.row() >= 0 and index.row() < self.rowCount():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        else:
            return QtCore.Qt.NoItemFlags
    
    def data(self, index, role = QtCore.Qt.DisplayRole):
        if index.isValid() and index.row() >= 0 and index.row() < self.rowCount():
            row = index.row()
            if role == QtCore.Qt.DisplayRole:
                return self.__w[row] if self.__whatType else self.__t[row]
            if role == QtCore.Qt.EditRole:
                # Edits everything in text areas, not spinboxes.
                return str(self.__w[row]) if self.__whatType else str(self.__t[row])
            elif role == QtCore.Qt.UserRole:
                # Returns a ([x0, x1, ..., xn], [y0, y1, ..., yn]) tuple.
                return (self.__t, self.__z[row]) if self.__whatType \
                    else (self.__w, [self.__z[j][row] for j in range(len(self.__z))])
            elif role == QtCore.Qt.ToolTipRole:
                if self.__whatType:
                    return 'Min: ' + str(min(self.__z[row])) + ' Max: ' + str(max(self.__z[row]))
                else:
                    lowest = min([self.__z[j][row] for j in range(len(self.__z))])
                    highest = max([self.__z[j][row] for j in range(len(self.__z))])
                    return 'Lowest: ' + str(lowest) + " Highest: " + str(highest)
        return None
    
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if index.isValid() and index.row() >= 0 and index.row() < self.rowCount():
            row = index.row()
            if role == QtCore.Qt.EditRole:
                pArray = self.__w if self.__whatType else self.__t
                editSuccess = 0
                try:
                    num = float(value)
                except ValueError:
                    str1 = str(value)
                    if str1.startswith(':s/'):
                        strSplit = str1[3:].split('/')
                        if len(strSplit) == 3:
                            if strSplit[2] == 'g':
                                for j in range(len(pArray)):
                                    try:
                                        num = float(str(pArray[j]).replace(strSplit[0], strSplit[1]))
                                    except ValueError:
                                        pass
                                    else:
                                        pArray[j] = num
                                        editSuccess += 1
                            elif strSplit[2] == '':
                                try:
                                    num = float(str(pArray[row]).replace(strSplit[0], strSplit[1]))
                                except ValueError:
                                    pass
                                else:
                                    pArray[row] = num
                                    editSuccess += 1
                else:
                    pArray[row] = num
                    editSuccess += 1
                if editSuccess:
                    return True                    
        return False
        
# Model for processing files
class DataFilesListModel(QtCore.QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.__files = []    
        
    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self.__files)
    
    def flags(self, index):
        if index.isValid() and index.row() >= 0 and index.row() < self.rowCount():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        else:
            return QtCore.Qt.NoItemFlags
    
    def data(self, index, role = QtCore.Qt.DisplayRole):
        if index.isValid() and index.row() >= 0 and index.row() < self.rowCount():
            row = index.row()
            shortName = path.basename(self.__files[row].fName)
            if role == QtCore.Qt.DisplayRole:
                return str(row)+ ': ' + (shortName if (len(shortName) < 34) else (shortName[0:15] + '...' + shortName[-15:])) \
                    + ': ' + str(len(self.__files[row].w)) + ' x ' + str(len(self.__files[row].t))
            elif role == QtCore.Qt.ToolTipRole:
                return 'File: ' + self.__files[row].fName + '\n' \
                    + str(len(self.__files[row].w)) + ' Wavelengths: ' \
                    + str(self.__files[row].w[0]) + ' ... ' +str(self.__files[row].w[-1]) + '\n' \
                    + str(len(self.__files[row].t)) + ' Timepoints: ' \
                    + str(self.__files[row].t[0]) + ' ... ' +str(self.__files[row].t[-1])            
            elif role == QtCore.Qt.UserRole:
                return self.__files[row]
        return None                
       
    def removeRows(self, row, count, parent = QtCore.QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        del self.__files[row : row + count]
        self.endRemoveRows()
        return True
    
    def appendRow(self, fileName, parent = QtCore.QModelIndex()):        
        file1 = DataFileObject(fileName)
        if file1.isValid():
            self.beginInsertRows(parent, self.rowCount(), self.rowCount())
            self.__files.append(file1)
            self.endInsertRows()
            return True
        return False

# A table model for a fake list view.
class PlotListModel(QtCore.QAbstractTableModel):
    # Uses check states: Qt.Unchecked for invisible, PartiallyChecked for scatter, Checked for line plots.
    # Sets plot styles and color rotation.
    fontSize = 16
    lineWidth = 2
    maxMarkers = 100
    markerRatio = 2.5
    __palette = mpl_cm.get_cmap('Dark2')
    __currentColor = -1
    __maxColor = 8
    __xmargin = 0.02
    __ymargin = 0.02    

    def __nextColor(self):
        PlotListModel.__currentColor += 1
        if PlotListModel.__currentColor >= PlotListModel.__maxColor:
            PlotListModel.__currentColor = 0
        return mpl_colors.to_hex(PlotListModel.__palette( \
                PlotListModel.__currentColor / PlotListModel.__maxColor), keep_alpha = True)
    
    # Takes a figure, and uses MPL Line2D to store data.
    def __init__(self, figure):
        super().__init__()
        self.__names = []
        self.__annotations = []
        self.__linestyles = []
        figure.clf()
        # Just uses MPL's Line2D as item model.
        self.__axes = figure.add_subplot(111)
        self.__gridOn = False
        # __legendOn is the user setting for legend.
        # __visibleCount is the internal bookkeeping for visible lines.
        # Legend must remove() before __visibleCount becomes zero, or error.
        self.__legendOn = False
        self.__visibleCount = 0
    
    # Custom functions for connecting model to matplotlib figure.
    # MPL doesn't provide OOP controls for axis grid.
    def setGrid(self, bool1):
        self.__axes.grid(bool1)
        self.__gridOn = bool
        self.refreshLayout()
    
    def getGrid(self):
        return self.__gridOn
        
    def setLegend(self, bool1):
        self.__legendOn = bool1
        self.refreshLegend()
        self.refreshLayout()
                        
    def getLegend(self):
        return self.__legendOn
    
    def refreshLegend(self):
        if self.__visibleCount > 0 and self.__legendOn:
            if self.__axes.get_legend() != None:
                self.__axes.get_legend().remove()
            self.__axes.legend(fontsize = PlotListModel.fontSize)           
        else:
            if self.__axes.get_legend() != None:
                self.__axes.get_legend().remove()
        # debug: print(self.__axes.get_children())
                
    def refreshStyle(self):
        for line1 in self.__axes.lines:
            line1.set_lw(PlotListModel.lineWidth)
            line1.set_ms(PlotListModel.lineWidth * PlotListModel.markerRatio)
            y = 1 if len(line1.get_xdata()) < PlotListModel.maxMarkers \
                else int(len(line1.get_xdata()) / PlotListModel.maxMarkers)
            line1.set_markevery(y)
        self.__axes.set_xlabel(self.__axes.get_xlabel(), fontsize = PlotListModel.fontSize)                    
        self.__axes.tick_params(labelsize = PlotListModel.fontSize)
        
        self.refreshLegend()
            
    def autoResizeAxes(self):
        if self.__visibleCount > 0:
            x0 = min([min(l.get_xdata()) for l in self.__axes.lines if l.get_visible()])
            x1 = max([max(l.get_xdata()) for l in self.__axes.lines if l.get_visible()])            
            y0 = min([min(l.get_ydata()) for l in self.__axes.lines if l.get_visible()])
            y1 = max([max(l.get_ydata()) for l in self.__axes.lines if l.get_visible()])
            if self.__axes.get_xscale() == 'log':
                x0f = x0
                x1f = x1
            else:
                x0f = x0 - (x1 - x0) * self.__xmargin
                x1f = x1 + (x1 - x0) * self.__xmargin
            if self.__axes.get_yscale() == 'log':
                y0f = y0
                y1f = y1
            else:
                y0f = y0 - (y1 - y0) * self.__xmargin
                y1f = y1 + (y1 - y0) * self.__xmargin    
            self.__axes.set_xlim(x0f, x1f)
            self.__axes.set_ylim(y0f, y1f)
            return (x0f, x1f, y0f, y1f)
        else:
            return (0, 0, 0, 0)
            
    def refreshLayout(self):
        self.__axes.get_figure().tight_layout()
        self.__axes.get_figure().canvas.draw()
        
    def redrawAll(self):
        x0, x1, y0, y1 = self.autoResizeAxes()
        self.refreshStyle()
        self.refreshLayout()
        return (x0, x1, y0, y1)
                
    # Mandatary functions for Qt.
    def rowCount(self, parent = QtCore.QModelIndex()):
        if self.__axes:
            return len(self.__axes.lines)
        else:
            return 0
        
    def columnCount(self, parent = QtCore.QModelIndex()):
        return 3
    
    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and section < self.columnCount():
            if role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignLeft
            elif role == QtCore.Qt.ToolTipRole:
                return 'Double click fields to edit. \nCan use _s/find/replace/ to do replacement, or _s/find/replace/g to replace in all files.'
            elif section == 0 and role == QtCore.Qt.DisplayRole:
                return 'Name'
            elif section == 1 and role == QtCore.Qt.DisplayRole:
                return '#RGBA'
            elif section == 2 and role == QtCore.Qt.DisplayRole:
                return 'Style'
        elif orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole and section < self.rowCount():
            return section
        else:
            return None
    
    def flags(self, index):
        if index.isValid() and index.row() < self.rowCount() and index.column() < self.columnCount():
            if index.column() == 0:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable \
                | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsUserTristate
            elif index.column() == 1 or index.column() == 2:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        return QtCore.Qt.NoItemFlags
    
    def data(self, index, role = QtCore.Qt.DisplayRole):
        if index.isValid() and index.row() < self.rowCount() and index.column() < self.columnCount():
            row = index.row()
            col = index.column()
            line1 = self.__axes.lines[row]
            if col == 0 and role == QtCore.Qt.CheckStateRole:
                if line1.get_visible():
                    if line1.get_marker() == 'None' and line1.get_linestyle() != 'None':
                        return QtCore.Qt.Checked
                    elif line1.get_marker() == 'o' and line1.get_linestyle() == 'None':
                        return QtCore.Qt.PartiallyChecked
                else:
                    return QtCore.Qt.Unchecked
            elif col == 0 and (role == QtCore.Qt.EditRole or role == QtCore.Qt.DisplayRole):
                return self.__names[row]
            elif col == 0 and role == QtCore.Qt.UserRole:
                return (line1.get_xdata(), line1.get_ydata())
            elif col == 1 and role == QtCore.Qt.DecorationRole:
                pixmap1 = QtGui.QPixmap(16, 16)
                # Qt and MPL use different definitions for RGBa hex strings!
                # Uses MPL definition #RRGGBBAA, and convert to Qt's #AARRGGBB
                color1 = mpl_colors.to_hex(line1.get_color(), keep_alpha = True)
                pixmap1.fill(QtGui.QColor(color1[0] + color1[7:9] + color1[1:7]))
                return pixmap1
            elif col == 1 and (role == QtCore.Qt.EditRole or role == QtCore.Qt.DisplayRole):
                return mpl_colors.to_hex(line1.get_color(), keep_alpha = True)
            elif col == 2 and (role == QtCore.Qt.EditRole or role == QtCore.Qt.DisplayRole):
                return self.__linestyles[row]
        return None
    
    def setData(self, indices, values, role = QtCore.Qt.EditRole):
        if not (type(indices) is list and type(values) is list):
            # Can accept list or individual indices and values.
            indices = [indices]
            values = [values]
        minRow = indices[0].row()
        maxRow = indices[0].row()
        changed = False
        for index, value in zip(indices, values):
            if index.isValid() and index.row() < self.rowCount() and index.column() < self.columnCount():
                row = index.row()
                col = index.column()
                line1 = self.__axes.lines[row]
                if col == 0 and role == QtCore.Qt.CheckStateRole:            
                    if value == QtCore.Qt.Unchecked:
                        if line1.get_visible():
                            self.__visibleCount -= 1
                            line1.set_visible(False)
                            line1.set_label('_' + self.__names[row])                    
                    else:
                        if not line1.get_visible():
                            self.__visibleCount += 1
                            line1.set_visible(True)
                            line1.set_label(self.__names[row])                    
                        if value == QtCore.Qt.Checked:
                            line1.set_linestyle(self.__linestyles[row])
                            line1.set_marker('None')
                        elif value == QtCore.Qt.PartiallyChecked:
                            line1.set_linestyle('None')
                            line1.set_marker('o')
                        else:
                            continue
                elif col == 0 and role == QtCore.Qt.EditRole:
                    newName = str(value)
                    # Doesn't accept empty string or a string starting with '_'.
                    if newName and newName[0] != '_':
                        self.__names[row] = newName
                        if line1.get_visible():
                            line1.set_label(self.__names[row])
                    elif newName.startswith('_s/'):
                        splitNewName = newName[3:].split('/')
                        if len(splitNewName) == 3:
                            if splitNewName[2] == 'g':
                                for i in range(self.rowCount()):
                                    self.__names[i] = self.__names[i].replace(splitNewName[0], splitNewName[1])
                                    if self.__axes.lines[i].get_visible():
                                        self.__axes.lines[i].set_label(self.__names[i])
                                minRow = 0
                                maxRow = self.rowCount() - 1
                            elif splitNewName[2] == '':
                                self.__names[row] = self.__names[row].replace(splitNewName[0], splitNewName[1])
                                if line1.get_visible():
                                    line1.set_label(self.__names[row])
                            else:
                                continue
                        else:
                            continue
                    else:
                        continue                    
                elif col == 1 and role == QtCore.Qt.EditRole and mpl_colors.is_color_like(value):
                    # If color is valid color string.
                    line1.set_color(mpl_colors.to_hex(value, keep_alpha = True))
                elif col == 2 and role == QtCore.Qt.EditRole \
                        and value in ['-', '--', '-.', ':', 'solid', 'dashed', 'dashdot' 'dotted']:
                    if line1.get_linestyle != 'None' and line1.get_marker() == 'None' :
                        line1.set_linestyle(value)
                        self.__linestyles[row] = line1.get_linestyle()
                else:
                    continue
                changed = True
                if row < minRow:
                    minRow = row
                elif row > maxRow:
                    maxRow = row
        if changed:
            self.dataChanged.emit(self.index(minRow, 0), self.index(maxRow, self.columnCount() - 1))
            self.refreshLegend()
            self.refreshLayout()
        return changed
                  
    def appendRow(self, nameStrings, dataXs, dataYs, parent = QtCore.QModelIndex()):    
        count = min(len(nameStrings), len(dataXs), len(dataYs))
        count1 = 0
        self.beginInsertRows(parent, self.rowCount(), self.rowCount() + count - 1)
        xDataError = QtWidgets.QMessageBox.No
        altX = None
        for nameString, dataX, dataY in zip(nameStrings, dataXs, dataYs):
            newName = str(nameString)
            # If too many points, mark every total /  maxMarkers instead.
            y = 1 if len(dataX) < PlotListModel.maxMarkers else int(len(dataX) / PlotListModel.maxMarkers)
            # Accounts for dataX is a list of str situation: tries to convert to number.
            # If fails, uses negative axis as x axis, and keeps dataX as annotations.            
            try:
                altX = [float(x) for x in dataX]
            except ValueError:                    
                if xDataError != QtWidgets.QMessageBox.YesToAll and xDataError != QtWidgets.QMessageBox.NoToAll:
                    xDataError = QtWidgets.QMessageBox.question(None, 'Invalid X-Axis Data.', \
                        'Texts instead of numbers found in x-axis data.\n' \
                        + 'This will lead to wacky plot behavior. Still use them?', \
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.YesToAll \
                        | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.NoToAll, \
                        QtWidgets.QMessageBox.No)
                if xDataError == QtWidgets.QMessageBox.Yes or xDataError == QtWidgets.QMessageBox.YesToAll:
                    altX = (range(-len(dataX) * 10, 0, 10))
                    self.__annotations.append(dataX)
                else:
                    altX = None
                    count1 += 1
            else:
                self.__annotations.append(None)
            finally:
                if altX:
                    self.__axes.plot(numpy.array(altX), numpy.array(dataY), \
                        lw = PlotListModel.lineWidth, c = self.__nextColor(), \
                        ms = PlotListModel.lineWidth * PlotListModel.markerRatio, fillstyle = 'full', \
                        label = newName, marker = 'None', linestyle = '-', markevery = y) 
                    self.__names.append(copy.deepcopy(newName))
                    self.__linestyles.append('-')
                    self.__visibleCount += 1
        self.endInsertRows()
        # This is used for fixing cosmetic error.
        if count1:
            self.beginRemoveRows(parent, self.rowCount(), self.rowCount() + count1 - 1)
            self.endRemoveRows()
        return True
        
    def removeRows(self, row, count, parent = QtCore.QModelIndex()):
        if count > 0 and row + count <= self.rowCount():
            self.beginRemoveRows(parent, row, row + count - 1)
            rmVisibleCount = len([row for line1 in \
                self.__axes.lines[row : row + count] if line1.get_visible()])
            del self.__names[row : row + count]
            del self.__axes.lines[row : row + count]
            del self.__linestyles[row : row + count]
            self.__visibleCount -= rmVisibleCount
            self.endRemoveRows()
            return True
        return False
