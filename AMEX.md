# AMEX Endpoints

`/auth_transactions/authorize` - AMEX authentication endpoint

`/auth_transactions/amex` - AMEX Auth transactions endpoint

## Authentication

Takes a client id and secret from AMEX, compares them to equivelents stored in the KeyVault

```shell
curl --url http://localhost:9000/auth_transactions/authonrize \
  --header 'Content-Type: application/json' \
  --data '{"client_id":"DWHafwf8OLzbzL7vIQfZ6jXuYsuQf6EShJ4IkKoGBIwNd0xfNG","client_secret":"dFuupR8r2TJPYUxpByBVBHHkJiR4nriZDCWndD4755jMsX0usq"}'
```

Response like:
```json
{"api_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MzMwMDY3NzgsIm5iZiI6MTYzMzAwNjQ3OCwiaXNzIjoiYmluayIsImF1ZCI6Imh0dHBzOi8vYXBpLmdiLmJpbmsuY29tIiwiaWF0IjoxNjMzMDA2NDc4LCJzdWIiOiJEV0hhZndmOE9MemJ6TDd2SVFmWjZqWHVZc3VRZjZFU2hKNElrS29HQkl3TmQweGZORyJ9.WqkOzEqdt8mOkOwoQHvXFALvkXr-eUEJiwyOuUNcpnA"}
```

The JWT is a HS256 signed token:
```json
{
  "exp": 1633006778,
  "nbf": 1633006478,
  "iss": "bink",
  "aud": "https://api.gb.bink.com",
  "iat": 1633006478,
  "sub": "DWHafwf8OLzbzL7vIQfZ6jXuYsuQf6EShJ4IkKoGBIwNd0xfNG"
}
```


## Auth Transactions

```shell
curl --url http://localhost:9000/auth_transactions/amex \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Token JSON_WEB_TOKEN_HERE' \
  --data '{
  "transaction_time":"2021-09-29 04:39:37",
  "transaction_id":"002864977578472",
  "offer_id":"0",
  "cm_alias":"d49f6b4ade1b4895af3524110bf",
  "transaction_amount":"9.90",
  "merchant_number":"9447911819",
  "approval_code":"829162",
  "transaction_currency":"GBP"
}'
```

Response:
```json
{"success": true}
```

## Settlement Transactions

TODO