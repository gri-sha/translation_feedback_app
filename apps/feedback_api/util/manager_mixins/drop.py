class DropMixin:
    """
    Mixin for dropping tables.
    
    Requires host class to provide:
    - transaction() -> Generator[sqlite3.Cursor, None, None]: Context manager for DB transactions
    """

    def drop_all_tables(self) -> bool:
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

    def clear_all_tables(self) -> bool:
        try:
            with self.transaction() as cursor:
                cursor.execute("TRUNCATE TABLE Rankings RESTART IDENTITY CASCADE")
                cursor.execute("TRUNCATE TABLE Translations RESTART IDENTITY CASCADE")
                cursor.execute("TRUNCATE TABLE Targets RESTART IDENTITY CASCADE")
                print("All table data cleared.")
                return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False
