from flask import Flask, jsonify, request
import requests
import random
import threading
import time
import socket
import os

app = Flask(__name__)

# Function to read hosts from file
def get_hosts():
    with open('hosts.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Get list of hosts
hosts = get_hosts()

# Get the current hostname (service name)
current_hostname = socket.gethostname()
current_service = os.getenv('SERVICE_NAME', 'default_service')
print(f"CURRENT HOSTNAME IS: {current_hostname}")
# Remove the current service from the list of targets
targets = [host for host in hosts if host != current_service]

# Choose a random target for the entire lifecycle of the app
target_service = random.choice(targets) if targets else None

def ping_target_continuously():
    print(f"[{current_hostname}] Background thread started, targeting {target_service}")
    while True:
        print(f"[{current_hostname}] Attempting to send ping to {target_service}")
        try:
            response = requests.post(f'http://{target_service}:5000/ping', json={"origin": current_service})
            print(f"[{current_hostname}] Received response from {target_service}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[{current_hostname}] Error pinging {target_service}: {e}")
        time.sleep(random.randint(5, 10))

def notify_sidecar(origin):
    sidecar_url = f"http://localhost:5001/notify"
    payload = {"origin": origin}
    try:
        requests.post(sidecar_url, json=payload)
    except Exception as e:
        print(f"Error notifying sidecar: {e}")

@app.route('/ping', methods=['POST'])
def ping():
    data = request.json
    origin = data.get('origin', 'unknown')
    notify_sidecar(origin)
    return jsonify({"message": "Pong!"})

if __name__ == '__main__':
    if target_service:
        print(f"[{current_hostname}] Starting background thread for pinging")
        threading.Thread(target=ping_target_continuously, daemon=True).start()
    app.run(debug=False, host='0.0.0.0', port=5000)
