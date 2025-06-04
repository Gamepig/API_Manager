from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            "message": "Hello from Python API!",
            "timestamp": time.time(),
            "language": "Python"
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8001):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting Python API on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run() 