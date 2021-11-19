from unittest import mock

from falcon.testing import TestCase

from app import create_app


@mock.patch("app.queue.add")
class TestVisa(TestCase):
    TESTING = True
    visa_endpoint = "/auth_transactions/visa"
    payload = {
        "CardId": "e9636096-be12-f404-g595-006966f87787",
        "ExternalUserId": "1445552",
        "MessageElementsCollection": [
            {"Key": "Transaction.PanLastFour", "Value": "1234"},
            {"Key": "Transaction.VisaMerchantName", "Value": "GAP"},
            {"Key": "Transaction.VisaMerchantId", "Value": "60000088"},
            {"Key": "Transaction.VisaStoreName", "Value": "GAP STORE#45"},
            {"Key": "Transaction.VisaStoreId", "Value": "80004499"},
            {"Key": "Transaction.TimeStampYYMMDD", "Value": "2015-03-25T18:23:00"},
            {"Key": "Transaction.ClearingAmount", "Value": "11.23"},
            {"Key": "Offer.OfferId", "Value": "43426"},
        ],
        "MessageId": "6465b7cd-6126-4c94-887c-0b81fe506bc6",
        "MessageName": "endpoint429997350000008800",
        "UserDefinedFieldsCollection": [{"Key": "MessageType", "Value": "Auth"}],
        "UserProfileId": "dac4307d-e03e-4024-a72b-0da7513eea14",
    }

    def setUp(self):
        super(TestVisa, self).setUp()
        self.app = create_app()

    def tearDown(self):
        super(TestVisa, self).tearDown()

    def test_successful_call(self, _):
        resp = self.simulate_post(self.visa_endpoint, json=self.payload)
        self.assertEqual(resp.status_code, 200)

    def test_no_payload_request(self, _):
        resp = self.simulate_post(self.visa_endpoint, json={})
        self.assertEqual(resp.status_code, 200)

    def test_return_transaction(self, _):
        ret_payload = {
            "CardId": "caff902c-db4d-eb11-813a-f403433e0c0d",
            "ExternalUserId": "QuDOmG7HzPLZttyEcrQxwlgFKvq",
            "MessageElementsCollection": [
                {"Key": "ReturnTransaction.DateTime", "Value": "1/5/2021 3:12:43 PM"},
                {"Key": "ReturnTransaction.Amount", "Value": "5.0"},
                {"Key": "ReturnTransaction.CurrencyCode", "Value": "826"},
                {"Key": "ReturnTransaction.AcquirerAmount", "Value": "5.0"},
                {"Key": "ReturnTransaction.AcquirerCurrencyCode", "Value": "826"},
                {"Key": "ReturnTransaction.AcquirerBIN", "Value": "469818"},
                {"Key": "ReturnTransaction.CardAcceptorIdCode", "Value": "22784392"},
                {"Key": "ReturnTransaction.VisaMerchantId", "Value": "20298840"},
                {"Key": "ReturnTransaction.VisaStoreId", "Value": "261035990"},
                {
                    "Key": "ReturnTransaction.VisaMerchantName",
                    "Value": "ICELAND FROZEN FOODS",
                },
                {"Key": "ReturnTransaction.VisaStoreName", "Value": "ICELAND"},
                {
                    "Key": "ReturnTransaction.MerchantGroupName.0.Name",
                    "Value": "BINK_DEFAULT_MRCH_GRP",
                },
                {
                    "Key": "ReturnTransaction.MerchantGroupName.0.ExternalId",
                    "Value": "ICELAND-BONUS-CARD",
                },
                {"Key": "ReturnTransaction.TransactionUSDAmount", "Value": "6.77"},
                {
                    "Key": "ReturnTransaction.SettlementId",
                    "Value": "BBA1103607926820210105",
                },
                {
                    "Key": "ReturnTransaction.VipTransactionId",
                    "Value": "631005547637588",
                },
                {"Key": "ReturnTransaction.AuthCode", "Value": ""},
            ],
            "MessageId": "0c1286bb-3cb4-413f-821a-0da91007841f",
            "MessageName": "endpoint584612460000000251",
            "UserDefinedFieldsCollection": [{"Key": "TransactionType", "Value": "RETURN"}],
            "UserProfileId": "c170543a-39bd-40b2-bd77-f4aa132fe4f7",
        }
        resp = self.simulate_post(self.visa_endpoint, json=ret_payload)
        self.assertEqual(resp.status_code, 200)
