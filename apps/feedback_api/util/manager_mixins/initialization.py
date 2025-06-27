import os
import json


class InitMixin:
    """
    Mixin for initializing the DB.
    
    Requires host class to provide:
    - transaction() -> Generator[sqlite3.Cursor, None, None]: Context manager for DB transactions
    - data_dir: str: Path to directory where database should be stored
    - example_dir: str: Path to example data JSON file
    """

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
                        numEvals INTEGER NOT NULL DEFAULT 0,
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

                # Performance indexes
                cursor.execute(
                    "CREATE INDEX idx_translations_target_id ON Translations(targetId)"
                )
                cursor.execute(
                    "CREATE INDEX idx_translations_num_evals ON Translations(numEvals, id)"
                )
                cursor.execute(
                    "CREATE INDEX idx_rankings_translation_id ON Rankings(translationId)"
                )
                cursor.execute(
                    "CREATE INDEX idx_rankings_eval_id ON Rankings(evalId)"
                )
                cursor.execute(
                    "CREATE INDEX idx_translations_evals_target ON Translations(numEvals, targetId, id)"
                )

                # Triggers to maintain numEvals consistency
                cursor.execute(
                    """
                    CREATE TRIGGER update_translation_evals_insert
                    AFTER INSERT ON Rankings
                    FOR EACH ROW
                    BEGIN
                        UPDATE Translations 
                        SET numEvals = (
                            SELECT COUNT(*) 
                            FROM Rankings 
                            WHERE translationId = NEW.translationId
                        )
                        WHERE id = NEW.translationId;
                    END
                """
                )

                cursor.execute(
                    """
                    CREATE TRIGGER update_translation_evals_delete
                    AFTER DELETE ON Rankings
                    FOR EACH ROW
                    BEGIN
                        UPDATE Translations 
                        SET numEvals = (
                            SELECT COUNT(*) 
                            FROM Rankings 
                            WHERE translationId = OLD.translationId
                        )
                        WHERE id = OLD.translationId;
                    END
                """
                )

            print("Database schema initialized successfully.")
            return True

        except Exception as e:
            print(f"Error initializing database: {e}")
            return False

    def load_example_data(
        self,
        include_translations: bool = True,
        include_rankings: bool = True,
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
                            "INSERT INTO Translations(id, targetId, translation, model, numEvals) VALUES (?, ?, ?, ?, ?)",
                            (
                                translation["id"],
                                translation["targetId"],
                                translation["translation"],
                                translation["model"],
                                translation["numEvals"],
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
