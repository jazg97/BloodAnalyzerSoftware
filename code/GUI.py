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
            try:
                self.selected_items.remove(index.data())
            except:
                pass
        else:
            item.setCheckState(QtCore.Qt.CheckState.Checked)
            self.selected_items.append(item.text())
        if len(self.selected_items)>0:
            self.setCurrentText(', '.join(self.selected_items))
        #print(self.selected_items)
    
    def setCurrentText(self, text):
        self.lineEdit().setText(text)

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

        #self.new_label  = QtWidgets.QLabel("")
        #self.new_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.new_button = QtWidgets.QPushButton("Generate new csv file(s)")
        #self.new_button.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.new_button.setToolTip('Select a directory with XML files from the study of interest.')
        
        #self.load_label = QtWidgets.QLabel("")
        #self.load_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.load_button = QtWidgets.QPushButton("Load csv file")
        #self.load_button.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.load_button.setToolTip('Select a previously generated csv file to explore and visualize data.')  

        root_layout = QtWidgets.QVBoxLayout()
        new_layout  = QtWidgets.QHBoxLayout()
        load_layout = QtWidgets.QHBoxLayout()
        second_row  = QtWidgets.QHBoxLayout()
        third_row   = QtWidgets.QHBoxLayout()

        myQWidget.setLayout(root_layout)
        self.setCentralWidget(myQWidget)

        #new_layout.addWidget(self.new_label)
        new_layout.addWidget(self.new_button)

        #load_layout.addWidget(self.load_label)
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
        raw_df = parse_multiple_files(directory, self.progress_bar)
        clean_df = clean_dataframe(raw_df)
        
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save as', os.path.dirname(os.path.abspath(__file__)), "Comma-separated values (*.csv)")
        print(filename)
        print(len(clean_df))
        owner_groups = clean_df.groupby('FIELD_SID_OWNER_LASTNAME')
        owner_dict = {owner: owner_groups.get_group(owner) for owner in clean_df['FIELD_SID_OWNER_LASTNAME'].unique()}
        
        for owner, owner_df in owner_dict.items():
            subset_filename = filename.split('.')[0]+'_'+owner+'.csv'
            print(subset_filename)
            owner_df.to_csv(subset_filename, index=False)

        #clean_df.to_csv(filename, index=False)
        #self.selected_file = filename
        
        self.progress_bar.setVisible(False)
        self.warning_label.setVisible(False)
        #self.signal.emit('Closed')
        #self.close()

    def choose_file(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select a file",
                                                        os.path.dirname(os.path.abspath(__file__)),
                                                        "Comma-separated values (*.csv)")
        if file !='':
            self.selected_file = file
            self.signal.emit('Closed')
            self.close()

class WelcomeDialog(QtWidgets.QDialog):
    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent)
        location = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(os.path.join(location, 'BloodAnalyzerIcon.png')))
        self.setWindowTitle('Welcome')
        
        # Add the logo to the message box
        logo_label = QtWidgets.QLabel()
        logo_pixmap = QtGui.QPixmap(os.path.join(location, 'BloodAnalyzer_Logo.png'))  # Replace "path/to/your/logo.png" with the actual path to your logo
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(QtCore.Qt.AlignCenter)

        # Add welcome message to the layout
        welcome_label = QtWidgets.QLabel(self)
        welcome_label.setText("Welcome to BAS!")
        welcome_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Add instructions to the layout
        instructions_label = QtWidgets.QLabel(self)
        instructions_label.setText('Here are some brief instructions to get you started:\n\n1.'+
                                   'Select the patients IDs.\n2. Select the type of blood test.\n3.'+
                                   'Select the features family.\n4. Generate the desired plot')
        instructions_label.setAlignment(QtCore.Qt.AlignCenter)   
        #'<a href="https://github.com/your_username/your_repository">Click here to visit the GitHub repository</a>'
        #Add link to the Github repo
        link_label = QtWidgets.QLabel()
        link_label.setText('For more information, please visit our '+
                               '<a href="https://github.com/jazg97/BloodAnalyzerSoftware">GitHub repository</a>.')
        link_label.setAlignment(QtCore.Qt.AlignCenter)
        link_label.setOpenExternalLinks(True)
        link_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        #self.info_box.addWidget(QtWidgets.QMessageBox.Ok)
        
        message_layout = QtWidgets.QVBoxLayout()
        message_layout.addWidget(logo_label)
        message_layout.addWidget(welcome_label)
        message_layout.addWidget(instructions_label)
        message_layout.addWidget(link_label)
        #message_layout.addWidget(QtWidgets.QMessageBox.Ok)
        
        self.setLayout(message_layout)        

#Class wrapper for Dialog test window
#Class wrapper for Dialog test window
class SecondWindow(QtWidgets.QMainWindow):
    def __init__(self, filename, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root = '\\'.join(os.path.dirname(os.path.realpath(__file__)).split('\\')[:-1])
        location = os.path.dirname(os.path.realpath(__file__))

        self.filename = filename
        self.dataframe = pd.read_csv(self.filename)
        self.unique_ids = np.sort(np.unique(self.dataframe['FIELD_SID_PATIENT_ID'].astype(str).values))

        self.features = sorted([column.split('_')[0] for column in self.dataframe.columns
                                if 'Value' in column])

        root_layout = QtWidgets.QHBoxLayout()
        myQWidget = QtWidgets.QWidget()

        first_column = QtWidgets.QVBoxLayout()
        second_column = QtWidgets.QVBoxLayout()
        myQWidget.setLayout(root_layout)
        self.setCentralWidget(myQWidget)
        
        subsection_font = QtGui.QFont()
        subsection_font.setBold(True)
        subsection_font.setUnderline(True)
        subsection_font.setPointSize(16)
        
        label_font = QtGui.QFont()
        label_font.setBold(True)
        label_font.setUnderline(False)
        label_font.setPointSize(12)
        
        self.menubar = self.menuBar()
        self.file_menu = self.menubar.addMenu('File')
        self.edit_menu = self.menubar.addMenu('Window')
        self.import_menu= self.menubar.addMenu('Import')
        self.data_menu = self.menubar.addMenu('Data')
        self.help_menu = self.menubar.addMenu('Help')
        
        self.open_action = QtWidgets.QAction('Open csv File', self)
        self.file_menu.addAction(self.open_action)
        
        self.reset_action = QtWidgets.QAction('Reset Window', self)
        self.reset_action.triggered.connect(self.reset_window)
        self.edit_menu.addAction(self.reset_action)
        
        self.showAll_action = QtWidgets.QAction('Show All Dataframe', self)
        self.showAll_action.triggered.connect(self.show_dataframe)
        self.data_menu.addAction(self.showAll_action)
        self.showSel_action = QtWidgets.QAction('Show Selected Dataframe', self)
        self.data_menu.addAction(self.showSel_action)
        
        self.importNew_action = QtWidgets.QAction('Import New xml Files', self)
        self.import_menu.addAction(self.importNew_action)
        self.importMeta_action= QtWidgets.QAction('Import Metadata', self)
        self.importMeta_action.triggered.connect(self.import_data)
        self.import_menu.addAction(self.importMeta_action)
        
        self.column_label = QtWidgets.QLabel(self)
        self.column_label.setText('Filter Options')
        self.column_label.setFont(subsection_font)
        self.column_label.setToolTip('Select and Filter Data to plot.') 
        
        #self.explanation_label = QtWidgets.QLabel(self)
        #self.explanation_label.setText('Select data to plot')
        
        self.first_label = QtWidgets.QLabel(self)
        self.first_label.setText('1) Patient ID Selection')
        self.first_label.setFont(label_font)
        
        self.second_label = QtWidgets.QLabel(self)
        self.second_label.setText('2) Blood Source Selection')
        self.second_label.setFont(label_font)
        
        self.third_label = QtWidgets.QLabel(self)
        self.third_label.setText('3) Feature Selection')
        self.third_label.setFont(label_font)
        
        self.fourth_label = QtWidgets.QLabel(self)
        self.fourth_label.setText('4) Filter by Date')
        self.fourth_label.setFont(label_font)
        
        self.meta_label = QtWidgets.QLabel(self)
        self.meta_label.setText('5) Metadata Selection')
        self.meta_label.setFont(label_font)
        
        self.plot_button = QtWidgets.QPushButton("Generate Plot")
        self.plot_button.setToolTip('Generate Timeseries Plot based on ID, Feature Family & Blood Test.')
        self.canvas = MplCanvas(self, dpi=100)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.selected_label = QtGui.QStandardItem("----- Select Patient(s) -----")
        self.selected_label.setBackground(QtGui.QBrush(QtGui.QColor(150,200,120)))
        self.selected_label.setSelectable(False)
        
        self.feature_buttonGroup = QtWidgets.QButtonGroup(self)
        self.feature_groupbox = QtWidgets.QGroupBox('Feature Options')
        self.feature_groupbox.setStyleSheet("QGroupBox { background-color: #f0f0f0; }")
        self.feature_vbox  = QtWidgets.QVBoxLayout()

        self.feature_checkbox = [QtWidgets.QCheckBox(feature, self) for feature in families]
        _ = [(self.feature_buttonGroup.addButton(checkbox), self.feature_vbox.addWidget(checkbox))  for checkbox in self.feature_checkbox]
        self.feature_groupbox.setLayout(self.feature_vbox)
        self.feature_buttonGroup.setExclusive(True)
        
        self.test_buttonGroup = QtWidgets.QButtonGroup(self)
        self.test_groupbox = QtWidgets.QGroupBox('Blood Sources')
        self.test_vbox  = QtWidgets.QVBoxLayout()

        self.test_checkbox = [QtWidgets.QCheckBox(blood, self) for blood in np.unique(self.dataframe['FIELD_SID_ANIMAL_NAME'].values)]
        _ = [(self.test_buttonGroup.addButton(checkbox), self.test_vbox.addWidget(checkbox))  for checkbox in self.test_checkbox]
        self.test_groupbox.setLayout(self.test_vbox)
        self.test_buttonGroup.setExclusive(True)
        self.test_groupbox.setFlat(False)
        
        self.imported_label = QtGui.QStandardItem("----- Select Imported Metadata(s) -----")
        self.imported_label.setBackground(QtGui.QBrush(QtGui.QColor(150,200,120)))
        self.imported_label.setSelectable(False)
        
        self.date_label = QtGui.QStandardItem("----- Select/Deselect Dates -----")
        self.date_label.setBackground(QtGui.QBrush(QtGui.QColor(120,180,130)))
        self.date_label.setSelectable(False)

        self.id_box = CheckableComboBox()
        self.test_box = CheckableComboBox()
        
        self.initiate_idBox(self.unique_ids)        
        
        self.date_box = CheckableComboBox()
        self.date_box.model().setItem(0,0,self.date_label)
        self.date_box.lineEdit().setText("----- Select/Deselect Dates ------")

        self.imported_box = CheckableComboBox()
        self.imported_box.model().setItem(0,0,self.imported_label)
        self.imported_box.lineEdit().setText("----- Select Imported Metadata(s) -----")

        self.table_window= None
        self.selected_frame = None
        self.metadata = None
        
        self.meta_groupbox = QtWidgets.QGroupBox('Metadata Plotting Options')

        self.global_radio = QtWidgets.QRadioButton('Global Metrics')
        self.global_radio.setChecked(False)
        self.time_radio   = QtWidgets.QRadioButton('Time-series')
        self.time_radio.setChecked(False)

        self.contained_box = QtWidgets.QHBoxLayout()
        self.contained_box.addWidget(self.global_radio)
        self.contained_box.addWidget(self.time_radio)
        
        self.meta_groupbox.setLayout(self.contained_box)
        #self.feature_buttonGroup.setExclusive(True)

        self.stat_button = QtWidgets.QPushButton('Generate Box-Plot')
        self.stat_button.setToolTip('Generate Global or Time-based Boxplot based on Metadata.')
        
        self.warning_box = QtWidgets.QMessageBox()
        self.warning_box.setIcon(QtWidgets.QMessageBox.Warning)
        self.warning_box.setWindowTitle('Warning')
        self.warning_box.addButton(QtWidgets.QMessageBox.Ok)
        
        self.welcome_dialog = None
        
        self.reset_button = QtWidgets.QPushButton('Reset Window')
        
        first_column.addStretch()
        first_column.addWidget(self.column_label)
        #first_column.addWidget(self.explanation_label)
        first_column.addWidget(self.first_label, stretch = 2)
        first_column.addWidget(self.id_box, stretch = 1)
        first_column.addWidget(self.second_label, stretch = 2)
        first_column.addWidget(self.test_groupbox, stretch = 1)
        first_column.addWidget(self.third_label, stretch = 2)
        first_column.addWidget(self.feature_groupbox, stretch = 1)
        first_column.addWidget(self.fourth_label, stretch = 2)
        first_column.addWidget(self.date_box, stretch = 1)
        first_column.addWidget(self.meta_label, stretch = 2)
        first_column.addWidget(self.imported_box, stretch = 1)
        first_column.addWidget(self.meta_groupbox, stretch = 1)
        first_column.addStretch()
        first_column.addWidget(self.plot_button)
        first_column.addWidget(self.stat_button)
        second_column.addWidget(self.toolbar)
        second_column.addWidget(self.canvas)

        self.date_box.setEnabled(False)
        self.date_box.setVisible(True)
        root_layout.addLayout(first_column)
        #root_layout.addStretch()
        root_layout.addLayout(second_column)
        self.toolbar.setVisible(False)
        self.imported_box.setEnabled(False)
        self.canvas.setVisible(False)
        self.global_radio.setEnabled(False)
        self.time_radio.setEnabled(False)
        self.meta_groupbox.setEnabled(False)
        self.stat_button.setEnabled(False)
        self.fourth_label.setEnabled(False)
        self.meta_label.setEnabled(False)
        self.meta_groupbox.setEnabled(False)

        self.plot_button.clicked.connect(self.gen_plot)
        self.stat_button.clicked.connect(self.generate_boxplot)

        self.setWindowIcon(QtGui.QIcon(os.path.join(location, 'BloodAnalyzerIcon.png')))
        self.setWindowTitle("B.A.S.")
        
        print(self.size())
        
    def initiate_idBox(self, unique_ids):
        self.id_box.model().setItem(0,0,self.selected_label)
        self.id_box.lineEdit().setText("----- Select Patient(s) -----")
        count = self.id_box.count()
        for i in range(len(unique_ids)):
            #print(self.id_box.count())
            if(count>1):
                self.id_box.setItemText(i+1, 'Patient ID %s' % unique_ids[i])
                self.id_box.selected_items.clear()
            else:
                self.id_box.addItem('Patient ID %s' % unique_ids[i])
            item = self.id_box.model().item(i+1, 0)
            item.setCheckState(QtCore.Qt.CheckState.Unchecked)
    
    def get_checkedItem(self, buttonGroup):
    
        checked_id = buttonGroup.checkedId()
        checked_button = buttonGroup.button(checked_id)
        checked_text = checked_button.text()        
        return checked_text

    def gen_plot(self):
    
        selected_feature = self.get_checkedItem(self.feature_buttonGroup)
        selected_test = self.get_checkedItem(self.test_buttonGroup)
        
        print("Selected Patients:", self.id_box.selected_items)
        print("Selected Family:", selected_feature)
        print("Selected Tests:", selected_test)

        patient_ids = sorted(self.id_box.selected_items)
        #family = self.feature_box.selected_items
        #tests = self.test_box.selected_items
        selected_dates = self.date_box.selected_items
        if selected_dates:
            print("Selected Dates:", selected_dates)

        #if len(family) == 0:
        #    family.append('RBC FAMILY')
        #if len(tests) ==0:
        #    tests.append('BLOOD')

        self.toolbar.setVisible(True)
        self.canvas.setVisible(True)
        self.date_box.setEnabled(True)
        self.fourth_label.setEnabled(True)
        self.canvas.fig.clf()
        self.canvas.axs = []
        axis = None

        features = family_dict[selected_feature]

        warning_list = []
        unique_dates = []

        print(features)

        for idx,feature in enumerate(features):
            self.canvas.axs.append(axis)
            if selected_feature =='WBC FAMILY':
                axis = self.canvas.fig.add_subplot(3,3,idx+1)
            else:
                axis = self.canvas.fig.add_subplot(2,int(np.ceil(len(features)/2)),idx+1)
            raw_feature = feature + '_Value'
            print(raw_feature)
            data = []
            datepoints = []
            raw_dates = []
            for patient in patient_ids:
                complete_dates = None
                patient = patient.split(' ')[-1]
                print(patient)
                patient_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID']==str(patient))&
                                            (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin([selected_test]))]
                if selected_dates:
                    copy = patient_df.copy()
                    patient_df = patient_df[(self.dataframe['ANALYSIS_DATE'].str.contains('|'.join(
                                            selected_dates), case=True))]
                    complete_dates = [value.split(' ')[0] for value in copy['ANALYSIS_DATE'].values]
                    #print(np.unique(copy['ANALYSIS_DATE'].values))
                datapoints = patient_df[raw_feature]
                print(datapoints.values)
                dates = self.dataframe['ANALYSIS_DATE'][datapoints.index]
                dates = [date.split(' ')[0] for date in dates.values]
                print(dates)
                l, = axis.plot(dates, datapoints, ls=':', marker = 'o', linewidth=2.5)
                if len(l.get_ydata())>0:
                    l.set_label(patient)
                if complete_dates:
                    raw_dates.extend(complete_dates)
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
                #axis.axhline(y = limits[0], label='LowLimit', ls='-.', c='r')
                #axis.axhline(y = limits[1], label='HighLimit', ls='-.', c='y')
            except:
                pass
            #print('Raw dates:', raw_dates)
            axis.set_xlabel('Date')
            axis.set_ylabel(feature)
            axis.legend()

        warning_list = np.unique(warning_list).tolist()
        self.show_warning_message(warning_list, selected_test)
        self.canvas.fig.autofmt_xdate()
        self.canvas.fig.suptitle(t = selected_feature + " Time-series", fontsize = 24, y=0.95)
        self.canvas.draw()
        
        self.update_datebox(raw_dates, unique_dates)
        #print(self.canvas.size())
        #print(self.size())        
        self.resize(1620, 980)
        #self.showMaximized()

    def show_warning_message(self, warning_list, selected_test):

        if len(warning_list)==1:
            self.warning_box.setText('Patient ID #'+str(warning_list[0])+" has no "+selected_test+" samples." +'\n' + 'Try with another patients ID.')
            self.warning_box.exec_()
        elif len(warning_list)>1:
            self.warning_box.setText('Patients IDs #'+str(','.join(warning_list))+" have no "+selected_test+" samples." +'\n' + 'Try with another patients ID.')
            self.warning_box.exec_()

    def update_datebox(self, raw_dates, new_dates):
        try:
            new_dates = sorted(new_dates, key = lambda x: datetime.strptime(x, '%d-%m-%y'))
            raw_dates = sorted(raw_dates, key = lambda x: datetime.strptime(x, '%d-%m-%y'))
        except:
            new_dates = sorted(new_dates, key = lambda x: datetime.strptime(x, '%Y/%m/%d'))
            raw_dates = sorted(raw_dates, key = lambda x: datetime.strptime(x, '%Y/%m/%d'))    
        count = self.date_box.count()
        previous_dates = [self.date_box.itemText(i) for i in range(count)][1:]
        print('Old date count:', count)
        print('All date count:', len(raw_dates))
        print('Checked date count:', len(new_dates))
        if count == 1:
            for i in range(len(new_dates)):
                self.date_box.addItem('%s'% new_dates[i])
                item = self.date_box.model().item(i+1,0)
                item.setCheckState(QtCore.Qt.Checked)
                #self.date_box.selected_items.append(new_dates[i])
        elif count>1 and len(raw_dates)>0:
            for i in range(len(raw_dates)):
                if i <count-1:
                    self.date_box.setItemText(i+1, raw_dates[i])
                else:
                    self.date_box.addItem('%s'% raw_dates[i])
                item = self.date_box.model().item(i+1,0)
                if raw_dates[i] in new_dates:
                    item.setCheckState(QtCore.Qt.CheckState.Checked)
                else:
                    item.setCheckState(QtCore.Qt.CheckState.Unchecked)

            for item in previous_dates:
                if item not in new_dates:
                    self.date_box.removeItem(self.date_box.findText(item))
        elif count>1 and len(raw_dates)==0:
            for i in range(len(new_dates)):
                if i <count-1:
                    self.date_box.setItemText(i+1, new_dates[i])
                else:
                    self.date_box.addItem('%s'% new_dates[i])
                item = self.date_box.model().item(i+1,0)
                if new_dates[i] in raw_dates:
                    item.setCheckState(QtCore.Qt.CheckState.Checked)
                else:
                    item.setCheckState(QtCore.Qt.CheckState.Unchecked)

            for item in previous_dates:
                if item not in new_dates:
                    self.date_box.removeItem(self.date_box.findText(item))
        
        
        print('New date count:', self.date_box.count()-1)

    def show_dataframe(self):
        patient_ids = [patient.split(' ')[-1] for patient in self.id_box.selected_items]
        selected_feature = self.get_checkedItem(self.feature_buttonGroup)
        selected_test = self.get_checkedItem(self.test_buttonGroup)
        selected_dates = self.date_box.selected_items
        if selected_dates:
            patient_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID'].str.contains('|'.join(patient_ids), case=True))&
                                        (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin([selected_test]))&
                                        (self.dataframe['ANALYSIS_DATE'].str.contains('|'.join(selected_dates), case=True))]
            #self.dataframe['ANALYSIS_DATE'].isin(selected_dates)
            #print(patient_df)
        else:
            patient_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID'].str.contains('|'.join(patient_ids), case=True))&
                                        (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin([selected_test]))]
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
        
        if file != '':
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
            self.imported_box.setEnabled(True)
            self.global_radio.setEnabled(True)
            self.time_radio.setEnabled(True)
            self.stat_button.setEnabled(True)
            self.meta_label.setEnabled(True)
            self.meta_groupbox.setEnabled(True)

    def generate_boxplot(self):

        self.toolbar.setVisible(True)
        self.canvas.setVisible(True)
        #self.df_button.setVisible(True)
        #self.export_button.setVisible(True)
        
        selected_feature = self.get_checkedItem(self.feature_buttonGroup)
        selected_test = self.get_checkedItem(self.test_buttonGroup)

        #family = self.feature_box.selected_items
        #tests = self.test_box.selected_items

        meta_patients = [str(animal_id) for animal_id in self.metadata['animal_id'].values]
        #print(meta_patients)(self.dataframe['FIELD_SID_PATIENT_ID'].str.contains('|'.join(meta_patients), case=True))

        selected_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID'].str.contains('|'.join(meta_patients), case=True))&
                                     (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin([selected_test]))]

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
        features = family_dict[selected_feature] #self.get_checkedItem(self.feature_buttonGroup)
        features = [feature+'_Value' for feature in features]
        if self.global_radio.isChecked():
            print('Global')
            x_pos = 0.5
            for idx, feature in enumerate(features):
                if selected_feature =='WBC FAMILY':
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
                if selected_feature =='WBC FAMILY':
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

    def reset_window(self):
        self.initiate_idBox(self.unique_ids)        
        #self.initiate_testBox(np.unique(self.dataframe['FIELD_SID_ANIMAL_NAME'].values))
        #self.initiate_featureBox(families)
        self.date_box.clear()
        self.date_box.selected_items.clear()
        self.canvas.hide()

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
        #self.second_window.info_box.exec_()
        self.second_window.show()

if __name__ == '__main__':

    app = QtWidgets.QApplication(['Test'])
    app.setWindowIcon(QtGui.QIcon(os.path.join(root_dir,'BloodAnalyzerIcon.ico')))
    main_widget = ScreenHandler()

    #dialog_1 = Dialog()
    #dialog_1.show()
    
    app.exec_()

