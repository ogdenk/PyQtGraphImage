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
        ConstPixelDims = (int(ChestCT.Rows), int(ChestCT.Columns))
        ConstPixelSpacing = (float(ChestCT.PixelSpacing[0]), float(ChestCT.PixelSpacing[1]))
        print(ConstPixelDims)
        print(ConstPixelSpacing)
        print(ChestCT.pixel_array.dtype)

        ArrayDicom = np.zeros(ConstPixelDims, dtype=ChestCT.pixel_array.dtype)
        ArrayDicom[:, :] = ChestCT.pixel_array

        self.imv.setImage(ArrayDicom.T)


        #self.apply.clicked.connect(self.ApplyChecker)
        #self.reset.clicked.connect(self.Reset)
        #self.patient = PatientData.Patient() #object that holds the data and does the calculations

