from flask import Flask, request, jsonify
import requests
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/ping', methods=['POST'])
def forward_and_track_ping():
    data = request.json
    target_service = data['target']
    origin_service = os.getenv('SERVICE_NAME', 'default_service')
    
    # Forwarding the ping to the target service
    target_service_url = f"http://{target_service}:5000/ping"
    try:
        forward_response = requests.post(target_service_url, json={"origin": origin_service})
        forward_status = forward_response.status_code
    except Exception as e:
        forward_status = str(e)

    # Prepare data for tracking API
    tracking_data = {
        "origin": origin_service,
        "target": target_service,
        "timeStamp": datetime.utcnow().isoformat(),
        "forwardStatus": forward_status
    }

    # Send data to tracking API
    tracking_api_url = "http://tracker:5000/pings"
    try:
        requests.post(tracking_api_url, json=tracking_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "forwarded", "trackingStatus": "logged", "response": forward_status}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
