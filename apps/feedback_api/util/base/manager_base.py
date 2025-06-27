import sqlite3
import os
from contextlib import contextmanager
from typing import Generator
from util.config import get_config_db


class DBManagerBase:
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

    @contextmanager
    def read_only(self) -> Generator[sqlite3.Cursor, None, None]:
        """
        Context manager for read-only database access.

        Ensures:
        - Connection is properly opened and closed
        - No transaction is committed
        - Cursor can be used for read operations

        Usage:
            with db_manager.read_only() as cursor:
                cursor.execute("SELECT * FROM ...")

        Yields:
            sqlite3.Cursor: Database cursor for executing read queries

        Raises:
            sqlite3.Error: For database-related errors
            ValueError: For invalid working directory
        """
        self._validate_working_directory()

        conn = None
        cursor = None

        try:
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)  # mode=ro via URI to enforce read-only access
            cursor = conn.cursor()
            yield cursor
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Read-only query failed: {e}") from e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
