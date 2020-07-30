import sqlite3
import os.path

import utils.ConfigParser as config
import main as main

db_path = config.get('System', 'db_path')


def create_db():
    if not os.path.exists(db_path):
        recreate_database()


def recreate_database():

    sqlite_connection = sqlite3.connect(db_path)
    sqlite_drop_lists = "DROP TABLE IF EXISTS Lists"
    sqlite_drop_entries = "DROP TABLE IF EXISTS Entries"
    sqlite_create_lists = '''
    CREATE TABLE Lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    order_id INTEGER,
    created_date datetime DEFAULT (datetime('now','localtime'))); 
    '''
    sqlite_create_entries = '''
    CREATE TABLE Entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER,
    name TEXT NOT NULL,
    is_completed INTEGER DEFAULT 0,
    created_date datetime DEFAULT (datetime('now','localtime')),
    due_date datetime,
    frequency INTEGER DEFAULT 0);
    '''

    sqlite_insert_default_lists = '''
    INSERT INTO 'Lists' ('name', 'order_id') VALUES ("Supermarket", 1 ), ("To Do", 2 ), ("Drag Store", 3 ), ("Movies to watch", 4 );
    '''
    sqlite_insert_default_entries = '''
    INSERT INTO 'Entries' ('list_id', 'name') VALUES (1, 'first' ), (1, 'first2' ), (1, 'first3' ), (1, 'first4' );
    '''

    cursor = sqlite_connection.cursor()
    cursor.execute(sqlite_drop_lists)
    cursor.execute(sqlite_drop_entries)
    cursor.execute(sqlite_create_lists)
    cursor.execute(sqlite_create_entries)
    cursor.execute(sqlite_insert_default_lists)
    cursor.execute(sqlite_insert_default_entries)

    cursor.close()
    sqlite_connection.commit()
    sqlite_connection.close()



def execute_query(query):
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    cursor.execute(query)
    cursor.close()
    records = cursor.fetchall()
    return records


# Lists CRUD

def create_list(list_name):
    try:
        sqlite_connection = sqlite3.connect(db_path)
        cursor = sqlite_connection.cursor()
        query = "INSERT INTO 'Lists' ('name', 'order_id') VALUES (?, 1 )"
        cursor.execute(query, (list_name,))
    except sqlite3.Error as e:
        # TODO move this out. DBLayer must contain only db layer
        main.MainApp.open_error_popup('Cant create list with this name')
    cursor.close()
    sqlite_connection.commit()
    sqlite_connection.close()




def read_lists():
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT * FROM `Lists` ORDER BY order_id """
    cursor.execute(query)
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return records


def get_list_name(list_id):
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT name FROM `Lists` where id = ? """
    cursor.execute(query, (list_id,))
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return records[0][0]


def get_list_id(list_name):
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT id FROM `Lists` where name = ? """
    cursor.execute(query, (list_name,))
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return records[0][0]


def update_list(list_name, new_list_name):
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """UPDATE `Lists` SET name = ? WHERE name = ?"""
    cursor.execute(query, (new_list_name, list_name))
    cursor.close()
    sqlite_connection.commit()
    sqlite_connection.close()


def delete_list_by_name(list_name):
    list_id = get_list_id(list_name)
    delete_entries(list_id)
    delete_list_by_id(list_id)


def delete_list_by_id(list_id):
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """DELETE FROM `Lists` WHERE id = ? """
    cursor.execute(query, (list_id,))
    cursor.close()
    sqlite_connection.commit()
    sqlite_connection.close()


# Entries CRUD
def create_entry(list_id, entry_name):
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = "INSERT INTO 'Entries' ( 'list_id', 'name') VALUES (?, ? )"
    cursor.execute(query, (list_id, entry_name))
    cursor.close()
    sqlite_connection.commit()
    sqlite_connection.close()


def read_entries(list_id):
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT * FROM `Entries` WHERE list_id = ? and is_completed = 0"""
    cursor.execute(query, (list_id,))
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return records


def update_entry(entry_name, new_entry_name):
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """UPDATE `Entries` SET name = ? WHERE name = ?"""
    cursor.execute(query, (new_entry_name, entry_name))
    cursor.close()
    sqlite_connection.commit()
    sqlite_connection.close()


def read_all_entries():
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT * FROM `Entries` """
    cursor.execute(query, )
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return records


def read_entries_count(list_id):
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT COUNT(*) FROM `Entries` WHERE list_id = ?  and is_completed = 0"""
    cursor.execute(query, (list_id,))
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return str(records[0][0])


def complete_entry(entry_name):
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """UPDATE `Entries` SET is_completed = 1 WHERE name = ?"""
    cursor.execute(query, (entry_name,))
    cursor.close()
    sqlite_connection.commit()
    sqlite_connection.close()


def delete_entries(list_id):
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """DELETE FROM `Entries` WHERE list_id = ? """
    cursor.execute(query, (list_id,))
    cursor.close()
    sqlite_connection.commit()
    sqlite_connection.close()
