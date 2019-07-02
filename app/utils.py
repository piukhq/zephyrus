from decimal import Decimal

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


def format_visa_transaction(raw_data: dict) -> dict:
    message_element = {
        item['Key']: item['Value']
        for item in raw_data['MessageElementsCollection']
    }

    transaction = {
        'time': message_element['Transaction.TimeStampYYMMDD'],
        'amount': int(Decimal(message_element['Transaction.ClearingAmount']) * 100),
        'payment_card_token': raw_data['CardId'],
        'mid': message_element['Transaction.VisaMerchantId'],
        'third_party_id': raw_data['ExternalUserId'],
        'currency_code': 'GBP'
    }

    for collection in raw_data['UserDefinedFieldsCollection']:
        if collection['Key'] == 'MessageType' and collection['Value'] == 'Auth':
            transaction['auth_code'] = raw_data['MessageId']

    return transaction
