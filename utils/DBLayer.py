import os.path
import sqlite3

import utils.ConfigParser as config

db_path = config.get_option_value('db_path')

migrations_list = {
    1: '''ALTER TABLE `Entries` ADD COLUMN note TEXT;''',
}


def create_db():
    if not os.path.exists(db_path):
        recreate_database()


# TODO add feature to backup db and load from backup
# TODO default lists and entries - make it lang related
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
    completed_date datetime,
    frequency INTEGER NOT NULL,
    note TEXT);
    '''
    sqlite_create_entry_name_index = 'CREATE UNIQUE INDEX entry_name ON Entries(name);'

    sqlite_insert_default_lists = '''
    INSERT INTO 'Lists' ('name', 'order_id') VALUES ("Supermarket", 1 ), ("To Do", 2 ), ("Drug Store", 3 ), ("Movies to watch", 4 );
    '''
    sqlite_insert_default_entries = '''
    INSERT INTO 'Entries' ('list_id', 'name', 'frequency') VALUES (1, 'first', 1 ), (1, 'first2', 1 ), (1, 'first3', 1 ), (1, 'first4', 1 );
    '''

    cursor = sqlite_connection.cursor()
    cursor.execute(sqlite_drop_lists)
    cursor.execute(sqlite_drop_entries)
    cursor.execute(sqlite_create_lists)
    cursor.execute(sqlite_create_entries)
    cursor.execute(sqlite_create_entry_name_index)
    cursor.execute(sqlite_insert_default_lists)
    cursor.execute(sqlite_insert_default_entries)

    cursor.close()
    sqlite_connection.commit()
    sqlite_connection.close()


def run_migrations():
    current_db_version = int(config.get_option_value('db_version'))
    available_db_version = int(config.get_option_value('available_db_version'))
    if available_db_version > current_db_version:  # need to run migrations
        sqlite_connection = sqlite3.connect(db_path)
        for key, value in migrations_list.items():
            if key > current_db_version:
                cursor = sqlite_connection.cursor()
                cursor.execute(value)
                cursor.close()
                current_db_version = key
        sqlite_connection.commit()
        sqlite_connection.close()
        config.set_option_value('db_version', current_db_version)


# Lists CRUD
def create_list(list_name: str, order_id: int) -> bool:
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    try:
        query = "INSERT INTO 'Lists' ('name', 'order_id') VALUES (?, ? )"
        cursor.execute(query, (list_name, order_id))
    except sqlite3.Error as e:
        return False
    finally:
        cursor.close()
        sqlite_connection.commit()
        sqlite_connection.close()
    return True


def read_lists() -> list:
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT * FROM `Lists` ORDER BY order_id """
    cursor.execute(query)
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return records


def read_last_list() -> list:
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = '''SELECT id, name FROM `Lists` ORDER BY id DESC LIMIT 1;'''
    cursor.execute(query)
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return records


def get_list_name(list_id: int) -> str:
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT name FROM `Lists` where id = ? """
    cursor.execute(query, (list_id,))
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return records[0][0]


def get_list_id(list_name: str) -> int:
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT id FROM `Lists` where name = ? """
    cursor.execute(query, (list_name,))
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    if len(records) > 0:
        return records[0][0]


def rename_list(list_name: str, new_list_name: str):
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """UPDATE `Lists` SET name = ? WHERE name = ?"""
    cursor.execute(query, (new_list_name, list_name))
    cursor.close()
    sqlite_connection.commit()
    sqlite_connection.close()


def delete_list_by_id(list_id: int):
    delete_entries(list_id)
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    try:
        query = """DELETE FROM `Lists` WHERE id = ? """
        cursor.execute(query, (list_id,))
    except sqlite3.Error as e:
        return False
    finally:
        cursor.close()
        sqlite_connection.commit()
        sqlite_connection.close()


# Entries CRUD
def get_entry_name(entry_id: int or str) -> str:
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT name FROM `Entries` where id = ? """
    cursor.execute(query, (entry_id,))
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return records[0][0]


def get_entry_note(entry_id: int or str) -> str:
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT note FROM `Entries` where id = ? """
    cursor.execute(query, (entry_id,))
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return '' if (records[0][0] is None) else records[0][0]


def is_entry_exists(entry_name: str) -> bool:
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT * FROM `Entries` WHERE name = ?"""
    cursor.execute(query, (entry_name,))
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    if records:
        return True
    else:
        return False


def create_entry(list_id: int, entry_name: str):
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    if is_entry_exists(entry_name):
        query = """UPDATE `Entries` SET list_id = ?, is_completed = 0, frequency =  frequency + 1  WHERE name = ?"""
        cursor.execute(query, (list_id, entry_name,))
    else:
        query = """INSERT INTO 'Entries' ( 'list_id', 'name', 'is_completed', 'created_date', 'frequency') VALUES (?, ?, 0, date(), 1)"""
        cursor.execute(query, (list_id, entry_name,))
    cursor.close()
    sqlite_connection.commit()
    sqlite_connection.close()


def read_entries(list_id: int) -> list:
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT * FROM `Entries` WHERE list_id = ? and is_completed = 0"""
    cursor.execute(query, (list_id,))
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return records


def read_entries_history(list_id: int) -> list:
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT * FROM `Entries` WHERE list_id = ? and is_completed = 1"""
    cursor.execute(query, (list_id,))
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return records


def read_entries_by_name_part(list_id: int, name_part: str) -> list:
    count = int(config.get_option_value('max_suggestions_count'))
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = '''SELECT name FROM `Entries` WHERE list_id = ? and name like ? and is_completed = 1 ORDER BY frequency DESC LIMIT ?;'''
    cursor.execute(query, (list_id, name_part + '%', count))
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return records


def read_last_entry(list_id: int) -> list:
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = '''SELECT id, name FROM `Entries` WHERE list_id = ? ORDER BY id DESC LIMIT 1;'''
    cursor.execute(query, (list_id,))
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return records


def read_all_entries() -> list:
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT * FROM `Entries` """
    cursor.execute(query, )
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return records


def read_entries_count(list_id: int or str) -> int:
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT COUNT(*) FROM `Entries` WHERE list_id = ?  and is_completed = 0"""
    cursor.execute(query, (list_id,))
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return records[0][0]


# def rename_entry(entry_name, new_entry_name):
#     sqlite_connection = sqlite3.connect(db_path)
#     cursor = sqlite_connection.cursor()
#     query = """UPDATE `Entries` SET name = ? WHERE name = ?"""
#     cursor.execute(query, (new_entry_name, entry_name))
#     cursor.close()
#     sqlite_connection.commit()
#     sqlite_connection.close()


def complete_entry(entry_id: int or str):
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """UPDATE `Entries` SET is_completed = 1 WHERE id = ?"""
    cursor.execute(query, (entry_id,))
    cursor.close()
    sqlite_connection.commit()
    sqlite_connection.close()


def set_entry_note(entry_id: int or str, note_text: str):
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """UPDATE `Entries` SET note = ? WHERE id = ?"""
    cursor.execute(query, (note_text, entry_id,))
    cursor.close()
    sqlite_connection.commit()
    sqlite_connection.close()


def delete_entry(entry_id: int or str):
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """DELETE FROM `Entries` WHERE id = ? """
    cursor.execute(query, (entry_id,))
    cursor.close()
    sqlite_connection.commit()
    sqlite_connection.close()


def delete_entries(list_id: int or str):
    sqlite_connection = sqlite3.connect(db_path)
    cursor = sqlite_connection.cursor()
    query = """DELETE FROM `Entries` WHERE list_id = ? """
    cursor.execute(query, (list_id,))
    cursor.close()
    sqlite_connection.commit()
    sqlite_connection.close()
