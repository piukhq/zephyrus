from voluptuous import Invalid, Schema, Required, Optional


def _allowed_collection_elements(key: str) -> str:
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


visa_transaction_schema = Schema({
    Required('CardId'): str,
    Required('ExternalUserId'): str,
    Required('MessageId'): str,
    Required('MessageName'): str,
    Required('UserProfileId'): str,
    Optional('MessageElementsCollection'): Schema([{
        Optional('Key'): _allowed_collection_elements,
        Optional('Value'): str
    }]),
    Optional('UserDefinedFieldsCollection'): Schema([{
        Optional('Key'): str,
        Optional('Value'): str
    }]),
})
