import sqlite3
import json
from pprint import pprint
from util import DBManager, DataLoader

if __name__ == "__main__":
    db = DBManager()

    db.initialize_schema()
    db.load_example_data()

    data = {}

    with open("assets/example_eval.json") as f:
        example_eval_1 = json.load(f)
    
    with open("assets/example_eval_false.json") as f:
        example_eval_2 = json.load(f)

    # db.add_evaluation(example_eval_1)
    # db.add_evaluation(example_eval_2)
    # db.add_evaluation({})

    with open("assets/example_target.json") as f:
        example_targets = json.load(f)

    with open("assets/example_translation.json") as f:
        example_translations = json.load(f)

    db.add_targets(example_targets)
    db.add_translations(example_translations)


    with db.read_only() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        data["tables"] = cursor.fetchall()

        cursor.execute("SELECT * from Targets")
        data["targets"] = cursor.fetchall()

        cursor.execute("SELECT * from Translations")
        data["translations"] = cursor.fetchall()

        cursor.execute("SELECT * from Rankings")
        data["rankings"] = cursor.fetchall()

    # for key, value in data.items():
    #     print(f"\n{key.upper()}:")
    #     pprint(value)

    print(db.get_least_evaluated_translation())
