from decimal import Decimal

import requests

import settings
from app.errors import CONNECTION_ERROR, CustomException


def save_transaction(transaction: dict) -> None:
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


def format_visa_transaction(raw_data: dict) -> dict:
    message_elements = {
        item['Key']: item['Value']
        for item in raw_data['MessageElementsCollection']
    }
    user_defined_collections = {
        item['Key']: item['Value']
        for item in raw_data.get('UserDefinedFieldsCollection', [])
    }

    transaction = {
        'time': message_elements['Transaction.TimeStampYYMMDD'],
        'amount': int(Decimal(message_elements['Transaction.ClearingAmount']) * 100),
        'payment_card_token': raw_data['CardId'],
        'mid': message_elements['Transaction.VisaMerchantId'],
        'third_party_id': raw_data['ExternalUserId'],
        'currency_code': 'GBP'
    }

    if user_defined_collections.get('MessageType') == 'Auth':
        transaction['auth_code'] = raw_data['MessageId']

    return transaction
