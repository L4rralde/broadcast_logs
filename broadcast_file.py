import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyngrok import ngrok

# --- Configuration ---
log_file = "output.log"
port = 8080
reserved_subdomain = "" #Need to add
url_path = "/logs"
num_lines = 50  # number of lines to retrieve

# --- HTTP Handler ---
class TailHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != url_path:
            self.send_error(404, "Not Found")
            return

        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()

        try:
            # Read last N lines
            with open(log_file, "r") as f:
                lines = f.readlines()
                last_lines = lines[-num_lines:]
            self.wfile.write("".join(last_lines).encode())
        except Exception as e:
            self.wfile.write(f"Error reading file: {e}".encode())

# --- Start HTTP server ---
def serve():
    server = HTTPServer(("", port), TailHandler)
    print(f"Serving last {num_lines} lines of {log_file} at {url_path}")
    server.serve_forever()

threading.Thread(target=serve, daemon=True).start()

# --- Expose via ngrok ---
public_url = ngrok.connect(addr=port, proto="http", subdomain=reserved_subdomain)
print(f"Access last {num_lines} lines worldwide at: {public_url}{url_path}")

# --- Keep script alive ---
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped broadcasting.")
