from flask import Flask, request, jsonify
from flask_cors import CORS
from model import predict_news

app = Flask(__name__)
# Enable CORS for all routes to allow frontend to communicate
CORS(app)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    
    text = data['text']
    result = predict_news(text)
    
    return jsonify(result)

if __name__ == '__main__':
    print("Starting VerifyFirst Backend on port 5000...")
    app.run(debug=True, port=5000)
