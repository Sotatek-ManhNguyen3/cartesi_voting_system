import sqlite3


def init_conn():
    conn = sqlite3.connect('./voting_system.db')
    conn.row_factory = dict_factory
    return conn


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
