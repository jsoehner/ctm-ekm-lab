#!/usr/bin/env python3
"""Local HTTPS + mTLS CipherTrust Manager REST API Lab Server.

Provides a lightweight, zero-appliance-download local endpoint compatible with
`crypto-lab/python/ciphertrust_ekm_example.py` and `scripts/bootstrap_cm_ce.sh`.
"""

from __future__ import annotations

import base64
import json
import os
import secrets
import ssl
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEYS: dict[str, dict[str, Any]] = {}
TOKENS: set[str] = set()


class CipherTrustHandler(BaseHTTPRequestHandler):
    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _require_auth(self) -> bool:
        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Bearer ") or auth[7:] not in TOKENS:
            self._send_json(401, {"error": "Unauthorized"})
            return False
        return True

    def do_GET(self) -> None:  # noqa: N802
        if not self._require_auth():
            return
        if self.path.startswith("/api/v1/vault/keys2/"):
            name = self.path.split("/")[5]
            rec = KEYS.get(name)
            if not rec:
                self._send_json(404, {"error": "Key not found"})
                return
            self._send_json(
                200,
                {
                    "id": rec["id"],
                    "name": name,
                    "algorithm": "AES",
                    "size": 256,
                    "state": rec["state"],
                    "version": rec["current_version"],
                },
            )
            return
        self._send_json(404, {"error": f"Unknown endpoint: {self.path}"})

    def do_POST(self) -> None:  # noqa: N802
        payload = self._read_json()

        if self.path == "/api/v1/auth/tokens":
            expected_user = os.environ.get("CM_ADMIN_USER", "admin")
            expected_pass = os.environ.get("CM_ADMIN_PASSWORD", "lab-bootstrap-pass")
            if payload.get("username") == expected_user and payload.get("password") == expected_pass:
                token = secrets.token_urlsafe(32)
                TOKENS.add(token)
                self._send_json(200, {"jwt": token, "token_type": "Bearer"})
            else:
                self._send_json(401, {"error": "Invalid credentials"})
            return

        if not self._require_auth():
            return

        if self.path == "/api/v1/vault/keys2":
            name = payload["name"]
            if name not in KEYS:
                KEYS[name] = {
                    "id": f"cm-lab-{len(KEYS) + 1}",
                    "name": name,
                    "current_version": 1,
                    "versions": {1: os.urandom(32)},
                    "state": "Active",
                }
            rec = KEYS[name]
            self._send_json(
                201,
                {
                    "id": rec["id"],
                    "name": name,
                    "algorithm": "AES",
                    "size": 256,
                    "state": rec["state"],
                    "version": rec["current_version"],
                },
            )
            return

        if self.path.startswith("/api/v1/vault/keys2/") and self.path.endswith("/deactivate"):
            name = self.path.split("/")[5]
            if name not in KEYS:
                self._send_json(404, {"error": "Key not found"})
                return
            KEYS[name]["state"] = "Deactivated"
            self._send_json(200, {"name": name, "state": "Deactivated"})
            return

        if self.path.startswith("/api/v1/vault/keys2/") and self.path.endswith("/reactivate"):
            name = self.path.split("/")[5]
            if name not in KEYS:
                self._send_json(404, {"error": "Key not found"})
                return
            KEYS[name]["state"] = "Active"
            self._send_json(200, {"name": name, "state": "Active"})
            return

        if self.path.startswith("/api/v1/vault/keys2/") and self.path.endswith("/rotate"):
            name = self.path.split("/")[5]
            rec = KEYS.get(name)
            if not rec:
                self._send_json(404, {"error": "Key not found"})
                return
            new_ver = rec["current_version"] + 1
            rec["current_version"] = new_ver
            rec["versions"][new_ver] = os.urandom(32)
            self._send_json(200, {"id": rec["id"], "name": name, "version": new_ver, "state": rec["state"]})
            return

        if self.path == "/api/v1/crypto/encrypt":
            name = payload["id"]
            rec = KEYS.get(name)
            if not rec or rec["state"] != "Active":
                self._send_json(403, {"error": "Key inactive or missing"})
                return
            ver = rec["current_version"]
            nonce = os.urandom(12)
            aad = base64.b64decode(payload.get("aad", "")) if payload.get("aad") else b""
            pt = base64.b64decode(payload["plaintext"])
            ct_tag = AESGCM(rec["versions"][ver]).encrypt(nonce, pt, aad)
            self._send_json(
                200,
                {
                    "id": rec["id"],
                    "version": ver,
                    "ciphertext": base64.b64encode(ct_tag[:-16]).decode("ascii"),
                    "iv": base64.b64encode(nonce).decode("ascii"),
                    "tag": base64.b64encode(ct_tag[-16:]).decode("ascii"),
                },
            )
            return

        if self.path == "/api/v1/crypto/decrypt":
            name = payload["id"]
            rec = KEYS.get(name)
            if not rec or rec["state"] != "Active":
                self._send_json(403, {"error": "Key inactive or missing"})
                return
            ver = int(payload.get("version", rec["current_version"]))
            key_mat = rec["versions"].get(ver)
            if not key_mat:
                self._send_json(404, {"error": f"Key version {ver} not found"})
                return
            nonce = base64.b64decode(payload["iv"])
            ct = base64.b64decode(payload["ciphertext"])
            tag = base64.b64decode(payload["tag"])
            aad = base64.b64decode(payload.get("aad", "")) if payload.get("aad") else b""
            try:
                pt = AESGCM(key_mat).decrypt(nonce, ct + tag, aad)
            except Exception:
                self._send_json(400, {"error": "Decryption or authentication tag check failed"})
                return
            self._send_json(200, {"plaintext": base64.b64encode(pt).decode("ascii")})
            return

        self._send_json(404, {"error": f"Unknown endpoint: {self.path}"})

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    cert_dir = root / "certs"
    port = int(os.environ.get("CM_PORT", "8443"))

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(certfile=str(cert_dir / "cm-server.crt"), keyfile=str(cert_dir / "cm-server.key"))
    ctx.load_verify_locations(cafile=str(cert_dir / "lab-ca.crt"))
    if os.environ.get("CM_REQUIRE_MTLS", "false").lower() == "true":
        ctx.verify_mode = ssl.CERT_REQUIRED

    server = HTTPServer(("127.0.0.1", port), CipherTrustHandler)
    server.socket = ctx.wrap_socket(server.socket, server_side=True)
    print(f"CipherTrust Lab HTTPS server listening on https://127.0.0.1:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
