from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
import pyqtgraph as pqg
from pyqtgraph import *
import ui_PyQtGraphImage
import dicom
import numpy as np

class PyQtGraphImageMain(QMainWindow, ui_PyQtGraphImage.Ui_MainWindow):

    def __init__(self, parent=None):
        super(PyQtGraphImageMain, self).__init__(parent)
        pqg.setConfigOption('background', '#f0f0f0')
        pqg.setConfigOption('foreground', '#2d3142')
        pqg.mkPen(color=(0, 97, 255))
        self.setupUi(self)
        self.setMouseTracking(True)

        self.imv = pqg.ImageView(parent=self.graphicsView)
        #self.imv.show()

        PathDicom = "./data/"
        lstFilesDCM = []  # create an empty list
        for dirName, subdirList, fileList in os.walk(PathDicom):
            for filename in fileList:
                if ".dcm" in filename.lower():  # check whether the file's DICOM
                    if (dicom.read_file(os.path.join(dirName, filename))[0x18, 0x1030].value) == "PE Circ Time":
                        lstFilesDCM.append(os.path.join(dirName, filename))

        ChestCT = dicom.read_file(lstFilesDCM[0])

        #print("rescale intercept \n")
        #print(ChestCT[0x28,0x1052].value)
        ConstPixelDims = (int(ChestCT.Rows), int(ChestCT.Columns), len(lstFilesDCM))
        ConstPixelSpacing = (float(ChestCT.PixelSpacing[0]), float(ChestCT.PixelSpacing[1]), float(ChestCT.SliceThickness))
        out = ""
        out += "Pixel Dimentions: " + ConstPixelDims.__str__() + '\n' + "Pixel Spacing: " + ConstPixelSpacing.__str__() + '\n'


        seenPos = []#List to hold possible positions
        seenTime = []#List to hold possible times
        masterList = []#List to hold data in filename, position, time format

        for temp in lstFilesDCM:
            dc = dicom.read_file(temp)

            if seenPos.__contains__(dc[0x20, 0x1041].value):
                pass
            else:
                seenPos.append(dc[0x20, 0x1041].value)

            if seenTime.__contains__(dc[0x8, 0x32].value):
                pass
            else:
                seenTime.append(dc[0x8, 0x32].value)
            masterList.append([temp, dc[0x20, 0x1041].value, dc[0x8, 0x32].value])

        s = sorted(masterList, key=lambda x: (x[2]))
        s = sorted(masterList, key=lambda x: (x[1]), reverse=True)#Sorted by position then by time (maybe)


        nPos = seenPos.__len__()
        nTime = seenTime.__len__()

        finalArray = []#List holding all Dicom arrays
        for p in np.arange(0, nPos, 1):
            ArrayDicom = np.zeros(ConstPixelDims, dtype=ChestCT.pixel_array.dtype)
            for t in np.arange(0, nTime, 1):
                fileDCM = s[t+p*nTime][0]
                # read the file
                ds = dicom.read_file(fileDCM)
                # store the raw image data
                ArrayDicom[:, :, t] = ds.pixel_array
            finalArray.append(ArrayDicom)


        #ROI creation
        #Coordinate Boxes
        self.plainTextEdit.setPlainText("200")
        self.plainTextEdit_2.setPlainText("200")
        #Changes ROI based on GUI inputs
        def resizeROI():
            self.roi.setSize([self.spinBox.value(), self.spinBox.value()])

        self.spinBox.valueChanged.connect(resizeROI)

        self.roi = pqg.RectROI([0,0], [self.spinBox.value(), self.spinBox.value()])
        self.roiList = []
        self.ROIexists = False
        img2 = pqg.ImageView(self.graphicsView_2)


        #ROI buttons
        #Creates the ROI by linking the roi to the image
        def createROI():
            if self.ROIexists == False:
                self.ROIexists = True
                # Creates the ROI list
                self.roi.setParentItem(self.imv.getView())
                # roi.setPos(100,100)
                self.roi.sigRegionChanged.connect(update)
                self.roi.setPen(200, 50, 0)
                self.roi.setPos(float(self.plainTextEdit.toPlainText()), float(self.plainTextEdit_2.toPlainText()))
                for i in np.arange(0, nTime, 1):
                    self.roiList.append(self.roi.saveState())
                # Generates second image and output from ROI data
                ROIarray = self.roi.getArrayRegion(finalArray[self.verticalScrollBar.sliderPosition()][:, :, self.horizontalScrollBar.sliderPosition()].T,self.imv.getImageItem())
                np.fliplr(ROIarray)

        self.pushButton.clicked.connect(createROI)

        #Hides the by removing the link to the image and moving it out of frame
        def clearROI():
            self.roi.setParentItem(None)
            self.roi.setPos(-10000, 0)
            self.roi.setSize([self.spinBox.value(), self.spinBox.value()])
            self.roiList.clear()
            self.ROIexists = False

        self.pushButton_2.clicked.connect(clearROI)

        #Changes data based on moving of ROI as it happens
        def update(roi):
            ROIarray = roi.getArrayRegion(finalArray[self.verticalScrollBar.sliderPosition()][:, :, self.horizontalScrollBar.sliderPosition()].T, self.imv.getImageItem())
            np.fliplr(ROIarray)
            img2.setImage(ROIarray, autoRange=False, autoLevels=False)
            updatetext = ''
            updatetext += ROIarray.__str__() + "\nMean:\n" + ROIarray.mean().__str__() + "\nMax:\n" + ROIarray.max().__str__() + "\nMin:\n" + ROIarray.min().__str__()
            self.textBrowser.clear()
            self.textBrowser.setPlainText(out + updatetext)

        #Finds the mean of the data within each of the ROIs
        def collectMeans():
            mean = 0
            meanlst = []
            if self.ROIexists:
                update(self.roi)
                preMove()
                tempROI = self.roi
                tempState = tempROI.saveState()
                tempPlace = self.horizontalScrollBar.sliderPosition()
                for i in np.arange(0, nTime, 1):
                    self.imv.setImage(finalArray[self.verticalScrollBar.sliderPosition()][:, :, i].T, autoRange=False, autoLevels=False)
                    self.roi.setState(self.roiList[i])
                    mean += self.roi.getArrayRegion(finalArray[self.verticalScrollBar.sliderPosition()][:, :, i].T, self.imv.getImageItem()).mean()
                    meanlst.append(self.roi.getArrayRegion(finalArray[self.verticalScrollBar.sliderPosition()][:, :, i].T, self.imv.getImageItem()).mean())
                print(meanlst)
                mean = mean/nTime
                self.textBrowser_2.setText(mean.__str__())
                self.roi.setState(tempState)
                self.imv.setImage(finalArray[self.verticalScrollBar.sliderPosition()][:, :, tempPlace].T, autoRange=False,autoLevels=False)

        self.pushButton_3.clicked.connect(collectMeans)


        #Slider for time
        self.horizontalScrollBar.setMaximum(nTime-1)
        def updateT():
            self.imv.setImage(finalArray[self.verticalScrollBar.sliderPosition()][:, :, self.horizontalScrollBar.sliderPosition()].T, autoRange=False, autoLevels=False)
            if self.ROIexists:
                self.roi.setState(self.roiList[self.horizontalScrollBar.sliderPosition()])
                update(self.roi)

        #Saves current ROI state when the time is about to be changed
        def preMove():
            if self.ROIexists:
                self.roiList[self.horizontalScrollBar.sliderPosition()] = self.roi.saveState()

        self.horizontalScrollBar.sliderMoved.connect(updateT)
        self.horizontalScrollBar.sliderPressed.connect(preMove)


        #Slider for Z axis
        self.verticalScrollBar.setMaximum(nPos-1)
        def updateZ():
            self.imv.setImage(finalArray[self.verticalScrollBar.sliderPosition()][:, :, self.horizontalScrollBar.sliderPosition()].T, autoRange=False, autoLevels=False)
            if self.ROIexists:
                update(self.roi)

        self.verticalScrollBar.sliderMoved.connect(updateZ)


        #ROI slider functionality
        #Changes range
        def updateBot():
            min = self.verticalSlider.sliderPosition()-(self.horizontalSlider.sliderPosition()/2)
            max = self.verticalSlider.sliderPosition()+(self.horizontalSlider.sliderPosition()/2)
            if self.ROIexists:
                img2.setLevels(min, max)

        self.horizontalSlider.sliderMoved.connect(updateBot)
        self.horizontalSlider.sliderPressed.connect(updateBot)
        self.horizontalSlider.sliderReleased.connect(updateBot)

        #Changes level
        def updateTop():
            min = self.verticalSlider.sliderPosition()-(self.horizontalSlider.sliderPosition()/2)
            max = self.verticalSlider.sliderPosition()+(self.horizontalSlider.sliderPosition()/2)
            if self.ROIexists:
                img2.setLevels(min, max)

        self.verticalSlider.sliderMoved.connect(updateTop)
        self.verticalSlider.sliderPressed.connect(updateTop)
        self.verticalSlider.sliderReleased.connect(updateTop)


        #Main window slider functionality
        #Each functions the same as their ROI display counterparts
        def updateBottom():
            min = self.verticalSlider_2.sliderPosition()-(self.horizontalSlider_2.sliderPosition()/2)
            max = self.verticalSlider_2.sliderPosition()+(self.horizontalSlider_2.sliderPosition()/2)
            self.imv.setLevels(min, max)

        self.horizontalSlider_2.sliderMoved.connect(updateBottom)
        self.horizontalSlider_2.sliderPressed.connect(updateBottom)
        self.horizontalSlider_2.sliderReleased.connect(updateBottom)

        def updateSide():
            min = self.verticalSlider_2.sliderPosition()-(self.horizontalSlider_2.sliderPosition()/2)
            max = self.verticalSlider_2.sliderPosition()+(self.horizontalSlider_2.sliderPosition()/2)
            self.imv.setLevels(min, max)

        self.verticalSlider_2.sliderMoved.connect(updateBottom)
        self.verticalSlider_2.sliderPressed.connect(updateBottom)
        self.verticalSlider_2.sliderReleased.connect(updateBottom)

    #Changes the double click to set the coordinates to create an ROI
    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent):
        x = a0.x()
        y = a0.y()
        print(x, y)
        self.plainTextEdit.setPlainText(((x-70)-self.spinBox.value()/2).__str__())
        self.plainTextEdit_2.setPlainText(((y-70)-self.spinBox.value()/2).__str__())
