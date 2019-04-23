# Gantt Chart

BS17-07-05 project for DMD2. Gantt Chart using Clickhouse DB

## Technical information
### Database organization
![Database model diagram](https://cdn1.savepice.ru/uploads/2019/4/23/165ebb586577dde3d22f7e22c49cdddd-full.jpg)

The presented model diagram shows the structure of the project's database.
It consists of:
* <b>Task</b>: the main part from which the Gantt chart is created. Values like name, description and assigned a user or multiple users specify the particular task; start date, duration and task progress are needed to display the Gantt chart according to its main functionality. 
* <b>User</b>: consist of user's name which can be assigned to one or more tasks.
* <b>Score</b>: created for geospatial search queries. The table can be created for every task (suppose some initial task) and collects the values like name of some task in the database (let call it database task), database task's start date and score (the difference between the start date of initial task and database task). More details about it in the geospatial search section.

All entities save creation date which is necessary according to requirements of MergeTree engine in ClickHouse. 

### Geospatial search
1. Is used for getting k nearest Task records for specific task. 
2. Distance is the Euclidian distance where x is start_date and y is duration
```
#pseudocode
 def distance(task1, task2):
        # duration and start_date
        # sum of squared differences
        a = task1.start_date - task2.start_date
        b = task1.duration - task2.duration
        return sqrt(a**2 + b**2)
```

## Utilization of the project

### Install dependencies

1. You'll need docker to run СlickHouse. So, first of all, install Docker.
2. Then, create a container of the clickhouse (<a href="https://hub.docker.com/r/yandex/clickhouse-server/">more</a>): 
  
      <code> $ mkdir $HOME/gantt_clickhouse_db</code>  - creates volume for storing data<br>
  
      This will run the image: <br>
      <code> $ docker run -d -p 8123:8123 -p 9000:9000 --name gantt --ulimit nofile=262144:262144 --volume=$HOME/gantt_clickhouse_db:/var/lib/clickhouse yandex/clickhouse-server</code>
  
      After running this first time docker will install image of docker on your machine. 
      So now you have installed image and created container called "gantt".
  
      For next times use
  
      <code>$ docker stop gantt</code> to stop the container. And <br>
      <code>$ docker start gantt</code> to start it.
  
3. Install <a href="https://clickhouse-driver.readthedocs.io/en/latest/installation.html">clickhouse_driver</a>
  
      On the link above there is a manual how to install it. But most likely you'll need just to write
  
      <code>$ pip install clickhouse-driver </code>
  
4. Install PyQt5. <a href="https://www.metachris.com/2016/03/how-to-install-qt56-pyqt5-virtualenv-python3/">Link</a>
  
### How to run
At first, create database sample on your machine. Run the following command:

<code> python3 create_db_samples.py </code>

After it, you can run the project. Execute the next command and you will see the main window:

<code> python3 main.py </code>
  
### How to use the application
At first, to create your own Gantt Chart you need to create some amount of tasks and some amount of users to have the possibility to assign them to particular tasks.

Creation of a user: 
* print the name of a user in the corresponding line (near the button "add new dev")
* press the button "add new dev"
* see the appearance of the newly created user in the drop list 

Creation of a task:
* print the desirable name of the task in corresponding line (near the button "add new task")
* choose someone from users to assign the task to him or set it "None"
* press the button "add new task"
* see the task in the table from left
* press on the newly created task to change default values of start date, description, duration and assigned users (press on necessary attribute to write new value, add any number of assigned user by printing their names between spaces, print new description in the field below "Description of the task" inscription, after press the button "save changes") or to delete it (press the button "delete the task"). 

For now, you can see all your added tasks in the right table which represents created Gantt Chart. The application also provides some extra features.

Search a task:
* print your search query in the corresponding line (near the button "search")
* press the button "search"
* see all tasks with names which contain your search query

Spatial search (see section Geospatial search for details):
* press on the task for which you want to find nearest tasks
* mark the box "GS" and print the number of nearest task you want
* see results in the table from the right
