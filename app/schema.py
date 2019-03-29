from voluptuous import Schema, Required, Optional

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

visa_optional_transaction = Schema({
    Optional('PanLastFour'): str,
    Optional('VisaMerchantId'): str,
    Optional('VisaMerchantName'): str,
    Optional('VisaStoreId'): str,
    Optional('VisaStoreName'): str,
    Optional('TimeStampYYMMDD'): str,
    Optional('TransactionAmount'): str,
})

visa_optional_offer = Schema({
    Optional('OfferId'): str,
})

visa_auth_transaction = Schema({
    Required('CardId'): str,
    Required('ExternalUserId'): str,
    Required('MessageId'): str,
    Required('MessageName'): str,
    Required('UserProfileId'): str,
    Optional('Transaction'): visa_optional_transaction,
    Optional('Offer'): visa_optional_offer,
    Optional('UserDefinedFieldsCollection'): str,
})
