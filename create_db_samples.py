from clickhouse_driver import Client
from datetime import datetime
from random import randint


def main():
    client = Client(host='192.168.99.100')
    client.execute('DROP TABLE IF EXISTS Task')
    client.execute(''
                   'CREATE TABLE Task '
                   '(name String, start_date String, duration Int32, creation_date Date) '
                   'ENGINE = MergeTree(creation_date, name, 8192)')

    values = [[f'task {i}', str(datetime.today().date()), randint(1, 10), datetime.today().date()] for i in range(10)]

    client.execute('insert into Task values ', values)


if __name__ == '__main__':
    main()
