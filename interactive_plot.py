from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import numpy as np
from utils import *

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=12, height=9, dpi=100, axes=1):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax1= None
        self.ax2= None
        self.ax3= None
        super().__init__(self.fig)

class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self):
        super(CheckableComboBox, self).__init__()
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QtGui.QStandardItemModel(self))
        self.selected_items = []

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
            self.selected_items.pop(-1)
        else:
            item.setCheckState(QtCore.Qt.Checked)
            self.selected_items.append(item.text())
        #print(self.selected_items)

class Dialog(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        location = os.path.dirname(os.path.realpath(__file__))

        self.dataframe = pd.read_csv(os.path.join(location,'tests','cleaned_data.csv'))
        self.unique_ids = np.unique(self.dataframe['FIELD_SID_PATIENT_ID'].values)

        self.features = sorted([column.split('_')[0] for column in self.dataframe.columns if 'Raw' in column])
        
        myQWidget = QtWidgets.QWidget()
        myBoxLayout = QtWidgets.QHBoxLayout()
        myQWidget.setLayout(myBoxLayout)
        self.setCentralWidget(myQWidget)
        self.id_box = CheckableComboBox()
        self.plot_button = QtWidgets.QPushButton("Generate Plot")
        for i in range(len(self.unique_ids)):
            self.id_box.addItem('Patient ID %s' % self.unique_ids[i])
            item = self.id_box.model().item(i, 0)
            item.setCheckState(QtCore.Qt.Unchecked)
        self.feature_box = CheckableComboBox()
        for i in range(len(self.features)):
            self.feature_box.addItem('%s'% self.features[i])
            item = self.feature_box.model().item(i,0)
            item.setCheckState(QtCore.Qt.Unchecked)
        myBoxLayout.addWidget(self.id_box)
        myBoxLayout.addWidget(self.feature_box)
        myBoxLayout.addWidget(self.plot_button)
        self.plot_button.clicked.connect(self.gen_plot)

    def gen_plot(self):
        print("Selected Patients:", self.id_box.selected_items)
        print("Selected Features:", self.feature_box.selected_items)

if __name__ == '__main__':

    app = QtWidgets.QApplication(['Test'])
    dialog_1 = Dialog()
    dialog_1.show()
    app.exec_()
