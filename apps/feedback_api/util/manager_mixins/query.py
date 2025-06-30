from typing import Optional


class QueryMixin:
    """
    Mixin for running specific queries.

    Requires host class to provide:
    - transaction() -> Generator[sqlite3.Cursor, None, None]: Context manager for DB transactions
    """

    def get_least_evaluated_translation(self) -> Optional[dict]:
        try:
            with self.read_only() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        id,
                        targetId,
                        translation,
                        model,
                        numEvals
                    FROM Translations
                    ORDER BY numEvals ASC, id ASC
                    LIMIT 1
                """
                )

                result = cursor.fetchone()
                print(result)
                return self._translation_to_dict(result) if result else None

        except Exception as e:
            print(f"Error getting least evaluated translation: {e}")
            return None

    def add_evaluation(self, options_ranking: list[dict]) -> bool:
        try:
            self._validate_rankings(options_ranking)
            new_eval_id = self._get_new_eval_id()
            with self.transaction() as cursor:
                for eval in options_ranking:
                    cursor.execute(
                        "INSERT INTO Rankings (translationId, evalId, rank, discarded) VALUES (?, ?, ?, ?)",
                        (
                            eval["translationId"],
                            new_eval_id,
                            eval["rank"],
                            eval["discarded"],
                        ),
                    )
            print("Evaluation added")
            return True
        except Exception as e:
            print(f"Error adding evaluation: {e}")
            return False

    def add_targets(self, targets: list[dict]) -> bool:
        try:
            with self.transaction() as cursor:
                for target in targets:
                    cursor.execute(
                        "INSERT INTO Targets(context1, target, context2) VALUES (?, ?, ?)",
                        (
                            target["context1"],
                            target["target"],
                            target["context2"],
                        ),
                    )
            print("Targets added")
        except Exception as e:
            print(f"Error adding targets: {e}")
            return False

    def add_translations(self, translations: list[dict]) -> bool:
        try:
            self._validate_translations(translations)
            with self.transaction() as cursor:
                for translation in translations:
                    cursor.execute(
                        "INSERT INTO Translations(targetId, translation, model, numEvals) VALUES (?, ?, ?, 0)",
                        (
                            translation["targetId"],
                            translation["translation"],
                            translation["model"],
                        ),
                    )
            print("Translations added")
        except Exception as e:
            print(f"Error adding translations: {e}")
            return False
    
    def _translation_to_dict(self, translation: tuple) -> Optional[dict]:
        try:
            res = {}
            res["id"] = translation[0]
            res["targetId"] = translation[1]
            res["translation"] = translation[2]
            res["model"] = translation[3]
            res["numEval"] = translation[4]
            return res if res else None
        except Exception as e:
            print(f"Error creating dict from a row: {e}")
            return None

    def _validate_rankings(self, options_ranking: list[dict]) -> None:
        # Uniqueness of ranks is verified by db index, so here only translations are verified
        if not options_ranking:
            raise ValueError(f"Got not proper ranking dict: it is empty")

        unique_translations = [eval["translationId"] for eval in options_ranking]
        target = self._get_target_id(unique_translations[0])
        for tr in unique_translations[1:]:
            if target != self._get_target_id(tr):
                raise ValueError(
                    f"Got not proper ranking dict: rankings for different targets"
                )

        if not (len(unique_translations) == len(options_ranking)):
            raise ValueError(
                f"Got not proper ranking dict: rankings for same trnalsations"
            )

    def _validate_translations(self, translations) -> None:
        if not translations:
            raise ValueError(f"Got not proper tranlsations dict: it is empty")

        for translation in translations:
            try:
                with self.read_only() as cursor:
                    cursor.execute(
                        "SELECT * from Targets WHERE id=?", (translation["targetId"],)
                    )
                    res = cursor.fetchone()
                    if not res:
                        raise ValueError(
                            "Got not proper translations dict: target is not known"
                        )
            except:
                raise ValueError("Got not proper translations dict: imossible to validate")

    def _get_new_eval_id(self) -> Optional[int]:
        try:
            with self.read_only() as cursor:
                cursor.execute(
                    "SELECT evalId from Rankings ORDER BY evalId DESC LIMIT 1"
                )
                row = cursor.fetchone()
                return row[0] + 1 if row else 1

        except Exception as e:
            print(f"Error getting new evaluation id: {e}")
            return None

    def _get_target_id(self, translation_id: int) -> Optional[int]:
        try:
            with self.read_only() as cursor:
                cursor.execute(
                    "SELECT targetId from Translations WHERE id = ?", (translation_id,)
                )
                target_id = cursor.fetchone()
                return target_id[0] if target_id else None

        except Exception as e:
            print(f"Error getting getting target id: {e}")
            return None
