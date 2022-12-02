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

PLT = ['MPV','PLT']
RBC = ['HCT', 'HBG', 'MCH', 'MCHC', 'MCV', 'RBC', 'RDW']
WBC = ['EOS%', 'EOS#', 'GRA%', 'GRA#', 'LYM%', 'LYM#', 'MON%', 'MON#', 'WBC']

#Class wrapper for Canvas and Plotting Capabilities
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=12, height=9, dpi=100, axes=1):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axs = []
        super().__init__(self.fig)

class TableWindow(QtWidgets.QMainWindow):
    def __init__(self, dataframe, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        self.widget = QtWidgets.QWidget()
        self.scroll = QtWidgets.QScrollArea()
        self.layout = QtWidgets.QVBoxLayout()
        self.datatable = QtWidgets.QTableWidget()

        self.df = dataframe
        self.datatable.setColumnCount(self.df.shape[1])
        self.datatable.setRowCount(self.df.shape[0])

        self.datatable.setHorizontalHeaderLabels(self.df.columns)
        #self.datatable.horizontalHeaderItem().setTextAlignment(Qt.AlignHCenter)

        for i in range(self.df.shape[0]):
            for j in range(self.df.shape[1]):
                self.datatable.setItem(i,j,QtWidgets.QTableWidgetItem(str(self.df.iloc[i, j])))
        self.scroll.setWidget(self.datatable)
        self.layout.addWidget(self.datatable)
        
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.setWindowTitle("Dataframe")
        self.show()


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

        location = '\\'.join(os.path.dirname(os.path.realpath(__file__)).split('\\')[:-1])

        self.dataframe = pd.read_csv(os.path.join(location,'tests','cleaned_data.csv'))
        self.unique_ids = np.unique(self.dataframe['FIELD_SID_PATIENT_ID'].values)

        self.features = sorted([column.split('_')[0] for column in self.dataframe.columns if 'Raw' in column])

        root_layout = QtWidgets.QVBoxLayout()
        myQWidget = QtWidgets.QWidget()
        
        first_row = QtWidgets.QHBoxLayout()
        second_row = QtWidgets.QHBoxLayout()
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
        self.feature_label.setBackground(QtGui.QBrush(QtGui.QColor(140,120,150)))
        self.feature_label.setSelectable(False)

        self.family_label = QtGui.QStandardItem("----- Select Blood Test(s) -----")
        self.family_label.setBackground(QtGui.QBrush(QtGui.QColor(140,120,150)))
        self.family_label.setSelectable(False)
        
        self.id_box.model().setItem(0,0,self.selected_label)
        self.id_box.lineEdit().setText("----- Select Patient(s) -----")
        
        for i in range(len(self.unique_ids)):
            self.id_box.addItem('Patient ID %s' % self.unique_ids[i])
            item = self.id_box.model().item(i+1, 0)
            item.setCheckState(QtCore.Qt.Unchecked)

        self.test_box = CheckableComboBox()
        self.test_box.model().setItem(0,0,self.family_label)
        self.test_box.lineEdit().setText("----- Select Blood Test(s) -----")
        for i, value in enumerate(['BLOOD', 'SPLEEN', 'BM']):
            self.test_box.addItem('%s' % value)
            item = self.test_box.model().item(i+1,0)
            item.setCheckState(QtCore.Qt.Unchecked)
            

        self.feature_box = CheckableComboBox()
        self.feature_box.model().setItem(0,0,self.feature_label)
        self.feature_box.lineEdit().setText("----- Select Feature(s) -----")
        for i in range(len(self.features)):
            self.feature_box.addItem('%s'% self.features[i])
            item = self.feature_box.model().item(i+1,0)
            item.setCheckState(QtCore.Qt.Unchecked)

        self.date_label = QtGui.QStandardItem("----- Select/Deselect Dates -----")
        self.date_label.setBackground(QtGui.QBrush(QtGui.QColor(120,180,130)))
        self.date_label.setSelectable(False)
        self.date_box = CheckableComboBox()
        self.date_box.model().setItem(0,0,self.date_label)
        self.date_box.lineEdit().setText("----- Select/Deselect Dates ------")

        self.df_button = QtWidgets.QPushButton('Show Dataframe')
        self.table_window= None
        #self.df_button.setFont(font)
        
        first_row.addWidget(self.id_box)
        first_row.addWidget(self.test_box)
        first_row.addWidget(self.feature_box)
        first_row.addWidget(self.plot_button)
        second_row.addWidget(self.toolbar)
        second_row.addWidget(self.date_box)
        second_row.addWidget(self.df_button)
        second_row.addStretch()
        self.date_box.setVisible(False)
        root_layout.addLayout(first_row)
        root_layout.addLayout(second_row)
        root_layout.addWidget(self.canvas)
        self.toolbar.setVisible(False)
        self.df_button.setVisible(False)
        self.canvas.setVisible(False)
        self.plot_button.clicked.connect(self.gen_plot)
        self.df_button.clicked.connect(self.show_dataframe)

    def gen_plot(self):
        print("Selected Patients:", self.id_box.selected_items)
        print("Selected Features:", self.feature_box.selected_items)
        print("Selected Tests:", self.test_box.selected_items)
        
        patient_ids = self.id_box.selected_items
        features = self.feature_box.selected_items
        tests = self.test_box.selected_items
        selected_dates = self.date_box.selected_items
        if selected_dates:
            print("Selected Dates:", selected_dates)
        self.toolbar.setVisible(True)
        self.canvas.setVisible(True)
        self.date_box.setVisible(True)
        self.df_button.setVisible(True)
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
            #print(raw_feature)
            data = []
            datepoints = []
            for patient in patient_ids:
                patient = patient.split(' ')[-1]
                if selected_dates:
                    patient_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID']==patient) & (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin(tests)) & (self.dataframe['ANALYSIS_DATE'].str.contains('|'.join(selected_dates), case=True))]
                    #self.dataframe['ANALYSIS_DATE'].isin(selected_dates)
                    #print(patient_df)
                else:
                    patient_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID']==patient) & (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin(tests))]
                datapoints = patient_df[raw_feature]
                #print(datapoints.values)
                dates = self.dataframe['ANALYSIS_DATE'][datapoints.index]
                dates = [date.split(' ')[0] for date in dates.values]
                #print(dates)
                axis.plot(dates, datapoints, label=patient, ls=':', linewidth=2.5)
                limits = [self.dataframe[feature+'_'+limit][datapoints.index].values[0] for limit in ['LowLimit', 'HighLimit']]
                data.append(datapoints)
                datepoints.append(dates)

            min_value = np.min(np.hstack(data).flatten())
            max_value = np.max(np.hstack(data).flatten())

            unique_dates = np.unique(np.hstack(datepoints).flatten())

            axis.axhline(y = limits[0], label='LowLimit', ls='-.', c='r')
            axis.axhline(y = limits[1], label='HighLimit', ls='-.', c='y')       

            axis.set_xlabel('Date')
            axis.set_ylabel(feature)
            axis.title.set_text(raw_feature +' Timeseries')
            axis.set_ylim(min_value-1, max_value+2)
            axis.margins(0)
            axis.legend()
        self.canvas.draw()

        for i in range(len(unique_dates)):
            self.date_box.addItem('%s'% unique_dates[i])
            item = self.date_box.model().item(i+1,0)
            item.setCheckState(QtCore.Qt.Unchecked)
            #item.setCheckState(QtCore.Qt.Checked)

        #self.setFixedWidth(1500)
        #self.setFixedHeight(1200)

    def show_dataframe(self):
        patient_ids = [patient.split(' ')[-1] for patient in self.id_box.selected_items]
        features = self.feature_box.selected_items
        tests = self.test_box.selected_items
        selected_dates = self.date_box.selected_items
        if selected_dates:
            patient_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID'].str.contains('|'.join(patient_ids), case=True)) & (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin(tests)) & (self.dataframe['ANALYSIS_DATE'].str.contains('|'.join(selected_dates), case=True))]
            #self.dataframe['ANALYSIS_DATE'].isin(selected_dates)
            #print(patient_df)
        else:
            patient_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID'].str.contains('|'.join(patient_ids), case=True)) & (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin(tests))]
        cols = [col for col in patient_df.columns if col in features]
        print(cols)
        #patient_df = patient_df.loc[:, cols]
        self.table_window = TableWindow(patient_df)
        self.table_window.show()
 

if __name__ == '__main__':

    app = QtWidgets.QApplication(['Test'])
    dialog_1 = Dialog()
    dialog_1.show()
    app.exec_()
