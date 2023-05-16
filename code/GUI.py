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

colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (0.5, 0, 0.5)]

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
        self.resize(480,480)
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
        raw_df = parse_multiple_files([os.path.join(directory, file) for file in os.listdir(directory)], self.progress_bar)
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
            self.signal.emit('Open SecondWindow')
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
                                   'Select patients IDs of interest.\n2. Select a blood test.\n3.'+
                                   'Select the features family of interest.\n4. Filter the timeseries by the patient ID and dates.\n5.' 
                                   'Additionally, you can import metadata and generate a boxplot according to the desired values.')
        instructions_label.setAlignment(QtCore.Qt.AlignCenter)   
        #'<a href="https://github.com/your_username/your_repository">Click here to visit the GitHub repository</a>'
        #Add link to the Github repo
        link_label = QtWidgets.QLabel()
        link_label.setText('For more information and detailed usage examples, please visit our '+
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

class SimpleSelectionWindow(QtWidgets.QDialog):
    def __init__(self, parent=None, items = None , sel= None ,label = None, *args, **kwargs):
    
        super(SimpleSelectionWindow, self).__init__(parent)
        
        self.setWindowTitle('Select '+label)
        
        self.finish_button = QtWidgets.QPushButton("Finish")
        self.finish_button.setFixedSize(200,60)
        self.finish_button.clicked.connect(self.close)
        
        self.items = [item for item in items.tolist() if item not in sel]
        self.selected_items = sel
        
        self.initial_list_widget = QtWidgets.QListWidget()
        self.initial_list_widget.addItems(self.items)
        self.initial_list_widget.itemClicked.connect(self.update_list)
        
        self.selected_list_widget= QtWidgets.QListWidget()
        self.selected_list_widget.addItems(self.selected_items)
        
        self.add_button = QtWidgets.QPushButton(">>")
        self.add_button.setToolTip("Select an Item")
        self.add_button.clicked.connect(self.select_item)
        
        self.remove_button = QtWidgets.QPushButton("<<")
        self.remove_button.setToolTip("Deselect an Item")
        self.remove_button.clicked.connect(self.reset_item)
        
        self.button_layout = QtWidgets.QVBoxLayout()
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.remove_button)
        
        self.initial_box = QtWidgets.QVBoxLayout()
        self.initial_label = QtWidgets.QLabel("Available "+ label)
        self.initial_box.addWidget(self.initial_label)
        self.initial_box.addWidget(self.initial_list_widget)
        
        self.selected_box = QtWidgets.QVBoxLayout()
        self.selected_label = QtWidgets.QLabel("Selected " + label)
        self.selected_box.addWidget(self.selected_label)
        self.selected_box.addWidget(self.selected_list_widget)
        
        self.list_layout = QtWidgets.QHBoxLayout()
        self.list_layout.addLayout(self.initial_box, stretch = 2)
        self.list_layout.addLayout(self.button_layout, stretch = 1)
        self.list_layout.addLayout(self.selected_box, stretch = 2)
        
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.list_layout, stretch = 1)
        self.main_layout.addWidget(self.finish_button, stretch = 1)
        
        self.main_layout.setAlignment(self.finish_button, QtCore.Qt.AlignHCenter)
        
        self.setLayout(self.main_layout)
    
    def update_list(self, item):
        pass
    
    def select_item(self):
    
        item = self.initial_list_widget.currentItem()
        if item is None:
            return
        self.initial_list_widget.takeItem(self.initial_list_widget.row(item))
        self.selected_list_widget.addItem(item.text())
        self.selected_items.append(item.text())
        self.items.remove(item.text())
    
    def reset_item(self):
            
        item = self.selected_list_widget.currentItem()
        if item is None:
            return
        self.selected_list_widget.takeItem(self.selected_list_widget.row(item))
        self.initial_list_widget.addItem(item.text())
        self.selected_items.remove(item.text())
        self.items.append(item.text())

class ListSelectionWindow(QtWidgets.QDialog):
    def __init__(self, parent=None, patients_dict=None, *args, **kwargs):
        super(ListSelectionWindow, self).__init__(parent)

        self.setWindowTitle("Filter Series by Dates")
        self.setGeometry(100, 100, 850, 300)

        self.list_selection_button = QtWidgets.QPushButton("Update Plot")
        self.list_selection_button.setFixedSize(200, 60)
        self.list_selection_button.clicked.connect(self.close)
        
        self.patients = patients_dict
        
        self.removed_dates = {key: [] for key in self.patients.keys()}

        # create list widgets
        self.available_list_widget = QtWidgets.QListWidget()
        self.available_list_widget.addItems(list(self.patients.keys()))
        self.available_list_widget.itemClicked.connect(self.update_date_list)

        self.second_list_widget = QtWidgets.QListWidget()
        self.second_selected_list_widget = QtWidgets.QListWidget()        

        # create button to move items from available list to selected list
        self.add_button2 = QtWidgets.QPushButton(">>")
        self.add_button2.setToolTip('Remove a Date')
        self.add_button2.clicked.connect(self.select_second_item)

        # create button to move items from selected list to available list
        self.remove_button2 = QtWidgets.QPushButton("<<")
        self.remove_button2.setToolTip('Reinsert a Date')
        self.remove_button2.clicked.connect(self.reset_second_item)

        self.button_layout2 = QtWidgets.QVBoxLayout()
        self.button_layout2.addWidget(self.add_button2)
        self.button_layout2.addWidget(self.remove_button2)

        self.current_box = QtWidgets.QVBoxLayout()
        self.current_label = QtWidgets.QLabel("Selected IDs")
        self.current_box.addWidget(self.current_label)
        self.current_box.addWidget(self.available_list_widget)
        
        self.second_current_box = QtWidgets.QVBoxLayout()
        self.second_current_label = QtWidgets.QLabel("Selected Sample Dates")
        self.second_current_box.addWidget(self.second_current_label)
        self.second_current_box.addWidget(self.second_list_widget)
        
        self.second_removed_box = QtWidgets.QVBoxLayout()
        self.second_removed_label = QtWidgets.QLabel("Removed Sample Dates")
        self.second_removed_box.addWidget(self.second_removed_label)
        self.second_removed_box.addWidget(self.second_selected_list_widget)

        # create layout for lists
        self.list_layout = QtWidgets.QHBoxLayout()
        self.list_layout.addLayout(self.current_box, stretch = 2)
        self.list_layout.addLayout(self.second_current_box, stretch = 2)
        self.list_layout.addLayout(self.button_layout2, stretch = 1)
        self.list_layout.addLayout(self.second_removed_box, stretch = 2)

        # create main layout for window
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.list_layout, stretch = 1)
        self.main_layout.addWidget(self.list_selection_button, stretch = 1)

        self.main_layout.setAlignment(self.list_selection_button, QtCore.Qt.AlignHCenter)

        self.setLayout(self.main_layout)
    
    def update_date_list(self, id_item):
        
        self.second_list_widget.clear()
        self.second_selected_list_widget.clear()
        dates = self.patients[id_item.text()]
        removed = self.removed_dates[id_item.text()]
        self.second_list_widget.addItems(dates)
        self.second_selected_list_widget.addItems(removed)
        
    def select_second_item(self):
        item = self.second_list_widget.currentItem()
        id_item   = self.available_list_widget.currentItem()
        if item is None:
            return
        self.second_list_widget.takeItem(self.second_list_widget.row(item))
        self.second_selected_list_widget.addItem(item.text())
        self.removed_dates[id_item.text()].append(item.text())
        self.patients[id_item.text()].remove(item.text())

    def reset_second_item(self):
        item = self.second_selected_list_widget.currentItem()
        id_item = self.available_list_widget.currentItem()
        if item is None:
            return
        self.second_selected_list_widget.takeItem(self.second_selected_list_widget.row(item))
        self.second_list_widget.addItem(item.text())
        self.removed_dates[id_item.text()].remove(item.text())
        self.patients[id_item.text()].append(item.text())

#Class wrapper for Dialog test window
class SecondWindow(QtWidgets.QMainWindow):
    signal = QtCore.pyqtSignal(str)
    def __init__(self, filename, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root = '\\'.join(os.path.dirname(os.path.realpath(__file__)).split('\\')[:-1])
        location = os.path.dirname(os.path.realpath(__file__))

        self.filename = filename
        self.new_file = None
        self.dataframe = pd.read_csv(self.filename)
        self.unique_ids = np.sort(np.unique(self.dataframe['FIELD_SID_PATIENT_ID'].astype(str).values))
        self.selected_ids = []

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
        self.data_menu = self.menubar.addMenu('Data')
        self.import_menu= self.menubar.addMenu('Import')
        self.export_menu = self.menubar.addMenu('Export')
        self.help_menu = self.menubar.addMenu('Help')
        
        self.open_action = QtWidgets.QAction('Open csv File', self)
        self.file_menu.addAction(self.open_action)
        self.open_action.triggered.connect(self.open_file)
        
        self.reset_action = QtWidgets.QAction('Reset Window', self)
        self.reset_action.triggered.connect(self.reset_window)
        self.edit_menu.addAction(self.reset_action)
        
        self.showAll_action = QtWidgets.QAction('Show All Dataframe', self)
        self.showAll_action.triggered.connect(self.show_all_dataframe)
        self.data_menu.addAction(self.showAll_action)
        self.showSel_action = QtWidgets.QAction('Show Selected Dataframe', self)
        self.data_menu.addAction(self.showSel_action)
        self.showSel_action.triggered.connect(self.show_sel_dataframe)
        
        self.importNew_action = QtWidgets.QAction('Import New xml Files', self)
        self.import_menu.addAction(self.importNew_action)
        self.importNew_action.triggered.connect(self.add_rows)
        self.importMeta_action= QtWidgets.QAction('Import Metadata', self)
        self.importMeta_action.triggered.connect(self.import_data)
        self.import_menu.addAction(self.importMeta_action)
        
        self.exportSel_action = QtWidgets.QAction('Exported Selected Data', self)
        self.export_menu.addAction(self.exportSel_action)
        self.exportSel_action.triggered.connect(self.export_selection)
        
        self.getHelp_action = QtWidgets.QAction('Show B.A.S Instructions')
        self.help_menu.addAction(self.getHelp_action)
        self.getHelp_action.triggered.connect(self.open_HelpDialog)
        
        self.column_label = QtWidgets.QLabel(self)
        self.column_label.setText('Filter Options')
        self.column_label.setFont(subsection_font)
        self.column_label.setToolTip('Select and Filter Data to plot.') 

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
        
        self.selectId_button = QtWidgets.QPushButton('Select Patients IDs')
        self.selectId_button.setToolTip("Show Pop-up Window to Select IDs")
        
        self.date_button = QtWidgets.QPushButton('Filter Series by Date')
        self.date_button.setToolTip('Show Pop-up Window to Remove Datapoints by Date and ID.')
        
        self.selectMeta_button = QtWidgets.QPushButton('Select Metadata Fields')
        self.selectMeta_button.setToolTip('Show Pop-up Window to Select Metadata Fields')
        
        self.table_window= None
        self.selected_frame = None
        self.metadata = None
        self.popup_window = None
        self.id_window = None
        self.meta_window = None
        self.selected_fields = []
        self.desired_size = (1620, 980)
        
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

        self.stat_button = QtWidgets.QPushButton('Generate Scatter Plot')
        self.stat_button.setToolTip('Generate Global or Time-based Boxplot based on Metadata.')
        
        self.warning_box = QtWidgets.QMessageBox()
        self.warning_box.setIcon(QtWidgets.QMessageBox.Warning)
        self.warning_box.setWindowTitle('Warning')
        self.warning_box.addButton(QtWidgets.QMessageBox.Ok)
        
        self.welcome_dialog = None
        
        self.reset_button = QtWidgets.QPushButton('Reset Window')
        
        first_column.addStretch()
        first_column.addWidget(self.column_label)
        first_column.addWidget(self.first_label, stretch = 2)
        first_column.addWidget(self.selectId_button, stretch = 1)
        first_column.addWidget(self.second_label, stretch = 2)
        first_column.addWidget(self.test_groupbox, stretch = 1)
        first_column.addWidget(self.third_label, stretch = 2)
        first_column.addWidget(self.feature_groupbox, stretch = 1)
        first_column.addWidget(self.fourth_label, stretch = 2)
        first_column.addWidget(self.date_button, stretch = 1)
        first_column.addWidget(self.meta_label, stretch = 2)
        first_column.addWidget(self.selectMeta_button, stretch = 1)
        first_column.addWidget(self.meta_groupbox, stretch = 1)
        first_column.addStretch()
        first_column.addWidget(self.plot_button)
        first_column.addWidget(self.stat_button)
        second_column.addWidget(self.toolbar)
        second_column.addWidget(self.canvas)

        root_layout.addLayout(first_column)
        root_layout.addLayout(second_column)
        self.toolbar.setVisible(False)
        self.selectMeta_button.setEnabled(False)
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
        self.date_button.clicked.connect(self.show_datePopup)
        self.selectId_button.clicked.connect(self.select_items)
        self.selectMeta_button.clicked.connect(self.select_fields)
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(location, 'BloodAnalyzerIcon.png')))
        self.setWindowTitle("B.A.S.")
        
        print(self.size())
    
    def open_file(self):
    
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select a file",
                                                            os.path.dirname(os.path.abspath(__file__)),
                                                            "Comma-separated values (*.csv)")
        
        
        if file !='':
            self.new_file = file
            self.signal.emit('Change SecondWindow file')
            #print(self.new_file)
            self.close()
    
    def add_rows(self):
        
        filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select file(s)",
                                                        os.path.dirname(os.path.abspath(__file__)),
                                                        "Extensible Markup Language (*.xml)")
        
        if filenames:
            raw_df = parse_multiple_files(filenames)
            clean_df = clean_dataframe(raw_df)
        
            self.dataframe = pd.concat([self.dataframe, clean_df], axis=0)#self.dataframe()
            self.dataframe = self.dataframe.reset_index(drop=True)
            self.initiate_idBox(np.sort(np.unique(self.dataframe['FIELD_SID_PATIENT_ID'].astype(str).values)))
        
        self.dataframe.to_csv(self.filename, index=False)
    
    def open_HelpDialog(self):
        self.welcome_dialog = WelcomeDialog()
        self.welcome_dialog.exec_()
    
    def get_checkedItem(self, buttonGroup):
    
        checked_id = buttonGroup.checkedId()
        checked_button = buttonGroup.button(checked_id)
        checked_text = checked_button.text()        
        return checked_text
    
    def select_items(self):
        
        self.id_window = SimpleSelectionWindow(parent=None, items=self.unique_ids, sel=self.selected_ids, label='IDs')
        self.id_window.exec_()
        
        self.selected_ids = self.id_window.selected_items
    
    def select_fields(self):
        
        self.meta_window = SimpleSelectionWindow(parent=None, items=self.metadata.columns[1:], sel=[], label='Metadata Fields')
        self.meta_window.exec_()
        
        self.selected_fields = self.meta_window.selected_items        

    def show_datePopup(self):
    
        selected_test = self.get_checkedItem(self.test_buttonGroup)
        patient_ids = sorted(self.selected_ids, key = lambda x: x.split(' ')[-1])#[patient.split(' ')[-1] for patient in sorted(self.id_box.selected_items)]
        patient_ids = [id.split(' ')[-1] for id in patient_ids]
        
        pattern = '|'.join(['^{}$'.format(id) for id in patient_ids])
        
        patient_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID'].astype(str).str.contains(pattern))&
                                    (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin([selected_test]))]
        
        patient_dict = {patient: group['ANALYSIS_DATE'].tolist() for patient, group in patient_df.groupby('FIELD_SID_PATIENT_ID')}
        
        self.popup_window = ListSelectionWindow(parent=None, patients_dict= patient_dict)
        
        self.popup_window.exec_()
        
        modified_dict = self.popup_window.patients
        
        modified_set = set((key, date) for key, dates in modified_dict.items() for date in dates)
        filtered_df = patient_df[patient_df.apply(lambda x: (x['FIELD_SID_PATIENT_ID'], x['ANALYSIS_DATE'])  in modified_set, axis=1)]
        
        self.filtered_plot(filtered_df, patient_ids)
        
        current_size = self.size()
        
        if current_size.width() < self.desired_size[0] or current_size.height() < self.desired_size[1]:
            self.resize(*self.desired_size)
        
        #self.resize(1620, 980)

    def gen_plot(self):
    
        selected_feature = self.get_checkedItem(self.feature_buttonGroup)
        selected_test = self.get_checkedItem(self.test_buttonGroup)
        
        print("Selected Patients:", self.selected_ids)
        print("Selected Family:", selected_feature)
        print("Selected Tests:", selected_test)

        patient_ids = sorted(self.selected_ids, key = lambda x: x.split(' ')[-1])#[patient.split(' ')[-1] for patient in sorted(self.id_box.selected_items)]
        patient_ids = [id.split(' ')[-1] for id in patient_ids]

        self.toolbar.setVisible(True)
        self.canvas.setVisible(True)
        self.fourth_label.setEnabled(True)
        
        self.filtered_plot(self.dataframe, patient_ids)
        current_size = self.size()
        
        if current_size.width() < self.desired_size[0] or current_size.height() < self.desired_size[1]:
            self.resize(*self.desired_size)

    def show_warning_message(self, warning_list, selected_test):

        if len(warning_list)==1:
            self.warning_box.setText('Patient ID #'+str(warning_list[0])+" has no "+selected_test+" samples." +'\n' + 'Try with another patients ID.')
            self.warning_box.exec_()
        elif len(warning_list)>1:
            self.warning_box.setText('Patients IDs #'+str(','.join(warning_list))+" have no "+selected_test+" samples." +'\n' + 'Try with another patients ID.')
            self.warning_box.exec_()
    
    
    def filtered_plot(self, dataframe, patient_ids):
    
        selected_test = self.get_checkedItem(self.test_buttonGroup)
        selected_feature = self.get_checkedItem(self.feature_buttonGroup)
        features = family_dict[selected_feature]
        
        warning_list = []
        self.canvas.fig.clf()
        self.canvas.axs = []
        axis = None
        
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
                print(patient)
                patient_df = dataframe[(dataframe['FIELD_SID_PATIENT_ID'].astype(str)==str(patient))&
                                        (dataframe['FIELD_SID_ANIMAL_NAME'].isin([selected_test]))]
                datapoints = patient_df[raw_feature]
                print(datapoints.values)
                dates = dataframe['ANALYSIS_DATE'][datapoints.index]
                dates = [date.split(' ')[0] for date in dates.values]
                print(dates)
                l, = axis.plot(dates, datapoints, ls=':', marker = 'o', linewidth=2.5)
                if len(l.get_ydata())>0:
                    l.set_label(patient)
                if complete_dates:
                    raw_dates.extend(complete_dates)
                try:
                    limits = [dataframe[feature+'_'+limit][datapoints.index].values[0]
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
                axis.set_xlim(-0.5, len(unique_dates)-0.5)
            except:
                pass
            axis.set_xlabel('Date')
            axis.set_ylabel(feature)
            axis.legend()

        warning_list = np.unique(warning_list).tolist()
        self.show_warning_message(warning_list, selected_test)
        self.canvas.fig.autofmt_xdate()
        self.canvas.fig.suptitle(t = selected_feature + " Time-series", fontsize = 24)
        self.canvas.draw()
        
        self.canvas.setVisible(True)
        self.toolbar.setVisible(True)

    def show_sel_dataframe(self):
        patient_ids = [patient.split(' ')[-1] for patient in self.selected_ids]
        selected_feature = self.get_checkedItem(self.feature_buttonGroup)
        selected_test = self.get_checkedItem(self.test_buttonGroup)
        pattern = '|'.join(['^{}$'.format(id) for id in patient_ids])
        patient_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID'].astype(str).str.contains(pattern))&
                                    (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin([selected_test]))]
        
        self.selected_frame = patient_df
        self.table_window = TableWindow(self.selected_frame)
        self.table_window.show()
    
    def show_all_dataframe(self):
        self.table_window = TableWindow(self.dataframe)
        self.table_window.show()

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
            self.metadata['animal_id'] = self.metadata['animal_id'].astype(str)
            self.dataframe = pd.merge(self.dataframe, self.metadata, left_on = 'FIELD_SID_PATIENT_ID', right_on = 'animal_id', how='left')
            self.dataframe = self.dataframe.drop(columns = 'animal_id')

            self.global_radio.setEnabled(True)
            self.time_radio.setEnabled(True)
            self.stat_button.setEnabled(True)
            self.meta_label.setEnabled(True)
            self.meta_groupbox.setEnabled(True)
            self.selectMeta_button.setEnabled(True)
    
    def export_selection(self):
            
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save as', os.path.dirname(os.path.abspath(__file__)), "Comma-separated values (*.csv)")
        
        if filename != '':
            patient_ids = [patient.split(' ')[-1] for patient in self.selected_ids]
            selected_feature = self.get_checkedItem(self.feature_buttonGroup)
            selected_test = self.get_checkedItem(self.test_buttonGroup)
            pattern = '|'.join(['^{}$'.format(id) for id in patient_ids])
            patient_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID'].astype(str).str.contains(pattern))&
                                        (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin([selected_test]))]
            patient_df.to_csv(filename, index=False)        
        
    
    def generate_boxplot(self):

        self.toolbar.setVisible(True)
        self.canvas.setVisible(True)
        
        selected_feature = self.get_checkedItem(self.feature_buttonGroup)
        selected_test = self.get_checkedItem(self.test_buttonGroup)
        meta_patients = [str(animal_id) for animal_id in self.metadata['animal_id'].values]
        pattern = '|'.join(['^{}$'.format(id) for id in meta_patients])
        
        selected_df = self.dataframe[(self.dataframe['FIELD_SID_PATIENT_ID'].astype(str).str.contains(pattern))&
                                    (self.dataframe['FIELD_SID_ANIMAL_NAME'].isin([selected_test]))]

        filters = self.selected_fields

        if len(filters)>1:
            column = '-'.join(filters)
            selected_df[column] = selected_df[filters].apply(lambda x: '_'.join(x), axis=1)
            uniques = selected_df[column].unique()
        else:
            column = filters[0]
            uniques = selected_df[column].unique()

        groupings = [np.where(selected_df[column].values==unique) for unique in uniques]

        wd = 0.5
        self.canvas.fig.clf()
        self.canvas.axs = []
        axis = None

        features = family_dict[selected_feature] #self.get_checkedItem(self.feature_buttonGroup)
        features = [feature+'_Value' for feature in features]
        patches = [mpatches.Patch(color=colors[idx], label = uniques[idx])  for idx, group in enumerate(groupings)]
        if self.global_radio.isChecked():
            print('Global')
            x_pos = 0.5
            for idx, feature in enumerate(features):
                if selected_feature =='WBC FAMILY':
                    axis = self.canvas.fig.add_subplot(3,3,idx+1)
                else:
                    axis = self.canvas.fig.add_subplot(2,int(np.ceil(len(features)/2)),idx+1)

                total_points = []
                labels = []
                c_scatter = []
                _ = [(total_points.append(selected_df[feature].values[group])) for idx, group in enumerate(groupings)]
                _ = [labels.append([uniques[idx]]*len(total_points[idx])) for idx,group in enumerate(groupings)]
                _ = [c_scatter.append([colors[idx]]*len(total_points[idx])) for idx, group in enumerate(groupings)]
                
                means = [np.mean(sublist) for sublist in total_points]
                stds = [np.std(sublist) for sublist in total_points]
                
                axis.scatter([item for sub in labels for item in sub], [item for sub in total_points for item in sub],
                            alpha=1.0, c=[item for sub in c_scatter for item in sub])
                
                [axis.errorbar(position,mean,yerr=std, c=col[0], marker='*', markersize= 9, linestyle='none',capsize=5, capthick=2, alpha=0.3)
                 for idx,(position,mean,std,col) in enumerate(zip(np.arange(0,len(total_points)-1,1),means,stds,c_scatter))]
                axis.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=True)
                axis.set_xticks(np.arange(len(uniques)), uniques)
                axis.set_xlim(-0.5,len(uniques)*0.5 + 1.0)
                axis.set_ylim(max(0,min([item for sub in total_points for item in sub])-1.5), max([item for sub in total_points for item in sub])+1.5)
                axis.set_ylabel(feature)
                
        elif self.time_radio.isChecked():
            print('Time-based')
            unique_dates = selected_df['ANALYSIS_DATE'].apply(lambda x: x.split(' ')[0]).unique()
            x_pos = np.linspace(wd*sum(np.arange(1,len(groupings)+1,1))/len(groupings),
                                wd*sum(np.arange(1,len(groupings)+1,1))/len(groupings) + wd*(len(unique_dates)-1)*(len(groupings)+1), 
                                len(unique_dates), endpoint=True)# np.linspace(1.0, 1.0 + 0.5*(3+1)*(5-1),5)
            
            for idx, feature in enumerate(features):
                if selected_feature =='WBC FAMILY':
                    axis = self.canvas.fig.add_subplot(3,3,idx+1)
                else:
                    axis = self.canvas.fig.add_subplot(2,int(np.ceil(len(features)/2)),idx+1)
                total_points = []
                pos = []
                c_scatter = []
                labels = []
                for i, date in enumerate(unique_dates):                
                    selected_perdate = selected_df[selected_df['ANALYSIS_DATE'].str.contains(date)]
                    groupings = [np.where(selected_perdate[column].values == unique)
                                 for unique in uniques]                    
                    _ = [total_points.append(selected_perdate[feature].values[group]) for group in groupings]
                    _ = [pos.append([wd*(len(groupings)+1)*i +wd+idx*wd]*len(total_points[idx + i*len(groupings)])) for idx, group in enumerate(groupings)]
                    _ = [c_scatter.append([colors[idx]]*len(total_points[idx + i*len(groupings)])) for idx, group in enumerate(groupings)]
                
                means = [np.mean(sublist) for sublist in total_points]
                stds = [np.std(sublist) for sublist in total_points]
                #min_error = min([min(sublist) for sublist in total_points])
                
                axis.scatter([item for sub in pos for item in sub], [item for sub in total_points for item in sub], 
                            c = [item for sub in c_scatter for item in sub], alpha=1.0)
                [axis.errorbar(position[0],mean,yerr=std, c=col[0], marker='*', markersize= 9, linestyle='none',capsize=5, capthick=2, alpha=0.3)
                 for idx,(position,mean,std,col) in enumerate(zip(pos,means,stds,c_scatter))]
                axis.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=True)
                axis.set_xlim(-0.5,x_pos[-1]+1.5)
                axis.set_ylim(max(0,min([item for sub in total_points for item in sub])-1.5), max([item for sub in total_points for item in sub])+1.5)
                
                axis.set_ylabel(feature)
                axis.set_xticks(x_pos, unique_dates)
            self.canvas.fig.autofmt_xdate()#Comment if plotting fails
        else:
            pass
        self.canvas.fig.legend(handles=patches, loc='upper left')
        #self.canvas.fig.suptitle(family[0]+' & METADATA')
        self.canvas.draw()
        #self.resize(1620, 980)
        current_size = self.size()
        
        if current_size.width() < self.desired_size[0] or current_size.height() < self.desired_size[1]:
            self.resize(*self.desired_size)

    def reset_window(self):
        #self.initiate_idBox(self.unique_ids)   
        self.selected_ids = []
        self.resize(360, 980)
        self.canvas.fig.clf()
        self.toolbar.hide()
        self.canvas.draw()
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
        print(event)
        if event == 'Open SecondWindow':
            print(self.first_window.selected_file)
            self.second_window = SecondWindow(self.first_window.selected_file)
            self.second_window.signal.connect(self.change_window)
            self.second_window.setStyleSheet("QMainWindow { border: 1px solid black; }")

            #self.second_window.info_box.exec_()
            self.second_window.show()
        elif event == 'Change SecondWindow file':
            print(self.second_window.new_file)
            new_file = self.second_window.new_file
            self.second_window = SecondWindow(new_file)
            self.second_window.setStyleSheet("QMainWindow { border: 1px solid black; }")

            #self.second_window.info_box.exec_()
            self.second_window.show()

if __name__ == '__main__':

    app = QtWidgets.QApplication(['Test'])
    app.setWindowIcon(QtGui.QIcon(os.path.join(root_dir,'BloodAnalyzerIcon.ico')))
    main_widget = ScreenHandler()

    #dialog_1 = Dialog()
    #dialog_1.show()
    
    app.exec_()

