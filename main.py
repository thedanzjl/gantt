from PyQt5 import Qt
from PyQt5 import uic
from clickhouse_driver import Client
from interface import *

# import pyqtgraph as pg

import sys


class GanttApp(Qt.QMainWindow):

    tasks = Table('Task')

    def __init__(self, name):
        super().__init__()
        self.client = Client(host='localhost')
        self.setWindowTitle(name)
        self.init_ui()

    def init_ui(self):
        uic.loadUi('gantt.ui', self)
        self.taskTable.setRowCount(10)
        self.taskTable.setColumnCount(3)
        values = self.tasks.get_values()

        for i, row in enumerate(range(10)):
            for j, col in enumerate(range(3)):
                self.taskTable.setItem(i, j, Qt.QTableWidgetItem(str(values[i][j])))


if __name__ == '__main__':
    app = Qt.QApplication([])
    mw = GanttApp('Gantt Chart')
    mw.show()
    sys.exit(app.exec_())
