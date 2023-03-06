#GUI for blood data visualization and feature extraction
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import matplotlib
from PIL import Image, ImageQt
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from utils import *
plt.style.use('ggplot')
plt.rcParams['axes.xmargin'] = 0
plt.rcParams['axes.ymargin'] = 0
#plt.rcParams['figure.constrained_layout.use'] = True

PLT = ['MPV','PLT']
RBC = ['HCT', 'HGB', 'MCH', 'MCHC', 'MCV', 'RBC', 'RDW']
WBC = ['EOS%', 'EOS#', 'GRA%', 'GRA#', 'LYM%', 'LYM#', 'MON%', 'MON#', 'WBC']

family_dict = {'PLT FAMILY': PLT, 'RBC FAMILY': RBC, 'WBC FAMILY': WBC}

families = ['PLT FAMILY', 'RBC FAMILY', 'WBC FAMILY']

#Class wrapper for Canvas and Plotting Capabilities
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=12, height=9, dpi=100):
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

        self.main_df = dataframe
        self.datatable.setColumnCount(self.main_df.shape[1])
        self.datatable.setRowCount(self.main_df.shape[0])

        self.datatable.setHorizontalHeaderLabels(self.main_df.columns)
        #self.datatable.horizontalHeaderItem().setTextAlignment(Qt.AlignHCenter)

        for i in range(self.main_df.shape[0]):
            for j in range(self.main_df.shape[1]):
                self.datatable.setItem(i,j,QtWidgets.QTableWidgetItem(str(self.main_df.iloc[i, j])))
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
        self.setEditable(True) #check if this is really True
        self.lineEdit().setReadOnly(True)
        palette = QtWidgets.qApp.palette()
        palette.setBrush(QtGui.QPalette.Base, palette.button())
        self.lineEdit().setPalette(palette)
        self.selected_items = []

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.CheckState.Checked:
            item.setCheckState(QtCore.Qt.CheckState.Unchecked)
            self.selected_items.pop(-1)
        else:
            item.setCheckState(QtCore.Qt.CheckState.Checked)
            self.selected_items.append(item.text())
        #print(self.selected_items)

class InitialWindow(QtWidgets.QMainWindow):

    signal = QtCore.pyqtSignal(str)
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        location = os.path.dirname(os.path.realpath(__file__))

        self.selected_file = None

        myQWidget = QtWidgets.QWidget()

        self.pix_map = QtGui.QPixmap(os.path.join(location, 'BloodAnalyzer_InitialScreen.png'))

        self.image_label = QtWidgets.QLabel("")
        self.image_label.setPixmap(self.pix_map)
        self.image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.warning_label = QtWidgets.QLabel("Generating csv file...")
        self.warning_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.warning_label.setVisible(False)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setFixedWidth(450)
        self.progress_bar.setFixedHeight(50)
        self.progress_bar.setVisible(False)

        self.new_label  = QtWidgets.QLabel("Start New Analysis")
        self.new_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.new_button = QtWidgets.QPushButton("...")

        self.load_label = QtWidgets.QLabel("Load csv file")
        self.load_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.load_button = QtWidgets.QPushButton("...")

        root_layout = QtWidgets.QVBoxLayout()
        new_layout  = QtWidgets.QHBoxLayout()
        load_layout = QtWidgets.QHBoxLayout()
        second_row  = QtWidgets.QHBoxLayout()
        third_row   = QtWidgets.QHBoxLayout()

        myQWidget.setLayout(root_layout)
        self.setCentralWidget(myQWidget)

        new_layout.addWidget(self.new_label)
        new_layout.addWidget(self.new_button)

        load_layout.addWidget(self.load_label)
        load_layout.addWidget(self.load_button)

        second_row.addWidget(self.progress_bar)

        third_row.addLayout(new_layout)
        third_row.addLayout(load_layout)

        root_layout.addWidget(self.image_label)
        root_layout.addWidget(self.warning_label)
        root_layout.addLayout(second_row)
        root_layout.addLayout(third_row)

        self.new_button.clicked.connect(self.choose_directory)
        self.load_button.clicked.connect(self.choose_file)

        self.setFixedWidth(900)
        self.setFixedHeight(680)

        self.setWindowIcon(QtGui.QIcon(os.path.join(location, 'BloodAnalyzerIcon.png')))
        self.setWindowTitle("B.A.S.")

    def choose_directory(self):

        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select a folder", os.path.dirname(os.path.abspath(__file__)))

        if directory != '':
            self.warning_label.setVisible(True)
            self.progress_bar.setVisible(True)
            self.generate_csv(directory)

    def generate_csv(self, directory):

        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(len(os.listdir(directory)))

        current_date = ''.join(str(datetime.now()).split(' ')[0].split('-'))

        out_name = 'analysis_'+current_date+'.csv'

        location = os.path.dirname(os.path.realpath(__file__))

        out_name = os.path.join(location, out_name)

        raw_df = parse_multiple_files(directory, self.progress_bar)
        clean_df = clean_dataframe(raw_df)

        clean_df.to_csv(out_name, index=False)

        self.selected_file = out_name
        self.signal.emit('Closed')
        self.close()

    def choose_file(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select a file",
                                                        os.path.dirname(os.path.abspath(__file__)),
                                                        "Comma-separated values (*.csv)")
        if file !='':
            self.selected_file = file
            self.signal.emit('Closed')
            self.close()

#Class wrapper for Dialog test window
class SecondWindow(QtWidgets.QMainWindow):
    def __init__(self, filename, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root = '\\'.join(os.path.dirname(os.path.realpath(__file__)).split('\\')[:-1])
        location = os.path.dirname(os.path.realpath(__file__))

        self.filename = filename
        self.dataframe = pd.read_csv(self.filename)
        self.unique_ids = np.sort(np.unique(self.dataframe['FIELD_SID_PATIENT_ID'].values))

        self.features = sorted([column.split('_')[0] for column in self.dataframe.columns
                                if 'Value' in column])

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
            item.setCheckState(QtCore.Qt.CheckState.Unchecked)

        self.test_box = CheckableComboBox()
        self.test_box.model().setItem(0,0,self.family_label)
        self.test_box.lineEdit().setText("----- Select Blood Test(s) -----")
        for i, value in enumerate(np.unique(self.dataframe['FIELD_SID_ANIMAL_NAME'].values)):
            self.test_box.addItem('%s' % value)
            item = self.test_box.model().item(i+1,0)
            item.setCheckState(QtCore.Qt.CheckState.Unchecked)

        self.feature_box = CheckableComboBox()
        self.feature_box.model().setItem(0,0,self.feature_label)
        self.feature_box.lineEdit().setText("----- Select Feature(s) -----")
        for i in range(len(families)):
            self.feature_box.addItem('%s'% families[i])
            item = self.feature_box.model().item(i+1,0)
            item.setCheckState(QtCore.Qt.CheckState.Unchecked)

        self.date_label = QtGui.QStandardItem("----- Select/Deselect Dates -----")
        self.date_label.setBackground(QtGui.QBrush(QtGui.QColor(120,180,130)))
        self.date_label.setSelectable(False)
        self.date_box = CheckableComboBox()
        self.date_box.model().setItem(0,0,self.date_label)
        self.date_box.lineEdit().setText("----- Select/Deselect Dates ------")

        self.imported_label = QtGui.QStandardItem("----- Select Imported Metadata(s) -----")
        self.imported_label.setBackground(QtGui.QBrush(QtGui.QColor(150,200,120)))
        self.imported_label.setSelectable(False)

        self.imported_box = CheckableComboBox()
        self.imported_box.model().setItem(0,0,self.imported_label)
        self.imported_box.lineEdit().setText("----- Select Imported Metadata(s) -----")

        self.df_button = QtWidgets.QPushButton('Show Dataframe')
        self.table_window= None
        #self.df_button.setFont(font)

        self.export_button = QtWidgets.QPushButton('Export Selected Data')
        self.selected_frame = None

        self.import_button = QtWidgets.QPushButton('Import Metadata')
        self.metadata = None

        self.global_radio = QtWidgets.QRadioButton('Global Metrics')
        self.global_radio.setChecked(False)
        self.time_radio   = QtWidgets.QRadioButton('Time-based Metrics')
        self.time_radio.setChecked(False)

        self.stat_button = QtWidgets.QPushButton('Generate Box-Plot')

        self.warning_box = QtWidgets.QMessageBox()
        self.warning_box.setIcon(QtWidgets.QMessageBox.Warning)
        self.warning_box.setWindowTitle('Warning')
        self.warning_box.addButton(QtWidgets.QMessageBox.Ok)

        self.contained_box = QtWidgets.QHBoxLayout()
        self.contained_box.addWidget(self.global_radio)
        self.contained_box.addWidget(self.time_radio)
        self.contained_box.addWidget(self.stat_button)

        first_row.addWidget(self.id_box)
        first_row.addWidget(self.test_box)
        first_row.addWidget(self.feature_box)
        first_row.addWidget(self.plot_button)
        second_row.addWidget(self.toolbar)
        second_row.addWidget(self.date_box)
        second_row.addWidget(self.df_button)
        second_row.addWidget(self.export_button)
        second_row.addWidget(self.import_button)
        second_row.addWidget(self.imported_box)
        second_row.addLayout(self.contained_box)
        second_row.addStretch()

        self.date_box.setVisible(False)
        root_layout.addLayout(first_row)
        root_layout.addLayout(second_row)
        root_layout.addWidget(self.canvas)
        self.toolbar.setVisible(False)
        self.df_button.setVisible(False)
        self.export_button.setVisible(False)
        #self.import_button.setVisible(False)
        self.imported_box.setVisible(False)
        self.canvas.setVisible(False)
        self.global_radio.setVisible(False)
        self.time_radio.setVisible(False)
        self.stat_button.setVisible(False)

        self.plot_button.clicked.connect(self.gen_plot)
        self.df_button.clicked.connect(self.show_dataframe)
        self.export_button.clicked.connect(self.export_dataframe)
        self.import_button.clicked.connect(self.import_data)
        self.stat_button.clicked.connect(self.generate_boxplot)

        self.setWindowIcon(QtGui.QIcon(os.path.join(location, 'BloodAnalyzerIcon.png')))
        self.setWindowTitle("B.A.S.")

    def gen_plot(self):
        print("Selected Patients:", self.id_box.selected_items)
        print("Selected Family:", self.feature_box.selected_items)
        print("Selected Tests:", self.test_box.selected_items)

        patient_ids = self.id_box.selected_items
        family = self.feature_box.selected_items
        tests = self.test_box.selected_items
        selected_dates = self.date_box.selected_items
        if selected_dates:
            print("Selected Dates:", selected_dates)

        if len(family) == 0:
            family.append('RBC FAMILY')
        if len(tests) ==0:
            tests.append('BLOOD')

        self.toolbar.setVisible(True)
        self.canvas.setVisible(True)
        self.date_box.setVisible(True)
        self.df_button.setVisible(True)
        self.export_button.setVisible(True)
        self.import_button.setVisible(True)
        self.canvas.fig.clf()
        self.canvas.axs = []
        axis = None

        features = family_dict[family[0]]

        warning_list = []
        unique_dates = []

        print(features)

        for idx,feature in enumerate(features):
            self.canvas.axs.append(axis)
            if family[0] =='WBC FAMILY':
                axis = self.canvas.fig.add_subplot(3,3,idx+1)
            else:
                axis = self.canvas.fig.add_subplot(2,int(np.ceil(len(features)/2)),idx+1)
            raw_feature = feature + '_Value'
            print(raw_feature)
            data = []
            datepoints = []
            for patient in patient_ids:
                patient = patient.split(' ')[-1]
                print(patient)
                if selected_dates:
                    patient_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID']==patient)&
                                                (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin(tests))&
                                                (self.dataframe['ANALYSIS_DATE'].str.contains('|'.join(selected_dates),
                                                case=True))]
                    #self.dataframe['ANALYSIS_DATE'].isin(selected_dates)
                    #print(patient_df)
                else:
                    patient_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID']==str(patient))&
                                                (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin(tests))]
                datapoints = patient_df[raw_feature]
                print(datapoints.values)
                dates = self.dataframe['ANALYSIS_DATE'][datapoints.index]
                dates = [date.split(' ')[0] for date in dates.values]
                print(dates)
                axis.plot(dates, datapoints, label=patient, ls=':', marker = 'o', linewidth=2.5)
                try:
                    limits = [self.dataframe[feature+'_'+limit][datapoints.index].values[0]
                              for limit in ['LowLimit', 'HighLimit']]
                    data.append(datapoints)
                    datepoints.append(dates)
                except:
                    warning_list.append(patient)
                    limits = []
            
            try:
                unique_dates = np.unique(np.hstack(datepoints).flatten())
                min_value = np.min(np.hstack(data).flatten())
                max_value = np.max(np.hstack(data).flatten())
                axis.set_ylim(min_value-1, max_value+2)
                axis.axhline(y = limits[0], label='LowLimit', ls='-.', c='r')
                axis.axhline(y = limits[1], label='HighLimit', ls='-.', c='y')
            except:
                pass

            axis.set_xlabel('Date')
            axis.set_ylabel(feature)

            axis.legend()

        warning_list = np.unique(warning_list).tolist()
        self.show_warning_message(warning_list, tests)
        self.canvas.fig.autofmt_xdate()
        self.canvas.fig.suptitle(t = family[0] + " Time-series", fontsize = 24, y=0.95)
        self.canvas.draw()
        
        self.update_datebox(unique_dates)
        self.showMaximized()

    def show_warning_message(self, warning_list, tests):

        if len(warning_list)==1:
            self.warning_box.setText('Patient ID #'+str(warning_list[0])+" has no "+tests[0]+" samples." +'\n' + 'Try with another patient ID.')
            self.warning_box.exec_()
        elif len(warning_list)>1:
            self.warning_box.setText('Patient IDs #'+str(','.join(warning_list))+" have no "+tests[0]+" samples." +'\n' + 'Try with another patient ID.')
            self.warning_box.exec_()


    def update_datebox(self, new_dates):
        new_dates = sorted(new_dates, key = lambda x: datetime.strptime(x, '%d-%m-%y'))
        count = self.date_box.count()
        print('Old date count:', count)
        if count == 1:
            for i in range(len(new_dates)):
                self.date_box.addItem('%s'% new_dates[i])
                item = self.date_box.model().item(i+1,0)
                item.setCheckState(QtCore.Qt.Unchecked)
        else:
            for i in range(len(new_dates)):
                if i <count-1:
                    self.date_box.setItemText(i+1, new_dates[i])
                else:
                    self.date_box.addItem('%s'% new_dates[i])
                item = self.date_box.model().item(i+1,0)
                item.setCheckState(QtCore.Qt.Unchecked)
        print('New date count:', self.date_box.count())

    def show_dataframe(self):
        patient_ids = [patient.split(' ')[-1] for patient in self.id_box.selected_items]
        features = self.feature_box.selected_items
        tests = self.test_box.selected_items
        selected_dates = self.date_box.selected_items
        if selected_dates:
            patient_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID'].str.contains('|'.join(patient_ids), case=True))&
                                        (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin(tests))&
                                        (self.dataframe['ANALYSIS_DATE'].str.contains('|'.join(selected_dates), case=True))]
            #self.dataframe['ANALYSIS_DATE'].isin(selected_dates)
            #print(patient_df)
        else:
            patient_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID'].str.contains('|'.join(patient_ids), case=True))&
                                        (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin(tests))]
        self.selected_frame = patient_df
        self.table_window = TableWindow(self.selected_frame)
        self.table_window.show()

    def export_dataframe(self):
        patient_ids = [patient.split(' ')[-1] for patient in self.id_box.selected_items]
        features = self.feature_box.selected_items
        tests = self.test_box.selected_items
        selected_dates = self.date_box.selected_items
        if selected_dates:
            patient_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID'].str.contains('|'.join(patient_ids), case=True))&
                                        (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin(tests))&
                                        (self.dataframe['ANALYSIS_DATE'].str.contains('|'.join(selected_dates), case=True))]
            #self.dataframe['ANALYSIS_DATE'].isin(selected_dates)
            #print(patient_df)
        else:
            patient_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID'].str.contains('|'.join(patient_ids), case=True))&
                                        (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin(tests))]
        self.selected_frame = patient_df
        filename = os.path.join(self.root,'tests', 'selected_data.csv')
        self.selected_frame.to_csv(filename, index=False)
        #current_date = str(datetime())

    def import_data(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Select a file",
                                                        os.path.dirname(os.path.abspath(__file__)),
                                                        "Comma-separated values (*.csv *.xlsx)")

        if file.split('.')[-1]=='csv':
            print('csv')
            metadata = pd.read_csv(file)
        else:
            print('xlsx')
            excel = pd.ExcelFile(file)
            metadata = excel.parse()

        self.metadata = metadata
        patient_ids = [str(animal_id) for animal_id in metadata['animal_id'].values]
        #selected_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID'].str.contains('|'.join(patient_ids), case=True))]
        for i,col in enumerate(metadata.columns[1:]):
            uniques = metadata[col].unique()
            self.dataframe[col]=''
            for idx, patient in enumerate(patient_ids):
                self.dataframe.loc[self.dataframe['FIELD_SID_PATIENT_ID'].str.contains(patient),col]= metadata[metadata['animal_id']==int(patient)][col].values[0]
            self.imported_box.addItem('%s'% col)
            item = self.imported_box.model().item(i+1,0)
            item.setCheckState(QtCore.Qt.Unchecked)
        self.imported_box.setVisible(True)
        self.global_radio.setVisible(True)
        self.time_radio.setVisible(True)
        self.stat_button.setVisible(True)

    def generate_boxplot(self):

        self.toolbar.setVisible(True)
        self.canvas.setVisible(True)
        self.df_button.setVisible(True)
        self.export_button.setVisible(True)

        family = self.feature_box.selected_items
        tests = self.test_box.selected_items

        meta_patients = [str(animal_id) for animal_id in self.metadata['animal_id'].values]
        #print(meta_patients)(self.dataframe['FIELD_SID_PATIENT_ID'].str.contains('|'.join(meta_patients), case=True))

        selected_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID'].str.contains('|'.join(meta_patients), case=True))&
                                     (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin(tests))]

        #print(selected_df)

        filters = self.imported_box.selected_items

        #print(filters)
        if len(filters)>1:
            column = '-'.join(filters)
            selected_df[column] = selected_df[filters].apply(lambda x: '_'.join(x), axis=1)
            uniques = selected_df[column].unique()
        else:
            column = filters[0]
            uniques = selected_df[column].unique()

        groupings = [np.where(selected_df[column].values==unique) for unique in uniques]

        #print(groupings)

        wd = 0.5
        self.canvas.fig.clf()
        self.canvas.axs = []
        axis = None

        #print('A')
        features = family_dict[family[0]]
        features = [feature+'_Value' for feature in features]
        if self.global_radio.isChecked():
            print('Global')
            x_pos = 0.5
            for idx, feature in enumerate(features):
                if family[0] =='WBC FAMILY':
                    axis = self.canvas.fig.add_subplot(3,3,idx+1)
                else:
                    axis = self.canvas.fig.add_subplot(2,int(np.ceil(len(features)/2)),idx+1)

                #print('B')
                for idy, group in enumerate(groupings):
                    series = selected_df[feature].values[group]
                    axis.bar(x_pos+idy*wd, np.mean(series), width=wd, yerr=np.std(series),
                             alpha=0.5, ecolor='black', capsize=6, label=uniques[idy])
                    axis.set_ylabel(feature)

        elif self.time_radio.isChecked():
            print('Time-based')
            unique_dates = selected_df['ANALYSIS_DATE'].apply(lambda x: x.split(' ')[0]).unique()

            medians = []
            stds  = []#lol
            for idx, date in enumerate(unique_dates):
                selected_perdate = selected_df[selected_df['ANALYSIS_DATE'].str.contains(date)]
                groupings = [np.where(selected_perdate[column].values == unique)
                             for unique in uniques]
                median_perdate = []
                std_perdate = []
                for idy, group in enumerate(groupings):
                    median_pergroup = np.median(selected_perdate[features].values[group], axis=0)
                    std_pergroup =  np.std(selected_perdate[features].values[group], axis=0)
                    median_perdate.append(median_pergroup)
                    std_perdate.append(std_pergroup)
                medians.append(np.vstack(median_perdate))
                stds.append(np.vstack(std_perdate))
            medians = np.array(medians)
            stds = np.array(stds)

            x_pos = np.arange(1,2*len(unique_dates), 2)

            for idx, feature in enumerate(features):
                if family[0] =='WBC FAMILY':
                    axis = self.canvas.fig.add_subplot(3,3,idx+1)
                else:
                    axis = self.canvas.fig.add_subplot(2,int(np.ceil(len(features)/2)),idx+1)
                [axis.bar(x_pos+i*wd, medians[:,i,idx], yerr=stds[:,i,idx],
                 width=wd, alpha=0.5, ecolor='black', capsize=6, label=uniques[i])
                 for i in range(medians.shape[1])]
                axis.set_ylabel(feature)
                axis.set_xticks(x_pos+wd, unique_dates)
            self.canvas.fig.autofmt_xdate()#Comment if plotting fails
        else:
            pass
        #print('F')
        handles, labels = axis.get_legend_handles_labels()
        self.canvas.fig.legend(handles,labels, loc='upper left')
        #self.canvas.fig.suptitle(family[0]+' & METADATA')
        self.canvas.draw()

class ScreenHandler(QtWidgets.QMainWindow):

    def __init__(self):

        super().__init__()
        self.first_window = InitialWindow()
        self.second_window = None
        self.first_window.signal.connect(self.change_window)
        self.first_window.show()

    @QtCore.pyqtSlot(str)
    def change_window(self, event):
        print(self.first_window.selected_file)
        self.second_window = SecondWindow(self.first_window.selected_file)
        self.second_window.show()

if __name__ == '__main__':

    app = QtWidgets.QApplication(['Test'])
    main_widget = ScreenHandler()

    #dialog_1 = Dialog()
    #dialog_1.show()

    app.exec()
