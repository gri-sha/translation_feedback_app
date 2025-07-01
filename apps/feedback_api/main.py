from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from util import DBManager, DataLoader

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

db = DBManager()


@app.route("/get_target", methods=["GET"])
def get_target_with_trnalsations():
    res = db.get_target_with_translations()
    return jsonify(res), 200


@app.route("/submit_evaluation", methods=["POST"])
def submit_evaluation():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing rankings"}), 400

    success = db.add_evaluation(data)
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
