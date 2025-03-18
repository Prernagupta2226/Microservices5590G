from flask import Flask, request, jsonify
from threading import Timer
import time

app = Flask(__name__)

# Service registry in-memory stores
services = {}
HEARTBEAT_TIMEOUT = 300  # 5 minutes

def remove_inactive_services():
    """Remove services that have not sent heartbeats in the last 5 minutes."""
    current_time = time.time()
    for service_name, service in list(services.items()):
        if current_time - service['last_heartbeat'] > HEARTBEAT_TIMEOUT:
            del services[service_name]
    Timer(60, remove_inactive_services).start()  # Run every minute

@app.route('/register', methods=['POST'])
def register_service():
    data = request.json
    service_name = data.get('service_name')
    service_address = data.get('service_address')

    if not service_name or not service_address:
        return jsonify({"error": "Service name and address are required"}), 400

    services[service_name] = {
        'address': service_address,
        'last_heartbeat': time.time()
    }

    return jsonify({"message": f"Service {service_name} registered successfully"}), 200

@app.route('/services', methods=['GET'])
def get_services():
    return jsonify(services)

@app.route('/message', methods=['POST'])
def forward_message():
    data = request.json
    target_service = data.get('service_name')
    message = data.get('message')

    if target_service not in services:
        return jsonify({"error": "Service not found"}), 404

    target_address = services[target_service]['address']
    return jsonify({"message": f"Forwarding to {target_service} at {target_address}: {message}"}), 200

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    service_name = request.json.get('service_name')

    if service_name not in services:
        return jsonify({"error": "Service not registered"}), 404

    services[service_name]['last_heartbeat'] = time.time()
    return jsonify({"message": "Heartbeat received"}), 200

if __name__ == '__main__':
    remove_inactive_services()  # Start the cleanup process
    app.run(host='0.0.0.0', port=5001)