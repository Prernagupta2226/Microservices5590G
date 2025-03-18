from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import threading
import time

app = Flask(__name__)
CORS(app)

# Service Details
service_name = 'microservice2'  # or 'microservice2' depending on the microservice
registry_url = 'https://cac2-2607-fea8-799e-3600-1567-badc-682e-23e1.ngrok-free.app'  # Service registry URL

# Register service
def register_service():
    payload = {
        'service_name': service_name,
        'service_address': f'https://bca3-2607-fea8-799e-3600-9064-8fe3-27f5-93b.ngrok-free.app'  # Replace with respective ngrok URL
    }
    response = requests.post(f"{registry_url}/register", json=payload)
    print(response.json())

# Send Heartbeat every 2 minutes
def send_heartbeat():
    while True:
        payload = {'service_name': service_name}
        response = requests.post(f"{registry_url}/heartbeat", json=payload)
        print(response.json())
        time.sleep(120)

# Receive message
@app.route('/message', methods=['POST'])
def receive_message():
    data = request.json
    message = data.get('message')
    print(f"📥 {service_name} received: {message}")
    return jsonify({"message": f"{service_name} received: {message}"}), 200

if __name__ == '__main__':
    threading.Thread(target=send_heartbeat).start()
    register_service()
    app.run(host='0.0.0.0', port=5003)  # Change port for each microservice