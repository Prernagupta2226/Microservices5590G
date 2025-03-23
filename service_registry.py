from flask import Flask, request, jsonify
from threading import Timer
import time
import requests

app = Flask(__name__)
services = {}
HEARTBEAT_TIMEOUT = 300  # 5 minutes

def remove_inactive_services():
    current_time = time.time()
    for service_name, service in list(services.items()):
        if current_time - service['last_heartbeat'] > HEARTBEAT_TIMEOUT:
            del services[service_name]
    Timer(60, remove_inactive_services).start()

@app.route('/register', methods=['POST'])
def register_service():
    data = request.json
    name = data.get('service_name')
    address = data.get('service_address')
    if not name or not address:
        return jsonify({"error": "Missing fields"}), 400
    services[name] = {
        'address': address,
        'last_heartbeat': time.time()
    }
    return jsonify({"message": f"{name} registered"}), 200

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    name = request.json.get('service_name')
    if name not in services:
        return jsonify({"error": "Service not registered"}), 404
    services[name]['last_heartbeat'] = time.time()
    return jsonify({"message": "Heartbeat received"}), 200

@app.route('/services', methods=['GET'])
def list_services():
    return jsonify(services), 200

@app.route('/message', methods=['POST'])
def forward_message():
    data = request.json
    target = data.get('service_name')
    if target not in services:
        return jsonify({"error": "Target service not found"}), 404
    try:
        res = requests.post(f"{services[target]['address']}/message", json=data)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    remove_inactive_services()
    app.run(host='0.0.0.0', port=5001)