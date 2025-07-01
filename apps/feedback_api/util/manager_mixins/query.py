from typing import Optional


class QueryMixin:
    """
    Mixin for running specific queries.

    Requires host class to provide:
    - transaction() -> Generator[sqlite3.Cursor, None, None]: Context manager for DB transactions
    - read_only() -> Generator[sqlite3.Cursor, None, None]: Context manager for read-only DB access
    """

    def get_target_with_translations(self) -> Optional[dict]:
        try:
            with self.read_only() as cursor:
                # Get the least evaluated translation
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
                row = cursor.fetchone()
                if not row:
                    print("No translations found.")
                    return None
                targetId = row[1]

                # Find corresponding target
                cursor.execute(
                    """
                    SELECT 
                        id,
                        context1,
                        target,
                        context2
                    FROM Targets
                    WHERE id=?
                    """,
                    (targetId,),
                )
                target = cursor.fetchone()
                if not target:
                    print(f"No target found for targetId {targetId}.")
                    return None

                # Get all translations for this target
                cursor.execute(
                    """
                    SELECT 
                        id,
                        targetId,
                        translation,
                        model,
                        numEvals
                    FROM Translations
                    WHERE targetId = ?
                    """,
                    (targetId,),
                )
                translations = cursor.fetchall()
                print(f"Found {len(translations)} translations")

            res = self._transform_to_dict(target, translations)
            return res if res else None

        except Exception as e:
            print(f"Error getting resulting dict: {e}")
            return None

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

    def add_evaluation(self, options_ranking: list[dict]) -> bool:
        try:
            print(options_ranking)
            self._validate_rankings(options_ranking)
            new_eval_id = self._get_new_eval_id()
            with self.transaction() as cursor:
                for eval in options_ranking:
                    cursor.execute(
                        "INSERT INTO Rankings (translationId, evalId, rank, discarded) VALUES (?, ?, ?, ?)",
                        (
                            int(eval["translationId"]),
                            new_eval_id,
                            int(eval["rank"]),
                            eval["discarded"],
                        ),
                    )
            print("Evaluation added")
            return True
        except Exception as e:
            print(f"Error adding evaluation: {e}")
            return False

    def _transform_to_dict(self, target: tuple, translations: tuple) -> Optional[dict]:
        try:
            res = {}
            res["target"] = {
                "id": target[0],
                "context1": target[1],
                "target": target[2],
                "context2": target[3],
            }
            res["translations"] = []
            for translation in translations:
                res["translations"].append(
                    {
                        "id": translation[0],
                        "targetId": translation[1],
                        "translation": translation[2],
                        "model": translation[3],
                        "numEvals": translation[4],
                    }
                )
            return res if res else None
        except Exception as e:
            print(f"Error creating dict from a target and translations: {e}")
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
                raise ValueError(
                    "Got not proper translations dict: imossible to validate"
                )

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
