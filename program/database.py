import sqlite3
import os
from hmm import gould, ker_cos

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'hmm.db')

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS gould_1d (
            id INTEGER PRIMARY KEY, n INTEGER UNIQUE, value INTEGER
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS ker_cos_2d (
            id INTEGER PRIMARY KEY, x INTEGER, y INTEGER,
            a REAL, value INTEGER, UNIQUE(x, y, a)
        )
    ''')
    conn.commit()
    cur.execute('SELECT COUNT(*) FROM gould_1d')
    if cur.fetchone()[0] < 1000:
        cur.executemany(
            'INSERT OR IGNORE INTO gould_1d (n, value) VALUES (?, ?)',
            [(n, gould(n)) for n in range(1000)]
        )
    cur.execute('SELECT COUNT(*) FROM ker_cos_2d')
    if cur.fetchone()[0] < 2500:
        A = 10.0
        rows = [(x, y, A, ker_cos(x, y, A)) for x in range(1, 51) for y in range(1, 51)]
        cur.executemany(
            'INSERT OR IGNORE INTO ker_cos_2d (x, y, a, value) VALUES (?, ?, ?, ?)', rows
        )
    conn.commit()
    conn.close()

def fetch_gould(limit=1000):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT n, value FROM gould_1d ORDER BY n LIMIT ?', (limit,))
    data = cur.fetchall()
    conn.close()
    return data

def fetch_ker_cos(xmin=1, xmax=50, ymin=1, ymax=50, A=10.0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        'SELECT COUNT(*) FROM ker_cos_2d WHERE a=? AND x BETWEEN ? AND ? AND y BETWEEN ? AND ?',
        (A, xmin, xmax, ymin, ymax)
    )
    if cur.fetchone()[0] < (xmax - xmin + 1) * (ymax - ymin + 1):
        rows = [(x, y, A, ker_cos(x, y, A))
                for x in range(xmin, xmax + 1) for y in range(ymin, ymax + 1)]
        cur.executemany(
            'INSERT OR IGNORE INTO ker_cos_2d (x, y, a, value) VALUES (?, ?, ?, ?)', rows
        )
        conn.commit()
    cur.execute(
        'SELECT x, y, value FROM ker_cos_2d WHERE a=? AND x BETWEEN ? AND ? AND y BETWEEN ? AND ?',
        (A, xmin, xmax, ymin, ymax)
    )
    data = {(r[0], r[1]): r[2] for r in cur.fetchall()}
    conn.close()
    return data
