import arrow
import logging
import jose
import requests

from shared_config_storage.vault.secrets import VaultError, read_vault
from settings import VAULT_TOKEN, VAULT_URL

_client_info = None


def load_secrets(vault_path: str):

    global _client_info

    try:
        if _client_info is None:
            _client_info = read_vault(vault_path, VAULT_URL, VAULT_TOKEN)
    except requests.RequestException as e:
        logging.exception(f"Unable to request the secrets from the Vault. {e}")
        raise VaultError(f"Unable to request the secrets from the Vault {e}") from e
    return _client_info


def generate_jwt(slug, credentials):
    client_secrets = load_secrets("/data/auth_transactions")
    client_id = client_secrets[slug].get("client_id", "").strip()
    secret = client_secrets[slug].get("secret", "").strip()

    if not validate_credentials(credentials, client_id, secret):
        return None

    time_now = arrow.now()
    claims = {
        "exp": time_now.shift(minutes=+5).timestamp,
        "nbf": time_now.timestamp,
        "iss": "bink",
        "aud": "https://api.bink.com",
        "iat": time_now.timestamp,
        "sub": client_id,
    }
    return jose.jwt.encode(claims, key=secret)


def validate_credentials(credentials, vault_client_id, vault_secret):
    is_valid = False
    if (
        credentials["client_id"]
        and credentials["client_id"].strip()
        and credentials["client_secret"]
        and credentials["client_secret"].strip()
    ):
        if credentials["client_id"] == vault_client_id and credentials["client_secret"] == vault_secret:
            is_valid = True
    return is_valid
