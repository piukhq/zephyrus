import requests

import settings
from app import CustomException
from app.errors import CONNECTION_ERROR


def format_data(data):
    formatted_data = {
        'payment_card_token': data['cm_alias'],
        'time': data['transaction_time'],
        'amount': int(float(data['transaction_amount']) * 100),   # conversion to pence
        'mid': data['merchant_number'],
        'third_party_id': data['offer_id'],
        'auth_code': data['transaction_id'],
        'currency_code': 'GBP'
    }

    return formatted_data


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