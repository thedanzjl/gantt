from clickhouse_driver import Client
from datetime import datetime
from random import randint


def main():
    client = Client(host='localhost')
    client.execute('DROP TABLE IF EXISTS Task')
    client.execute('DROP TABLE IF EXISTS User')

    client.execute(''
                   'CREATE TABLE Task '
                   '(name String, start_date String, duration Int32, assigned_users Array(String), creation_date Date) '
                   'ENGINE = MergeTree(creation_date, name, 8192)')
    client.execute(''
                   'CREATE TABLE User '
                   '(name String, creation_date Date) '
                   'ENGINE = MergeTree(creation_date, name, 8192)')

    values = [[f'task {i}', str(datetime.today().date()), randint(1, 10), [], datetime.today().date()] for i in range(10)]
    users = [[f'default_user{i}', datetime.today().date()] for i in range(2)]

    client.execute('insert into Task values ', values)
    client.execute('insert into User values', users)



if __name__ == '__main__':
    main()
