from flask import Flask, jsonify, request
import json
import os
from collections import defaultdict
import random
from util import DBManager, DataLoader

app = Flask(__name__)

db = DBManager()

@app.route('/api/get_phrase', methods=['GET'])
def get_phrase():
    """Get a phrase for evaluation (least evaluated first)"""
    try:
        phrase_data = data_manager.get_least_evaluated_phrase()
        
        if not phrase_data:
            return jsonify({
                'error': 'No evaluation data available'
            }), 404
        
        response_data = {
            'id': phrase_data.get('id'),
            'context': phrase_data.get('context'),
            'target_phrase': phrase_data.get('target_phrase'),
            'translation_options': phrase_data.get('translation_options', []),
            'evaluation_count': data_manager.evaluation_counts.get(phrase_data.get('id'), 0)
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/submit_evaluation', methods=['POST'])
def submit_evaluation():
    """Submit evaluation results"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['phrase_id', 'rankings']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Add timestamp and other metadata
        import datetime
        result_data = {
            'phrase_id': data['phrase_id'],
            'rankings': data['rankings'],  # Array of ranked translation indices
            'discarded': data.get('discarded', []),  # Array of discarded translation indices
            'timestamp': datetime.datetime.now().isoformat(),
            'user_id': data.get('user_id', 'anonymous')
        }
        
        # Save the result
        success = data_manager.save_evaluation_result(result_data)
        
        if success:
            return jsonify({
                'message': 'Evaluation submitted successfully',
                'phrase_id': data['phrase_id']
            })
        else:
            return jsonify({
                'error': 'Failed to save evaluation'
            }), 500
    
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get evaluation statistics"""
    try:
        total_phrases = len(data_manager.evaluation_data)
        total_evaluations = sum(data_manager.evaluation_counts.values())
        
        # Calculate phrases by evaluation count
        evaluation_distribution = defaultdict(int)
        for phrase_data in data_manager.evaluation_data:
            phrase_id = phrase_data.get('id')
            count = data_manager.evaluation_counts.get(phrase_id, 0)
            evaluation_distribution[count] += 1
        
        return jsonify({
            'total_phrases': total_phrases,
            'total_evaluations': total_evaluations,
            'evaluation_distribution': dict(evaluation_distribution),
            'average_evaluations_per_phrase': total_evaluations / total_phrases if total_phrases > 0 else 0
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/reload_data', methods=['POST'])
def reload_data():
    """Reload data from files (useful for development)"""
    try:
        global data_manager
        data_manager = EvaluationDataManager(DATA_FILE, RESULTS_FILE)
        return jsonify({
            'message': 'Data reloaded successfully',
            'phrases_loaded': len(data_manager.evaluation_data)
        })
    except Exception as e:
        return jsonify({
            'error': f'Failed to reload data: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)