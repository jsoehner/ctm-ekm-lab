# Connecting CipherTrust Manager CE to Azure & GCP EKM

## 1. GCP Cloud EKM (External Key Manager)
1. Enable the **Cloud EKM** interface in CipherTrust Manager (`Admin Settings -> Interfaces -> EKM`).
2. Create an external key (`demo-app-kek`) and grant `Use` / `Wrap` / `Unwrap` permissions to the GCP project service account (`service-<project-number>@gcp-sa-ekms.iam.gserviceaccount.com`).
3. In GCP Cloud KMS, create a `KeyRing` and an `External` (`EXTERNAL_VPC` or internet-routable TLS) `CryptoKey` pointing to the CipherTrust EKM key URI.
4. Deactivating or destroying the key in CipherTrust Manager immediately blocks GCP Cloud KMS `wrap`/`unwrap` calls.

## 2. Azure Key Vault / CCKM
1. For **BYOK without EKM**, use `python/azure_keyvault_byok_cmk_example.py` in `crypto-lab` to wrap keys with the Azure Managed HSM KEK (`RSA-OAEP-256` + `AES-256-KWP`).
2. For **CipherTrust Cloud Key Manager (CCKM)** orchestration, register your Azure Entra ID App Registration in CipherTrust CCKM to manage key rotation, synchronization, and revocation policies centrally.
