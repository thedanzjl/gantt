from PyQt5 import Qt, QtCore
from PyQt5 import uic
from interface import *
from datetime import datetime

import sys

# attributes for Task table
attributes = [
        'name', 'start_date', 'duration', 'creation_date'
    ]


class GanttApp(Qt.QMainWindow):
    tasks = Table('Task', attributes)
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
        self.taskDetailTable.itemChanged.connect(self.edit_task_meta)
        self.taskTable.itemClicked.connect(self.display_meta)

    def display(self):
        """
        displays tasks in taskTable
        """
        values = self.tasks.get_values()
        self.taskTable.setRowCount(len(values))

        # self.taskTable.setColumnCount(len(attributes))
        # self.taskTable.setHorizontalHeaderLabels(attributes)
        # for i, row in enumerate(range(len(values))):
        #     for j, col in enumerate(range(len(attributes))):
        #         item = Qt.QTableWidgetItem(str(values[i][j]))
        #         if attributes[col] in ['name', 'creation_date']:
        #             item.setFlags(QtCore.Qt.ItemIsEditable)
        #         self.taskTable.setItem(i, j, item)

        self.taskTable.setColumnCount(1)

        for row in range(len(values)):
            item = Qt.QTableWidgetItem(values[row][0])
            self.taskTable.setItem(row, 0, item)

    def display_meta(self, item):
        self.lock = True
        values = self.tasks.get_by_name(item.text())

        self.taskDetailTable.setRowCount(1)
        self.taskDetailTable.setColumnCount(len(attributes) - 1)
        self.taskDetailTable.setHorizontalHeaderLabels(attributes[1:])

        for col in range(1, len(attributes)):
            item = Qt.QTableWidgetItem(str(values[0][col]))
            if attributes[col] in ['creation_date']:
                item.setFlags(QtCore.Qt.ItemIsEditable)
            self.taskDetailTable.setItem(0, col-1, item)

        self.lock = False

    def add_task(self):
        name = self.taskLine.text()
        self.tasks.add(name=name, start_date=str(datetime.today().date()), creation_date=datetime.today().date(),
                       duration=1)
        self.taskTable.setRowCount(self.tasks.rows)

        item = Qt.QTableWidgetItem(name)
        self.lock = True
        self.taskTable.setItem(self.tasks.rows - 1, 0, item)
        self.lock = False

    def edit_task_meta(self, item):
        if self.lock:
            return
        row = self.taskDetailTable.row(item)
        col = self.taskDetailTable.column(item)
        name = self.taskTable.selectedItems()[0].text()
        data = item.text()
        if attributes[col + 1] == 'start_date':
            try:
                datetime.strptime(data, "%Y-%M-%d")
            except ValueError:
                Qt.QMessageBox.critical(self, 'Error', "Invalid date format")
                previous_value = self.tasks.query(f"select start_date from Task where name = '{name}'")[0][0]
                self.taskDetailTable.setItem(row, col, Qt.QTableWidgetItem(previous_value))
                return
        if attributes[col + 1] == 'duration':
            if not data.isdigit():
                Qt.QMessageBox.critical(self, 'Error', "Invalid int format")
                previous_value = self.tasks.query(f"select duration from Task where name = '{name}'")[0][0]
                self.taskDetailTable.setItem(row, col, Qt.QTableWidgetItem(str(previous_value)))
                return
        if not data.isdigit():
            data = f"'{data}'"
        print(data)
        self.tasks.update_by_name(name, value_to_update=(attributes[col + 1], data))


if __name__ == '__main__':
    app = Qt.QApplication([])
    mw = GanttApp('Gantt Chart')
    mw.show()
    sys.exit(app.exec_())
