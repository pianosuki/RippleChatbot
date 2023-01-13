import sqlite3, os, json
from src.logger import Logger

class DatabaseManager:
    def __init__(self, db_path):
        # Define the Logger
        self.logger = Logger(self.__class__.__name__)

        # Create the directory for the db file if it doesn't already exist
        os.makedirs(os.path.dirname(db_path), exist_ok = True)

        # Set up the connection and cursor objects
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

        # Load database structure configuration
        with open("config/schema.json", "r") as schema:
            self.schema = json.load(schema)

        # Migrate database
        self.migrate()

    def migrate(self):
        # Create each table 1 by 1 based on schema
        for table in self.schema["tables"]:

            # Define the table name
            table_name = table["name"]

            # Compose the definition for the columns
            column_def = self.get_column_def(table["columns"])

            # Compose the definition for foreign keys if any
            foreign_key_def = self.get_foreign_key_def(table["foreign_keys"]) if "foreign_keys" in table else None

            # Send definitions to be constructed into a SQLite command to create the table with
            self.create_table(table_name, column_def, foreign_key_def)

    def get_column_def(self, columns):
        column_defs = []

        # Iterate through each column in schema to return a formatted SQLite-compatable string
        for column in columns:
            column_defs.append(self.format_column_def(**column))

        # Join all individual column definition strings into one string and return it
        column_def = ", ".join(column_defs)
        return column_def

    def format_column_def(self, name, type, **kwargs):
        column_name = name
        column_type = type
        column_constraints = []

        # Handle any contraints specified in the schema
        for key, value in kwargs.items():
            match key:
                case "primary_key":
                    if value: column_constraints.append("PRIMARY KEY")
                case "nullability":
                    if not value: column_constraints.append("NOT NULL")
                case "unique":
                    if value: column_constraints.append("UNIQUE")
                case "auto_increment":
                    if value: column_constraints.append("AUTOINCREMENT")
                # TO-DO: add more cases

        # Combine constraints
        column_constraint = " ".join(column_constraints)

        # Return a formatted SQLite-compatable string piece
        return "{0} {1} {2}".format(column_name, column_type, column_constraint).rstrip()

    def get_foreign_key_def(self, foreign_keys):
        foreign_key_defs = []

        # Iterate through each foreign key in schema to return a formatted SQLite-compatable string
        for foreign_key in foreign_keys:
            foreign_key_defs.append(self.format_foreign_key_def(**foreign_key))

        # Join all individual foreign key definition strings into one string and return it
        foreign_key_def = ", ".join(foreign_key_defs)
        return foreign_key_def

    def format_foreign_key_def(self, column, table, reference, **kwargs):
        child_key = column
        parent_table = table
        parent_key = reference
        clause_actions = []

        # Handle any action clauses specified in the schema
        for key, value in kwargs.items():
            match key:
                case "on_update":
                    clause_actions.append("ON UPDATE {}".format(value.upper()))
                case "on_delete":
                    clause_actions.append("ON DELETE {}".format(value.upper()))

        # Combine clauses
        action_clause = " ".join(clause_actions)

        # Return a formatted SQLite-compatable string piece
        return "FOREIGN KEY ({0}) REFERENCES {1} ({2}) {3}".format(child_key, parent_table, parent_key, clause_actions).rstrip()

    def close(self):
        self.connection.close()

    def create_table(self, table_name, column_def, foreign_key_def = None):
        command = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_def})"

        # If foreign keys are defined, then add them to the SQLite command
        if not foreign_key_def is None:
            command += ", {}".format(foreign_key_def)

        self.cursor.execute(command)
        self.connection.commit()

    def drop_table(self, table_name):
        command = f"DROP TABLE {table_name}"
        self.cursor.execute(command)
        self.connection.commit()

    def add_column(self, table_name, column_def, foreign_key_def = None):
        command = f"ALTER TABLE {table_name} ADD COLUMN ({column_def})"

        # If foreign keys are defined, then add them to the SQLite command
        if not foreign_key_def is None:
            command += ", {}".format(foreign_key_def)

        self.cursor.execute(command)
        self.connection.commit()

    def user_exists(self, user_id):
        # Check if the user's id exists in database
        command = "SELECT * FROM users WHERE id = ?"
        args = [(user_id,)]
        self.cursor.execute(command, *args)

        # Return the result to be evaluated as True or False
        return self.cursor.fetchone()

    def add_user(self, user_id):
        # If the user doesn't already exist, then add them
        if not self.user_exists(user_id):
            command = "INSERT INTO users (id, auto_beatconnect) VALUES (?, ?)"
            args = [(user_id, self.schema["defaults"]["users"]["auto_beatconnect"])]
            self.cursor.execute(command, *args)
            self.connection.commit()

            # Log the addition
            self.logger.log(f"Added user '{user_id}'")

    def update_user(self, user_id, column, value):
        # If the user exists, then proceed with the update
        if self.user_exists(user_id):
            command = f"UPDATE users SET {column} = ? WHERE id = ?"
            args = [(value, user_id)]
            self.cursor.execute(command, *args)
            self.connection.commit()

            # Log the update
            self.logger.log(f"Updated preference '{column}' to '{value}' for user '{user_id}'")
        else:
            # Add the user then recurse
            self.add_user(user_id)
            self.update_user(user_id, column, value)

    def get_user_column(self, user_id, column):
        # If the user exists, then proceed with the column retrieval
        if self.user_exists(user_id):
            command = f"SELECT {column} FROM users WHERE id = ?"
            args = [(user_id,)]
            self.cursor.execute(command, *args)
            self.connection.commit()
        else:
            # Add the user then recurse
            self.add_user(user_id)
            self.get_user_column(user_id, column)

        # Return the value of the column
        return self.cursor.fetchone()[0]
