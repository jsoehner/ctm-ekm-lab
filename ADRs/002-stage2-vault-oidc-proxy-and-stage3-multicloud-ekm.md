# ADR-002: Stage 2 Vault Transit + Keycloak OIDC Proxy & Stage 3 Multi-Cloud Sovereign EKM Architecture

## Metadata

| Field | Value |
|---|---|
| ADR ID | ADR-002 |
| Status | Accepted |
| Created Date | 2026-11-20 |
| Decision Date | 2026-11-20 |
| Effective Date | 2026-11-20 |
| Architecture Domain | Sovereign EKM / Identity & Access / Multi-Cloud Security |
| Scope | `ctm-ekm-lab` (`v2.0.0`) paired with `crypto-lab` (`v2.0.0`) |

---

## Context

[ADR-001](001-local-ekm-control-plane-and-mtls-architecture.md) established `ctm-ekm-lab` as a local HTTPS + X.509 v3 mTLS CipherTrust Manager Community Edition control plane (Stage 1). As the sovereign key management architecture matured, two additional layers were required:
1. **Stage 2 — Defense-in-Depth OIDC + mTLS EKM Proxy:** Previously maintained in a separate `ekm-demo` repository, combining Layer-7 Keycloak OIDC JWT validation, Layer-4 mutual TLS termination, and Layer-1 HashiCorp Vault Transit encryption.
2. **Stage 3 — Multi-Cloud Sovereign EKM Cascade:** Connecting external sovereign KEKs (CipherTrust / Vault) to cloud-native EKM services (Azure CCKM / Managed HSM and GCP Cloud EKM) while guaranteeing zero cloud key custody.

Maintaining a third standalone `ekm-demo` repository fragmented compose stacks, PKI scripts, and documentation across three repos.

---

## Alternatives Considered

| Option | Pros | Cons | Disposition |
|---|---|---|---|
| **Option 1: Keep `ekm-demo` as a third separate repository** | Independent release cadence. | Duplicated PKI generation scripts, fragmented Docker Compose topologies, and disjoint developer onboarding. | **Rejected** |
| **Option 2: Consolidate Stage 1 + Stage 2 + Stage 3 Infrastructure in `ctm-ekm-lab` (`v2.0.0`) (Selected)** | Unified sovereign EKM infrastructure repo (`docker-compose.yml` + `docker-compose.vault-oidc.yml`), shared mTLS PKI patterns, paired `v2.0.0` versioning with `crypto-lab`, and single automated verification gate. | Slightly larger compose/documentation surface in `ctm-ekm-lab`. | **Selected** |

---

## Decision

1. **Absorb Stage 2 Vault + OIDC EKM Proxy (`ekm-demo`):** House `vault-oidc-proxy/proxy.py`, `docker-compose.vault-oidc.yml`, `config/vault.hcl`, `scripts/generate_vault_oidc_certs.sh`, and `docs/vault-oidc-ekm-guide.md` directly inside `ctm-ekm-lab`.
2. **Formalize Stage 3 Multi-Cloud EKM Patterns:** Maintain `docs/stage3-multi-cloud-architecture.md` and `docs/azure-gcp-ekm-integration.md` alongside the Stage 1 and Stage 2 stacks.
3. **Paired `v2.0.0` Release & Automated Verification:** Bump `ctm-ekm-lab` to `v2.0.0` (matching `crypto-lab` `v2.0.0`), onboard to the split-horizon Trusted OSS registry with `.git/info/exclude` hygiene, and require live HTTPS + mTLS verification (including `crypto-lab`'s 8 live integration tests) via **Jeffs' Automated build and deploy agent** (`docs/BUILD_VERIFICATION.md`).

---

## Consequences

- **Positive:** Developers and architects have one authoritative infrastructure repo (`ctm-ekm-lab`) covering all three stages of sovereign EKM, cleanly separated from `crypto-lab`'s lightweight multi-language reference code.
- **Trade-offs:** Local lab certificates (`certs/`) and `.env.ciphertrust` remain git-ignored and generated on demand to prevent credential leakage.
