from flask import Flask, jsonify, request
import numpy as np
import requests
import random
import threading
import time
import socket
import os

app = Flask(__name__)
    
num_targets = int(os.getenv('NUM_TARGETS', 1))
service_num = int(os.getenv('SERVICE_NUM', 1))

services = [f'service{i}' for i in range(1, service_num + 1)]

# Function to choose multiple random targets
def choose_random_targets(targets, num_targets):
    if num_targets >= len(targets):
        return targets
    else:
        return random.sample(targets, num_targets)

# Get the current hostname (service name)
current_hostname = socket.gethostname()
current_service = os.getenv('SERVICE_NAME', 'default_service')

# Remove the current service from the list of targets
targets = [service for service in services if service != current_service]

# Choose a random target for the entire lifecycle of the app
target_services = choose_random_targets(targets, num_targets) if targets else []

# Assign random weights to each target service
weights = np.random.random(len(target_services))
weights /= weights.sum()  # Normalize to make the sum of weights equal to 1

target_service_weights = dict(zip(target_services, weights))
print(f"Target services with weights: {target_service_weights}")

def weighted_random_choice(choices):
    services, probs = zip(*choices.items())
    return np.random.choice(services, p=probs)

def ping_targets_continuously():
    sidecar_url = f"http://localhost:5001/ping"
    while True:
        target_service = weighted_random_choice(target_service_weights)
        print(f"[{current_hostname}] Attempting to send ping to {target_service}")
        try:
            response = requests.post(sidecar_url, json={"target": target_service})
            print(f"[{current_hostname}] Received response from sidecar for {target_service}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[{current_hostname}] Error pinging sidecar for {target_service}: {e}")
        time.sleep(random.randint(5, 10))

@app.route('/ping', methods=['POST'])
def ping():
    return jsonify({"message": "Pong!"})

if __name__ == '__main__':
    if target_services:
        print(f"[{current_hostname}] Starting background thread for pinging")
        threading.Thread(target=ping_targets_continuously, daemon=True).start()
    app.run(debug=False, host='0.0.0.0', port=5000)
