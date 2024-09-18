import sqlite3
import os
import json
from typing import Any

from .logger import Logger


class DatabaseManager:
    def __init__(self, db_path: str):
        self.logger = Logger(self.__class__.__name__)

        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

        with open("config/schema.json", "r") as schema:
            self.schema = json.load(schema)

        self.create_database()

    def create_database(self):
        for table in self.schema["tables"]:

            table_name = table["name"]
            column_def = self.get_column_def(table["columns"])
            foreign_key_def = self.get_foreign_key_def(table["foreign_keys"]) if "foreign_keys" in table else None

            self.create_table(table_name, column_def, foreign_key_def)

    def get_column_def(self, columns: list[dict]) -> str:
        column_defs = []

        for column in columns:
            column_name = column["name"]
            column_type = column["type"]
            column_defs.append(self.format_column_def(column_name=column_name, column_type=column_type, **column))

        column_def = ", ".join(column_defs)
        return column_def

    @staticmethod
    def format_column_def(column_name: str, column_type: str, **kwargs) -> str:
        column_name = column_name
        column_type = column_type
        column_constraints = []

        for key, value in kwargs.items():
            match key:
                case "primary_key":
                    if value:
                        column_constraints.append("PRIMARY KEY")
                case "nullability":
                    if not value:
                        column_constraints.append("NOT NULL")
                case "unique":
                    if value:
                        column_constraints.append("UNIQUE")
                case "auto_increment":
                    if value:
                        column_constraints.append("AUTOINCREMENT")

        column_constraint = " ".join(column_constraints)

        return "{0} {1} {2}".format(column_name, column_type, column_constraint).rstrip()

    def get_foreign_key_def(self, foreign_keys: list[dict]):
        foreign_key_defs = []

        for foreign_key in foreign_keys:
            foreign_key_defs.append(self.format_foreign_key_def(**foreign_key))

        foreign_key_def = ", ".join(foreign_key_defs)
        return foreign_key_def

    @staticmethod
    def format_foreign_key_def(column: str, table: str, reference: str, **kwargs):
        child_key = column
        parent_table = table
        parent_key = reference
        clause_actions = []

        for key, value in kwargs.items():
            match key:
                case "on_update":
                    clause_actions.append("ON UPDATE {}".format(value.upper()))
                case "on_delete":
                    clause_actions.append("ON DELETE {}".format(value.upper()))

        action_clause = " ".join(clause_actions)

        return "FOREIGN KEY ({0}) REFERENCES {1} ({2}) {3}".format(child_key, parent_table, parent_key, action_clause).rstrip()

    def close(self):
        self.connection.close()

    def create_table(self, table_name: str, column_def: str, foreign_key_def: str = None):
        command = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_def})"

        if foreign_key_def is not None:
            command += ", {}".format(foreign_key_def)

        self.cursor.execute(command)
        self.connection.commit()

    def drop_table(self, table_name: str):
        command = f"DROP TABLE {table_name}"

        self.cursor.execute(command)
        self.connection.commit()

    def add_column(self, table_name: str, column_def: str, foreign_key_def: str = None):
        command = f"ALTER TABLE {table_name} ADD COLUMN ({column_def})"

        if foreign_key_def is not None:
            command += ", {}".format(foreign_key_def)

        self.cursor.execute(command)
        self.connection.commit()

    def user_exists(self, user_id: int) -> Any:
        command = "SELECT * FROM users WHERE id = ?"
        args = [(user_id,)]

        self.cursor.execute(command, *args)

        return self.cursor.fetchone()

    def add_user(self, user_id: int):
        if not self.user_exists(user_id):
            command = "INSERT INTO users (id, auto_beatconnect) VALUES (?, ?)"
            args = [(user_id, self.schema["defaults"]["users"]["auto_beatconnect"])]

            self.cursor.execute(command, *args)
            self.connection.commit()

            self.logger.log(f"Added user '{user_id}'")

    def update_user(self, user_id: int, column: str, value: Any):
        if self.user_exists(user_id):
            command = f"UPDATE users SET {column} = ? WHERE id = ?"
            args = [(value, user_id)]

            self.cursor.execute(command, *args)
            self.connection.commit()

            self.logger.log(f"Updated preference '{column}' to '{value}' for user '{user_id}'")
        else:
            self.add_user(user_id)
            self.update_user(user_id, column, value)

    def get_user_column(self, user_id: int, column: str) -> Any:
        if self.user_exists(user_id):
            command = f"SELECT {column} FROM users WHERE id = ?"
            args = [(user_id,)]

            self.cursor.execute(command, *args)
            self.connection.commit()
        else:
            self.add_user(user_id)
            self.get_user_column(user_id, column)

        return self.cursor.fetchone()[0]
