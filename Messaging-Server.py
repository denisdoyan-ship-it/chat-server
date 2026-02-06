import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

DATA_FILE = 'BDMDataBase.json'

def read_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return json.loads(content) if content else []
    except Exception as e:
        print(f"Error reading {DATA_FILE}: {e}")
        return []

def write_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error writing to {DATA_FILE}: {e}")

class Handler(BaseHTTPRequestHandler):
    def set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self.set_headers(204)

    def do_GET(self):
        if self.path == '/':
            self.set_headers(200, 'text/plain')
            self.wfile.write(b"Server is online and ready.")
        elif self.path == '/data':
            try:
                self.set_headers()
                data = read_data()
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.set_headers(404)
            self.wfile.write(b'{"error": "Not found"}')

    def do_POST(self):
        if self.path == '/data':
            try:
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                new_entry = json.loads(body)

                data = read_data()
                if isinstance(data, list):
                    if isinstance(new_entry, dict) and "id" not in new_entry:
                        new_entry["id"] = (data[-1]["id"] + 1 if data and isinstance(data[-1], dict) and "id" in data[-1] else len(data) + 1)
                    data.append(new_entry)
                else:
                    data = [new_entry]

                write_data(data)

                self.set_headers(201)
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
                
            except Exception as e:
                self.set_headers(500)
                self.wfile.write(f'{{"error": "Server error: {str(e)}"}}'.encode('utf-8'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f"Server starting on port {port}...")
    server.serve_forever()
