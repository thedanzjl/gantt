from clickhouse_driver import Client

attributes = {'name': 'String', 'start_date': 'Date', 'duration': 'Int32'}


class Table:

    def __init__(self, name):
        self.client = Client(host='localhost')
        self.table_name = name

    def get_columns(self):
        columns = self.client.execute(f'describe {self.table_name}')
        return list(map(lambda x: x[0], columns))

    def get_values(self):
        return self.client.execute(f'select * from {self.table_name}')


if __name__ == '__main__':
    t = Table('Task')
    print(t.get_values())
