import datetime
import time


from clickhouse_driver import Client
client = Client('localhost')

# t:  return value of client.execute("SELECT * FROM Task WHERE name = 'task1'")
# so it is 1 record of Task
# num: number of nearest tasks (if top 3, k = 3)
# also prints elapsed time since it is required search will take less then minute on 1000 records
def search(t, k):

    start = time.time()

    aim = t[0][1]

    all = client.execute("SELECT * FROM Task")

    client.execute('DROP TABLE IF EXISTS Score')

    client.execute(''
                   'CREATE TABLE Score '
                   '(name String, start_date String, score Float32, creation_date Date) '
                   'ENGINE = MergeTree(creation_date, name, 8192)')

    values = [[str(i[0]), str(i[1]), abs((datetime.datetime.strptime(i[1], '%Y-%m-%d') - datetime.datetime.strptime(aim,
                                                                                                                    '%Y-%m-%d')) / datetime.timedelta(
        days=1)), datetime.datetime.today().date()] for i in all]
    client.execute('insert into Score values ', values)

    result = client.execute('SELECT name, start_date from Score ORDER BY score')

    end = time.time()

    print('search time: ', end - start)

    result = result[:k]

    return result


t = client.execute("SELECT * FROM Task WHERE name = 'task1'")

print(search(t,3))

#[('task 0', '2019-04-22', 10, (), 'description of task 0', 97, datetime.date(2019, 4, 22)),