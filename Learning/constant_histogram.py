import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class Histogram_Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def update(self, new_frame):

        print("Debugging histogram")
        print(f"Frame = {new_frame}")
        print(f"Type Frame = {type(new_frame)}")
        
        if type(new_frame) == "NoneType":
            return None
        self.frame = new_frame
        self.plot_histogram()

    def plot_histogram(self):
        self.figure.clear()
        plt.hist(self.frame.flatten(), bins='auto')
        plt.title("Histogram")
        plt.xlabel("Value")
        plt.ylabel("Frequency")
        self.canvas.draw()
