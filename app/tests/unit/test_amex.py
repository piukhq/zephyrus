from unittest import mock

from falcon.testing import TestCase

from app import create_app
from app.clients import ClientInfo


@mock.patch.object(ClientInfo, "get_client")
@mock.patch("jose.jwt.decode")
@mock.patch("app.queue.add")
class TestAmex(TestCase):
    TESTING = True
    headers = {"Authorization": "token wwed"}
    amex_endpoint = "/auth_transactions/amex"

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

    def test_process_auth_transaction_success(self, _, mock_decode, mock_get_client):
        resp = self.simulate_post(self.amex_endpoint, json=self.payload, headers=self.headers)

        self.assertTrue(mock_decode.called)
        self.assertTrue(mock_get_client.called)
        self.assertEqual(resp.status_code, 200)
