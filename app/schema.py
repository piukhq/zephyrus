from voluptuous import Schema, Required, Optional

client_info = Schema({Required("organisation"): str, Required("client_id"): str, Required("secret"): str})

client_info_list = Schema([client_info])

auth_transaction_schema = Schema(
    {
        Required("time"): str,
        Optional("auth_code"): str,
        Required("amount"): str,
        Required("payment_card_token"): str,
        Required("mid"): str,
        Required("third_party_id"): str,
        Required("currency_code"): str,
    }
)
