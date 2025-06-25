import sqlite3
import os
import json
from contextlib import contextmanager
from typing import Generator
from util.config import get_config_db


class DBManager:
    def __init__(self):
        self.config = get_config_db()
        self.data_dir = self.config["folder"]
        self.db_name = self.config["name"]
        self.root_dir = self.config["root"]
        self.example_dir = self.config["example"]

    @property
    def db_path(self) -> str:
        """Get full path to database file."""
        return os.path.join(self.data_dir, self.db_name)

    def _validate_working_directory(self) -> None:
        """Validate current working directory."""
        cwd = os.getcwd()
        if not cwd.endswith(self.root_dir):
            raise ValueError(f"Expected cwd to end with {self.root_dir}, got {cwd}")

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Cursor, None, None]:
        """
        Context manager for database transactions.

        Ensures that:
        - Connection is properly opened and closed
        - Transaction is committed on success
        - Transaction is rolled back on any exception
        - Resources are always cleaned up

        Usage:
            with db_manager.transaction() as cursor:
                cursor.execute("INSERT INTO ...")
                cursor.execute("UPDATE ...")
                # Automatically committed if no exception

        Yields:
            sqlite3.Cursor: Database cursor for executing queries

        Raises:
            sqlite3.Error: For database-related errors
            ValueError: For invalid working directory
        """
        self._validate_working_directory()

        conn = None
        cursor = None

        try:
            # Open connection and begin transaction
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            conn.execute("BEGIN TRANSACTION")

            # Yield cursor for use in with block
            yield cursor

            # If we get here, no exception occurred - commit the transaction
            conn.commit()

        except sqlite3.Error as e:
            # Database error - rollback transaction
            if conn:
                try:
                    conn.rollback()
                except sqlite3.Error as rollback_error:
                    # Log rollback failure but raise original error
                    print(f"Warning: Rollback failed: {rollback_error}")
            raise sqlite3.Error(f"Transaction failed: {e}") from e

        except Exception as e:
            # Non-database error - still rollback transaction
            if conn:
                try:
                    conn.rollback()
                except sqlite3.Error as rollback_error:
                    print(
                        f"Warning: Rollback failed during error handling: {rollback_error}"
                    )
            raise

        finally:
            # Close connection and cursor
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def initialize_schema(self) -> bool:
        try:
            os.makedirs(self.data_dir, exist_ok=True)

            with self.transaction() as cursor:
                # Drop existing tables
                cursor.execute("DROP TABLE IF EXISTS Rankings")
                cursor.execute("DROP TABLE IF EXISTS Translations")
                cursor.execute("DROP TABLE IF EXISTS Targets")

                # Create tables
                cursor.execute(
                    """
                    CREATE TABLE Targets (
                        id INTEGER PRIMARY KEY,
                        target TEXT NOT NULL,
                        context1 TEXT NOT NULL,
                        context2 TEXT NOT NULL
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE Translations (
                        id INTEGER PRIMARY KEY,
                        targetId INTEGER NOT NULL,
                        translation TEXT NOT NULL,
                        model TEXT NOT NULL,
                        FOREIGN KEY(targetId) REFERENCES Targets(id)
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE Rankings (
                        id INTEGER PRIMARY KEY,
                        translationId INTEGER NOT NULL,
                        evalId INTEGER NOT NULL,
                        rank INTEGER,
                        discarded BOOLEAN,
                        FOREIGN KEY(translationId) REFERENCES Translations(id)
                    )
                """
                )

            print("Database initialized successfully.")
            return True

        except Exception as e:
            print(f"Error initializing database: {e}")
            return False

    def drop_all_tables(self):
        try:
            with self.transaction() as cursor:
                cursor.execute("DROP TABLE IF EXISTS Rankings")
                cursor.execute("DROP TABLE IF EXISTS Translations")
                cursor.execute("DROP TABLE IF EXISTS Targets")
                print("All tables dropped.")
                return True
        except Exception as e:
            print(f"Error dropping database: {e}")
            return False

    def load_example_data(
        self, include_translations: bool = True, include_rankings: bool = True
    ) -> bool:
        try:
            with open(self.example_dir) as f:
                example_data = json.load(f)

            with self.transaction() as cursor:
                # Targets
                for target in example_data["targets"]:
                    cursor.execute(
                        "INSERT INTO Targets(id, context1, target, context2) VALUES (?, ?, ?, ?)",
                        (
                            target["id"],
                            target["context1"],
                            target["target"],
                            target["context2"],
                        ),
                    )

                # Translations if enabled
                if include_translations:
                    for translation in example_data["translations"]:
                        cursor.execute(
                            "INSERT INTO Translations(id, targetId, translation, model) VALUES (?, ?, ?, ?)",
                            (
                                translation["id"],
                                translation["targetId"],
                                translation["translation"],
                                translation["model"],
                            ),
                        )

                # Rankings if enabled
                if include_rankings:
                    for ranking in example_data["rankings"]:
                        cursor.execute(
                            "INSERT INTO Rankings(id, evalId, translationId, rank, discarded) VALUES (?, ?, ?, ?, ?)",
                            (
                                ranking["id"],
                                ranking["evalId"],
                                ranking["translationId"],
                                ranking["rank"],
                                ranking["discarded"],
                            ),
                        )

            print("Example data loaded successfully.")
            return True

        except Exception as e:
            print(f"Error loading example data: {e}")
            return False
