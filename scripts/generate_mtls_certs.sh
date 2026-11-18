#!/usr/bin/env bash
set -euo pipefail

CERT_DIR="$(cd "$(dirname "$0")/.." && pwd)/certs"
mkdir -p "$CERT_DIR"

echo "Generating local lab CA and mTLS certificates in $CERT_DIR ..."

cat > "$CERT_DIR/ca-ext.cnf" <<EOF
[v3_ca]
basicConstraints = critical,CA:TRUE
keyUsage = critical,keyCertSign,cRLSign
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
EOF

openssl genrsa -out "$CERT_DIR/lab-ca.key" 4096
openssl req -x509 -new -nodes -key "$CERT_DIR/lab-ca.key" -sha256 -days 365 \
  -subj "/CN=CipherTrust-Lab-CA" \
  -config <(cat /etc/ssl/openssl.cnf "$CERT_DIR/ca-ext.cnf") \
  -extensions v3_ca \
  -out "$CERT_DIR/lab-ca.crt"

# Generate mTLS client certificate
openssl genrsa -out "$CERT_DIR/ekm-client.key" 3072
openssl req -new -key "$CERT_DIR/ekm-client.key" \
  -subj "/CN=ekm-reference-client" -out "$CERT_DIR/ekm-client.csr"
cat > "$CERT_DIR/client-ext.cnf" <<EOF
basicConstraints = CA:FALSE
keyUsage = critical,digitalSignature,keyEncipherment
extendedKeyUsage = clientAuth
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid,issuer
EOF
openssl x509 -req -in "$CERT_DIR/ekm-client.csr" \
  -CA "$CERT_DIR/lab-ca.crt" -CAkey "$CERT_DIR/lab-ca.key" -CAcreateserial \
  -extfile "$CERT_DIR/client-ext.cnf" \
  -out "$CERT_DIR/ekm-client.crt" -days 365 -sha256

# Generate server certificate for local lab testing (localhost / 127.0.0.1)
openssl genrsa -out "$CERT_DIR/cm-server.key" 3072
openssl req -new -key "$CERT_DIR/cm-server.key" \
  -subj "/CN=localhost" -out "$CERT_DIR/cm-server.csr"
cat > "$CERT_DIR/server-ext.cnf" <<EOF
basicConstraints = CA:FALSE
keyUsage = critical,digitalSignature,keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = DNS:localhost,IP:127.0.0.1
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid,issuer
EOF
openssl x509 -req -in "$CERT_DIR/cm-server.csr" \
  -CA "$CERT_DIR/lab-ca.crt" -CAkey "$CERT_DIR/lab-ca.key" -CAcreateserial \
  -extfile "$CERT_DIR/server-ext.cnf" \
  -out "$CERT_DIR/cm-server.crt" -days 365 -sha256

rm -f "$CERT_DIR"/*.csr "$CERT_DIR"/*.cnf
chmod 600 "$CERT_DIR"/*.key
echo "Done. Upload $CERT_DIR/lab-ca.crt as a Trusted CA in CipherTrust Manager."
