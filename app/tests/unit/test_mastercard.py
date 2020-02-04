from unittest.mock import patch

import falcon
import lxml.etree as etree
from falcon.testing import TestCase

from app import create_app
from app.mastercard.process_xml_request import mastercard_request, get_valid_signed_data_elements
from app.tests.test_helpers.signed_xml import (
    Certificate,
    SignedXML,
    MockMastercardAuthTransaction,
    valid_transaction_xml,
    UnsignedXML,
)


@patch("app.queue.add")
class MasterCardAuthTestCases(TestCase):
    TESTING = True
    mastercard_endpoint = "/auth_transactions/mastercard"
    headers = {"Content-Type": falcon.MEDIA_XML}

    @classmethod
    def setUpClass(cls):
        # Create a self-signed "signing" certificate and private key for making signed XML which
        # includes the generated signature and certificate generated form the above.
        # note: MasterCard will send us only the signing certificate (root certificate) and confirmation of the
        # common name used in that certificate.
        # during tests the certificate above is used to mock the sign process MasterCard will do
        # The signed XML is validated against the signed xml produced  simulating the message sent to us.
        # get_certificate_details gets the signing certificate and common name which is normally stored on azure.
        cls.cert = Certificate()

    def setUp(self):
        super(MasterCardAuthTestCases, self).setUp()
        self.app = create_app()

    def test_valid_transaction_response(self, _):
        signed_xml = SignedXML(MockMastercardAuthTransaction(), signing_cert=self.cert)
        with patch("app.mastercard.process_xml_request.azure_read_cert") as mock_certificate:
            mock_certificate.return_value = signed_xml.mock_signing_certificate()
            resp = self.simulate_post(self.mastercard_endpoint, body=signed_xml.xml, headers=self.headers)
        self.assertTrue(valid_transaction_xml(resp.json), "Invalid XML response")
        self.assertEqual(resp.status_code, 200)

    def test_invalid_transaction_response_to_wrong_cert(self, _):
        signed_xml = SignedXML(MockMastercardAuthTransaction(), signing_cert=self.cert)
        with patch("app.mastercard.process_xml_request.azure_read_cert") as mock_certificate:
            cert = Certificate()
            mock_certificate.return_value = cert.root_pem_certificate
            resp = self.simulate_post(self.mastercard_endpoint, body=signed_xml.xml, headers=self.headers)
        self.assertTrue(valid_transaction_xml(resp.json), "Invalid XML response")
        self.assertEqual(resp.status_code, 403)

    def test_invalid_transaction_response_no_amount_in_xml(self, _):
        xml_obj = UnsignedXML(MockMastercardAuthTransaction())
        xml_obj.remove("transAmt")
        print(xml_obj.xml)
        signed_xml = SignedXML(xml_obj.get_transaction(), signing_cert=self.cert)

        with patch("app.mastercard.process_xml_request.azure_read_cert") as mock_certificate:
            cert = Certificate()
            mock_certificate.return_value = cert.root_pem_certificate
            resp = self.simulate_post(self.mastercard_endpoint, body=signed_xml.xml, headers=self.headers)
        self.assertTrue(valid_transaction_xml(resp.json), "Invalid XML response")
        self.assertEqual(resp.status_code, 403)

    def test_tampered_message(self, _):
        trans = MockMastercardAuthTransaction(
            "XXÿ",
            "2018-04-07T17:51:01.0000700-00:00",
            "999456789012345",
            trans_id="11111",
            trans_amt="0.45",
            merch_id="88888888",
            merch_name_loc="Best #456 Hollywood, FL",
            trans_date="12312010",
            trans_time="154539",
            merch_cat_cd="5542",
            acquirer_ica="7246",
            wlt_id="103",
            token_rqstr_id="50110030273",
            ret_cd="0",
            digest="oh5jTf3ufNbKvfE8WzsssHce95E=",
        )
        signed_xml = SignedXML(trans, signing_cert=self.cert)
        tampered_xml = signed_xml.xml.decode("utf8").replace("0.45", "500")
        with patch("app.mastercard.process_xml_request.azure_read_cert") as mock_certificate:
            cert = Certificate()
            mock_certificate.return_value = cert.root_pem_certificate
            resp = self.simulate_post(self.mastercard_endpoint, body=tampered_xml.encode("utf8"), headers=self.headers)
        self.assertTrue(valid_transaction_xml(resp.json), "Invalid XML response")
        self.assertEqual(resp.status_code, 403)

    def test_xml_mastercard_processing(self, _):
        signed_xml = SignedXML(MockMastercardAuthTransaction(), signing_cert=self.cert)
        with patch("app.mastercard.process_xml_request.azure_read_cert") as mock_certificate:
            mock_certificate.return_value = signed_xml.mock_signing_certificate()
            return_xml, mc_data, message, code = mastercard_request(signed_xml.xml)
        self.assertEquals(message, None)
        self.assertEquals(code, falcon.HTTP_200)
        expected = {
            "amount": "200.59",
            "payment_card_token": "123456789012345",
            "third_party_id": "MDSPX38FG",
            "mid": "687555537877464",
            "time": "2010-12-31 15:45:39",
            "currency_code": "GBP",
        }
        self.assertDictEqual(expected, mc_data)

    def test_xml_mastercard_processing_alt_data1(self, _):
        trans = MockMastercardAuthTransaction(
            "XXÿ",
            "2018-04-07T17:51:01.0000700-00:00",
            "999456789012345",
            trans_id="11111",
            trans_amt="45",
            merch_id="88888888",
            merch_name_loc="Best #456 Hollywood, FL",
            trans_date="12312010",
            trans_time="154539",
            merch_cat_cd="5542",
            acquirer_ica="7246",
            wlt_id="103",
            token_rqstr_id="50110030273",
            ret_cd="0",
            digest="oh5jTf3ufNbKvfE8WzsssHce95E=",
        )
        signed_xml = SignedXML(trans, signing_cert=self.cert)
        with patch("app.mastercard.process_xml_request.azure_read_cert") as mock_certificate:
            mock_certificate.return_value = signed_xml.mock_signing_certificate()
            return_xml, mc_data, message, code = mastercard_request(signed_xml.xml)
        self.assertEquals(message, None)
        self.assertEquals(code, falcon.HTTP_200)
        expected = {
            "amount": "45",
            "payment_card_token": "999456789012345",
            "third_party_id": "XXÿ",
            "mid": "88888888",
            "time": "2010-12-31 15:45:39",
            "currency_code": "GBP",
        }
        self.assertDictEqual(expected, mc_data)

    def test_xml_mastercard_processing_tampered_message(self, _):
        signed_xml = SignedXML(MockMastercardAuthTransaction(trans_amt="0.45"), signing_cert=self.cert)
        tampered_xml = signed_xml.xml.decode("utf8").replace("0.45", "500")
        with patch("app.mastercard.process_xml_request.azure_read_cert") as mock_certificate:
            mock_certificate.return_value = signed_xml.mock_signing_certificate()
            return_xml, mc_data, message, code = mastercard_request(tampered_xml.encode("utf8"))
        self.assertEqual(mc_data, {})
        self.assertEquals(message, "Error Digest mismatch for reference 0")
        self.assertEquals(code, falcon.HTTP_403)

    def test_xml_mastercard_processing_wrong_certificate(self, _):
        signed_xml = SignedXML(MockMastercardAuthTransaction(trans_amt="0.45"), signing_cert=self.cert)
        with patch("app.mastercard.process_xml_request.azure_read_cert") as mock_certificate:
            cert = Certificate()
            mock_certificate.return_value = cert.root_pem_certificate
            return_xml, mc_data, message, code = mastercard_request(signed_xml.xml)
        self.assertIn("Signature verification", message)
        self.assertEquals(code, falcon.HTTP_403)
        self.assertEqual(mc_data, {})

    def test_get_valid_signed_data_elements(self, _):
        """ Tests a certificate can be produced, a transaction signed and verified by signXML
        This tests the get_valid_signed_data function in process_xml_request will
        get all the required data
        """
        # Create test self signed root certificate
        cert = Certificate()
        # Create a mock transaction
        trans = MockMastercardAuthTransaction(
            "XXÿ",
            "2018-04-07T17:51:01.0000700-00:00",
            "999456789012345",
            trans_id="11111",
            trans_amt="0.45",
            merch_id="88888888",
            merch_name_loc="Best #456 Hollywood, FL",
            trans_date="12312010",
            trans_time="154539",
            merch_cat_cd="5542",
            acquirer_ica="7246",
            wlt_id="103",
            token_rqstr_id="50110030273",
            ret_cd="0",
            digest="oh5jTf3ufNbKvfE8WzsssHce95E=",
        )
        root_generated_signed_xml = cert.sign(trans.xml_tree)
        generated_signed_xml = etree.tostring(root_generated_signed_xml)
        valid_data_elements = get_valid_signed_data_elements(generated_signed_xml, cert.root_pem_certificate)
        count = 0
        for element in valid_data_elements:
            if element.tag in trans.tags_list:
                self.assertEqual(getattr(trans, trans.args_list[count]), element.text)
                count += 1
