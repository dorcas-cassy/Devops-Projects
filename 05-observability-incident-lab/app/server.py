from http.server import BaseHTTPRequestHandler, HTTPServer

requests = {"total": 0, "errors": 0}
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        requests["total"] += 1
        if self.path == "/health":
            self.send_response(200); self.end_headers(); self.wfile.write(b'{"status":"ok"}')
        elif self.path == "/error":
            requests["errors"] += 1; self.send_response(500); self.end_headers(); self.wfile.write(b'{"error":"simulated failure"}')
        elif self.path == "/metrics":
            self.send_response(200); self.send_header("Content-Type", "text/plain"); self.end_headers()
            self.wfile.write(f'portfolio_requests_total {requests["total"]}\nportfolio_errors_total {requests["errors"]}\n'.encode())
        else:
            self.send_response(404); self.end_headers()
    def log_message(self, *_): pass
HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
