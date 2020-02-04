import arrow
import logging
import jose
import requests

from shared_config_storage.vault.secrets import VaultError, read_vault
from settings import VAULT_TOKEN, VAULT_URL, VAULT_PATH

_client_info = None


def load_secrets():

    global _client_info

    logging.info(f"Obtain secrets from vault at {VAULT_URL}  secrets: {VAULT_PATH}")
    try:
        if _client_info is None:
            _client_info = read_vault(VAULT_PATH, VAULT_URL, VAULT_TOKEN)
    except requests.RequestException as e:
        logging.exception(f"Unable to request the secrets from the Vault. {e}")
        raise VaultError(f'Unable to request the secrets from the Vault {e}') from e
    return _client_info


def generate_jwt(slug):
    client_secrets = load_secrets()
    client_id = client_secrets[slug]["client_id"]
    secret = client_secrets[slug]["secret"]
    if client_id and client_id.strip() and secret and secret.strip():
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
    else:
        return None
