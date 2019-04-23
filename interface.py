from clickhouse_driver import Client


class Table:

    """
    Representation of ClickHouse table.
    Before use, make sure that docker container is running (more in README.md).
    """

    client = Client(host='localhost')

    def __init__(self, name, attributes):

        self.table_name = name
        self.rows = len(self.get_values())
        self.cols = len(attributes)

    def get_values(self):
        return self.client.execute(f'select * from {self.table_name} order by name')

    def get_by_name(self, name):
        return self.client.execute(f"select * from {self.table_name} where name='{name}'")

    def update_by_name(self, name, value_to_update=None):
        """
        :param name: filter to search for row
        :param value_to_update: tuple of 2 elements. Used in where closet. e.g. ('duration', '2') will
        set duration to 2. Note! if your value (second arg.) is string, then use double quotes:
        ('name', "'my task'"), since by default it doesn't put quotes in query.
        """
        assert value_to_update is not None, 'pls provide value to update'
        assert type(value_to_update) == tuple
        assert len(value_to_update) == 2
        self.client.execute(f""
                            f"alter table {self.table_name} "
                            f"update {value_to_update[0]} = {value_to_update[1]} "
                            f"where name = '{name}'")

    @staticmethod
    def query(text):
        return Table.client.execute(text)

    def add(self, **values):
        self.client.execute(f'insert into {self.table_name} values', [values])
        self.rows += 1

    def delete_by_name(self, name):
        self.client.execute(f""
                            f"alter table {self.table_name} "
                            f"delete where name = '{name}'")
        self.rows -= 1


if __name__ == '__main__':
    pass

