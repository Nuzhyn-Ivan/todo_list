import os.path
import sqlite3
from typing import Tuple, List, Union

from Models.utils import ConfigParser as config

database_path = config.get_option_value('db_path')
migrations_list = {
    1: '''ALTER TABLE `Entries` ADD COLUMN note TEXT;''',
}


def execute_query(query, *args):
    """
    Execute given query with given params
    :param query: SQL query
    :param args: params for a query
    :type args: tuple
    :return: result of query execution
    """
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    try:
        cursor.execute(query, *args)
        records = cursor.fetchall()
        sqlite_connection.commit()
        return records
    except sqlite3.Error as error:
        print(f"Error executing query: {error}")
        # todo add error handling - open error popup
    finally:
        cursor.close()
        sqlite_connection.close()


# TODO update documentation, refactor DBLayer(try to extract sqlite part from def)
def database_exist() -> bool:
    return os.path.exists(database_path)


def drop_database():
    """
    Drop database
    """
    if database_exist():
        os.remove(database_path)


def actualize_database():
    """
    Run database migrations if db state not actual. Create db if not exist.
    """
    if database_exist():
        run_migrations()
    else:
        create_database()


# TODO add feature to backup db and load from backup
# TODO default lists and entries - make it lang related
def create_database():
    """
    Create the database tables and insert default values.
    """
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
    note TEXT,
    FOREIGN KEY(list_id) REFERENCES Lists(id));
    '''
    sqlite_create_entries_source = '''
    CREATE TABLE EntriesSource (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL);
    '''
    sqlite_create_entries_history = '''
    CREATE TABLE EntriesHistory (
    entry_id INTEGER,
    source_id INTEGER,
    price INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    special_price INTEGER NOT NULL,
    PRIMARY KEY (entry_id, source_id, price),
    UNIQUE(entry_id, source_id, price),
    FOREIGN KEY(entry_id) REFERENCES Entries(id),
    FOREIGN KEY(source_id) REFERENCES EntriesSource(id));
    '''
    sqlite_create_entry_name_index = '''CREATE UNIQUE INDEX entry_name ON Entries(name);'''
    sqlite_insert_default_lists = '''
    INSERT INTO 'Lists' ('name', 'order_id') VALUES ("Supermarket", 1 ), ("To Do", 2 ), ("Drug Store", 3 ), ("Movies to watch", 4 );
    '''
    sqlite_insert_default_entries = '''
    INSERT INTO 'Entries' ('list_id', 'name', 'frequency') VALUES (1, 'first', 1 ), (1, 'first2', 1 ), (1, 'first3', 1 ), (1, 'first4', 1 );
    '''

    # Create tables
    execute_query(sqlite_create_lists)
    execute_query(sqlite_create_entries)
    execute_query(sqlite_create_entry_name_index)
    execute_query(sqlite_create_entries_history)
    execute_query(sqlite_create_entries_source)

    # Insert default values
    execute_query(sqlite_insert_default_lists)
    execute_query(sqlite_insert_default_entries)


def run_migrations():
    # todo add try except
    current_db_version = int(config.get_option_value('db_version'))
    available_db_version = int(config.get_option_value('available_db_version'))
    if current_db_version == available_db_version:
        return
    else:
        for key, query in migrations_list.items():
            if key > current_db_version:
                execute_query(query)
                current_db_version = key
        config.set_option_value('db_version', str(current_db_version))


# Lists CRUD
def create_list(list_name: str, order_id: int):
    query = '''INSERT INTO 'Lists' ('name', 'order_id') VALUES (?, ? )'''
    execute_query(query, (list_name, order_id))


def read_lists() -> list[tuple]:
    """
    Select all entries from Lists table
    :return: [id, name, order_id, created_date]
    """
    query = '''SELECT * FROM `Lists` ORDER BY order_id'''
    records = execute_query(query)
    return records


def read_last_list() -> list[tuple]:
    query = '''SELECT id, name FROM `Lists` ORDER BY id DESC LIMIT 1'''
    records = execute_query(query)
    return records[0]


def get_list_name(list_id: str) -> str:
    query = '''SELECT name FROM `Lists` WHERE id = ?'''
    records = execute_query(query, (list_id,))
    list_name = records[0][0]
    return list_name


def get_list_id(list_name: str) -> int:
    query = '''SELECT id FROM `Lists` WHERE name = ?'''
    records = execute_query(query, (list_name,))
    list_id = records[0][0]
    return list_id


def rename_list(list_name: str, new_list_name: str):
    query = '''UPDATE `Lists` SET name = ? WHERE name = ?'''
    execute_query(query, (new_list_name, list_name,))


def delete_list_by_id(list_id: str or int):
    delete_entries(list_id)
    query = '''DELETE FROM `Lists` WHERE id = ? '''
    execute_query(query, (list_id,))


# Entries CRUD
def get_entry_name(entry_id: str) -> str:
    query = '''SELECT name FROM `Entries` WHERE id = ? '''
    records = execute_query(query, (entry_id,))
    return records[0][0]


def get_entry_note(entry_id: str) -> str:
    query = '''SELECT note FROM `Entries` WHERE id = ? '''
    records = execute_query(query, (entry_id,))
    return '' if (records[0][0] is None) else records[0][0]


def entry_exists(entry_name: str) -> bool:
    query = '''SELECT * FROM `Entries` WHERE name = ?'''
    records = execute_query(query, (entry_name,))
    return bool(records)


def create_entry(list_id: int, entry_name: str):
    """
    Create entry OR set 'is_completed=1' if exist
    """
    if entry_exists(entry_name):
        query = '''
        UPDATE `Entries` 
        SET list_id = ?, is_completed = 0, frequency =  frequency + 1  
        WHERE name = ?'''
        execute_query(query, (list_id, entry_name,))

    else:
        query = '''
        INSERT INTO 'Entries' ( 'list_id', 'name', 'is_completed', 'created_date', 'frequency') 
        VALUES (?, ?, 0, date(), 1)
        '''
        execute_query(query, (list_id, entry_name,))


def read_entries(list_id: str, completed: bool = False) -> list[tuple]:
    query = '''SELECT * FROM `Entries` WHERE list_id = ? and is_completed = ?'''
    records = execute_query(query, (list_id, completed))
    return records


def read_entries_by_name_part(list_id: str, name_part: str, limit: int) -> list[tuple]:
    query = '''
    SELECT name 
    FROM `Entries` 
    WHERE list_id = ? and name like ? and is_completed = 1 
    ORDER BY frequency DESC LIMIT ?;
    '''
    records = execute_query(query, (list_id, f'{name_part}%', limit))
    return records


def read_last_entry(list_id: str) -> list[tuple]:
    query = '''SELECT id, name FROM `Entries` WHERE list_id = ? ORDER BY id DESC LIMIT 1;'''
    records = execute_query(query, (list_id,))
    return records


def read_all_entries() -> list[tuple]:
    query = '''SELECT * FROM `Entries` '''
    records = execute_query(query, )
    return records


def read_entries_count(list_id: str) -> int:
    query = '''SELECT COUNT(*) FROM `Entries` WHERE list_id = ? and is_completed = 0'''
    records = execute_query(query, (list_id,))
    return records[0][0]


def complete_entry(entry_id: str):
    query = '''UPDATE `Entries` SET is_completed = 1 WHERE id = ?'''
    execute_query(query, (entry_id,))


def set_entry_note(entry_id: str, note_text: str):
    query = '''UPDATE `Entries` SET note = ? WHERE id = ?'''
    execute_query(query, (note_text, entry_id,))


def delete_entry(entry_id: str):
    query = '''DELETE FROM `Entries` WHERE id = ? '''
    execute_query(query, (entry_id,))


def delete_entries(list_id: str):
    query = '''DELETE FROM `Entries` WHERE list_id = ?'''
    execute_query(query, (list_id,))


# Sources CRUD
def create_source(source_name: str):
    # todo - fix, it doesnt work
    if not source_exist(source_name):
        query = '''INSERT INTO 'EntriesSource' ('name') VALUES (?)'''
        execute_query(query, (source_name,))


def read_sources_by_name_part(list_id: str, name_part: str, limit: int) -> list[tuple]:
    query = '''
    SELECT EntriesSource.name 
    FROM `EntriesHistory` 
    INNER JOIN 'EntriesSource' on EntriesHistory.source_id = EntriesSource.id 
    INNER JOIN  'Entries' on Entries.id = EntriesHistory.entry_id 
    WHERE Entries.list_id = ? and EntriesSource.name LIKE ? 
    ORDER BY quantity DESC LIMIT ?
    '''
    records = execute_query(query, (list_id, f'{name_part}%', limit))
    return records


def source_exist(source_name: str) -> bool:
    query = '''SELECT id FROM `EntriesSource` WHERE name = ?'''
    records = execute_query(query, (source_name,))
    return bool(records)


def get_source_id(source_name: str) -> str:
    query = '''SELECT id FROM `EntriesSource` WHERE name like ?'''
    records = execute_query(query, (f'{source_name}%',))
    return records[0][0]


# EntriesHistory CRUD
def create_entries_history(
        source_id: Union[int, str],
        entry_id: Union[int, str],
        price: float,
        quantity: Union[int, str]):
    """Create entry in EntriesHistory or update if exist"""
    if entry_history_exists(source_id, entry_id, price):
        query = '''
        UPDATE `EntriesHistory` 
        SET quantity = quantity + ?, special_price = 0, 
        WHERE entry_id = ? and source_id = ? and price = ? 
        '''
        execute_query(query, (quantity, entry_id, source_id, price))
    else:
        query = '''
        INSERT INTO 'EntriesHistory' ('entry_id', 'source_id', 'price', 'quantity', 'special_price') 
        VALUES (?, ?, ?, ?, 0)
        '''
        execute_query(query, (entry_id, source_id, price, quantity,))


# todo add annotation
def entry_history_exists(source_id, entry_id, price):
    query = '''SELECT * FROM `EntriesHistory` WHERE source_id = ? and entry_id = ? and price = ?'''
    records = execute_query(query, (source_id, entry_id, price,))
    return bool(records)

