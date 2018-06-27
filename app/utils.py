import requests

import settings
from app import CustomException
from app.errors import CONNECTION_ERROR


def save_transaction(transaction):
    headers = {
        'Authorization': f'token {settings.SERVICE_API_KEY}'
    }
    try:
        resp = requests.post(f'{settings.HERMES_URL}/payment_cards/auth_transaction',
                             headers=headers,
                             json=transaction)
    except requests.RequestException as e:
        raise CustomException(CONNECTION_ERROR) from e

    if resp.status_code != 201:
        raise CustomException(CONNECTION_ERROR)
