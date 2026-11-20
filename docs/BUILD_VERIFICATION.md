# Build & Functional Verification Report

- **Repository:** `jsoehner/ctm-ekm-lab`
- **Version:** `v2.0.0` (`VERSION`)
- **Verification Date:** `2026-11-20`
- **Verified By:** **Jeffs' Automated build and deploy agent**
- **Overall Status:** `VERIFIED` (Shell/Python Syntax, Compose YAML Validation, Live HTTPS + X.509 v3 mTLS Server, `curl` API Probe, and 8/8 Live `crypto-lab` Integration Tests)

---

## 1. Trusted OSS Split-Horizon Registry Configuration

Configured via `setup_trusted_oss_repo.py` (`--mode virtual`):

| Scope | Setting | Value |
| :--- | :--- | :--- |
| Local LAN | `TRUSTED_OSS_CACHE_URL` (`.env`, git-excluded) | `http://oss.jsigroup.local:8080` (`healthz`: HTTP `200`) |
| GitHub Actions WAN | `TRUSTED_OSS_CACHE_URL` repo variable | `https://jsigroup-oss.duckdns.org` |
| GitHub Actions Mode | `TRUSTED_OSS_MODE` / `TRUSTED_OSS_GPG_EMAIL` | `virtual` / `oss-signing@the-techy.com` |
| GitHub Actions mTLS | `OSS_MTLS_CLIENT_CERT` / `OSS_MTLS_CLIENT_KEY` | Configured as repository secrets |
| Git Hygiene | `.git/info/exclude` | `.env`, `uv.toml`, `.mvn/settings.xml`, `.mvn/maven.config`, `.npmrc` |

---

## 2. Verification Commands & Results

### 1. Shell, Python (`-W error`) & Docker Compose YAML Validation
```bash
for f in scripts/*.sh; do bash -n "$f"; done
python3 -W error -m py_compile mock-cm-ce/server.py vault-oidc-proxy/proxy.py
python3 -c 'import yaml; [yaml.safe_load(open(f)) for f in ["docker-compose.yml", "docker-compose.vault-oidc.yml"]]'
```
- **Shell Scripts:** `3/3` passed `bash -n`
- **Python Servers:** `2/2` passed `python3 -W error -m py_compile` (resolved `IndentationError` on line 305 of `vault-oidc-proxy/proxy.py` caught during verification)
- **Docker Compose Files:** `2/2` valid YAML (`docker-compose.yml`, `docker-compose.vault-oidc.yml`)

### 2. Live HTTPS + X.509 v3 mTLS Server & `curl` API Probe
Started `mock-cm-ce/server.py` on isolated port `18443` with `CM_REQUIRE_MTLS=true` and local X.509 v3 lab certificates (`certs/cm-server.crt`, `certs/lab-ca.crt`):
```bash
curl -sS --cacert certs/lab-ca.crt --cert certs/ekm-client.crt --key certs/ekm-client.key \
  -H "Content-Type: application/json" \
  -d '{"grant_type":"password","username":"admin","password":"lab-bootstrap-pass"}' \
  -o /dev/null -w "%{http_code}\n" https://127.0.0.1:18443/api/v1/auth/tokens
```
- **Result:** `HTTP 200` (Bearer JWT issued over strict X.509 v3 mutual TLS).

### 3. End-to-End Live `crypto-lab` Integration Suite (`test_ctm_integration.py`)
Executed `crypto-lab`'s full Python test suite against the live `https://127.0.0.1:18443` server:
- **Result:** **23 / 23 tests passed** (`Ran 23 tests in 2.164s OK`), including all **8 live CTM mTLS integration tests**:
  1. Key creation & metadata lookup (`POST/GET /api/v1/vault/keys2`)
  2. Live DEK envelope wrap/unwrap (`/api/v1/crypto/{encrypt,decrypt}`)
  3. Wrong AAD (`HTTP 400`) & tampered ciphertext (`InvalidTag`) rejection
  4. Cryptographic kill-switch (`deactivate` -> `HTTP 403`) & recovery (`reactivate`)
  5. Versioned key rotation (`v1 -> v2`) preserving `v1` envelope decryption
  6. Multi-tenant blast-radius isolation (`ctm-tenant-a` vs `ctm-tenant-b`)
  7. Invalid credentials & forged JWT rejection (`HTTP 401`)
  8. Missing mTLS client certificate rejection (`SSLError`)

---

## 3. Cleanup
- Stopped temporary `mock-cm-ce/server.py` (`PORT=18443`) and removed `/tmp/ctm-verify-venv`, `/tmp/pycache-ctm`, and `/tmp/ctm-mock-verify.log`.
- Verified `.env`, `.env.ciphertrust`, and `certs/` remain excluded from git tracking.
