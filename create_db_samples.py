from clickhouse_driver import Client
from datetime import datetime
from random import randint


def main():
    client = Client(host='localhost')
    client.execute('DROP TABLE IF EXISTS Task')
    client.execute(''
                   'CREATE TABLE Task '
                   '(name String, start_date Date, duration Int32) '
                   'ENGINE = MergeTree(start_date, name, 8192)')

    values = [[f'task {i}', datetime.today(), randint(1, 10)] for i in range(10)]
    print(values)

    client.execute('insert into Task values ', values)


if __name__ == '__main__':
    main()
