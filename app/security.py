import arrow
import jose
import json

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import HttpResponseError
from functools import lru_cache
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)

import settings


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=3, max=12),
    reraise=True,
)
@lru_cache(16)
def load_secrets(secret_name: str):
    if settings.KEYVAULT_URI is None:
        raise Exception("Vault Error: settings.KEYVAULT_URI not set")

    kv_credential = DefaultAzureCredential()
    kv_client = SecretClient(vault_url=settings.KEYVAULT_URI, credential=kv_credential)

    try:
        return json.loads(kv_client.get_secret(secret_name).value)
    except HttpResponseError as e:
        raise Exception(f"Vault Error: {e}") from e


def generate_jwt(slug, credentials):
    client_secrets = load_secrets("data-auth-transactions")
    client_id = client_secrets[slug].get("client_id", "").strip()
    secret = client_secrets[slug].get("secret", "").strip()

    if not validate_credentials(credentials, client_id, secret):
        return None

    time_now = arrow.now()
    claims = {
        "exp": time_now.shift(minutes=+5).int_timestamp,
        "nbf": time_now.int_timestamp,
        "iss": "bink",
        "aud": "https://api.gb.bink.com",
        "iat": time_now.int_timestamp,
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
