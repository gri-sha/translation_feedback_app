from flask import Flask, jsonify, request
import json
import os
from util import DBManager, DataLoader

app = Flask(__name__)
db = DBManager()

@app.route('/api/get_target', methods=['GET'])
def get_phrase():
    pass

@app.route('/api/submit_evaluation', methods=['POST'])
def submit_evaluation():
    pass

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    pass