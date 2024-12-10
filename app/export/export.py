import pymysql
import sqlite3
import json
import logging
import sys
import getpass
import os
from datetime import datetime
from typing import List, Dict, Any, Union
from contextlib import closing


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

MYSQL_CONFIG = {"host": "localhost", "user": "root", "database": "marzban"}
SQLITE_PATH = "/var/lib/marzban/db.sqlite3"
TABLES = ["users", "jwt", "admins"]
OUTPUT_FILE = "marzban.json"
MAX_ATTEMPTS = 3
P1 = "VLESS"
P2 = "VMess"


def get_protocol_type() -> None:
    """Prompt the user to select the protocol type."""
    while True:
        print(
            "Select which protocol UUID you want to transfer!\n If the user doesn't have a UUID for VLESS, then a VMess UUID will be used. If there is nothing at all, then the UUID will be null."
        )
        type = int(input("\n1) VLESS\n2) VMess \n\nEnter protocol type number: "))
        match type:
            case 1:
                print("Selected protocol: VLESS")
                return "VLESS"
            case 2:
                print("Selected protocol: VMess")
                return "VMess"
            case _:
                logging.error("Invalid input. Please enter 1 or 2.")


def get_database_type() -> str:
    """Prompt the user to select the database type."""
    while True:
        db_type = int(input("\n1) Mysql\n2) Sqlite \n\nEnter database type number: "))
        if db_type in [1, 2]:
            return "mysql" if db_type == 1 else "sqlite"
        logging.error("Invalid input. Please enter 'mysql' or 'sqlite'.")


def get_and_verify_mysql_password() -> str:
    """Prompt for the MySQL database password and verify it."""
    for attempt in range(MAX_ATTEMPTS):
        password = getpass.getpass("Enter MySQL database password: ")
        try:
            with closing(pymysql.connect(**MYSQL_CONFIG, password=password)):
                logging.info("MySQL password verified successfully.")
                return password
        except pymysql.Error:
            remaining = MAX_ATTEMPTS - attempt - 1
            if remaining > 0:
                logging.error(f"Incorrect password. {remaining} attempts remaining.")
            else:
                logging.error("Maximum password attempts reached. Exiting.")
                sys.exit(1)


def get_database_connection(
    db_type: str, password: str = None
) -> Union[pymysql.connections.Connection, sqlite3.Connection]:
    """Create and return a database connection."""
    try:
        if db_type == "mysql":
            return pymysql.connect(**MYSQL_CONFIG, password=password)
        else:  # sqlite
            if not os.path.exists(SQLITE_PATH):
                logging.error(f"SQLite database file not found at {SQLITE_PATH}")
                sys.exit(1)
            return sqlite3.connect(SQLITE_PATH)
    except (pymysql.Error, sqlite3.Error) as e:
        logging.error(f"Error connecting to {db_type} database: {e}")
        sys.exit(1)


def fetch_table_data(
    cursor: Union[pymysql.cursors.Cursor, sqlite3.Cursor], table_name: str
) -> List[Dict[str, Any]]:
    """Fetch data from a specific table."""
    try:
        if table_name == "users":
            cursor.execute(
                f"SELECT users.*, COALESCE( JSON_EXTRACT(T1.settings, '$.id'), JSON_EXTRACT(T2.settings, '$.id') ) AS uuid, CASE WHEN JSON_EXTRACT(T1.settings, '$.id') IS NOT NULL THEN '{P1}' WHEN JSON_EXTRACT(T2.settings, '$.id') IS NOT NULL THEN '{P2}' ELSE NULL END AS proxy_type FROM users LEFT JOIN proxies AS T1 ON users.id = T1.user_id AND T1.type = '{P1}' LEFT JOIN proxies AS T2 ON users.id = T2.user_id AND T2.type = '{P2}';"
            )
        else:
            cursor.execute(f"SELECT * FROM {table_name}")
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except (pymysql.Error, sqlite3.Error) as e:
        logging.error(f"Error fetching data from table {table_name}: {e}")
        return []


def serialize_data(obj: Any) -> Any:
    """Convert specific data types to JSON-serializable format."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def export_to_json(data: Dict[str, List[Dict[str, Any]]], output_file: str) -> None:
    """Save data to a JSON file."""
    try:
        with open(output_file, "w", encoding="utf-8") as json_file:
            json.dump(
                data, json_file, ensure_ascii=False, indent=4, default=serialize_data
            )
        logging.info(f"Data successfully exported to -> '{output_file}'")
    except IOError as e:
        logging.error(f"Error writing JSON file: {e}")


def display_statistics(database_data: Dict[str, List[Dict[str, Any]]]) -> None:
    """Display the number of users and admins."""
    user_count = len(database_data.get("users", []))
    admin_count = len(database_data.get("admins", []))

    logging.info(f"Number of 'ADMINS' extracted: {admin_count}")
    logging.info(f"Number of 'USERS' extracted: {user_count}")


def main():
    """Main function of the program."""
    db_type = get_database_type()
    password = get_and_verify_mysql_password() if db_type == "mysql" else None
    database_data = {}

    global P1
    P1 = get_protocol_type()
    global P2
    P2 = "VMess" if P1 == "VLESS" else "VLESS"

    with closing(get_database_connection(db_type, password)) as connection:
        cursor = connection.cursor()
        for table in TABLES:
            logging.info(f"Extracting data from table {table}...")
            database_data[table] = fetch_table_data(cursor, table)
        cursor.close()

    display_statistics(database_data)
    export_to_json(database_data, OUTPUT_FILE)


if __name__ == "__main__":
    main()
