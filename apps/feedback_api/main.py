from flask import Flask, jsonify, request
import json
import os
from util import DBManager, DataLoader

app = Flask(__name__)
db = DBManager()


@app.route("/get_target", methods=["GET"])
def get_phrase():
    res = db.get_least_evaluated_translation()
    if res:
        return jsonify({"response": res}), 200
    return jsonify({"response": None}), 200


@app.route("/submit_evaluation", methods=["POST"])
def submit_evaluation():
    data = request.get_json()
    if not data or "rankings" not in data:
        return jsonify({"error": "Missing rankings"}), 400

    success = db.add_evaluation(data["rankings"])
    if success:
        return jsonify({"message": "Evaluation submitted successfully"}), 200
    else:
        return jsonify({"error": "Failed to submit evaluation"}), 500


if __name__ == "__main__":
    db.initialize_schema()
    db.load_example_data()

    # Add targets and translations with 0 evaluations
    with open("assets/example_target.json") as f:
        example_targets = json.load(f)

    with open("assets/example_translation.json") as f:
        example_translations = json.load(f)

    db.add_targets(example_targets)
    db.add_translations(example_translations)

    app.run(debug=True)
