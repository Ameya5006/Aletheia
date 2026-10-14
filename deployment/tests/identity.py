"""Test-only HTTPS JWKS fixture; no login, production identities or token endpoint."""

import ssl
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in {"/jwks", "/health"}:
            self.send_error(404)
            return
        data = (
            Path("/identity/jwks.json").read_bytes()
            if self.path == "/jwks"
            else b"alive"
        )
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


server = HTTPServer(("0.0.0.0", 8443), Handler)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain("/identity/identity_ca", "/identity/signing.pem")
server.socket = context.wrap_socket(server.socket, server_side=True)
server.serve_forever()
