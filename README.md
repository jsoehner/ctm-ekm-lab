# CTM EKM Lab (CipherTrust Manager Community Edition)

Companion infrastructure and bootstrap repository for running **Thales CipherTrust Manager Community Edition (CM CE)** and connecting it to [crypto-lab](https://github.com/jsoehner/crypto-lab).

## Why a Separate Repository?

CipherTrust Manager Community Edition is distributed as a full virtual appliance (OVA/QCOW2/VHD) requiring ~8 GB RAM and portal-gated download. Separating appliance deployment and local lab PKI from `crypto-lab` keeps the cryptographic reference repo lightweight and CI-friendly.

## Quickstart

### 1. Deploy CipherTrust Manager Community Edition
1. Download the **CipherTrust Manager Community Edition** appliance (OVA or QCOW2) from the Thales Customer Support / Community portal.
2. Boot the appliance with at least **2 vCPUs, 8 GB RAM, 100 GB disk** and complete the initial admin password + community license activation.
3. Export the appliance URL:
   ```bash
   export CIPHERTRUST_URL="https://<appliance-ip-or-fqdn>"
   export CIPHERTRUST_USER="admin"
   export CIPHERTRUST_PASSWORD="<your-bootstrap-password>"
   ```

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

### 4. Run the Reference Client
From `crypto-lab`:
```bash
set -a && source /home/jsoehner/ctm-ekm-lab/.env.ciphertrust && set +a
python3 python/ciphertrust_ekm_example.py
```

## Cloud EKM Integration
See [docs/azure-gcp-ekm-integration.md](docs/azure-gcp-ekm-integration.md) for wiring CM CE to **GCP Cloud EKM** and **Azure Cloud Key Management (CCKM)**.
