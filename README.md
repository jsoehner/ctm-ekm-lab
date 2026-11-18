# CTM EKM Lab (CipherTrust Manager Community Edition)

Companion infrastructure and bootstrap repository for running **Thales CipherTrust Manager Community Edition (CM CE)** and connecting it to [crypto-lab](https://github.com/jsoehner/crypto-lab).

## Why a Separate Repository?

CipherTrust Manager Community Edition is distributed as a full virtual appliance (OVA/QCOW2/VHD) requiring ~8 GB RAM and portal-gated download. Separating appliance deployment and local lab PKI from `crypto-lab` keeps the cryptographic reference repo lightweight and CI-friendly.

## Quickstart

### 1. Deploy CipherTrust Manager (Real Appliance OR Local Lab Mock)

**Option A — Real CipherTrust Manager Community Edition Appliance:**
1. Download the **CipherTrust Manager Community Edition** appliance (OVA or QCOW2) from the Thales Customer Support / Community portal.
2. Boot the appliance with at least **2 vCPUs, 8 GB RAM, 100 GB disk** and complete the initial admin password + community license activation.
3. Export the appliance URL:
   ```bash
   export CIPHERTRUST_URL="https://<appliance-ip-or-fqdn>"
   export CIPHERTRUST_USER="admin"
   export CIPHERTRUST_PASSWORD="<your-bootstrap-password>"
   ```

**Option B — Local HTTPS + mTLS Lab Server (Immediate Testing Without Appliance):**
```bash
bash scripts/generate_mtls_certs.sh
python3 mock-cm-ce/server.py &
export CIPHERTRUST_URL="https://127.0.0.1:8443"
export CIPHERTRUST_USER="admin"
export CIPHERTRUST_PASSWORD="lab-bootstrap-pass"
```
*(Or run via Docker/Podman with `docker compose up -d`.)*

### 2. Generate Lab mTLS Certificates
```bash
bash scripts/generate_mtls_certs.sh
```
This creates a local lab CA and client certificate under `certs/` (git-ignored).

### 3. Bootstrap Key & Client Config
```bash
bash scripts/bootstrap_cm_ce.sh
```
This creates `demo-app-kek` (AES-256) in CipherTrust Manager and writes `.env.ciphertrust` (git-ignored).

### 4. Run `crypto-lab` Against This Instance
From `crypto-lab`:
```bash
set -a && source /home/jsoehner/ctm-ekm-lab/.env.ciphertrust && set +a

# Demo runner automatically detects CIPHERTRUST_URL and runs live EKM encryption
./demo_langs.sh python

# Runs all 13 offline unit tests + 8 live CTM integration tests (21 total)
python3 -m unittest discover -s python -p 'test_*.py' -v
```

### Supported Live Integration Test Cases (`test_ctm_integration.py`)
- **Key Lifecycle & Metadata**: `POST /api/v1/vault/keys2`, `GET /api/v1/vault/keys2/{name}`
- **Live DEK Envelope**: `POST /api/v1/crypto/encrypt` and `/decrypt` over HTTPS + mTLS
- **AAD & Tamper Rejection**: Mismatched AAD (`HTTP 400`) and modified ciphertext (`InvalidTag`)
- **Kill-Switch & Recovery**: `deactivate` (`HTTP 403` blocks decrypt) and `reactivate` (restores decrypt)
- **Key Rotation**: `rotate` increments KEK to `v2` while `v1` envelopes continue to unwrap
- **Multi-Tenant Isolation**: Revoking `ctm-tenant-a` does not affect `ctm-tenant-b`
- **Negative Auth & mTLS**: Invalid credentials/JWT (`HTTP 401`) and missing client cert (`SSLError`)

## Cloud EKM Integration
See [docs/azure-gcp-ekm-integration.md](docs/azure-gcp-ekm-integration.md) for wiring CM CE to **GCP Cloud EKM** and **Azure Cloud Key Management (CCKM)**.
