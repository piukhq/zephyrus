from voluptuous import Schema, Required

client_info = Schema({
    Required('organisation'): str,
    Required('client_id'): str,
    Required('secret'): str
})

client_info_list = Schema([client_info])

auth_transaction = Schema({
    Required('time'): str,
    Required('auth_code'): str,
    Required('amount'): str,
    Required('payment_card_token'): str,
    Required('mid'): str,
    Required('third_party_id'): str,
    Required('currency_code'): str,
})

auth_transaction = Schema({
    Required('transaction_time'): str,
    Required('transaction_id'): str,
    Required('transaction_amount'): str,
    Required('cm_alias'): str,
    Required('merchant_number'): str,
    Required('offer_id'): str,
})