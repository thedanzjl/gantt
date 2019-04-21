import sys
from datetime import datetime

from PyQt5 import QtWidgets as Qt
from PyQt5 import QtCore
from PyQt5 import uic

from interface import *

# attributes for Task table
attributes = [
    'name', 'start_date', 'duration', 'assigned_user', 'creation_date'
]
users_attributes = ['name', 'creation_date']


class GanttApp(Qt.QMainWindow):
    tasks = Table('Task', attributes)
    users = Table('User', users_attributes)
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
        self.userComboBox.addItem('None')
        self.userComboBox.addItems([list(i)[0] for i in self.users.query('select name from User')])
        self.addTaskButton.clicked.connect(self.add_task)
        self.taskLine.returnPressed.connect(self.add_task)
        self.display()
        self.taskDetailTable.itemChanged.connect(self.edit_task_meta)
        self.mainTable.itemClicked.connect(self.display_meta)

        self.addUserButton.clicked.connect(self.add_user)
        self.userLine.returnPressed.connect(self.add_user)

    def display(self):
        """
        displays tasks and users in mainTable
        """
        task_names = self.tasks.get_values()
        user_names = self.users.get_values()
        rows = max(len(task_names), len(user_names))
        self.mainTable.setRowCount(rows)
        self.mainTable.setColumnCount(2)
        self.mainTable.setHorizontalHeaderLabels(['tasks', 'users'])
        self.mainTable.horizontalHeader().setStretchLastSection(True)

        for row in range(len(task_names)):
            task_item = Qt.QTableWidgetItem(task_names[row][0])
            self.mainTable.setItem(row, 0, task_item)

        for row in range(len(user_names)):
            user_item = Qt.QTableWidgetItem(user_names[row][0])
            self.mainTable.setItem(row, 1, user_item)

    def display_meta(self, item):
        self.lock = True
        if item.column() == 1:  # user name column clicked
            self.lock = False
            return

        values = self.tasks.get_by_name(item.text())

        self.taskDetailTable.setRowCount(1)
        self.taskDetailTable.setColumnCount(len(attributes) - 1)
        self.taskDetailTable.setHorizontalHeaderLabels(attributes[1:])

        for col in range(1, len(attributes)):
            if attributes[col] in ['assigned_user']:
                users = values[0][col]
                item = Qt.QTableWidgetItem(' '.join(users))
            else:
                item = Qt.QTableWidgetItem(str(values[0][col]))
            if attributes[col] in ['creation_date']:
                item.setFlags(QtCore.Qt.ItemIsEditable)
            self.taskDetailTable.setItem(0, col - 1, item)

        self.lock = False

    def add_task(self):
        name = self.taskLine.text()
        name = name.replace("'", '')
        # assigned_users = self.tasks.query(f"select assigned_user from Task where name = '{name}'")
        if self.userComboBox.currentText() == 'None':
            assigned_users = []
        else:
            assigned_users = [self.userComboBox.currentText()]
        self.tasks.add(name=name, start_date=str(datetime.today().date()), creation_date=datetime.today().date(),
                       duration=1, assigned_user=assigned_users)

        self.mainTable.setRowCount(self.tasks.rows)

        item = Qt.QTableWidgetItem(name)
        self.lock = True
        self.mainTable.setItem(self.tasks.rows - 1, 0, item)
        self.lock = False

    def edit_task_meta(self, item):  # Print spaces between names of users to edit assigned_user field
        if self.lock:
            return
        row = self.taskDetailTable.row(item)
        col = self.taskDetailTable.column(item)
        name = self.mainTable.selectedItems()[0].text()
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
        if attributes[col + 1] == 'assigned_user':
            data = data.split()
            if len(data) != 0 and data[-1] not in [list(i)[0] for i in self.users.query('select name from User')]:
                Qt.QMessageBox.critical(self, 'Error', "There is no such user")
                previous_value = self.tasks.query(f"select assigned_user from Task where name = '{name}'")[0][0]
                users = ' '.join(previous_value)
                self.taskDetailTable.setItem(row, col, Qt.QTableWidgetItem(users))
                return
            if len(data) != 0 and data[-1] in data[:-1]:
                Qt.QMessageBox.critical(self, 'Error', "You've already assigned the user")
                previous_value = self.tasks.query(f"select assigned_user from Task where name = '{name}'")[0][0]
                users = ' '.join(previous_value)
                self.taskDetailTable.setItem(row, col, Qt.QTableWidgetItem(users))
                return
        if not isinstance(data, list) and not data.isdigit():
            data = f"'{data}'"
        self.tasks.update_by_name(name, value_to_update=(attributes[col + 1], data))

    def add_user(self):
        name = self.userLine.text()
        name = name.replace(' ', '_')
        self.users.add(name=name, creation_date=datetime.today().date())
        self.userComboBox.addItem(name)

        item = Qt.QTableWidgetItem(name)
        self.lock = True
        self.mainTable.setItem(self.users.rows - 1, 1, item)
        self.lock = False


if __name__ == '__main__':
    app = Qt.QApplication([])
    mw = GanttApp('Gantt Chart')
    mw.show()
    sys.exit(app.exec_())
