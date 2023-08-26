# Libraries
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout
import sys
import pyqtgraph as pg
import numpy as np

class Histogram_Widget(QWidget):
    """
    Widget used to show histograms of array or list of lists.

    Args:
        QWidget (class): QWidget can be put in another widget and / or window.
    """

    def __init__(self, histogramTitle, FrameOrLists, timer):
        """
        Initialisation of our histogram.

        Args:
            histogramTitle (str): Title given to the histogram.
            FrameOrLists (str): "frame" or "lists", given to adapt the update method to the frame one 
                                    or to the lists of list one.
            timer (QTimer): Timer used to update our histogram.
        """
        super().__init__()
        self.setStyleSheet("background-color: #4472c4; border-radius: 10px; border-width: 1px;"
                           "border-color: black; padding: 6px; font: bold 12px; color: white;"
                           "text-align: center; border-style: solid;")

        # Setting important values as attributs
        self.histogramTitle = histogramTitle
        self.FrameOrLists = FrameOrLists

        self.colors = ['red', 'blue', 'green', 'orange']

        # Calling sub-initialisation's method
        self.UiComponents()

        # Creating a timer
        self.timerUpdate = timer #ms

    def UiComponents(self):
        """
        Sub-initialisation's method.
        """
        # Creating a plot window
        self.plotChart = pg.PlotWidget()
        
        # Adding some Labels to show the mean(s) and std(s)

        # !!! Warning !!! pg.LabelItem doesn't support LaTeX or overthings
        # It is code on a HTML basis, thus, you need to write it in HTML balises

        self.text_label_1 = pg.LabelItem("Mean & Std", color = "black", size = "8pt")
        self.text_label_1.setParentItem(self.plotChart.graphicsItem())
        self.text_label_1.anchor(itemPos=(1,0), parentPos=(1,0), offset=(-20,40))
        
        self.text_label_2 = pg.LabelItem("", color = "black", size = "8pt")
        self.text_label_2.setParentItem(self.plotChart.graphicsItem())
        self.text_label_2.anchor(itemPos=(1,0), parentPos=(1,0), offset=(-20,50))

        self.text_label_3 = pg.LabelItem("", color = "black", size = "8pt")
        self.text_label_3.setParentItem(self.plotChart.graphicsItem())
        self.text_label_3.anchor(itemPos=(1,0), parentPos=(1,0), offset=(-20,60))

        self.text_label_4 = pg.LabelItem("", color = "black", size = "8pt")
        self.text_label_4.setParentItem(self.plotChart.graphicsItem())
        self.text_label_4.anchor(itemPos=(1,0), parentPos=(1,0), offset=(-20,70))
       
        self.plotChart.setBackground("w")
        self.plotChart.setTitle(self.histogramTitle, color = "black", size = "12pt")
        self.plotChart.setLabel('left', 'Frequency', color = "black")  # Set Y-axis label
        self.plotChart.setLabel('bottom', 'test', color = "black")  # Set X-axis label
       
        self.plotChart.addLegend()

        # Create horizontal list i.e x-axis
        self.abscissas = range(4097) # 10^bits + 1 / bits = 12

        # Creating a grid layout
        layoutMain = QGridLayout()

        # Setting this layout to the widget
        self.setLayout(layoutMain)

        # Plot window goes on right side, spanning 3 rows
        layoutMain.addWidget(self.plotChart, 0, 0, 1, 1) #row = 0, column = 0, rowSpan = 1, columnSpan = 1

    def calculateHistogram(self, values):
        """
        Method used to calculate an histogram from 0 to 256 (include) from a list.

        Args:
            values (list): list coonverted inot a histogram.

        Returns:
            list: histogram converted from the list.
        """
        histogram = [0] * 4097  # Index 0 to 2^12+1

        for value in values:
            if 0 <= value <= 4096:
                histogram[value] += 1

        return histogram

    def update(self, data, numberOfPoints = None):
        """
        Update method for the histogram.

        Args:
            data ("np.darray" or "list of lists"): frame or lists that will be ploted into a histogram.
        """
        # Erase the last histogram
        self.plotChart.clear()

        # Plot method for the frame
        if self.FrameOrLists == "frame":
            data = data.flatten()

            # Take the value of mean and std before changing it into an histogram
            mean = round(np.mean(data), 2)
            std = round(np.std(data), 2)

            data = self.calculateHistogram(data)
            firstIndex, lastIndex = self.findFirstLastIndex(data)
            barGraph = pg.BarGraphItem(x = self.abscissas[firstIndex:lastIndex], height = data[firstIndex:lastIndex], width = 1, brush ='blue')
            self.plotChart.addItem(barGraph)

            # Set the text of the label
            self.text_label_1.setText(f"<html>M&#772; = {mean} & &#963; = {std}</html>")


        # Plot method for the list of lists
        elif self.FrameOrLists == "lists":
            if numberOfPoints == 1:
                color = self.colors[0]

                # Take the value of mean and std before changing it into an histogram
                mean = round(np.mean(data[0]), 2)
                std = round(np.std(data[0]), 2)

                histogram = self.calculateHistogram(data[0])
                firstIndex, lastIndex = self.findFirstLastIndex(histogram)
                barGraph = pg.BarGraphItem(x = self.abscissas[firstIndex:lastIndex], height = histogram[firstIndex:lastIndex], width = 0.6, brush = color, name = "Pixel n°" + str(1))
                self.plotChart.addItem(barGraph)

                # Set the text of the labels
                self.text_label_1.setText(f"<html>M&#772; = {mean} & &#963; = {std}</html>")
                self.text_label_2.setText("")
                self.text_label_3.setText("")
                self.text_label_4.setText("")

            else:
                for i, datum in enumerate(data):
                    color = self.colors[i]
                    mean1, mean2, mean3, mean4 = round(np.mean(data[0]), 2), round(np.mean(data[1]), 2), round(np.mean(data[2]), 2), round(np.mean(data[3]), 2)
                    std1, std2, std3, std4 = round(np.std(data[0]), 2), round(np.std(data[1]), 2), round(np.std(data[2]), 2), round(np.std(data[3]), 2)
                    
                    histogram = self.calculateHistogram(datum)
                    firstIndex, lastIndex = self.findFirstLastIndex(histogram)
                    barGraph = pg.BarGraphItem(x = self.abscissas[firstIndex:lastIndex], height = histogram[firstIndex:lastIndex], width = 0.6, brush = color, name = "Pixel n°" + str(i + 1))
                    self.plotChart.addItem(barGraph)

                    # Set the text of the labels
                    self.text_label_1.setText(f"<html>M&#772;<sub>1</sub> = {mean1} & &#963;<sub>1</sub> = {std1}</html>")
                    self.text_label_2.setText(f"<html>M&#772;<sub>2</sub> = {mean2} & &#963;<sub>2</sub> = {std2}</html>")
                    self.text_label_3.setText(f"<html>M&#772;<sub>3</sub> = {mean3} & &#963;<sub>3</sub> = {std3}</html>")
                    self.text_label_4.setText(f"<html>M&#772;<sub>4</sub> = {mean4} & &#963;<sub>4</sub> = {std4}</html>")

    def findFirstLastIndex(self, list):
        """
        Method used to find the first and the last index between or the intersting values are <=> values != 0.

        Args:
            list (list): list studied.

        Returns:
            int: first and last interesting index.
        """
        first_index = None
        last_index = None
        
        for i in range(len(list)):
            if list[i] != 0:
                if first_index is None:
                    first_index = i
                last_index = i

        # I add +1 here to prevent the +1 everywhere else, since it is a list index ...
        return first_index, last_index + 1

    def startMethod(self):
        """
        Method used to launch the update method.
        """
        if not self.timerUpdate.isActive():
            self.timerUpdate.start()

    def stopMethod(self):
        """
        Method used to stop the update method.
        """
        if self.timerUpdate.isActive():
            self.timerUpdate.stop()

# Launching as main for tests
if __name__ == "__main__":
    App = QApplication(sys.argv)

    window = Histogram_Widget("Histogram Test", "lists")
    window.update([[0,0,0,0,1,1,1,2,2,3,4], [0,23,4,5,5,5,5,4,6,5,23], [0,0,0,0,1,1,1,2,2,3,4], [0,0,0,0,1,1,1,2,2,3,4],])
    window.show()

    sys.exit(App.exec())
