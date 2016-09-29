import sys
import operator
import shutil
from PyQt4 import QtCore
from PyQt4 import QtGui


class EditorModel(QtCore.QAbstractTableModel):
    HOSTS_FILE = "/etc/hosts"

    COLUMN_ADDR = 0
    COLUMN_HOST = 1
    COLUMN_COMMENT = 2

    def __init__(self, data, parent=None, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.hosts = data

    def rowCount(self, parent):
        return len(self.hosts)

    def columnCount(self, parent):
        return 3

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return QtCore.QVariant(self.hosts[index.row()][index.column()])

        return QtCore.QVariant()

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return ["IP", "Host", "Comment"][col]

    def flags(self, index):
        flags = super(self.__class__, self).flags(index)
        flags |= QtCore.Qt.ItemIsEnabled
        flags |= QtCore.Qt.ItemIsSelectable
        flags |= QtCore.Qt.ItemIsEditable

        return flags

    def setData(self, index, value, role):
        self.hosts[index.row()][index.column()] = str(value.toString().toUtf8()).strip()

        return True

    def sort(self, col, order):
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.hosts = sorted(self.hosts, key=operator.itemgetter(col))
        if order == QtCore.Qt.DescendingOrder:
            self.hosts.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))

    def load(self):
        hosts = []

        f = open(self.HOSTS_FILE, "r")
        for line in f:
            comment = ""

            hash = line.find('#')
            if hash > -1:
                # Wszystko po '#' jest komentarzem
                comment = line[hash + 1:]

            data = line[:hash].split()
            if len(data) >= 2:
                addr = data[0]
                host = data[1]

                hosts.append([addr, host, comment])
        f.close()

        self.beginResetModel()
        self.hosts = hosts
        self.endResetModel()

    def save(self):
        shutil.copy(self.HOSTS_FILE, self.HOSTS_FILE + '.old')

        f = open(self.HOSTS_FILE, "w")
        for row in self.hosts:
            f.write(row[self.COLUMN_ADDR])
            f.write(' ')
            f.write(row[self.COLUMN_HOST])
            f.write(' ')
            if row[self.COLUMN_COMMENT]:
                f.write('#')
                f.write(row[self.COLUMN_COMMENT])
            f.write('\n')
        f.close()

    def removeRows(self, row, count, parent=None):
        if row < 0 or row > len(self.hosts):
            return False

        self.beginRemoveRows(QtCore.QModelIndex(), row, row + count - 1)
        while count != 0:
            del self.hosts[row]
            count -= 1
        self.endRemoveRows()

        return True

    def addRow(self, row):
        pos = len(self.hosts)

        self.beginInsertRows(QtCore.QModelIndex(), pos, pos)
        self.hosts.append(row)
        self.endInsertRows()


class IPValidator(QtGui.QValidator):
    IPV4_REGEXP = '^(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
    IPV6_REGEXP = '^(?:(?:[0-9A-Fa-f]{1,4}:){6}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|::(?:[0-9A-Fa-f]{1,4}:){5}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){4}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){3}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,2}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){2}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,3}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}:(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,4}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,5}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}|(?:(?:[0-9A-Fa-f]{1,4}:){,6}[0-9A-Fa-f]{1,4})?::)$'

    def __init__(self, parent):
        QtGui.QValidator.__init__(self, parent)

    def validate(self, value, pos):
        return (QtGui.QValidator.Acceptable, pos)


class EditorForm(QtGui.QWidget):
    def __init__(self):
        super(EditorForm, self).__init__()

        self.addr = QtGui.QLineEdit()
        self.addr.setPlaceholderText("IP")
        self.addr.setContentsMargins(0, 0, 0, 0)
        self.addr.setValidator(IPValidator(self))

        self.host = QtGui.QLineEdit()
        self.host.setPlaceholderText("Host")

        self.comment = QtGui.QLineEdit()
        self.comment.setPlaceholderText("Comment")

        self.submit = QtGui.QPushButton()
        self.submit.setText("Add")

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.addr)
        layout.addWidget(self.host)
        layout.addWidget(self.comment)
        layout.addWidget(self.submit)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def data(self):
        return [
            self.addr.text(),
            self.host.text(),
            self.comment.text()
        ]

    def reset(self):
        self.addr.clear()
        self.host.clear()
        self.comment.clear()


class Editor(QtGui.QMainWindow):
    def __init__(self):
        super(Editor, self).__init__()

        self._model = EditorModel([], self)
        self._model.load()

        self._proxy = QtGui.QSortFilterProxyModel()
        self._proxy.setSourceModel(self._model)
        self._proxy.setDynamicSortFilter(True)
        self._proxy.setFilterKeyColumn(-1)
        self._proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self._filter = QtGui.QLineEdit()
        self._filter.setPlaceholderText("Search ...")
        self._filter.textChanged.connect(self._proxy.setFilterFixedString)

        self._table = QtGui.QTableView()
        self._table.setModel(self._proxy)
        self._table.setSortingEnabled(True)
        self._table.verticalHeader().setVisible(False)
        self._table.resizeColumnsToContents()
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().sectionResized.connect(self.onHeaderResize)
        self._table.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked)
        self._table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self._table.setAlternatingRowColors(True)

        self._form = EditorForm()
        self._form.addr.setFixedWidth(self._table.columnWidth(EditorModel.COLUMN_ADDR))
        self._form.host.setFixedWidth(self._table.columnWidth(EditorModel.COLUMN_HOST))
        self._form.submit.clicked.connect(self.doCreate)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self._filter)
        layout.addWidget(self._table)
        layout.addWidget(self._form)

        central = QtGui.QWidget()
        central.setLayout(layout)

        self.setWindowTitle("/ets/hosts")
        self.resize(760, 520)
        self.setCentralWidget(central)
        self.createMenu()
        self.show()

    def reload(self):
        self._model.load()

    def save(self):
        # TODO: Blokada edycji na czas zapisu
        self._model.save()

    def create(self):
        self._form.addr.setFocus()

    def doCreate(self):
        self._model.addRow(self._form.data())
        self._form.reset()

    def remove(self):
        if not self._table.selectionModel().hasSelection():
            return

        selection = self._table.selectedIndexes()
        for index in selection:
            self._proxy.removeRows(index.row(), 1, index.parent())

    def createMenu(self):
        reload = QtGui.QAction('Reload', self)
        reload.setShortcut('Ctrl+R')
        reload.setToolTip('Loads hosts file')
        reload.triggered.connect(self.reload)

        save = QtGui.QAction('Save', self)
        save.setShortcut('Ctrl+S')
        save.setToolTip('Saves hosts file')
        save.triggered.connect(self.save)

        separator = QtGui.QAction(self)
        separator.setSeparator(True)

        exit = QtGui.QAction('Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        exit.triggered.connect(self.close)

        create = QtGui.QAction('Insert', self)
        create.setShortcut("Ctrl+N")
        create.triggered.connect(self.create)

        delete = QtGui.QAction('Delete', self)
        delete.setShortcut("Ctrl+D")
        delete.triggered.connect(self.remove)

        about = QtGui.QAction('About', self)

        file = self.menuBar().addMenu('&File')
        file.addAction(reload)
        file.addAction(save)
        file.addAction(separator)
        file.addAction(exit)

        edit = self.menuBar().addMenu('&Edit')
        edit.addAction(create)
        edit.addAction(delete)

        help = self.menuBar().addMenu('&Help')
        help.addAction(about)

    def onHeaderResize(self, index, old, new):
        if index == EditorModel.COLUMN_ADDR:
            self._form.addr.setFixedWidth(new)
        elif index == EditorModel.COLUMN_HOST:
            self._form.host.setFixedWidth(new)


def main():
    app = QtGui.QApplication(sys.argv)
    editor = Editor()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
