from PyQt5 import Qt, QtCore
from PyQt5 import uic
from interface import *
from datetime import datetime


import sys


class GanttApp(Qt.QMainWindow):

    tasks = Table('Task')

    def __init__(self, name):
        super().__init__()
        self.client = Client(host='localhost')
        self.setWindowTitle(name)
        self.init_ui()

    def init_ui(self):
        """
        initialises GUI. Write down here all widgets, tabs and stuff like that
        """
        uic.loadUi('gantt.ui', self)
        self.addTaskButton.clicked.connect(self.add_task)
        self.taskLine.returnPressed.connect(self.add_task)
        self.display()
        self.taskTable.itemChanged.connect(self.edit_task_meta)

    def display(self):
        """
        displays tasks in table
        """
        values = self.tasks.get_values()
        self.taskTable.setRowCount(len(values))
        self.taskTable.setColumnCount(len(attributes))
        self.taskTable.setHorizontalHeaderLabels(attributes.keys())

        for i, row in enumerate(range(len(values))):
            for j, col in enumerate(range(len(attributes))):
                item = Qt.QTableWidgetItem(str(values[i][j]))
                if col <= 1:
                    item.setFlags(QtCore.Qt.ItemIsEditable)
                self.taskTable.setItem(i, j, item)

    def add_task(self):
        self.tasks.add(name=self.taskLine.text(), start_date=datetime.today(), duration=1)
        values = self.tasks.query(f"select * from {self.tasks.table_name} where name='{self.taskLine.text()}'")
        self.taskTable.setRowCount(self.tasks.rows)
        for i in range(len(attributes)):
            self.taskTable.setItem(self.tasks.rows-1, i, Qt.QTableWidgetItem(str(values[0][i])))

    def edit_task_meta(self, item):
        row = self.taskTable.row(item)
        col = self.taskTable.column(item)
        name = self.taskTable.item(row, 0).text()
        data = item.text()
        if not data.isdigit():
            data = f"'{data}'"
        self.tasks.update_by_name(name, value_to_update=(self.taskTable.horizontalHeaderItem(col).text(), data))


if __name__ == '__main__':
    app = Qt.QApplication([])
    mw = GanttApp('Gantt Chart')
    mw.show()
    sys.exit(app.exec_())
