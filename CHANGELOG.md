# Changelog

All notable changes to `ctm-ekm-lab` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-11-20

### Architecture & Major Changes
- **Major Version Bump (`v2.0.0`):** Reflects the expansion from a single-stage local CipherTrust Manager mock (`v1.x`) to a **Three-Stage Sovereign EKM Control Plane** paired with `crypto-lab` `v2.0.0`:
  - **Stage 1:** Local HTTPS + X.509 v3 mTLS CipherTrust Manager CE mock (`mock-cm-ce/server.py`, `docker-compose.yml`).
  - **Stage 2:** Absorbed `ekm-demo` OIDC + mTLS Vault Transit EKM Proxy (`vault-oidc-proxy/proxy.py`, `docker-compose.vault-oidc.yml`, `config/vault.hcl`, `scripts/generate_vault_oidc_certs.sh`).
  - **Stage 3:** Multi-Cloud Sovereign EKM Cascade architecture (`docs/stage3-multi-cloud-architecture.md`, `docs/azure-gcp-ekm-integration.md`).
- **Updated Visual Infographic:** Replaced `docs/assets/ekms-control-plane-infographic.jpg` with the `v2.0.0` Three-Stage Sovereign EKM & PQC architecture infographic and added a Mermaid logical flow diagram to `README.md`.
- **Fixed `vault-oidc-proxy/proxy.py` Indentation Regression:** Fixed `IndentationError` on line 305 caught by `python3 -W error -m py_compile` during functional verification.

### Governance, Decisions & Verification
- **ADR-002 & ADR Index:** Added [ADRs/002-stage2-vault-oidc-proxy-and-stage3-multicloud-ekm.md](ADRs/002-stage2-vault-oidc-proxy-and-stage3-multicloud-ekm.md) and [ADRs/README.md](ADRs/README.md).
- **Trusted OSS Split-Horizon & Automated Verification:** Onboarded repository to Trusted OSS split-horizon registry with `.git/info/exclude` hygiene and verified end-to-end (including live HTTPS + mTLS server + all 8 live `crypto-lab` CTM integration tests) via **Jeffs' Automated build and deploy agent** ([docs/BUILD_VERIFICATION.md](docs/BUILD_VERIFICATION.md)).

## [1.1.0] - 2026-11-18

### Added
- Absorbed `ekm-demo` Vault Transit + Keycloak OIDC EKM Proxy stack and Stage 3 Multi-Cloud EKM documentation.

## [1.0.0] - 2026-11-18

### Added
- Initial CipherTrust Manager Community Edition EKM lab bootstrap, X.509 v3 mTLS PKI scripts, local HTTPS+mTLS mock server (`mock-cm-ce/server.py`), key rotation/reactivation/metadata endpoints, and ADR-001.
