from PyQt5 import Qt, QtCore
from PyQt5 import uic
from interface import *
from datetime import datetime

import sys


class GanttApp(Qt.QMainWindow):
    tasks = Table('Task')
    lock = False

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
        self.taskTable.setHorizontalHeaderLabels(attributes)

        for i, row in enumerate(range(len(values))):
            for j, col in enumerate(range(len(attributes))):
                item = Qt.QTableWidgetItem(str(values[i][j]))
                if attributes[col] in ['name', 'creation_date']:
                    item.setFlags(QtCore.Qt.ItemIsEditable)
                self.taskTable.setItem(i, j, item)

    def add_task(self):
        self.tasks.add(name=self.taskLine.text(), start_date=str(datetime.today().date()), creation_date=datetime.today(),
                       duration=1)
        values = self.tasks.query(f"select * from {self.tasks.table_name} where name='{self.taskLine.text()}'")
        self.taskTable.setRowCount(self.tasks.rows)
        for i in range(len(attributes)):
            item = Qt.QTableWidgetItem(str(values[0][i]))
            if attributes[i] in ['name', 'creation_date']:
                item.setFlags(QtCore.Qt.ItemIsEditable)
            self.lock = True  # lock signal from edit_task_meta trigger
            self.taskTable.setItem(self.tasks.rows - 1, i, item)
            self.lock = False

    def edit_task_meta(self, item):
        if self.lock:
            return
        row = self.taskTable.row(item)
        col = self.taskTable.column(item)
        name = self.taskTable.item(row, 0).text()
        data = item.text()
        if attributes[col] == 'start_date':
            try:
                datetime.strptime(data, "%Y-%M-%d")
            except ValueError:
                Qt.QMessageBox.critical(self, 'Error', "Invalid date format")
                previous_value = self.tasks.query(f"select start_date from Task where name = '{name}'")[0][0]
                self.taskTable.setItem(row, col, Qt.QTableWidgetItem(previous_value))
                return
        if attributes[col] == 'duration':
            if not data.isdigit():
                Qt.QMessageBox.critical(self, 'Error', "Invalid int format")
                previous_value = self.tasks.query(f"select duration from Task where name = '{name}'")[0][0]
                self.taskTable.setItem(row, col, Qt.QTableWidgetItem(str(previous_value)))
                return
        if not data.isdigit():
            data = f"'{data}'"
        print(data)
        self.tasks.update_by_name(name, value_to_update=(attributes[col], data))


if __name__ == '__main__':
    app = Qt.QApplication([])
    mw = GanttApp('Gantt Chart')
    mw.show()
    sys.exit(app.exec_())
