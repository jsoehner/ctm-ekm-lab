#!/usr/bin/env bash
set -euo pipefail

CERT_DIR="$(cd "$(dirname "$0")/.." && pwd)/certs"
mkdir -p "$CERT_DIR"

echo "Generating local lab CA and mTLS client certificate in $CERT_DIR ..."

openssl genrsa -out "$CERT_DIR/lab-ca.key" 4096
openssl req -x509 -new -nodes -key "$CERT_DIR/lab-ca.key" -sha256 -days 365 \
  -subj "/CN=CipherTrust-Lab-CA" -out "$CERT_DIR/lab-ca.crt"

openssl genrsa -out "$CERT_DIR/ekm-client.key" 3072
openssl req -new -key "$CERT_DIR/ekm-client.key" \
  -subj "/CN=ekm-reference-client" -out "$CERT_DIR/ekm-client.csr"

openssl x509 -req -in "$CERT_DIR/ekm-client.csr" \
  -CA "$CERT_DIR/lab-ca.crt" -CAkey "$CERT_DIR/lab-ca.key" -CAcreateserial \
  -out "$CERT_DIR/ekm-client.crt" -days 365 -sha256

rm -f "$CERT_DIR/ekm-client.csr"
chmod 600 "$CERT_DIR"/*.key
echo "Done. Upload $CERT_DIR/lab-ca.crt as a Trusted CA in CipherTrust Manager."
