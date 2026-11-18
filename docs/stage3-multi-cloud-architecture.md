# Stage 3: External KMS + Vault Transit + Cloud/SaaS Vaults

This stage unifies all three control-plane layers:

1. **Sovereign External KMS (`ctm-ekm-lab` / CipherTrust)**: Holds the Root KEK (`sovereign-root-kek`).
2. **HashiCorp Vault Transit (`vault-oidc-proxy`)**: Brokers Service KEKs to microservices with OIDC JWT + mTLS.
3. **Cloud & SaaS Vaults (Azure Key Vault, GCP Cloud KMS, SaaS)**: Hold cloud-side BYOK/EKM-linked Service KEKs wrapped by the Sovereign Root KEK.

## Security Posture Benefit
Deactivating `sovereign-root-kek` in the External KMS triggers **cascade revocation** across Vault Transit, Azure Key Vault, GCP Cloud KMS, and SaaS tenants simultaneously.

Run the reference orchestration in `crypto-lab`:
```bash
python3 python/stage3_multi_cloud_ekm_orchestration.py
```
