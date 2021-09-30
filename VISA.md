# VISA Endpoint

The VISA endpoint is `/auth_transactions/visa`. Test it with the following cURL.

## Auth transaction

```shell
 curl --url http://localhost:9000/auth_transactions/visa \
  --header 'Content-Type: application/json' \
  --data '{
  "CardId":"8cdf34a4-0921-4857-8e47-f58a66bfc5c3",
  "ExternalUserId":"bb573d55acbc4ba2a44f5202e21",
  "MessageElementsCollection":[
    {
      "Key":"Transaction.PanLastFour",
      "Value":"0000"
    },{
      "Key":"Transaction.BillingAmount",
      "Value":"1.05"
    },{
      "Key":"Transaction.TimeStampYYMMDD",
      "Value":"2021-09-29T12:56:36"
    },{
      "Key":"Transaction.MerchantCardAcceptorId",
      "Value":"35730602"
    },{
      "Key":"Transaction.MerchantAcquirerBin",
      "Value":"400701"
    },{
      "Key":"Transaction.TransactionAmount",
      "Value":"1.05"
    },{
      "Key":"Transaction.VipTransactionId",
      "Value":"481272465966120"
    },{
      "Key":"Transaction.VisaMerchantName",
      "Value":"ICELAND FROZEN FOODS"
    },{
      "Key":"Transaction.VisaMerchantId",
      "Value":"20298840"
    },{
      "Key":"Transaction.VisaStoreName",
      "Value":"ICELAND FROZEN FOODS"
    },{
      "Key":"Transaction.VisaStoreId",
      "Value":"415443560"
    },{
      "Key":"Transaction.CurrencyCodeNumeric",
      "Value":"826"
    },{
      "Key":"Transaction.BillingCurrencyCode",
      "Value":"826"
    },{
      "Key":"Transaction.SettlementDate",
      "Value":""
    },{
      "Key":"Transaction.SettlementAmount",
      "Value":"0"
    },{
      "Key":"Transaction.SettlementCurrencyCodeNumeric",
      "Value":"0"
    },{
      "Key":"Transaction.MerchantGroup.0.Name",
      "Value":"BINK_DEFAULT_MRCH_GRP"
    },{
      "Key":"Transaction.MerchantGroup.0.ExternalId",
      "Value":"ICELAND-BONUS-CARD"
    },{
      "Key":"Transaction.AuthCode",
      "Value":"083636"
    }],
  "MessageId":"c4e865b5-e467-440a-bb39-3551366b78d4",
  "MessageName":"endpoint584723810000000303",
  "UserDefinedFieldsCollection":[{"Key":"TransactionType","Value":"AUTH"}],
  "UserProfileId":"97f52757-22da-448c-8a64-90ebd9dc2e33"
}'
```

Response:
```json
{"error_msg": "", "status_code": "0"}
```