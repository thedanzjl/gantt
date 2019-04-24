import sys
from datetime import datetime, timedelta

from PyQt5 import QtWidgets as Qt
from PyQt5 import QtCore
from PyQt5 import uic
from PyQt5.QtGui import QColor
from PyQt5.uic.properties import QtWidgets


from search import search as gs_search
# from Qt import QtGui

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
        self.userComboBox.addItems([list(i)[0] for i in Table.query('select name from User')])
        self.addTaskButton.clicked.connect(self.add_task)
        self.taskLine.returnPressed.connect(self.add_task)
        self.display()
        self.taskDetailTable.itemChanged.connect(self.edit_task_meta)
        self.mainTable.cellClicked.connect(self.display_meta)
        self.saveDescButton.clicked.connect(self.save_task_desc)
        self.addUserButton.clicked.connect(self.add_user)
        self.userLine.returnPressed.connect(self.add_user)
        self.taskDescriptionText.textChanged.connect(self.desc_changed)
        self.deleteTaskButton.clicked.connect(self.delete_task)
        self.saveDescButton.setStyleSheet("background-color: green")
        self.searchButton.clicked.connect(self.search)
        self.taskSearch.returnPressed.connect(self.search)
        self.GSBox.stateChanged.connect(self.GS_turned)
        self.GSTopNspinBox.valueChanged.connect(self.GS)
        self.timelineTable.horizontalHeader().setStretchLastSection(True)
        self.ganttTabWidget.setCurrentIndex(0)
        self.taskDetailTable.verticalHeader().setStretchLastSection(True)

        self.timeline(self.tasks)

    def timeline(self, table, label_content=''):
        self.timelineTable.clearContents()
        min_date = Table.query(f'select min(start_date) from {table.table_name}')
        min_date = min_date[0][0]
        min_dateObj = datetime.strptime(min_date, '%Y-%m-%d')
        finish_dates = []
        task_dates = Table.query(f'select start_date, duration from {table.table_name} order by start_date')  # start date with durations

        for task_date in task_dates:
            dat, duration = task_date
            finish = datetime.strptime(dat, '%Y-%m-%d') + timedelta(int(duration), 0, 0)
            finish_dates.append(finish)

        max_duration = Table.query(f'select max(duration) from {table.table_name}')[0][0]
        max_date = Table.query(f'select max(start_date) from {table.table_name}')[0][0]
        self.timelineLabel.setText('Timeline. ' + label_content)
        max_days_after_start = (datetime.strptime(max_date, '%Y-%m-%d') - min_dateObj).days
        max_duration += max_days_after_start - 1

        task_names = Table.query(f'select name from {table.table_name} order by start_date')
        self.timelineTable.setRowCount(len(task_names))

        task_names = map(lambda x: x[0], task_names)

        self.timelineTable.setVerticalHeaderLabels(task_names)

        column_names = [min_date]
        for i in range(1, max_duration):
            next_date = str((min_dateObj + timedelta(days=i)).date())
            column_names.append(next_date)
        num_cols = len(column_names)
        self.timelineTable.setColumnCount(num_cols)
        self.timelineTable.setHorizontalHeaderLabels(column_names)

        for i, task in enumerate(task_dates):
            start_date, duration = task
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            days_after_start = (start_date - min_dateObj).days
            for day in range(duration):
                task_item = Qt.QTableWidgetItem('')
                task_item.setBackground(QColor(200, 0, 200))
                self.timelineTable.setItem(i, days_after_start + day, task_item)

    def update_timeline(self):
        if self.GSBox.checkState() > 0:  # GS mode activated
            top_closest = self.GSTopNspinBox.value()
            current_task_name = self.mainTable.selectedItems()[0].text()
            current_task = self.tasks.get_by_name(current_task_name)
            gs_search(current_task, top_closest)
            result_task_table = Table('ResultTask', attributes=['name', 'start_date', 'duration'])
            self.timeline(
                table=result_task_table,
                label_content=f'Geospatial Search for task: "{current_task_name}". Top {top_closest} closest. ')
        else:  # GS mode deactivated
            self.timeline(table=self.tasks)

    def display(self):
        """
        displays tasks and users in mainTable
        """
        task_values = self.tasks.get_values()
        num_tasks = len(task_values)
        self.GSTopNspinBox.setMaximum(num_tasks)

        self.mainTable.setRowCount(len(task_values))
        self.mainTable.setColumnCount(1)
        self.mainTable.setHorizontalHeaderLabels(['tasks'])
        self.mainTable.horizontalHeader().setStretchLastSection(True)
        self.mainTable.verticalHeader().setStretchLastSection(True)
        self.mainTable.verticalHeader().setDefaultSectionSize(57)

        progress_i = attributes.index('progress')

        for row in range(num_tasks):
            task = task_values[row]
            task_widget = Qt.QWidget()
            layout = Qt.QVBoxLayout()
            pgbar = Qt.QProgressBar()
            pgbar.setValue(task[progress_i])
            layout.addWidget(Qt.QLabel(task[0]))
            layout.addWidget(pgbar)

            task_widget.setLayout(layout)
            self.mainTable.setCellWidget(row, 0, task_widget)

    def display_meta(self):
        self.lock = True

        self.deleteTaskButton.setEnabled(True)
        self.taskDescriptionText.setEnabled(True)
        self.saveDescButton.setEnabled(True)
        self.GSBox.setEnabled(True)

        task_name = self.get_current_task_name()
        self.taskNameLabel.setText(task_name)

        values = self.tasks.get_by_name(task_name)

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

        task_widget = Qt.QWidget()
        layout = Qt.QVBoxLayout()
        pgbar = Qt.QProgressBar()
        pgbar.setValue(0)
        layout.addWidget(Qt.QLabel(name))
        layout.addWidget(pgbar)
        task_widget.setLayout(layout)
        self.lock = True
        self.mainTable.setCellWidget(self.tasks.rows - 1, 0, task_widget)
        self.lock = False

        self.taskLine.setText('')  # clear textline
        self.mainTable.setCurrentCell(self.tasks.rows - 1, 0)

        self.update_timeline()

    def edit_task_meta(self, item):  # Print spaces between names of users to edit assigned_users field
        if self.lock:
            return
        row = self.taskDetailTable.row(item)
        col = self.taskDetailTable.column(item)
        name = self.get_current_task_name()
        data = item.text()
        actual_attrs = list(filter(lambda x: x not in hidden_attrs, attributes))
        if actual_attrs[col] == 'start_date':
            try:
                datetime.strptime(data, "%Y-%M-%d")
            except ValueError:
                Qt.QMessageBox.critical(self, 'Error', "Invalid date format")
                previous_value = Table.query(f"select start_date from Task where name = '{name}'")[0][0]
                self.taskDetailTable.setItem(row, col, Qt.QTableWidgetItem(previous_value))
                return
        elif actual_attrs[col] == 'duration':
            if not data.isdigit():
                Qt.QMessageBox.critical(self, 'Error', "Invalid int format")
                previous_value = Table.query(f"select duration from Task where name = '{name}'")[0][0]
                self.taskDetailTable.setItem(row, col, Qt.QTableWidgetItem(str(previous_value)))
                return
        elif actual_attrs[col] == 'assigned_users':
            data = data.split()
            if len(data) != 0 and data[-1] not in [list(i)[0] for i in Table.query('select name from User')]:
                Qt.QMessageBox.critical(self, 'Error', "There is no such user")
                previous_value = Table.query(f"select assigned_users from Task where name = '{name}'")[0][0]
                users = ' '.join(previous_value)
                self.taskDetailTable.setItem(row, col, Qt.QTableWidgetItem(users))
                return
            if len(data) != 0 and data[-1] in data[:-1]:
                Qt.QMessageBox.critical(self, 'Error', "You've already assigned the user")
                previous_value = Table.query(f"select assigned_users from Task where name = '{name}'")[0][0]
                users = ' '.join(previous_value)
                self.taskDetailTable.setItem(row, col, Qt.QTableWidgetItem(users))
                return
        elif actual_attrs[col] == 'progress':
            if not data.isdigit():
                Qt.QMessageBox.critical(self, 'Error', "Invalid int format")
                previous_value = Table.query(f"select progress from Task where name = '{name}'")[0][0]
                self.taskDetailTable.setItem(row, col, Qt.QTableWidgetItem(str(previous_value)))
                return
            if int(data) not in range(0, 101):
                Qt.QMessageBox.critical(self, 'Error', "Progress should be in [0, 100] borders")
                previous_value = Table.query(f"select progress from Task where name = '{name}'")[0][0]
                self.taskDetailTable.setItem(row, col, Qt.QTableWidgetItem(str(previous_value)))
                return
            self.taskProgressBar.setValue(int(data))
            widget = self.mainTable.cellWidget(self.mainTable.currentRow(), self.mainTable.currentColumn())
            pgbar = widget.layout().itemAt(1).widget()
            pgbar.setValue(int(data))
        if not isinstance(data, list) and not data.isdigit():
            data = f"'{data}'"
        self.tasks.update_by_name(name, value_to_update=(actual_attrs[col], data))

        self.update_timeline()

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
            result_task = Table.query('select name, progress from Task where like(name, \'%' + search_query + '%\')')
        else:
            result_task = Table.query('select name, progress from Task')

        self.mainTable.setRowCount(len(result_task))
        self.mainTable.setColumnCount(1)
        self.mainTable.setHorizontalHeaderLabels(['tasks'])
        self.mainTable.horizontalHeader().setStretchLastSection(True)
        self.mainTable.verticalHeader().setStretchLastSection(True)

        for row in range(len(result_task)):
            task_widget = Qt.QWidget()
            layout = Qt.QVBoxLayout()
            pgbar = Qt.QProgressBar()
            pgbar.setValue(result_task[row][1])
            layout.addWidget(Qt.QLabel(result_task[row][0]))
            layout.addWidget(pgbar)

            task_widget.setLayout(layout)
            self.mainTable.setCellWidget(row, 0, task_widget)

    def get_current_task_name(self):
        row, col = self.mainTable.currentRow(), self.mainTable.currentColumn()
        item = self.mainTable.cellWidget(row, col)
        item_layout = item.layout()
        item_widget = item_layout.itemAt(0).widget()
        item_name = item_widget.text()
        return item_name

    def delete_task(self):
        task_name = self.get_current_task_name()
        task_row = self.mainTable.currentRow()
        answ = Qt.QMessageBox.question(self, 'Delete task', f'You sure you want to delete {task_name}')
        if answ == Qt.QMessageBox.Yes:
            self.tasks.delete_by_name(task_name)
            self.mainTable.removeRow(task_row)
        self.update_timeline()

    def GS_turned(self, state):
        """
        :param state: state of checkbox GSBox. if activated state > 0, otherwise 0
        """
        self.GSTopNspinBox.setEnabled(state > 0)
        if state == 0:
            self.timeline(self.tasks)
        else:
            if self.GSTopNspinBox.value():
                self.update_timeline()

    def GS(self, top_closest):
        current_task_name = self.get_current_task_name()
        current_task = self.tasks.get_by_name(current_task_name)
        gs_search(current_task, top_closest)

        result_tasks_table = Table("ResultTask", attributes=['name', 'start_date', 'duration'])
        self.timeline(result_tasks_table,
                      label_content=f'Geospatial Search for task: "{current_task_name}". Top {top_closest} closest. ')


if __name__ == '__main__':
    app = Qt.QApplication([])
    mw = GanttApp('Gantt Chart')
    mw.show()
    sys.exit(app.exec_())
