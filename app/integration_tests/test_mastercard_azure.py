from app import create_app
from flask_testing import TestCase
from flask import make_response
from unittest.mock import patch
from app.tests.test_helpers.signed_xml import Certificate, azure_write, SignedXML, MockMastercardAuthTransaction,\
    valid_transaction_xml
import settings


class TestSelfSignedCertificateOnAzure(TestCase):
    """ Warning only use for integration testing with Azure
    The test will add a test certificate to mastercard_test area so
    will not over write any manually installed certificates

    """

    TESTING = True
    mastercard_endpoint = '/auth_transactions/mastercard'

    def create_app(self):
        return create_app(self, )

    @classmethod
    def setUpClass(cls):
        settings.MASTERCARD_SIGNING_CERTIFICATE_AZURE_BLOB_NAME = "mastercard_test/test_self_sign_perm_cert"
        cls.cert = Certificate()
        azure_write(settings.MASTERCARD_SIGNING_CERTIFICATE_AZURE_BLOB_NAME, cls.cert.root_pem_certificate)

    def setUp(self):
        pass

    def test_azure_cert(self):
        signed_xml = SignedXML(MockMastercardAuthTransaction(), signing_cert=self.cert)
        with patch('app.utils.requests.post') as mock_post:
            mock_post.return_value = make_response("", 201)
            resp = self.client.post(self.mastercard_endpoint, data=signed_xml.xml, content_type="text/xml")
        self.assertTrue(valid_transaction_xml(resp.json), "Invalid XML response")
        self.assert200(resp)
