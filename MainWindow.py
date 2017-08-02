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

        self.imv = pqg.ImageView(parent=self.graphicsView)
        #self.imv.show()

        PathDicom = "./data/"
        lstFilesDCM = []  # create an empty list
        for dirName, subdirList, fileList in os.walk(PathDicom):
            for filename in fileList:
                if ".dcm" in filename.lower():  # check whether the file's DICOM
                    if (dicom.read_file(os.path.join(dirName, filename))[0x18, 0x1030].value) == "Face Child  8-18 yrs  (Volume)":
                        lstFilesDCM.append(os.path.join(dirName, filename))

        ChestCT = dicom.read_file(lstFilesDCM[0])


        #print("rescale intercept \n")
        #print(ChestCT[0x28,0x1052].value)
        ConstPixelDims = (int(ChestCT.Rows), int(ChestCT.Columns), len(lstFilesDCM))
        ConstPixelSpacing = (float(ChestCT.PixelSpacing[0]), float(ChestCT.PixelSpacing[1]), float(ChestCT.SliceThickness))
        out = ""
        #print(ConstPixelDims)
        #print(ConstPixelSpacing)
        #print(ChestCT.pixel_array.dtype)
        out += "Pixel Dimentions: " + ConstPixelDims.__str__() + '\n' + "Pixel Spacing: " + ConstPixelSpacing.__str__() + '\n'

        ArrayDicom = np.zeros(ConstPixelDims, dtype=ChestCT.pixel_array.dtype)
        #ArrayDicom[:, :] = ChestCT.pixel_array+ChestCT[0x28,0x1052].value

        for filenameDCM in lstFilesDCM:
            # read the file
            ds = dicom.read_file(filenameDCM)
            # store the raw image data
            ArrayDicom[:, :, lstFilesDCM.index(filenameDCM)] = ds.pixel_array

        self.imv.setImage(ArrayDicom.transpose((2, 1, 0)))
        #self.imv.autoRange()


        #Slider for Z axis
        self.horizontalScrollBar.setMaximum(len(lstFilesDCM)-1)

        def updateZ():
            self.imv.setImage(ArrayDicom[:, :, self.horizontalScrollBar.sliderPosition()])

        self.horizontalScrollBar.sliderMoved.connect(updateZ)


        #Creates the ROI
        roi = pqg.RectROI([250,250], [150,150])
        roi.setParentItem(self.imv.getView())
        #roi.setAngle(-90)
        #roi.setPos(100,100)


        
        #Generates second image and output from ROI data
        img2 = pqg.ImageView(self.graphicsView_2)
        ROIarray = roi.getArrayRegion(ArrayDicom.transpose(0, 2, 1), self.imv.getImageItem())
        #print(ROIarray)
        np.fliplr(ROIarray)
        out += "ROI array:\n" + ROIarray.__str__()
        img2.setImage(ROIarray, autoLevels=False, autoRange=False)
        img2.setLevels(ROIarray.min(), ROIarray.max())

        '''
        def update(roi):
            ROIarray = roi.getArrayRegion(ArrayDicom.transpose((1, 0, 2)), self.imv.getImageItem())
            np.fliplr(ROIarray)
            img2.setImage(ROIarray, autoRange=False, autoLevels=False, scale=[0.5, 0.5])
            #print(ROIarray)
            #print(ROIarray.mean())
            #print(ROIarray.max())
            #print(ROIarray.min())
            updatetext = ''
            updatetext += ROIarray.__str__() + "\nMean:\n" + ROIarray.mean().__str__() + "\nMax:\n" + ROIarray.max().__str__() + "\nMin:\n" + ROIarray.min().__str__()
            self.textBrowser.clear()
            self.textBrowser.setPlainText(out + updatetext)


        roi.sigRegionChanged.connect(update)



        #Slider functionality

        def updateBot():
            min = (self.verticalSlider.sliderPosition())-(self.horizontalSlider.sliderPosition()/2)
            max = (self.verticalSlider.sliderPosition())+(self.horizontalSlider.sliderPosition()/2)
            img2.setLevels(min, max)

        self.horizontalSlider.sliderMoved.connect(updateBot)

        def updateTop():
            min = (self.verticalSlider.sliderPosition())-(self.horizontalSlider.sliderPosition()/2)
            max = (self.verticalSlider.sliderPosition())+(self.horizontalSlider.sliderPosition()/2)
            img2.setLevels(min, max)

        self.verticalSlider.sliderMoved.connect(updateTop)
        '''
