from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import requests
import time

app = Flask(__name__)
CORS(app)

# ---------------------
# CONFIG (CHANGE THESE)
# ---------------------
service_name = 'microservice1'  # Use 'microservice2' on Laptop sC
port = 5002                     # Use 5003 on Laptop C
ngrok_url = 'https://35fa-2607-fea8-799e-3600-78fc-7db1-2999-4a21.ngrok-free.app'  # Replace with your Ngrok
registry_url = 'https://d265-2607-fea8-799e-3600-8534-2ae0-c364-dd86.ngrok-free.app'
ollama_url = 'http://localhost:11434/api/generate'

# ---------------------
# Register and Heartbeat
# ---------------------
def register():
    payload = {
        'service_name': service_name,
        'service_address': ngrok_url
    }
    try:
        res = requests.post(f"{registry_url}/register", json=payload)
        print(f"✅ Registered: {res.json()}")
    except Exception as e:
        print(f"❌ Registration error: {e}")

def heartbeat():
    while True:
        try:
            res = requests.post(f"{registry_url}/heartbeat", json={'service_name': service_name})
            print(f"💓 Heartbeat: {res.json()}")
        except Exception as e:
            print(f"❌ Heartbeat error: {e}")
        time.sleep(120)

# ---------------------
# Receive message and bounce response
# ---------------------
@app.route('/message', methods=['POST'])
def receive_message():
    data = request.json
    prompt = data.get('message', '')
    loop_count = data.get('loop_count', 0)

    print(f"📥 {service_name} received (loop {loop_count}): {prompt}")

    payload = {
        "model": "llama2",
        "prompt": prompt,
        "stream": False
    }

    try:
        res = requests.post(ollama_url, json=payload)
        reply = res.json().get('response', 'No response')

        print(f"🤖 {service_name} LLM reply: {reply}")

        if loop_count >= 10:
            print("🛑 Max loop reached.")
            return jsonify({"response": reply})

        target = 'microservice2' if service_name == 'microservice1' else 'microservice1'
        forward_payload = {
            "target": target,
            "message": reply,
            "loop_count": loop_count + 1
        }

        # Add slight delay to avoid LLM spam
        time.sleep(2)

        requests.post(f"{ngrok_url}/send_message", json=forward_payload)

        return jsonify({"response": reply})

    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------------
# Send message via registry
# ---------------------
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    target = data.get('target')
    message = data.get('message')
    loop_count = data.get('loop_count', 0)

    payload = {
        "service_name": target,
        "message": message,
        "loop_count": loop_count
    }

    try:
        res = requests.post(f"{registry_url}/message", json=payload)
        print(f"📤 Sent to {target}: {message} (Loop {loop_count})")
        print(f"📬 Response from {target}: {res.json()}")
        return jsonify(res.json())
    except Exception as e:
        print(f"❌ Send message error: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------------
# Run the server
# ---------------------
if __name__ == '__main__':
    threading.Thread(target=heartbeat).start()
    register()
    app.run(host='0.0.0.0', port=port)
