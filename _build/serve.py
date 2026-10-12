"""Local preview server for public/ with clean URLs (/platform -> /platform/index.html), like Vercel."""
import http.server, os, socketserver
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public")
PORT = int(os.environ.get("PORT", 4610))

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)
    def send_head(self):
        p = self.path.split("?")[0].split("#")[0]
        if p != "/" and not os.path.splitext(p)[1] and not p.endswith("/"):
            if os.path.isfile(os.path.join(ROOT, p.lstrip("/"), "index.html")):
                self.path = p + "/index.html"
        return super().send_head()
    def send_error(self, code, message=None, explain=None):
        if code == 404 and os.path.isfile(os.path.join(ROOT, "404.html")):
            self.send_response(404); self.send_header("Content-Type", "text/html"); self.end_headers()
            self.wfile.write(open(os.path.join(ROOT, "404.html"), "rb").read()); return
        super().send_error(code, message, explain)
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()
    def log_message(self, *a): pass

class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True  # one stalled browser connection must not block every other request

with Server(("", PORT), H) as s:
    s.serve_forever()
