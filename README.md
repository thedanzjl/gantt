# gantt

BS17-07-05 project for DMD2. Gantt Chart using Clickhouse DB

## Install dependencies

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
  
## How to run

<code> python3 main.py </code>
  
## (Удалить этот пойнт потом) Как использовать clickhouse в питоне

Вообще посмотрите эту <a href="https://github.com/mymarilyn/clickhouse-driver">линку</a> - 
там есть описание как с этим работать (в readme написано и вообще там мануал есть).
Главное чтобы контейнер был запущен (читать выше), тогда client.execute('show tables') будет работать

