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

#Class wrapper for Canvas and Plotting Capabilities
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=12, height=9, dpi=100, axes=1):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axs = []
        super().__init__(self.fig)

#Class wrapper for multi-item combo box
class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self):
        super(CheckableComboBox, self).__init__()
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QtGui.QStandardItemModel(self))
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        palette = QtWidgets.qApp.palette()
        palette.setBrush(QtGui.QPalette.Base, palette.button())
        self.lineEdit().setPalette(palette)
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

#Class wrapper for Dialog test window
class Dialog(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        location = os.path.dirname(os.path.realpath(__file__))

        self.dataframe = pd.read_csv(os.path.join(location,'tests','cleaned_data.csv'))
        self.unique_ids = np.unique(self.dataframe['FIELD_SID_PATIENT_ID'].values)

        self.features = sorted([column.split('_')[0] for column in self.dataframe.columns if 'Raw' in column])

        root_layout = QtWidgets.QVBoxLayout()
        myQWidget = QtWidgets.QWidget()
        
        first_row = QtWidgets.QHBoxLayout()
        myQWidget.setLayout(root_layout)
        self.setCentralWidget(myQWidget)
        self.id_box = CheckableComboBox()
        self.plot_button = QtWidgets.QPushButton("Generate Plot")
        self.canvas = MplCanvas(self, dpi=100)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.selected_label = QtGui.QStandardItem("----- Select Patient(s) -----")
        self.selected_label.setBackground(QtGui.QBrush(QtGui.QColor(150,200,120)))
        self.selected_label.setSelectable(False)
            
        self.feature_label = QtGui.QStandardItem("----- Select Feature(s) -----")
        self.feature_label.setBackground(QtGui.QBrush(QtGui.QColor(80,120,150)))
        self.feature_label.setSelectable(False)
        
        self.id_box.model().setItem(0,0,self.selected_label)
        self.id_box.lineEdit().setText("----- Select Patient(s) -----")
        
        for i in range(len(self.unique_ids)):
            self.id_box.addItem('Patient ID %s' % self.unique_ids[i])
            item = self.id_box.model().item(i+1, 0)
            item.setCheckState(QtCore.Qt.Unchecked)

        self.feature_box = CheckableComboBox()
        self.feature_box.model().setItem(0,0,self.feature_label)
        self.feature_box.lineEdit().setText("----- Select Feature(s) -----")
        for i in range(len(self.features)):
            self.feature_box.addItem('%s'% self.features[i])
            item = self.feature_box.model().item(i+1,0)
            item.setCheckState(QtCore.Qt.Unchecked)
        first_row.addWidget(self.id_box)
        first_row.addWidget(self.feature_box)
        first_row.addWidget(self.plot_button)
        root_layout.addLayout(first_row)
        root_layout.addWidget(self.toolbar)
        root_layout.addWidget(self.canvas)
        self.toolbar.setVisible(False)
        self.canvas.setVisible(False)
        self.plot_button.clicked.connect(self.gen_plot)

    def gen_plot(self):
        print("Selected Patients:", self.id_box.selected_items)
        print("Selected Features:", self.feature_box.selected_items)

        patient_ids = self.id_box.selected_items
        features = self.feature_box.selected_items
        self.toolbar.setVisible(True)
        self.canvas.setVisible(True)
        self.canvas.fig.clf()
        self.canvas.axs = []
        axis = None

        for idx,feature in enumerate(features):
            self.canvas.axs.append(axis)
            if len(features) ==1:
                axis = self.canvas.fig.add_subplot(1,1,idx+1)
            else:
                axis = self.canvas.fig.add_subplot(2,int(np.ceil(len(features)/2)),idx+1)
            raw_feature = feature + '_Raw'
            print(raw_feature)
            flag = False
            data = []
            for patient in patient_ids:
                patient = patient.split(' ')[-1]
                patient_df = self.dataframe[self.dataframe['FIELD_SID_PATIENT_ID']==patient]
                datapoints = patient_df[raw_feature]
                print(datapoints.values)
                dates = self.dataframe['ANALYSIS_DATE'][datapoints.index]
                dates = [date.split(' ')[0] for date in dates.values]
                print(dates)
                axis.plot(dates, datapoints, label=patient, ls=':', linewidth=2.5)
                limits = [self.dataframe[feature+'_'+limit][datapoints.index].values[0] for limit in ['LowLimit', 'HighLimit']]
                data.append(datapoints)

            min_value = np.min(np.hstack(data).flatten())
            max_value = np.max(np.hstack(data).flatten())

            print(min_value)
            print(max_value)

            axis.axhline(y = limits[0], label='LowLimit', ls='-.', c='r')
            axis.axhline(y = limits[1], label='HighLimit', ls='-.', c='y')       

            axis.set_xlabel('Date')
            axis.set_ylabel(feature)
            axis.title.set_text(raw_feature +' Timeseries')
            axis.set_ylim(min_value-1, max_value+2)
            axis.margins(0)
            axis.legend()
        self.canvas.draw()

        #self.setFixedWidth(1500)
        #self.setFixedHeight(1200)

if __name__ == '__main__':

    app = QtWidgets.QApplication(['Test'])
    dialog_1 = Dialog()
    dialog_1.show()
    app.exec_()
