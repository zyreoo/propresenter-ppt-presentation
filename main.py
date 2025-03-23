import requests
import threading
import time
from requests.auth import HTTPBasicAuth
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# ProPresenter connection settings
PROPRESENTER_IP = "192.168.3.37"  # Your ProPresenter machine's IP
PROPRESENTER_PORT = "49334"       # API Port from ProPresenter settings
PASSWORD = "Horea25a"             # Your ProPresenter controller password

loop_running = False  # Controls the auto-loop

def send_command(action):
    """Send a command to ProPresenter (next/previous slide)."""
    url = f"http://{PROPRESENTER_IP}:{PROPRESENTER_PORT}/v1/presentation/active/{action}/trigger"
    auth = HTTPBasicAuth('control', PASSWORD)
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.get(url, headers=headers, auth=auth, timeout=5)
        response.raise_for_status()
        return {"status": "success", "message": f"{action.upper()} triggered!"}

    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

def auto_loop():
    """Continuously sends 'next' command every 3 seconds."""
    global loop_running
    while loop_running:
        send_command("next")
        time.sleep(3)  # Adjust time interval if needed

@app.route("/")
def home():
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ProPresenter Remote</title>
        <style>
            body { text-align: center; font-family: Arial, sans-serif; margin-top: 50px; }
            button { font-size: 20px; padding: 15px 30px; margin: 10px; cursor: pointer; border: none; border-radius: 10px; }
            .next { background-color: #28a745; color: white; }
            .prev { background-color: #dc3545; color: white; }
            .loop { background-color: #007bff; color: white; }
            .stop { background-color: #ff8800; color: white; }
        </style>
        <script>
            let loopRunning = false;
            let loopInterval;

            function sendCommand(action) {
                fetch('/' + action, { method: 'GET' })
                .then(response => response.json())
                .then(data => console.log(data.message))
                .catch(error => console.error('Error:', error));
            }

            function startLoop() {
                if (!loopRunning) {
                    loopRunning = true;
                    document.getElementById("status").innerText = "Loop Running...";
                    loopInterval = setInterval(() => sendCommand('next'), 3000);
                }
            }

            function stopLoop() {
                loopRunning = false;
                document.getElementById("status").innerText = "Loop Stopped.";
                clearInterval(loopInterval);
            }
        </script>
    </head>
    <body>
        <h1>ProPresenter Remote</h1>
        <button class="prev" onclick="sendCommand('prev')">⏮ Previous Slide</button>
        <button class="next" onclick="sendCommand('next')">⏭ Next Slide</button>
        <br><br>
        <button class="loop" onclick="startLoop()">🔄 Start Loop</button>
        <button class="stop" onclick="stopLoop()">⏹ Stop Loop</button>
        <p id="status">Loop Stopped.</p>
    </body>
    </html>
    """
    return render_template_string(html_code)

@app.route("/next")
def next_slide():
    return jsonify(send_command("next"))

@app.route("/prev")
def prev_slide():
    return jsonify(send_command("previous"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
