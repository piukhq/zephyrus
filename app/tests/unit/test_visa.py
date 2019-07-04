import base64
from copy import copy
from unittest import mock

from falcon.testing import TestCase

import settings
from app import create_api


class TestVisa(TestCase):
    TESTING = True
    VISA_CREDENTIALS_HOLD = None
    VISA_TEST_CREDENTIALS = {'username': 'user@bink.test', 'password': 'Password1'}
    headers = {}
    visa_endpoint = '/auth_transactions/visa'
    payload = {
        "CardId": "e9636096-be12-f404-g595-006966f87787",
        "ExternalUserId": "1445552",
        "MessageElementsCollection": [
            {
                "Key": "Transaction.PanLastFour",
                "Value": "1234"
            },
            {
                "Key": "Transaction.VisaMerchantName",
                "Value": "GAP"
            },
            {
                "Key": "Transaction.VisaMerchantId",
                "Value": "60000088"
            },
            {
                "Key": "Transaction.VisaStoreName",
                "Value": "GAP STORE#45"
            },
            {
                "Key": "Transaction.VisaStoreId",
                "Value": "80004499"
            },
            {
                "Key": "Transaction.TimeStampYYMMDD",
                "Value": "2015-03-25T18:23:00"
            },
            {
                "Key": "Transaction.ClearingAmount",
                "Value": "11.23"
            },
            {
                "Key": "Offer.OfferId",
                "Value": "43426"
            }
        ],
        "MessageId": "6465b7cd-6126-4c94-887c-0b81fe506bc6",
        "MessageName": "endpoint429997350000008800",
        "UserDefinedFieldsCollection": [
            {
                "Key": "MessageType",
                "Value": "Auth"
            }
        ],
        "UserProfileId": "dac4307d-e03e-4024-a72b-0da7513eea14"
    }

    def setUp(self):
        self.VISA_CREDENTIALS_HOLD = settings.VISA_CREDENTIALS
        settings.VISA_CREDENTIALS = self.VISA_TEST_CREDENTIALS
        valid_credentials = base64.b64encode(b'user@bink.test:Password1').decode('utf-8')
        self.headers = {'Authorization': f'basic {valid_credentials}'}
        super(TestVisa, self).setUp()
        self.app = create_api()

    def tearDown(self):
        settings.VISA_CREDENTIALS = self.VISA_CREDENTIALS_HOLD
        super(TestVisa, self).tearDown()

    def test_valid_auth_credentials(self):
        resp = self.simulate_post('/auth_transactions/visa', headers=self.headers)
        self.assertEqual(resp.status_code, 200)

    def test_wrong_auth_credentials(self):
        headers = {'Authorization': 'basic wrong_data'}
        resp = self.simulate_post('/auth_transactions/visa', headers=headers)
        self.assertEqual(resp.status_code, 401)

    @mock.patch('requests.post')
    def test_successful_call(self, mock_request):
        mock_request.return_value.status_code = 201

        resp = self.simulate_post(self.visa_endpoint, json=self.payload, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(mock_request.called)

    def test_payload_extra_key(self):
        payload = {
            'WrongKey': 'InvalidPayload',
            **self.payload
        }
        expected_result = {'status_code': 100, 'error_msg': 'extra keys not allowed'}

        resp = self.simulate_post(self.visa_endpoint, json=payload, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, expected_result)

    def test_payload_wrong_data(self):
        payload = copy(self.payload)
        del payload['MessageElementsCollection']
        payload['MessageElementsCollection'] = [
            {
                'Key': 'Transaction.WrongKey',
                'Value': '11.80'
            }
        ]
        expected_result = {'status_code': 100, 'error_msg': 'Transaction.WrongKey is an invalid key.'}

        resp = self.simulate_post(self.visa_endpoint, json=payload, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, expected_result)
