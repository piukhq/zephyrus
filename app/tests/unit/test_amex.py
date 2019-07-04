from unittest import mock
from unittest.mock import MagicMock

import requests
from falcon.testing import TestCase

from app import create_api
from app.clients import ClientInfo


@mock.patch.object(ClientInfo, 'get_client')
@mock.patch('jose.jwt.decode')
class TestAmex(TestCase):
    TESTING = True
    headers = {'Authorization': 'token wwed'}
    amex_endpoint = '/auth_transactions/amex'

    payload = {
        "transaction_time": "2013-05-23 20:30:15",
        "transaction_id": "12349",
        "transaction_amount": "249.99",
        "cm_alias": "88578a9d-0130-4cd9-b099-92977cc0345f",
        "merchant_number": "1042789701",
        "offer_id": "1225"
    }

    def setUp(self):
        super(TestAmex, self).setUp()
        self.app = create_api()

    @mock.patch('requests.post')
    def test_process_auth_transaction_success(self, mock_request, mock_decode, mock_get_client):
        mock_request.return_value.status_code = 201

        resp = self.simulate_post(self.amex_endpoint, json=self.payload, headers=self.headers)

        self.assertTrue(mock_decode.called)
        self.assertTrue(mock_get_client.called)
        self.assertTrue(mock_request.called)
        self.assertEqual(resp.status_code, 200)

    def test_invalid_format_raises_exception(self, mock_decode, mock_get_client):
        payload = {
            "transaction_time": "2013-05-23 20:30:15",
            "transaction_id": "12349",
            "cm_alias": "88578a9d-0130-4cd9-b099-92977cc0345f",
            "offer_id": "1225"
        }

        resp = self.simulate_post(self.amex_endpoint, json=payload, headers=self.headers)
        self.assertTrue(mock_decode.called)
        self.assertTrue(mock_get_client.called)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json['name'], 'INVALID_DATA_FORMAT')

    @mock.patch('requests.post')
    def test_error_connecting_to_hermes_raises_exception(self, mock_request, mock_decode, mock_get_client):
        mock_request.side_effect = requests.ConnectionError
        resp = self.simulate_post(self.amex_endpoint, json=self.payload, headers=self.headers)

        self.assertTrue(mock_decode.called)
        self.assertTrue(mock_get_client.called)
        self.assertEqual(resp.status_code, 545)
        self.assertEqual(resp.json['name'], 'CONNECTION_ERROR')

    @mock.patch('requests.post')
    def test_error_from_hermes_raises_exception(self, mock_request, mock_decode, mock_get_client):
        hermes_resp = MagicMock()
        hermes_resp.status_code = 400
        mock_request.return_value = hermes_resp

        resp = self.simulate_post(self.amex_endpoint, json=self.payload, headers=self.headers)

        self.assertTrue(mock_decode.called)
        self.assertTrue(mock_get_client.called)
        self.assertEqual(resp.status_code, 545)
        self.assertEqual(resp.json['name'], 'CONNECTION_ERROR')
