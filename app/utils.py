import requests

import settings
from app.celery import app as celery_app
from app.errors import CONNECTION_ERROR, CustomException


def send_to_hermes(transaction: dict) -> None:
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


def send_to_zagreus(transaction: dict, provider: str, location: str = '') -> None:
    transaction['provider'] = provider
    transaction['location'] = location
    celery_app.send_task('auth-transactions.save', args=[transaction, ])
