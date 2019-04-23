# Gantt chart

BS17-07-05 project for DMD2. Gantt Chart using Clickhouse DB

## Technical details
### Database organization
![Database model diagram](https://cdn1.savepice.ru/uploads/2019/4/23/6b1beb5cbab0646dfe03aec82954f1da-full.jpg)

The presented model diagram shows the structure of the project's database.
It consists of:
* <b>Task</b>: the main part from which the Gantt chart is created. Values like name, description and assigned a user or multiple users specify the particular task; start date, duration and task progress are needed to display the Gantt chart according to its main functionality. 
* <b>User</b>: consist of user's name which can be assigned to one or more tasks.
* <b>Dependency</b>: implements another important functionality of the Gantt chart. Beginning of one task can be dependent on another task ends. Dependency entity collects such relationships (task_in for the task which is dependent on the task in task_out).
* <b>Score</b>: created for geospatial search queries. The table can be created for every task (suppose some initial task) and collects the values like name of some task in the database (let call it database task), database task's start date and score (the difference between the start date of initial task and database task). More details about it in the geospatial search section.

All entities save creation date which is necessary according to requirements of MergeTree engine in ClickHouse. 

### Geospatial search

## Utilization of the project

### Install dependencies

1. You'll need docker to run clickhouse. So, first of all, install docker.
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

