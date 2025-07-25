from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['pdf']

    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    # Simulate processing
    print(f"Received file: {file.filename}")
    result = f"Successfully processed file: {file.filename}"

    return jsonify({'result': result})
