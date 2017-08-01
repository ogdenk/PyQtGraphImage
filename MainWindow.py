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
        ChestCT = dicom.read_file("ch_250.dcm")
        print("rescale intercept \n")
        print(ChestCT[0x28,0x1052].value)
        ConstPixelDims = (int(ChestCT.Rows), int(ChestCT.Columns))
        ConstPixelSpacing = (float(ChestCT.PixelSpacing[0]), float(ChestCT.PixelSpacing[1]))
        out = ""
        print(ConstPixelDims)
        print(ConstPixelSpacing)
        print(ChestCT.pixel_array.dtype)
        out += "Pixel Dimentions: " + ConstPixelDims.__str__() + '\n' + "Pixel Spacing: " + ConstPixelSpacing.__str__() + '\n'

        ArrayDicom = np.zeros(ConstPixelDims, dtype=ChestCT.pixel_array.dtype)
        ArrayDicom[:, :] = ChestCT.pixel_array+ChestCT[0x28,0x1052].value

        self.imv.setImage(ArrayDicom.T)
        self.imv.autoRange()

        #Creates the ROI
        roi = pqg.RectROI([250,250], [150,150])
        roi.setParentItem(self.imv.getView())
        #roi.setAngle(-90)
        #roi.setPos(100,100)


        #Generates second image and output from ROI data
        img2 = pqg.ImageView(self.graphicsView_2)
        ROIarray = roi.getArrayRegion(ArrayDicom, self.imv.getImageItem())
        print(ROIarray)
        np.fliplr(ROIarray)
        out += "ROI array:\n" + ROIarray.__str__()
        img2.setImage(ROIarray.T, autoLevels=False, autoRange=False, scale=[0.5, 0.5])
        img2.setLevels(ROIarray.min(),ROIarray.max())

        def update(roi):
            ROIarray = roi.getArrayRegion(ArrayDicom.T, self.imv.getImageItem())
            np.fliplr(ROIarray)
            img2.setImage(ROIarray, autoRange=False, autoLevels=False, scale=[0.5, 0.5])
            print(ROIarray)
            print(ROIarray.mean())
            print(ROIarray.max())
            print(ROIarray.min())
            updatetext = ''
            updatetext += ROIarray.__str__() + "\nMean:\n" + ROIarray.mean().__str__() + "\nMax:\n" + ROIarray.max().__str__() + "\nMin:\n" + ROIarray.min().__str__()
            self.textBrowser.clear()
            self.textBrowser.setPlainText(out + updatetext)

        roi.sigRegionChanged.connect(update)

