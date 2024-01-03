from flask import Flask, request, jsonify
import requests
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/notify', methods=['POST'])
def notify():
    data = request.json
    data['destiny'] = os.getenv('SERVICE_NAME', 'default_service')  # Use environment variable
    data['timeStamp'] = datetime.utcnow().isoformat()

    tracking_api_url = "http://tracker:5000/pings"
    try:
        requests.post(tracking_api_url, json=data)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
