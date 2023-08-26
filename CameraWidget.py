# -*- coding: utf-8 -*-

#   Libraries to import

# Graphical interface
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QGridLayout, QComboBox, QSlider, QLineEdit
    )
from PyQt5.QtGui import QPixmap, QImage

# Standard
import numpy as np
import cv2
import sys
import math

from PyQt5.QtWidgets import QMainWindow, QLabel, QComboBox, QWidget, QGroupBox
from PyQt5.QtCore import QTimer, Qt

# Camera
from pyueye import ueye
import cameraUeye as camera
if camera.get_nb_of_cam() == 0 :
    import cameraBasler as camera
    if camera.get_nb_of_cam() == 0 :
        print("No camera detected, try to search for an answer.")
        sys.exit()
    else:
        print("Using a Basler camera.")
else:
    print('Using a uEye camera.')

#-----------------------------------------------------------------------------------------------

class Camera_Widget(QWidget):
    """
    Widget used to show our camera.
    Args:
        QWidget (class): QWidget can be put in another widget and / or window.
    """

    def __init__(self, colormode = "MONO8", type = "basler"):
        """
        Initialisation of our camera widget.
        """
        super().__init__(parent=None)

        self.setStyleSheet("background-color: #4472c4; border-radius: 10px;"
                           "border-color: black; border-width: 2px; font: bold 12px; padding: 20px;"
                           "border-style: solid;")

        # Camera
        self.max_width = 0
        self.max_height = 0
        self.colormode = colormode
        self.aoiTrueFalse = False
        self.camera = None
        self.type = type

        # Graphical interface
        self.cameraInfo = QLabel("Camera Info")
        self.cameraListCombo = QComboBox()
        self.initListCamera()

        self.cameraDisplay = QLabel()
        
        # Center the camera widget
        self.cameraDisplay.setAlignment(Qt.AlignCenter)

        # Create a self.layout and add widgets
        self.layout = QGridLayout()

        self.layout.addWidget(self.cameraDisplay, 0, 0, 4, 4) # row = 0, column = 0, rowSpan = 4, columnSpan = 4
        
        self.setLayout(self.layout)

        # Other variables
        self.timerUpdate = QTimer()
        self.frameWidth = self.cameraDisplay.width()
        self.frameHeight = self.cameraDisplay.height()
        print(f'Width : {self.frameWidth} - Height : {self.frameHeight}')

    def launchVideo(self):
        """
        Method used to launch the video.
        """
        self.timerUpdate.setInterval(int(self.camera.get_frame_rate()))
        self.timerUpdate.timeout.connect(self.refreshGraph)
        self.timerUpdate.start()    

    def refreshGraph(self):
        """
        Method used to refresh the graph for the image display.
        """
        self.cameraRawArray = self.camera.get_image()

        AOIX, AOIY, AOIWidth, AOIHeight = self.camera.get_aoi()

        # On teste combien d'octets par pixel
        if(self.bytes_per_pixel >= 2):
            # on créée une nouvelle matrice en 16 bits / C'est celle-ci qui compte pour les graphiques temporelles et les histogrammes
            self.cameraFrame = self.cameraRawArray.view(np.uint16)
            self.cameraFrame = np.reshape(self.cameraFrame, (AOIHeight, AOIWidth, -1))
            
            # on génère une nouvelle matrice spécifique à l'affichage.
            cameraFrame8b = self.cameraFrame / (2**(self.nBitsPerPixel-8))
            self.cameraArray = cameraFrame8b.astype(np.uint8)    
        else:
            self.cameraFrame = self.cameraRawArray.view(np.uint8)
            self.cameraFrame = np.reshape(self.cameraFrame, (AOIHeight, AOIWidth, -1))
            self.cameraArray = self.cameraFrame


        # Resize the Qpixmap at the great size
        widgetWidth, widgetHeight = self.widgetGeometry()
        
        # On retaille si besoin à la taille de la fenètre
        self.cameraDisp = np.reshape(self.cameraArray, (AOIHeight, AOIWidth, -1))
        self.cameraDisp = cv2.resize(self.cameraDisp, dsize=(self.frameWidth, self.frameHeight), interpolation=cv2.INTER_CUBIC)
        
        # Convert the frame into an image
        image = QImage(self.cameraDisp, self.cameraDisp.shape[1], self.cameraDisp.shape[0], self.cameraDisp.shape[1], QImage.Format_Indexed8)
        pmap = QPixmap(image)

        # display it in the cameraDisplay
        self.cameraDisplay.setPixmap(pmap)

        # "plot" it in the cameraDisplay
        self.cameraDisplay.setPixmap(pmap)

    def initListCamera(self):
        """
        Method used to initialize the different cameras linked to the computer.
        """
        self.nb_cam = camera.get_nb_of_cam()
        self.cameraInfo.setText('Cam Nb = '+str(self.nb_cam))
        if(self.nb_cam > 0):
            self.cameraList = camera.get_cam_list() 
            self.cameraListCombo.clear()
            for i in range(self.nb_cam):
                cam = self.cameraList[i]
                self.cameraListCombo.addItem(f'{cam[2]} (SN : {cam[1]})')

    def widgetGeometry(self):
        """
        Method use to get the width and the height of the widget.

        Returns:
            int: widget's width and height.
        """
        geometry = self.geometry()
        widgetWidth = geometry.width()
        widgetHeight = geometry.height()
        return widgetWidth, widgetHeight

    def connectCamera(self):
        """
        Method used to connect the camera.
        """
        self.selectedCamera = self.cameraListCombo.currentIndex()
        try :
            self.camera = camera.uEyeCamera(self.selectedCamera)
            self.type = 'ueye'
        except :
            try :
                self.camera = camera.BaslerCamera()
                self.type = 'basler'
            except :
                print("Error : No camera detected.")

        self.max_width = int(self.camera.get_sensor_max_width())
        self.max_height = int(self.camera.get_sensor_max_height())

        self.camera.set_exposure(100000)
        
        if self.type == 'ueye':
            if self.colormode == "MONO8":
                self.m_nColorMode = ueye.IS_CM_MONO8
                self.camera.set_colormode(self.m_nColorMode)

            elif self.colormode == "MONO10":
                self.m_nColorMode = ueye.IS_CM_MONO10
                self.camera.set_colormode(self.m_nColorMode)

            elif self.colormode == "MONO12":
                self.m_nColorMode = ueye.IS_CM_MONO12
                self.camera.set_colormode(self.m_nColorMode)

            else:
                try : 
                    self.m_nColorMode = ueye.IS_CM_MONO12
                    self.camera.set_colormode(self.m_nColorMode)

                except :
                    print("MONO 12 unavailable.")

                    try : 
                        self.m_nColorMode = ueye.IS_CM_MONO10
                        self.camera.set_colormode(self.m_nColorMode)

                    except : 
                        print("MONO 10 unavailable.")
                        self.camera.set_colormode(self.m_nColorMode)

                        try : 
                            self.m_nColorMode = ueye.IS_CM_MONO8
                            self.camera.set_colormode(self.m_nColorMode)

                        except : 
                            print("MONO 8 unavailable.")
                            print("Camera unavailable.")

        elif self.type == 'basler' :
            if self.colormode == "MONO8":
                self.m_nColorMode = 'Mono8'
                print(f'self.m_nColorMode : {self.m_nColorMode}')
                self.camera.set_colormode(self.m_nColorMode)

            elif self.colormode == "MONO10":
                self.m_nColorMode = 'Mono10'
                self.camera.set_colormode(self.m_nColorMode)

            elif self.colormode == "MONO12":
                self.m_nColorMode = 'Mono12'
                self.camera.set_colormode(self.m_nColorMode)

            else:
                try : 
                    self.m_nColorMode = 'Mono12'
                    self.camera.set_colormode(self.m_nColorMode)

                except :
                    print("MONO 12 unavailable.")

                    try : 
                        self.m_nColorMode = 'Mono10'
                        self.camera.set_colormode(self.m_nColorMode)

                    except : 
                        print("MONO 10 unavailable.")
                        self.camera.set_colormode(self.m_nColorMode)

                        try : 
                            self.m_nColorMode = 'Mono8'
                            self.camera.set_colormode(self.m_nColorMode)

                        except : 
                            print("MONO 8 unavailable.")
                            print("Camera unavailable.")  

        if self.type == 'ueye' :
            self.nBitsPerPixel = self.camera.nBitsPerPixel
        elif self.type == 'basler' :
            self.nBitsPerPixel = self.camera.nBitsPerPixel
            print(f'self.nBitsPerPixel : {self.nBitsPerPixel}')

        self.bytes_per_pixel = int(np.ceil(self.nBitsPerPixel / 8))
        print("nBitsPerPixel:\t", self.nBitsPerPixel)
        print("BytesPerPixel:\t", self.bytes_per_pixel)
        
        self.camera.set_aoi(0, 0, self.max_width-1, self.max_height-1)

        self.camera.alloc()
        self.camera.capture_video()

        # There is a way to set the initial minimumValue of the exposure as near as possible from the original minimumValue of the
        # camera, for any camera

        self.setLayout(self.layout)
        self.refreshGraph()

    def generateExpositionRangeList(self, pointsNumber):
        """
        Method used to create a list of pointsNumber points in the range of the camera's exposition.

        Args:
            nombrePoints (int): number of points possible in the range.

        Returns:
            list: list of points in the range of the camera's exposure.
        """
        (expositionRangeMinimum, expositionRangeMaximum) = self.camera.get_exposure_range()
        return np.linspace(expositionRangeMinimum+0.01, expositionRangeMaximum, pointsNumber) 

    def getFPSRange(self):
        """
        Method used to get the mininimum and maximum value of FPS.

        Returns:
            int: minimum and maximum values of FPS' range.
        """
        minTimePerFrame, maxTimePerFrame, timePerFrameIntervals = self.camera.get_frame_time_range()
        return int(1 / maxTimePerFrame) + 1, int(1 / minTimePerFrame) + 1

    def closeApp(self):
        """
        Method used to close the App.
        """
        self.close()
        self.closeEvent(None)

    def closeEvent(self, event):
        """
        Method used to close an event.

        Args:
            event (_???_): ???
        """
        if(self.camera != None):
            self.camera.stop_camera()
        QApplication.quit()

    def getGraphValues(self, farness = 5):
        """
        Method used to return the value of 4 points near the center of the frame.

        Args:
            farness (int, optional): how far are the points from the center. Defaults to 5.

        Returns:
            list: list of the value of the four points.
        """
        height, width, _ = self.cameraFrame.shape
        value1 = self.cameraFrame[width // 2 + farness][height // 2][0]
        value2 = self.cameraFrame[width // 2 - farness][height // 2][0]
        value3 = self.cameraFrame[width // 2][height // 2 + farness][0]
        value4 = self.cameraFrame[width // 2][height // 2 - farness][0]
        return [value1, value2, value3, value4]

    def launchAOI(self, AOIX, AOIY, AOIWidth, AOIHeight, type = None):
        """
        Method used to launch the AOI.
        I know it is not optimised, but that avoid a bug where the image is in black when students are changing the setting
        values without being in AOI mode.
        """
        if not self.aoiTrueFalse and type == "forced":
            pass
        else:
            # Do Forced / Do Unforced / Undo AOI Mode

            # "Pause" refresh
            self.timerUpdate.stop()

            # Stop video and un_alloc memory # Merci M Villemejane
            self.camera.stop_video()
            self.camera.un_alloc()

            if self.aoiTrueFalse and type == "forced":

                # Setting the AOI
                self.camera.set_aoi(AOIX, AOIY, AOIWidth, AOIHeight)

            elif not self.aoiTrueFalse and type == None:

                # Setting the AOI
                self.camera.set_aoi(AOIX, AOIY, AOIWidth, AOIHeight)
                self.aoiTrueFalse = True 
                print("--- AOI Active ---") 

            elif self.aoiTrueFalse and type == None:

                # Stop AOI
                self.camera.set_aoi(0, 0, self.max_width, self.max_height)
                self.aoiTrueFalse = False 
                print("--- Whole Camera ---")
                
            # Re-alloc memory and re-run video
            self.camera.alloc()
            self.camera.capture_video()

            # Restart the refresh
            self.timerUpdate.setInterval(int(self.camera.get_frame_rate()))
            self.timerUpdate.start()

    def setColor(self, color):
        """
        Method used to fast setup the color of the widget.

        Args:
            color (str): tell if it needs to be blue or orange.
        """
        if color == "blue":
            self.setStyleSheet("background-color: #4472c4; border-radius: 10px;"
                           "border-color: black; border-width: 2px; font: bold 12px; padding: 20px;"
                           "border-style: solid;")
        elif color == "orange":
            self.setStyleSheet("background-color: #c55a11; border-radius: 10px;"
                           "border-color: black; border-width: 2px; font: bold 12px; padding: 20px;"
                           "border-style: solid;")

#-----------------------------------------------------------------------------------------------

class Setting_Widget_Float(QWidget):
    """
    Widget designed to select a value in a list.

    Args:
        QWidget (class): QWidget can be put in another widget and / or window.
    """
    def __init__(self, selectionLabel, floatListToSelect):
        """
        Initialiszation of the widget.

        Args:
            selectionLabel (str): name given to the box and to the unit.
            floatListToSelect (list): list that will be described by the slider.
        """
        super().__init__()
        self.floatListToSelect = floatListToSelect
        self.selectionLabel = selectionLabel
        self.value = 0.01
        self.initUI()

    def initUI(self):
        """
        Sub-initialization method
        """
        group_box = QGroupBox(self.selectionLabel)
        layout = QGridLayout()

        # Create a layout
        line_label_layout = QGridLayout()

        # Create a line widget and place it into the grid layout
        self.line = QLineEdit(self)
        line_label_layout.addWidget(self.line, 0, 0, 1, 1) # row = 0, column = 0, rowSpan = 1, columnSpan = 1
        self.line.textChanged.connect(self.linetextValueChanged)

        # Create a label widget and place it into the grid layout
        self.labelValue = QLabel()
        line_label_layout.addWidget(self.labelValue, 0, 1, 1, 1) # row = 0, column = 1, rowSpan = 1, columnSpan = 1

        # Create a slider widget and place it into the grid layout
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, len(self.floatListToSelect) - 1)
        self.slider.valueChanged.connect(self.sliderValueChanged)

        layout.addWidget(self.slider, 0, 0, 1, 4) # row = 0, column = 0, rowSpan = 1, columnSpan = 4
        layout.addLayout(line_label_layout, 1, 0, 1, 4) # row = 1, column = 0, rowSpan = 1, columnSpan = 4

        group_box.setLayout(layout)

        main_layout = QGridLayout()
        main_layout.addWidget(group_box, 0, 0, 1, 1) # row = 0, column = 0, rowSpan = 1, columnSpan = 0 <=> QHBoxLayout or V
        self.setLayout(main_layout)

    def sliderValueChanged(self, value):
        """
        Method used to set the self.value and and the labelValue text each time the slider is triggered.

        Args:
            value (float): useful value of the slider.
        """
        self.value = self.floatListToSelect[value]
        self.labelValue.setText(self.selectionLabel + "= "+ str(math.floor(self.value * 100) / 100))

    def linetextValueChanged(self, text):
        """
        Method used to set the self.value, self and the labelValue text each time the line is triggered.

        Args:
            text (str): string that'll be converted in float to changed the important values.
        """
        self.value = float(text)
        self.labelValue.setText(self.selectionLabel + str(math.floor(float(text) * 100) / 100))
        self.setValue(float(text))
    
    def setValue(self, value):
        """
        Method used to set the value of the slider without using a long line each time.
        It sets the nearest value present in the list from the real value to the slider.

        Args:
            value (float): near value that will be put.
        """
        self.slider.setValue(np.argmin(np.abs(self.floatListToSelect - value)))

#-----------------------------------------------------------------------------------------------

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Camera Window")
        self.setGeometry(100, 100, 400, 300)

        widget = Camera_Widget(colormode = "MONO12")
        widget.connectCamera()
        widget.launchVideo()

        self.setCentralWidget(widget)

#-----------------------------------------------------------------------------------------------

# Launching as main for tests
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    sys.exit(app.exec_())
