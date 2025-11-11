from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        'message': 'Welcome to MARC-A-BOT Backend API',
        'status': 'running'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'MARC-A-BOT Backend'
    })

@app.route('/api/process', methods=['POST'])
def process_data():
    try:
        data = request.get_json()
        # Xử lý dữ liệu ở đây
        return jsonify({
            'success': True,
            'message': 'Data processed successfully',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
