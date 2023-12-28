from flask import Flask
import requests
import random
import threading
import time
import socket

app = Flask(__name__)

# Function to read hosts from file
def get_hosts():
    with open('hosts.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Get list of hosts
hosts = get_hosts()

# Get the current hostname (service name)
current_hostname = socket.gethostname()
print(f"CURRENT HOSTNAME IS: {current_hostname}")
# Remove the current service from the list of targets
targets = [host for host in hosts if not current_hostname.startswith(host)]

# Choose a random target for the entire lifecycle of the app
target_service = random.choice(targets) if targets else None

def ping_target_continuously():
    print(f"[{current_hostname}] Background thread started, targeting {target_service}")
    while True:
        if target_service:
            print(f"[{current_hostname}] Attempting to send ping to {target_service}")
            try:
                response = requests.get(f'http://{target_service}:5000/ping')
                print(f"[{current_hostname}] Received response from {target_service}: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"[{current_hostname}] Error pinging {target_service}: {e}")
        time.sleep(10)  # Wait for 10 seconds between pings

@app.route('/ping', methods=['GET'])
def ping():
    return "Pong!"

def start_background_thread():
    if target_service:
        # Start the background thread for pinging
        threading.Thread(target=ping_target_continuously, daemon=True).start()

if __name__ == '__main__':
    if target_service:
        print(f"[{current_hostname}] Starting background thread for pinging")
        threading.Thread(target=start_background_thread).start()
    app.run(debug=False, host='0.0.0.0', port=5000)
