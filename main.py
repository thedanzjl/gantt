import sys
from datetime import datetime, timedelta

from PyQt5 import QtWidgets as Qt
from PyQt5 import QtCore
from PyQt5 import uic
from PyQt5.QtGui import QColor
from PyQt5.uic.properties import QtWidgets
from Qt import QtGui

from interface import *

# attributes for Task table
attributes = [
    'name', 'start_date', 'duration', 'assigned_users', 'description', 'progress', 'creation_date'
]
hidden_attrs = ['name', 'description']  # attributes that you want to hide from users (not show in display_meta)
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
        self.saveDescButton.clicked.connect(self.save_task_desc)
        self.addUserButton.clicked.connect(self.add_user)
        self.userLine.returnPressed.connect(self.add_user)
        self.taskDescriptionText.textChanged.connect(self.desc_changed)
        self.deleteTaskButton.clicked.connect(self.delete_task)
        self.saveDescButton.setStyleSheet("background-color: green")
        self.tableWidget.setRowCount(len(self.users.query('select name from Task')))
        minimalDate = self.tasks.query('select min(start_date) from Task')
        minimalDate = minimalDate[0][0]
        minimumDateObj = datetime.strptime(minimalDate, '%Y-%m-%d')
        finishDates = []
        tempFinishDates = []
        temp = self.tasks.query('select start_date, duration from Task')
        ind = 0

        task_names = self.tasks.get_values()
        task_names.sort(key=lambda x: x[1])

        for i in temp:
            dat = i[0]
            year = dat[:4]
            month = dat[6:7]
            day = dat[-2:]
            dateTemp = year + '-' + month + '-' + day
            d = datetime.strptime(dateTemp, '%Y-%m-%d') + timedelta(int(i[1]), 0, 0)
            tempFinishDates.append(d)
            finishDates.append(d.strftime('%Y-%m-%d'))
        maximumDeltaTime = minimumDateObj - tempFinishDates[-1]
        for i in range(len(tempFinishDates)):
            if ((tempFinishDates[i] - minimumDateObj) > maximumDeltaTime):
                maximumDeltaTime = tempFinishDates[i] - minimumDateObj
                ind = i
        tteemmpp = str(maximumDeltaTime)
        while (tteemmpp[-1]!='d'):
            tteemmpp = tteemmpp[:-2]
        tteemmpp = tteemmpp[:-2]
        numOfColumns = int(tteemmpp)
        self.tableWidget.setColumnCount(numOfColumns)

        task_names = self.tasks.get_values()
        task_names.sort(key=lambda x: x[1])
        
        taskNames = []
        for i in task_names:
            taskNames.append(i)

        rowNames = []
        for i in taskNames:
            rowNames.append(i[0])
        self.tableWidget.setVerticalHeaderLabels(rowNames)
        columnNames = [minimumDateObj.strftime('%Y-%m-%d')]
        currDateObj = minimumDateObj
        qq = 0
        while (tempFinishDates[ind] != currDateObj):
            currDateObj = currDateObj + timedelta(days=1)
            columnNames.append(currDateObj.strftime('%Y-%m-%d'))
        self.tableWidget.setHorizontalHeaderLabels(columnNames)

        for task in task_names:
            start_date = task[1]
            duration = task[2]
            for i in range(duration):
                task_item = Qt.QTableWidgetItem('')
                self.tableWidget.setItem(task_names.index(task), columnNames.index(start_date) + i, task_item)
                self.tableWidget.item(task_names.index(task), columnNames.index(start_date) + i).setBackground(QColor(200, 0, 200))

        self.searchButton.clicked.connect(self.search)
        self.taskSearch.returnPressed.connect(self.search)

    def display(self):
        """
        displays tasks and users in mainTable
        """
        task_names = self.tasks.get_values()
        self.mainTable.setRowCount(len(task_names))
        self.mainTable.setColumnCount(1)
        self.mainTable.setHorizontalHeaderLabels(['tasks'])
        self.mainTable.horizontalHeader().setStretchLastSection(True)

        for row in range(len(task_names)):
            task_item = Qt.QTableWidgetItem(task_names[row][0])
            self.mainTable.setItem(row, 0, task_item)

    def display_meta(self, item):
        self.lock = True

        self.deleteTaskButton.setEnabled(True)
        self.taskDescriptionText.setEnabled(True)
        self.saveDescButton.setEnabled(True)

        values = self.tasks.get_by_name(item.text())

        self.taskDetailTable.setRowCount(1)
        self.taskDetailTable.setColumnCount(len(attributes) - len(hidden_attrs))
        self.taskDetailTable.horizontalHeader().setStretchLastSection(True)

        attrs = zip(attributes, values[0])
        actual_attrs = list()
        description = ''
        progress = 0
        for item in attrs:
            if item[0] == 'description':
                description = item[1]
            elif item[0] not in hidden_attrs:
                actual_attrs.append(item)
            if item[0] == 'progress':
                progress = item[1]
        self.taskDetailTable.setHorizontalHeaderLabels(map(lambda x: x[0].replace("_", " "), actual_attrs))

        for col, (attr, value) in enumerate(actual_attrs):
            if attr == 'assigned_users':
                item = Qt.QTableWidgetItem(' '.join(value))
                item.setToolTip('enter names of developers separated by space')
            else:
                item = Qt.QTableWidgetItem(str(value))
                if attr == 'creation_date':
                    item.setFlags(QtCore.Qt.ItemIsEditable)
                elif attr == 'progress':
                    item.setToolTip('progress of the task in percents')
                elif attr == 'start_date':
                    item.setToolTip('date of starting the task')
                elif attr == 'duration':
                    item.setToolTip('how many days required to accomplish the task')
            self.taskDetailTable.setItem(0, col, item)

        self.taskDescriptionText.setPlainText(description)
        self.taskProgressBar.setValue(progress)
        self.saveDescButton.setStyleSheet("background-color: green")

        self.lock = False

    def add_task(self):
        name = self.taskLine.text()
        name = name.replace("'", '')
        if self.userComboBox.currentText() == 'None':
            assigned_users = []
        else:
            assigned_users = [self.userComboBox.currentText()]
        self.tasks.add(name=name, start_date=str(datetime.today().date()), creation_date=datetime.today().date(),
                       duration=1, assigned_users=assigned_users, progress=0, description='')

        self.mainTable.setRowCount(self.tasks.rows)

        item = Qt.QTableWidgetItem(name)
        self.lock = True
        self.mainTable.setItem(self.tasks.rows - 1, 0, item)
        self.lock = False
        self.taskLine.setText('')  # clear textline
        self.mainTable.setCurrentItem(item, QtCore.QItemSelectionModel.Select)

    def edit_task_meta(self, item):  # Print spaces between names of users to edit assigned_users field
        if self.lock:
            return
        row = self.taskDetailTable.row(item)
        col = self.taskDetailTable.column(item)
        name = self.mainTable.selectedItems()[0].text()
        data = item.text()
        actual_attrs = list(filter(lambda x: x not in hidden_attrs, attributes))
        if actual_attrs[col] == 'start_date':
            try:
                datetime.strptime(data, "%Y-%M-%d")
            except ValueError:
                Qt.QMessageBox.critical(self, 'Error', "Invalid date format")
                previous_value = self.tasks.query(f"select start_date from Task where name = '{name}'")[0][0]
                self.taskDetailTable.setItem(row, col, Qt.QTableWidgetItem(previous_value))
                return
        elif actual_attrs[col] == 'duration':
            if not data.isdigit():
                Qt.QMessageBox.critical(self, 'Error', "Invalid int format")
                previous_value = self.tasks.query(f"select duration from Task where name = '{name}'")[0][0]
                self.taskDetailTable.setItem(row, col, Qt.QTableWidgetItem(str(previous_value)))
                return
        elif actual_attrs[col] == 'assigned_users':
            data = data.split()
            if len(data) != 0 and data[-1] not in [list(i)[0] for i in self.users.query('select name from User')]:
                Qt.QMessageBox.critical(self, 'Error', "There is no such user")
                previous_value = self.tasks.query(f"select assigned_users from Task where name = '{name}'")[0][0]
                users = ' '.join(previous_value)
                self.taskDetailTable.setItem(row, col, Qt.QTableWidgetItem(users))
                return
            if len(data) != 0 and data[-1] in data[:-1]:
                Qt.QMessageBox.critical(self, 'Error', "You've already assigned the user")
                previous_value = self.tasks.query(f"select assigned_users from Task where name = '{name}'")[0][0]
                users = ' '.join(previous_value)
                self.taskDetailTable.setItem(row, col, Qt.QTableWidgetItem(users))
                return
        elif actual_attrs[col] == 'progress':
            if not data.isdigit():
                Qt.QMessageBox.critical(self, 'Error', "Invalid int format")
                previous_value = self.tasks.query(f"select progress from Task where name = '{name}'")[0][0]
                self.taskDetailTable.setItem(row, col, Qt.QTableWidgetItem(str(previous_value)))
                return
            if int(data) not in range(0, 101):
                Qt.QMessageBox.critical(self, 'Error', "Progress should be in [0, 100] borders")
                previous_value = self.tasks.query(f"select progress from Task where name = '{name}'")[0][0]
                self.taskDetailTable.setItem(row, col, Qt.QTableWidgetItem(str(previous_value)))
                return
            self.taskProgressBar.setValue(int(data))
        if not isinstance(data, list) and not data.isdigit():
            data = f"'{data}'"
        self.tasks.update_by_name(name, value_to_update=(actual_attrs[col], data))

    def add_user(self):
        name = self.userLine.text()
        name = name.replace(' ', '_')
        self.users.add(name=name, creation_date=datetime.today().date())
        self.userComboBox.addItem(name)
        self.userLine.setText('')

    def save_task_desc(self):
        desc = self.taskDescriptionText.toPlainText()
        task_name = self.mainTable.selectedItems()[0].text()
        self.tasks.update_by_name(task_name, ('description', f"'{desc}'"))
        self.saveDescButton.setStyleSheet("background-color: green")

    def desc_changed(self):
        self.saveDescButton.setStyleSheet("background-color: red")

    def search(self):
        self.mainTable.clearContents()
        search_query = self.taskSearch.text()
        if len(search_query) != 0:
            result_task = self.tasks.query('select name from Task where like(name, \'%' + search_query + '%\')')
        else:
            result_task = self.tasks.get_values()

        self.mainTable.setRowCount(len(result_task))
        self.mainTable.setColumnCount(1)
        self.mainTable.setHorizontalHeaderLabels(['tasks'])
        self.mainTable.horizontalHeader().setStretchLastSection(True)

        for row in range(len(result_task)):
            task_item = Qt.QTableWidgetItem(result_task[row][0])
            self.mainTable.setItem(row, 0, task_item)

    def delete_task(self):
        task_item = self.mainTable.selectedItems()[0]
        task_name = task_item.text()
        task_row = task_item.row()
        answ = Qt.QMessageBox.question(self, 'Delete task', f'You sure you want to delete {task_name}')
        if answ == Qt.QMessageBox.Yes:
            self.tasks.delete_by_name(task_name)
            self.mainTable.removeRow(task_row)


if __name__ == '__main__':
    app = Qt.QApplication([])
    mw = GanttApp('Gantt Chart')
    mw.show()
    sys.exit(app.exec_())
