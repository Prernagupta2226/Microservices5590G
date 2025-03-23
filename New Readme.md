# LLM-to-LLM Communication via Flask Microservices

This project sets up two microservices (each powered by an LLM using Ollama) that communicate back and forth through a central service registry. No frontend or GUI is required — everything runs in the terminal.

---

## Prerequisites

- Python 3.x
- `requests`, `flask`, `flask_cors` (Install with `pip install flask flask-cors requests`)
- Ngrok (https://ngrok.com/download)
- [Ollama](https://ollama.com) installed and running locally

---

## Ollama Setup

1. **Install Ollama:**
   - Visit https://ollama.com/download and install for your OS.

2. **Start Ollama daemon (if not auto-running):**
   ```bash
   ollama serve
   ```

3. **Pull your LLM model (e.g., llama2):**
   ```bash
   ollama pull llama2
   ```

This will make Ollama accessible at `http://localhost:11434/api/generate`

---

## Ngrok Setup

1. **Install Ngrok**: [Download from here](https://ngrok.com/download)
2. **Authenticate Ngrok (once):**
   ```bash
   ngrok config add-authtoken YOUR_NGROK_TOKEN
   ```
3. **Expose each microservice:**
   - For microservice1:
     ```bash
     ngrok http 5002
     ```
   - For microservice2:
     ```bash
     ngrok http 5003
     ```
4. Copy the Ngrok forwarding URL (e.g., `https://abc123.ngrok-free.app`) and place it in the respective microservice code under `ngrok_url`

---

## Registry Setup

```bash
cd registry
python registry.py
```

Runs on port 5001. You can also expose this using Ngrok:
```bash
ngrok http 5001
```

---

## Microservice Setup

### microservice1 (5002)
```bash
cd microservice1
python app.py
```
Update config in the file with:
- `service_name = 'microservice1'`
- `port = 5002`
- `ngrok_url = 'https://<ms1-ngrok-url>'`
- `registry_url = 'https://<registry-ngrok-url>'`

### microservice2 (5003)
```bash
cd microservice2
python app.py
```
Update config with:
- `service_name = 'microservice2'`
- `port = 5003`
- `ngrok_url = 'https://<ms2-ngrok-url>'`
- `registry_url = 'https://<registry-ngrok-url>'`

---

## Test Communication

Use PowerShell or Postman to trigger the first message:

```powershell
Invoke-RestMethod -Uri https://<registry-ngrok-url>/message `
  -Method POST `
  -Body (@{
    service_name = "microservice1"
    message = "Hello, how are you?"
    loop_count = 0
  } | ConvertTo-Json -Depth 10) `
  -ContentType "application/json".

