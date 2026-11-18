#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
: "${CIPHERTRUST_URL:?Set CIPHERTRUST_URL (e.g. https://192.168.122.50)}"
: "${CIPHERTRUST_USER:?Set CIPHERTRUST_USER}"
: "${CIPHERTRUST_PASSWORD:?Set CIPHERTRUST_PASSWORD}"

CURL_TLS_ARGS=()
if [[ -f "$ROOT_DIR/certs/lab-ca.crt" ]]; then
  CURL_TLS_ARGS+=(--cacert "$ROOT_DIR/certs/lab-ca.crt")
else
  echo "Warning: certs/lab-ca.crt not found; using -k for self-signed lab appliance."
  CURL_TLS_ARGS+=(-k)
fi
if [[ -f "$ROOT_DIR/certs/ekm-client.crt" && -f "$ROOT_DIR/certs/ekm-client.key" ]]; then
  CURL_TLS_ARGS+=(--cert "$ROOT_DIR/certs/ekm-client.crt" --key "$ROOT_DIR/certs/ekm-client.key")
fi

echo "Authenticating to $CIPHERTRUST_URL ..."
TOKEN=$(curl -sSf "${CURL_TLS_ARGS[@]}" -X POST "$CIPHERTRUST_URL/api/v1/auth/tokens" \
  -H "Content-Type: application/json" \
  -d "{\"grant_type\":\"password\",\"username\":\"$CIPHERTRUST_USER\",\"password\":\"$CIPHERTRUST_PASSWORD\"}" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['jwt'])")

echo "Creating AES-256 KEK 'demo-app-kek' ..."
curl -sSf "${CURL_TLS_ARGS[@]}" -X POST "$CIPHERTRUST_URL/api/v1/vault/keys2" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"demo-app-kek","algorithm":"AES","size":256,"undeletable":false,"unexportable":true}' >/dev/null

cat > "$ROOT_DIR/.env.ciphertrust" <<EOF
CIPHERTRUST_URL=$CIPHERTRUST_URL
CIPHERTRUST_USER=$CIPHERTRUST_USER
CIPHERTRUST_PASSWORD=$CIPHERTRUST_PASSWORD
CIPHERTRUST_CA_BUNDLE=$ROOT_DIR/certs/lab-ca.crt
CIPHERTRUST_CLIENT_CERT=$ROOT_DIR/certs/ekm-client.crt
CIPHERTRUST_CLIENT_KEY=$ROOT_DIR/certs/ekm-client.key
EOF

chmod 600 "$ROOT_DIR/.env.ciphertrust"
echo "Bootstrap complete. Environment written to $ROOT_DIR/.env.ciphertrust"
