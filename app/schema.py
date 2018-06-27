from voluptuous import Schema, Required

client_info = Schema({
    Required('organisation'): str,
    Required('client_id'): str,
    Required('secret'): str
})

client_info_list = Schema([client_info])

amex_auth_transaction = Schema({
    Required('transaction_time'): str,
    Required('transaction_id'): str,
    Required('transaction_amount'): str,
    Required('cm_alias'): str,
    Required('merchant_number'): str,
    Required('offer_id'): str,
})

auth_transaction = Schema({
    Required('transaction_time'): str,
    Required('transaction_id'): str,
    Required('transaction_amount'): str,
    Required('cm_alias'): str,
    Required('merchant_number'): str,
    Required('offer_id'): str,
})