from voluptuous import Schema, Required, Optional, Invalid

client_info = Schema({
    Required('organisation'): str,
    Required('client_id'): str,
    Required('secret'): str
})

client_info_list = Schema([client_info])

auth_transaction = Schema({
    Required('time'): str,
    Optional('auth_code'): str,
    Required('amount'): str,
    Required('payment_card_token'): str,
    Required('mid'): str,
    Required('third_party_id'): str,
    Required('currency_code'): str,
})


def allowed_elements_visa(key: str) -> str:
    valid_keys = (
        'Transaction.PanLastFour',
        'Transaction.VisaMerchantId',
        'Transaction.VisaMerchantName',
        'Transaction.VisaStoreId',
        'Transaction.VisaStoreName',
        'Transaction.TimeStampYYMMDD',
        'Transaction.ClearingAmount',
        'Offer.OfferId'
    )
    if key not in valid_keys:
        raise Invalid(f"{key} is an invalid key.")
    return key


visa_auth_transaction = Schema({
    Required('CardId'): str,
    Required('ExternalUserId'): str,
    Required('MessageId'): str,
    Required('MessageName'): str,
    Required('UserProfileId'): str,
    Optional('MessageElementsCollection'): Schema([{
        Optional('Key'): allowed_elements_visa,
        Optional('Value'): str
    }]),
    Optional('UserDefinedFieldsCollection'): Schema([{
        Optional('Key'): str,
        Optional('Value'): str
    }]),
})
