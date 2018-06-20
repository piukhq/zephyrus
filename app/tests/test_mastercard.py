from app import create_app
from flask_testing import TestCase
from app.mastercard.process_soap_request import mastercard_request
from app.mastercard.process_soap_request import SignedXML, UnsignedXML


class MockMastercardAuthTransaction:

    def __init__(self, *args, **kwargs):
        self.ref_num = "MDSPX38FG"
        self.timestamp = "2011-04-07T17:51:01.0000700-05:00"
        self.bank_cust_num = "123456789012345"
        self.trans_id = "20110405123456"
        self.trans_amt = "200.59"
        self.merch_id = "687555537877464"
        self.merch_name_loc = "Best #456 Hollywood, FL"
        self.trans_date = "12312010"
        self.trans_time = "154539"
        self.merch_cat_cd = "5542"
        self.acquirer_ica = "7246"
        self.wlt_id = "103"
        self.token_rqstr_id = "50110030273"
        self.ret_cd = "0"
        self.digest = "oh5jTf3ufNbKvfE8WzsssHce95E="
        self.signature_value = "p8TkEWT0+LZfGo246jxMYev0qyIRTPolhog19b45keFHEbguSHnDxl75ZHVraBch29MtFwN4nVOSpYdJiw" \
                               "Euyc74jbvTAfOfIu9Bh4N16bS421uiUoLsZrpbreqaHYkwhhCn+s11tNnAVI/p2nZyOGVyssFfFU9PH09m" \
                               "cbrn2T0="
        self.x509_cert = \
            "MIIE1DCCA7ygAwIBAgIRAMpP4+8x8zLTs9QtLr8UTlAwDQYJKoZIhvcNAQEFBQAweDELMAkGA1UEBhMCVVMxHTA" \
            "bBgNVBAoTFE1hc3RlckNhcmQgV29ybGR3aWRlMSkwJwYDVQQLEyBHbG9iYWwgVGVjaG5vbG9neSBhbmQgT3BlcmF" \
            "0aW9uczEfMB0GA1UEAxMWTWFzdGVyQ2FyZCAgU1NMIFN1YiBDQTAeFw0wODA4MjkxNDA0NDhaFw0xMDA4MjkxNDA0" \
            "NDlaMIGgMQswCQYDVQQGEwJVUzERMA8GA1UECBMITWlzc291cmkxFDASBgNVBAcTC1NhaW50IExvdWlzMR0wGwYDV" \
            "QQKExRNYXN0ZXJDYXJkIFdvcmxkd2lkZTEdMBsGA1UECxMUY2l0aXplbnMtb25saW5lLW1hbGwxKjAoBgNVBAMTIXN" \
            "0bG1yc2pzZWN0MS5jb3JwLm1hc3RlcmNhcmQudGVzdDCBnzANBgkqhkiG9w0BAQEFAAOBjQAwgYkCgYEAtM6O3e" \
            "r9A2BRLxT9l3CPqqGv4jAe35K8pA2NxX7qSqwLiszaDiC5GV5GzvJ0/stlr6pM6CRR1gLIyVEyQjL1kA+qBFQ1YO" \
            "I8AzypxeSxiAyW5DZ3rt4+qOIzJxTOOyAqUw80Hfuqk+J0NdchXZkAaMU5Sx9T6inL ElrzCbNQMUUCAwEAAaOCAb" \
            "IwggGuMB8GA1UdIwQYMBaAFNVf0euD27u/RRw+3HIysV/aF4rDMAkGA1UdEwQCMAAwggERBgNVHSAEggEIMIIBBD" \
            "CCAQAGCSqGSIb3DQUGATCB8jAzBggrBgEFBQcCARYnaHR0cDovL2NlcnRpZmljYXRlcy5tYXN0ZXJjYXJkLmNvbS9" \
            "DUFMvMIG6BggrBgEFBQcCAjCBrTAbFhRNYXN0ZXJDYXJkIFdvcmxkd2lkZTADAgEBGoGNVGhlIE1hc3RlckNhcmQg" \
            "V29ybGR3aWRlIENlcnRpZmljYXRpb24gUHJhY3RpY2UgU3RhdGVtZW50IGdvdmVybnMgdGhpcyBjZXJ0aWZpY2F0ZS" \
            "BhbmQgaXMgaW5jb3Jwb3JhdGVkIGJ5IHJlZmVyZW5jZSBoZXJlaW4uIExpbWl0ZWQgTGlhYmlsaXR5MDwGA1UdHwQ1" \
            "MDMwMaAvoC2GK2h0dHA6Ly9jZXJ0aWZpY2F0ZXMubWFzdGVyY2FyZC5jb20vQ1JMX1BVQi8wDgYDVR0PAQH/BAQDA" \
            "geAMB0GA1UdDgQWBBTewBdq6vV1ym9QqBv55hE4TjZ1eTANBgkqhkiG9w0BAQUFAAOCAQEAB6+Htrkv7V48OllLzO" \
            "hzaaCafuW3PQNFQze2cpH7QGPrKuB+XOQDYMatb8KN887T00GS/GQxdkU7KCxK8CV1Ms6fjpp5atWQqtRTzuyC1kh" \
            "F3HvwlvE6zAW6v7UKqHIxAktPPXRmikUU+u5OiXSsIpf3T1rO+20IIWLJY3dl3iGKRgFEe/LRWvrOnXUNMRajSA89" \
            "15EVcxWrYDpa8IlNhUdnr+gFDY4cj/YPOr5GtbikinqEr6z5tn/lj0UpIvk9Ab97bA9v7NITVml/9DkjIrQ0DW5q8" \
            "cv2gerg47xmsLPHuLIQsKEGlyb9sr9v382gU6pj22n5n7SIwdn6rM7dVw=="

        self.signature = ""

        args_list = [
            'ref_num','timestamp', 'bank_cust_num','trans_id', "trans_amt", "merch_id", "merch_name_loc", "trans_date",
            "trans_time", "merch_cat_cd", "acquirer_ica","wlt_id", "token_rqstr_id", "ret_cd", "digest",
            "signature_value", "x509_cert"
        ]

        for v in range(0, len(args)):
            setattr(self, args_list[v], args[v])

        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def xml(self):
        return f"""<?xml version="1.0" encoding="UTF-8"?>
    <Transaction xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <refNum>{self.ref_num}</refNum>
        <timestamp>{self.timestamp}</timestamp>
        <bankCustNum>{self.bank_cust_num}</bankCustNum>
        <transId>{self.trans_id}</transId>
        <transAmt>{self.trans_amt}</transAmt>
        <merchId>{self.merch_id}</merchId>
        <merchNameLoc>{self.merch_name_loc}</merchNameLoc>
        <transDate>{self.trans_date}</transDate>
        <transTime>{self.trans_time}</transTime>
        <merchCatCd>{self.merch_cat_cd}</merchCatCd>
        <acquirerIca>{self.acquirer_ica}</acquirerIca>
        <de48se26sf1WltId>{self.wlt_id}</de48se26sf1WltId>
        <de48se33sf6TokenRqstrId>{self.token_rqstr_id}</de48se33sf6TokenRqstrId>
        <retCd>{self.ret_cd}</retCd>
        {self.signature}</Transaction>"""

    def get_signature(self):
        return f"""<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
            <ds:SignedInfo>
                <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
                <ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
                <ds:Reference URI="">
                    <ds:Transforms>
                        <ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
                        <ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#">
                            <ec:InclusiveNamespaces xmlns:ec="http://www.w3.org/2001/10/xml-exc-c14n#"
                                                    PrefixList="code ds kind rw samlp saml typens #default xsd xsi"/>
                        </ds:Transform>
                    </ds:Transforms>
                    <ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
                    <ds:DigestValue>{self.digest}</ds:DigestValue>
                </ds:Reference>
            </ds:SignedInfo>
            <ds:SignatureValue>{self.signature_value}
            </ds:SignatureValue>
            <ds:KeyInfo>
                <ds:X509Data>
                    <ds:X509Certificate>{self.x509_cert}
                    </ds:X509Certificate>
                </ds:X509Data>
            </ds:KeyInfo>
        </ds:Signature>
"""

    @property
    def signed_xml(self):
        self.signature = self.get_signature()
        return self.xml


class MasterCardAuthTestCases(TestCase):

    TESTING = True

    def create_app(self):
        return create_app(self, )

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_xml_request(self):
        trans = MockMastercardAuthTransaction()
        mc_data, success, message = mastercard_request(trans.signed_xml)
        self.assertEquals(message, None)
        self.assertTrue(success)
        expected = {
            'amount': 20059,
            'payment_card_token': '123456789012345',
            'third_party_id': 'MDSPX38FG',
            'mid': '687555537877464',
            'date': '12312010',
            'time': '154539',
            'currency_code': 'GBP',
            'auth_code': '.'
        }
        self.assertDictEqual(expected, mc_data)

    def test_xml_request2(self):
        trans = MockMastercardAuthTransaction(
            "XXÿ", "2018-04-07T17:51:01.0000700-00:00", "999456789012345",
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
        mc_data, success, message = mastercard_request(trans.signed_xml)
        self.assertEquals(message, None)
        self.assertTrue(success)
        expected = {
            'amount': 45,
            'payment_card_token': '999456789012345',
            'third_party_id': 'XXÿ',
            'mid': '88888888',
            'date': '12312010',
            'time': '154539',
            'currency_code': 'GBP',
            'auth_code': '.'
        }
        self.assertDictEqual(expected, mc_data)

    def test_auth_response(self):
        trans = MockMastercardAuthTransaction()
        resp = self.client.post('/mastercard', data=trans.signed_xml, content_type="text/xml")
        self.assert200(resp)

    def test_xml_signed(self):
        trans = MockMastercardAuthTransaction()
        signed_xml = SignedXML(trans.signed_xml)
        signed_xml.process_signed_envelope()

        trans2 = MockMastercardAuthTransaction()
        unsigned_xml = UnsignedXML(trans2.xml)
        f2 = unsigned_xml.canonicalize_xml(unsigned_xml.tree)
        print(unsigned_xml.get_hash(f2.getvalue()))
        print(f2.getvalue())

