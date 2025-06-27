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
                        t.id,
                        t.targetId,
                        t.translation,
                        t.model,
                        COUNT(r.id) as numEvals,
                        tar.target,
                        tar.context1,
                        tar.context2
                    FROM Translations t
                    LEFT JOIN Rankings r ON t.id = r.translationId
                    JOIN Targets tar ON t.targetId = tar.id
                    GROUP BY t.id, t.targetId, t.translation, t.model, tar.target, tar.context1, tar.context2
                    ORDER BY numEvals ASC, t.id ASC
                    LIMIT 1
                """
                )

                result = cursor.fetchone()
                return dict(result) if result else None

        except Exception as e:
            print(f"Error getting least evaluated translation: {e}")
            return None

    def add_evaluation(self, options_ranking: list[dict]) -> bool:
        self._validate_rankings(options_ranking)

        new_eval_id = self._get_new_eval_id()

        try:
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
        except Exception as e:
            print(f"Error getting least evaluated translation: {e}")
            return None

    def _validate_rankings(options_ranking: dict) -> None:
        discarded_count = sum(1 for eval in options_ranking if eval["discarded"])
        unique_ranks = {eval["rank"] for eval in options_ranking}
        unique_translations = {eval["translationId"] for eval in options_ranking}

        total = discarded_count + len(unique_ranks)
        if not (total == len(options_ranking) and len(unique_translations) == len(options_ranking)):
            raise ValueError(f"Got not proper ranking dict: {options_ranking}")

    def _get_new_eval_id(self) -> Optional[int]:
        try:
            with self.read_only() as cursor:
                cursor.execute(
                    "SELECT evalId from Rankings ORDER BY evalId DESC LIMIT 1"
                )
                row = cursor.fetchone()
                return row[0] + 1 if row else None

        except Exception as e:
            print(f"Error getting new evaluation id: {e}")
            return None
