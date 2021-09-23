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
