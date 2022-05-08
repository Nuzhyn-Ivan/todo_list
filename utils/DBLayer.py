import os.path
import sqlite3

import utils.ConfigParser as config

database_path = config.get_option_value('db_path')
migrations_list = {
    1: '''ALTER TABLE `Entries` ADD COLUMN note TEXT;''',
}


# TODO update documentation, refactor DBLayer
def is_database_exist() -> bool:
    if os.path.exists(database_path):
        return True
    else:
        return False


def drop_database():
    """
    Drop database
    """
    if os.path.exists(database_path):
        os.remove(database_path)


def actualize_database():
    """
    Run database migrations if db state not actual. Create db if not exist.
    """
    if is_database_exist():
        run_migrations()
    else:
        create_database()


# TODO add feature to backup db and load from backup
# TODO default lists and entries - make it lang related
def create_database():
    sqlite_connection = sqlite3.connect(database_path)

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

    sqlite_create_entry_name_index = 'CREATE UNIQUE INDEX entry_name ON Entries(name);'

    sqlite_insert_default_lists = '''
    INSERT INTO 'Lists' ('name', 'order_id') VALUES ("Supermarket", 1 ), ("To Do", 2 ), ("Drug Store", 3 ), ("Movies to watch", 4 );
    '''
    sqlite_insert_default_entries = '''
    INSERT INTO 'Entries' ('list_id', 'name', 'frequency') VALUES (1, 'first', 1 ), (1, 'first2', 1 ), (1, 'first3', 1 ), (1, 'first4', 1 );
    '''

    cursor = sqlite_connection.cursor()
    try:

        # Create tables
        cursor.execute(sqlite_create_lists)
        cursor.execute(sqlite_create_entries)
        cursor.execute(sqlite_create_entry_name_index)
        cursor.execute(sqlite_create_entries_history)
        cursor.execute(sqlite_create_entries_source)

        # Insert default values
        cursor.execute(sqlite_insert_default_lists)
        cursor.execute(sqlite_insert_default_entries)

        cursor.close()
        sqlite_connection.commit()

    except sqlite3.Error as error:
        # todo add error handling - open error popup
        pass
    finally:
        sqlite_connection.close()


def run_migrations():
    # todo add try except
    current_db_version = int(config.get_option_value('db_version'))
    available_db_version = int(config.get_option_value('available_db_version'))
    if current_db_version == available_db_version:
        return
    else:
        sqlite_connection = sqlite3.connect(database_path)
        try:
            # Run all needed migrations
            for key, value in migrations_list.items():
                if key > current_db_version:
                    cursor = sqlite_connection.cursor()
                    cursor.execute(value)
                    cursor.close()
                    current_db_version = key

            sqlite_connection.commit()
            config.set_option_value('db_version', str(current_db_version))
        except sqlite3.Error as error:
            # todo add error handling - open error popup
            pass
        finally:
            sqlite_connection.close()


# Lists CRUD
def create_list(list_name: str, order_id: int) -> bool and sqlite3.Error:
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = "INSERT INTO 'Lists' ('name', 'order_id') VALUES (?, ? )"
    try:
        cursor.execute(query, (list_name, order_id))
        cursor.close()
        sqlite_connection.commit()
        return True, None
    except sqlite3.Error as error:
        # todo add error handling - open error popup
        return False, error
    finally:
        sqlite_connection.close()


def read_lists() -> list:
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT * FROM `Lists` ORDER BY order_id """
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        return records
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def read_last_list() -> list:
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = '''SELECT id, name FROM `Lists` ORDER BY id DESC LIMIT 1;'''
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        return records
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def get_list_name(list_id: int) -> str:
    # todo add try except
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT name FROM `Lists` where id = ? """
    try:
        cursor.execute(query, (list_id,))
        records = cursor.fetchall()
        cursor.close()
        return records[0][0]
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def get_list_id(list_name: str) -> int:
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT id FROM `Lists` where name = ? """
    try:
        cursor.execute(query, (list_name,))
        records = cursor.fetchall()
        cursor.close()
        list_id = records[0][0]
        return list_id
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def rename_list(list_name: str, new_list_name: str):
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = """UPDATE `Lists` SET name = ? WHERE name = ?"""
    try:
        cursor.execute(query, (new_list_name, list_name))
        cursor.close()
        sqlite_connection.commit()
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def delete_list_by_id(list_id: str):
    delete_entries(list_id)
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = """DELETE FROM `Lists` WHERE id = ? """
    try:
        cursor.execute(query, (list_id,))
        cursor.close()
        sqlite_connection.commit()
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


# Entries CRUD
def get_entry_name(entry_id: str) -> str:
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT name FROM `Entries` where id = ? """
    try:
        cursor.execute(query, (entry_id,))
        records = cursor.fetchall()
        cursor.close()
        return records[0][0]
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def get_entry_note(entry_id: str) -> str:
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT note FROM `Entries` where id = ? """
    try:
        cursor.execute(query, (entry_id,))
        records = cursor.fetchall()
        cursor.close()
        return '' if (records[0][0] is None) else records[0][0]
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def is_entry_exists(entry_name: str) -> bool:
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT * FROM `Entries` WHERE name = ?"""
    try:
        cursor.execute(query, (entry_name,))
        records = cursor.fetchall()
        cursor.close()
        return True if records else False
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def create_entry(list_id: int, entry_name: str):
    """
    Create entry OR set 'is_completed=1' if exist
    """
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    try:
        if is_entry_exists(entry_name):
            query = """UPDATE `Entries` SET list_id = ?, is_completed = 0, frequency =  frequency + 1  WHERE name = ?"""
            cursor.execute(query, (list_id, entry_name,))
        else:
            query = """INSERT INTO 'Entries' ( 'list_id', 'name', 'is_completed', 'created_date', 'frequency') VALUES (?, ?, 0, date(), 1)"""
            cursor.execute(query, (list_id, entry_name,))
        cursor.close()
        sqlite_connection.commit()
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def read_entries(list_id: int) -> list:
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT * FROM `Entries` WHERE list_id = ? and is_completed = 0"""
    try:
        cursor.execute(query, (list_id,))
        records = cursor.fetchall()
        cursor.close()
        return records
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def read_entries_history(list_id: int) -> list:
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT * FROM `Entries` WHERE list_id = ? and is_completed = 1"""
    try:
        cursor.execute(query, (list_id,))
        records = cursor.fetchall()
        cursor.close()
        return records
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def read_entries_by_name_part(list_id: int, name_part: str) -> list:
    max_suggestions_count = int(config.get_option_value('max_suggestions_count'))
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = '''SELECT name FROM `Entries` WHERE list_id = ? and name like ? and is_completed = 1 ORDER BY frequency DESC LIMIT ?;'''
    try:
        cursor.execute(query, (list_id, name_part + '%', max_suggestions_count))
        records = cursor.fetchall()
        cursor.close()
        return records
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def read_last_entry(list_id: int) -> list:
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = '''SELECT id, name FROM `Entries` WHERE list_id = ? ORDER BY id DESC LIMIT 1;'''
    try:
        cursor.execute(query, (list_id,))
        records = cursor.fetchall()
        cursor.close()
        return records
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def read_all_entries() -> list:
    # todo add docstring
    # todo add try except
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT * FROM `Entries` """
    try:
        cursor.execute(query, )
        records = cursor.fetchall()
        cursor.close()
        return records
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def read_entries_count(list_id: str) -> int:
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT COUNT(*) FROM `Entries` WHERE list_id = ?  and is_completed = 0"""
    try:
        cursor.execute(query, (int(list_id),))
        records = cursor.fetchall()
        cursor.close()
        return records[0][0]
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


# def rename_entry(entry_name, new_entry_name):
#     sqlite_connection = sqlite3.connect(database_path)
#     cursor = sqlite_connection.cursor()
#     query = """UPDATE `Entries` SET name = ? WHERE name = ?"""
#     try:
#         cursor.execute(query, (new_entry_name, entry_name))
#         cursor.close()
#         sqlite_connection.commit()
#     except sqlite3.Error as error:
#         pass
#         # todo add error handling - open error popup
#     finally:
#         sqlite_connection.close()

def complete_entry(entry_id: int):
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = """UPDATE `Entries` SET is_completed = 1 WHERE id = ?"""
    try:
        cursor.execute(query, (entry_id,))
        cursor.close()
        sqlite_connection.commit()
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def set_entry_note(entry_id: int, note_text: str):
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = """UPDATE `Entries` SET note = ? WHERE id = ?"""
    try:
        cursor.execute(query, (note_text, entry_id,))
        cursor.close()
        sqlite_connection.commit()
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def delete_entry(entry_id: int):
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = """DELETE FROM `Entries` WHERE id = ? """
    try:
        cursor.execute(query, (entry_id,))
        cursor.close()
        sqlite_connection.commit()
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def delete_entries(list_id: str):
    # todo add docstring
    # todo add try except
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = """DELETE FROM `Entries` WHERE list_id = ? """
    try:
        cursor.execute(query, (list_id,))
        cursor.close()
        sqlite_connection.commit()
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


# Sources CRUD
def create_source(source_name: str):
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    try:
        if not is_source_exist(source_name):
            query = """INSERT INTO 'EntriesSource' ( 'name') VALUES (?);"""
            cursor.execute(query, (source_name,))
        cursor.close()
        sqlite_connection.commit()
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def read_sources_by_name_part(list_id: int, name_part: str) -> list:
    max_suggestions_count = int(config.get_option_value('max_suggestions_count'))
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = '''SELECT EntriesSource.name FROM `EntriesHistory` INNER JOIN 'EntriesSource' on EntriesHistory.source_id = EntriesSource.id INNER JOIN  'Entries' on Entries.id = EntriesHistory.entry_id WHERE Entries.list_id = ? and EntriesSource.name like ? ORDER BY quantity DESC LIMIT ?;'''
    try:
        cursor.execute(query, (list_id, name_part + '%', max_suggestions_count))
        records = cursor.fetchall()
        cursor.close()
        return records
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


def is_source_exist(source_name: str):
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT id FROM `EntriesSource` WHERE name = ?;"""
    try:
        cursor.execute(query, (source_name,))
        source = cursor.fetchall()
        cursor.close()
        sqlite_connection.close()
        # todo replace with ternary
        if len(source) > 0:
            return True
        else:
            return False
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()

def get_source_id(source_name):
    # todo add docstring
    # todo add try except
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = '''SELECT id FROM `EntriesSource` WHERE name like ?;'''
    cursor.execute(query, (source_name + '%',))
    records = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return records[0][0]


# EntriesHistory CRUD
def create_entries_history(source_id: int, entry_id: int, price: float, quantity: int):
    """Create entry in EntriesHistory or update if exist"""
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    try:
        if is_entry_history_exists(source_id, entry_id, price):
            query = """UPDATE `EntriesHistory` SET quantity = quantity + ?, special_price = 0, WHERE entry_id = ? and source_id = ? and price = ? """
            cursor.execute(query, (quantity, entry_id, source_id, price))
        else:
            query = """INSERT INTO 'EntriesHistory' ('entry_id', 'source_id', 'price', 'quantity', 'special_price') VALUES (?, ?, ?, ?, 0)"""
            cursor.execute(query, (entry_id, source_id, price, quantity,))
        cursor.close()
        sqlite_connection.commit()
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()


# todo add annotation
def is_entry_history_exists(source_id, entry_id, price):
    sqlite_connection = sqlite3.connect(database_path)
    cursor = sqlite_connection.cursor()
    query = """SELECT * FROM `EntriesHistory` WHERE source_id = ? and entry_id = ? and price = ?;"""
    try:
        cursor.execute(query, (source_id, entry_id, price,))
        source = cursor.fetchall()
        cursor.close()
        # todo replace with ternary
        if len(source) > 0:
            return True
        else:
            return False
    except sqlite3.Error as error:
        pass
        # todo add error handling - open error popup
    finally:
        sqlite_connection.close()
