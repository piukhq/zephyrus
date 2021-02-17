from unittest import mock

from falcon.testing import TestCase

from app import create_app


@mock.patch("jose.jwt.decode")
@mock.patch("app.queue.add")
class TestAmex(TestCase):
    TESTING = True
    headers = {"Authorization": "token wwed"}

    payload = {
        "transaction_time": "2013-05-23 20:30:15",
        "transaction_id": "12349",
        "transaction_amount": "249.99",
        "cm_alias": "88578a9d-0130-4cd9-b099-92977cc0345f",
        "merchant_number": "1042789701",
        "offer_id": "1225",
    }

    def setUp(self):
        super(TestAmex, self).setUp()
        self.app = create_app()

    @mock.patch("app.amex.authentication.load_secrets")
    def test_process_auth_transaction_success(self, _, mock_decode, mock_load_secrets):
        amex_endpoint = "/auth_transactions/amex"
        mock_load_secrets.return_value = {"amex": {"client_id": "test123456789", "secret": "testsecret987654321"}}
        resp = self.simulate_post(amex_endpoint, json=self.payload, headers=self.headers)

        self.assertTrue(mock_decode.called)
        self.assertEqual(resp.status_code, 200)
