# ADR-001: Local eKMS Control Plane and mTLS Architecture

## Status
Accepted

## Context
Thales CipherTrust Manager Community Edition (CM CE) is distributed as a full virtual appliance (OVA/QCOW2/VHD) requiring ~8 GB RAM and portal-gated download. Embedding appliance deployment inside `crypto-lab` would bloat the reference repo and break lightweight CI.

## Decision
1. **Separate Companion Repository (`ctm-ekm-lab`)**: House CM CE bootstrap scripts, X.509 v3 PKI generation (`scripts/generate_mtls_certs.sh`), and a lightweight local HTTPS + mTLS REST server (`mock-cm-ce/server.py` + `docker-compose.yml`) in `ctm-ekm-lab`.
2. **Protocol Parity for Live Testing**: Implement `/api/v1/auth/tokens`, `/api/v1/vault/keys2` (create, metadata lookup, `deactivate`, `reactivate`, `rotate`), and `/api/v1/crypto/{encrypt,decrypt}` over strict X.509 v3 mTLS (`CM_REQUIRE_MTLS=true`) so `crypto-lab` runs identical client code against either the local lab server or a full CM CE appliance.

## Consequences
- Any developer can stand up a sovereign eKMS control plane locally in seconds without waiting on a multi-GB OVA download.
- Swapping `CIPHERTRUST_URL` transitions seamlessly from the local lab server to a production/community CipherTrust appliance.
