from flask import Flask, request, jsonify
import subprocess
import os
import socket
import pwd
import pty
import select
import termios
import struct
import fcntl
import signal
import time
import sys

app = Flask(__name__)

class ShellSession:
    def __init__(self):
        # Create master and slave PTY
        self.master_fd, slave_fd = pty.openpty()
        
        # Fork a new process
        pid = os.fork()
        if pid == 0:  # Child process
            # Close master in child
            os.close(self.master_fd)
            
            # Make slave the controlling terminal
            os.setsid()
            os.dup2(slave_fd, 0)  # stdin
            os.dup2(slave_fd, 1)  # stdout
            os.dup2(slave_fd, 2)  # stderr
            
            # Close slave in child
            os.close(slave_fd)
            
            # Execute shell
            os.execvp('/bin/bash', ['/bin/bash'])
        else:  # Parent process
            # Close slave in parent
            os.close(slave_fd)
            self.pid = pid
            
            # Set non-blocking mode for master
            flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
            fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            
            # Clear initial shell output
            self.read_output()

    def execute(self, command):
        # Write command to shell
        os.write(self.master_fd, (command + '\n').encode())
        
        # Read output
        return self.read_output()

    def read_output(self, timeout=1):
        output = ''
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout:
                break
                
            try:
                # Check if there's data to read
                r, _, _ = select.select([self.master_fd], [], [], 0.1)
                if not r:
                    continue
                    
                # Read available data
                chunk = os.read(self.master_fd, 1024).decode()
                if not chunk:
                    break
                output += chunk
            except (OSError, IOError) as e:
                if e.errno != errno.EAGAIN:
                    raise
                break
                
        # Remove command echo and prompt
        lines = output.split('\n')
        if len(lines) > 1:
            lines = lines[1:-1]
        return '\n'.join(lines)

    def get_cwd(self):
        # Execute pwd command to get current working directory
        os.write(self.master_fd, b'pwd\n')
        output = self.read_output()
        return output.strip()

    def cleanup(self):
        try:
            os.kill(self.pid, signal.SIGTERM)
            os.waitpid(self.pid, 0)
            os.close(self.master_fd)
        except:
            pass

# Global shell session
shell = ShellSession()

@app.route('/execute', methods=['POST'])
def execute_command():
    try:
        data = request.get_json()
        command = data.get("command")
        if not command:
            return jsonify({"error": "No command provided"}), 400

        # Execute command in shell session
        output = shell.execute(command)
        return jsonify({"output": output}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/info', methods=['GET'])
def get_user_info():
    try:
        user = pwd.getpwuid(os.getuid()).pw_name
        host = socket.gethostname()
        cwd = shell.get_cwd()  # Get current directory from shell session
        return jsonify({"user": user, "host": host, "cwd": cwd}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Cleanup on shutdown
import atexit
atexit.register(shell.cleanup)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)