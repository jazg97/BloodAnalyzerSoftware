from PyQt5 import QtCore, QtGui, QtWidgets

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
        print(self.selected_items)

class Dialog_01(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        myQWidget = QtWidgets.QWidget()
        myBoxLayout = QtWidgets.QHBoxLayout()
        myQWidget.setLayout(myBoxLayout)
        self.setCentralWidget(myQWidget)
        self.id_box = CheckableComboBox()
        for i in range(3):
            self.id_box.addItem('Patient ID %s' % i)
            item = self.id_box.model().item(i, 0)
            item.setCheckState(QtCore.Qt.Unchecked)
        self.feature_box = CheckableComboBox()
        for i in range(4):
            self.feature_box.addItem('Feature %s'% i)
            item = self.feature_box.model().item(i,0)
            item.setCheckState(QtCore.Qt.Unchecked)
        myBoxLayout.addWidget(self.id_box)
        myBoxLayout.addWidget(self.feature_box)

if __name__ == '__main__':

    app = QtWidgets.QApplication(['Test'])
    dialog_1 = Dialog_01()
    dialog_1.show()
    app.exec_()
