import datetime
import time


from clickhouse_driver import Client
from math import sqrt

client = Client('localhost')


def search(t, k):
    """
    :param t:  return value of client.execute("SELECT * FROM Task WHERE name = 'task1'")
    so it is 1 record of Task
    :param num: number of nearest tasks (if top 3, k = 3)
    also prints elapsed time since it is required search will take less then minute on 1000 records
    """
    def distance(first, second):
        # duration and start_time
        # sum of squared differences
        a = (datetime.datetime.strptime(first[1], '%Y-%m-%d') - datetime.datetime.strptime(second[0][1], '%Y-%m-%d')) / datetime.timedelta(days=1)
        b = first[2] - second[0][2]
        return sqrt(a**2 + b**2)

    start = time.time()

    aim = t[0][1]

    all = client.execute("SELECT * FROM Task")

    values = [
        [str(i[0]),
         str(i[1]),
         i[2],
         distance(i, t),
         datetime.datetime.today().date()
         ]
        for i in all if i[0] != t[0][0]]

    client.execute('insert into Score values ', values)


    result = client.execute('SELECT name, start_date, duration from Score ORDER BY score')
    end = time.time()
    print('search time: ', end - start)
    result = result[:k]
    client.execute('DROP TABLE IF EXISTS Result_task')

    client.execute(''
                   'CREATE TABLE Result_task '
                   '(name String, start_date String, duration Int32) '
                   'ENGINE = Memory()')

    client.execute('insert into Result_task values ', result)



if __name__ == '__main__':
    t = client.execute("SELECT * FROM Task WHERE name = 'task 1'")
    search(t, 3)

    e = client.execute("SELECT * from Result_task")
    print(e)
    # [('task 0', '2019-04-22', 10, (), 'description of task 0', 97, datetime.date(2019, 4, 22)),
