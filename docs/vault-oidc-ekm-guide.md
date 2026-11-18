# Vault Transit + Keycloak OIDC EKM Proxy (Absorbed from `ekm-demo`)

This staged profile adds a three-layer External Key Manager (EKM) stack alongside the CipherTrust Manager CE lab:

1. **Layer 7 (Application Identity)**: Keycloak OIDC JWT validation via JWKS (`http://localhost:8080/realms/ekm-demo`).
2. **Layer 4 (Transport Security)**: Mutual TLS (`mTLS`) between the Flask EKM-Proxy and HashiCorp Vault (`config/vault.hcl`).
3. **Layer 1 (Cryptographic Isolation)**: HashiCorp Vault Transit Secrets Engine (`my-master-kek`), ensuring root KEKs never leave Vault.

## Quickstart

```bash
# 1. Generate Vault + Proxy mTLS certificates
bash scripts/generate_vault_oidc_certs.sh

# 2. Launch Keycloak, Vault, and EKM-Proxy
docker compose -f docker-compose.vault-oidc.yml up -d
```

Once running, `crypto-lab` can target `EKM_PROXY_URL=http://localhost:5050` using `python/vault_ekm_proxy_example.py`.
