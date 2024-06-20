import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def select_data(columns_, from_, count_, where_=None, order_by_=None,
                limit_=None):
    joined_columns = ', '.join(columns_)
    query = f'SELECT {joined_columns} FROM {from_}'
    for i, j in [
        [where_, 'WHERE'],
        [order_by_, 'ORDER BY'],
        [limit_, 'LIMIT']
    ]:
        if i:
            query = f'{query} {j} {i}'
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(query)
            if count_ == 1:
                return cursor.fetchone()
            return cursor.fetchmany(count_)


def insert_data(into_, columns_, values_):
    joined_columns = f"({', '.join(columns_)})"
    shortcuts = ['%s'] * len(values_)
    joined_shortcuts = f"({', '.join(shortcuts)})"
    query = f'INSERT INTO {into_} {joined_columns} VALUES {joined_shortcuts}'
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(query, values_)
