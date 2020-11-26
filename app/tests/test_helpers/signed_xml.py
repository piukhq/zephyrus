from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from signxml import XMLVerifier, XMLSigner, methods as sign_methods
import lxml.etree as etree
import hashlib
import base64
import datetime
import io


class BasicXML:
    def __init__(self, xml=None, element=None):
        self.xml = None
        self.xml_doc = None
        self.tree = None
        if xml:
            self.xml = xml.encode("utf-8")
            if not element:
                element = etree.ElementTree(etree.fromstring(self.xml))
        if element:
            self.tree = element

    def remove(self, element_tag):
        element = self.get_xml_element(element_tag)
        parent = element.getparent()
        parent.remove(element)
        self.xml = etree.tostring(self.tree).decode("utf-8")

    def get_xml_element_tree(self, element_tag):
        return etree.ElementTree(self.get_xml_element(element_tag))

    def get_xml_element(self, element_tag):
        for element in self.tree.iter():
            if element_tag in element.tag:
                return element
        return None

    @staticmethod
    def get_hash(input_text):
        hash_object = hashlib.sha1(input_text)
        b_str = str(base64.b64encode(hash_object.digest()), "utf-8")
        return b_str

    @staticmethod
    def canonicalize_xml(xml_part):
        canonicalized_xml = io.BytesIO()
        xml_part.write_c14n(canonicalized_xml, exclusive=True)
        return canonicalized_xml


class UnsignedXML(BasicXML):
    def __init__(self, transaction):
        xml = etree.tostring(transaction.xml_tree)
        super().__init__(xml=xml.decode("utf8"))

    def get_transaction(self):
        return Transaction(self.xml)


class Transaction:
    def __init__(self, xml):
        self.transaction_xml = xml

    @property
    def xml_tree(self):
        return etree.ElementTree(etree.fromstring(self.transaction_xml.encode("utf-8")))

    @property
    def xml(self):
        return self.transaction_xml


class SignedXML(BasicXML):
    def __init__(self, transaction, signing_cert=None):

        if not signing_cert:
            self.signing_cert = Certificate()
        else:
            self.signing_cert = signing_cert

        self.transaction = transaction
        xml = etree.tostring(self.signing_cert.sign(self.transaction.xml_tree))

        super().__init__(xml=xml.decode("utf8"))

    def mock_signing_certificate(self):
        """
        This is the self signed certificate and common name as we expect to be
        supplied by Mastercard and placed in settings.  This is used to mock
        out mastercard.process_xml_request.read_vault_cert which normally
        returns the pem formated certificate

        Note the signed xml will also have a certificate created using this public
        signing certificate and the private key

        :return: A tuple of the valid credentials used when certificate was created and xml signed
        """
        return self.signing_cert.root_pem_certificate

    def verify_signature(self, root_cert, cert_subject_name):
        """
        Uses signML to verify signature and return only verified data checked by
        signature.  Much safer to use as it contains security measures against XML
        attacks.  Also supports other methods.
        A root certificate must be supplied to verify the X509 certificate in the
        XML signature - this is an in built security measure.
        However, requires more dev ops support to install system libraries etc.

        :return: valid_data
        """
        return XMLVerifier().verify(self.xml, x509_cert=root_cert, cert_subject_name=cert_subject_name).signed_xml


class Certificate:
    def __init__(self, public_key=None):
        self.common_name = "mysite.com"
        self.cert_subject = self.issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My Company"),
                x509.NameAttribute(NameOID.COMMON_NAME, self.common_name),
            ]
        )

        self.private_key = self.make_private_key()
        if public_key:
            self.public_key = public_key
        else:
            self.public_key = self.private_key.public_key()

        self.root_cert = self.make_root_certificate()

    @staticmethod
    def make_private_key():
        return rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    @property
    def private_pem_key(self):
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(b"passphrase"),
        ).decode("utf-8")

    def make_root_certificate(self):
        # Various details about who we are. For a self-signed certificate the
        # subject and issuer are always the same.
        return (
            x509.CertificateBuilder()
            .subject_name(self.cert_subject)
            .issuer_name(self.issuer)
            .public_key(self.public_key)
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=2))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False)
            .sign(self.private_key, hashes.SHA256(), default_backend())
        )

    @property
    def root_pem_certificate(self):
        return self.root_cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

    def sign(self, xml):
        return XMLSigner(
            method=sign_methods.enveloped,
            signature_algorithm="rsa-sha1",
            digest_algorithm="sha1",
            c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#",
        ).sign(xml, key=self.private_key, cert=self.root_pem_certificate)


class MockMastercardAuthTransaction(Transaction):
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
        self.signature_value = (
            "p8TkEWT0+LZfGo246jxMYev0qyIRTPolhog19b45keFHEbguSHnDxl75ZHVraBch29MtFwN4nVOSpYdJiw"
            "Euyc74jbvTAfOfIu9Bh4N16bS421uiUoLsZrpbreqaHYkwhhCn+s11tNnAVI/p2nZyOGVyssFfFU9PH09m"
            "cbrn2T0="
        )
        self.x509_cert = (
            "MIIE1DCCA7ygAwIBAgIRAMpP4+8x8zLTs9QtLr8UTlAwDQYJKoZIhvcNAQEFBQAweDELMAkGA1UEBhMCVVMxHTA"
            "bBgNVBAoTFE1hc3RlckNhcmQgV29ybGR3aWRlMSkwJwYDVQQLEyBHbG9iYWwgVGVjaG5vbG9neSBhbmQgT3BlcmF"
            "0aW9uczEfMB0GA1UEAxMWTWFzdGVyQ2FyZCAgU1NMIFN1YiBDQTAeFw0wODA4MjkxNDA0NDhaFw0xMDA4MjkxNDA0"
            "NDlaMIGgMQswCQYDVQQGEwJVUzERMA8GA1UECBMITWlzc291cmkxFDASBgNVBAcTC1NhaW50IExvdWlzMR0wGwYDV"
            "QQKExRNYXN0ZXJDYXJkIFdvcmxkd2lkZTEdMBsGA1UECxMUY2l0aXplbnMtb25saW5lLW1hbGwxKjAoBgNVBAMTIXN"
            "0bG1yc2pzZWN0MS5jb3JwLm1hc3RlcmNhcmQudGVzdDCBnzANBgkqhkiG9w0BAQEFAAOBjQAwgYkCgYEAtM6O3e"
            "r9A2BRLxT9l3CPqqGv4jAe35K8pA2NxX7qSqwLiszaDiC5GV5GzvJ0/stlr6pM6CRR1gLIyVEyQjL1kA+qBFQ1YO"
            "I8AzypxeSxiAyW5DZ3rt4+qOIzJxTOOyAqUw80Hfuqk+J0NdchXZkAaMU5Sx9T6inLElrzCbNQMUUCAwEAAaOCAb"
            "IwggGuMB8GA1UdIwQYMBaAFNVf0euD27u/RRw+3HIysV/aF4rDMAkGA1UdEwQCMAAwggERBgNVHSAEggEIMIIBBD"
            "CCAQAGCSqGSIb3DQUGATCB8jAzBggrBgEFBQcCARYnaHR0cDovL2NlcnRpZmljYXRlcy5tYXN0ZXJjYXJkLmNvbS9"
            "DUFMvMIG6BggrBgEFBQcCAjCBrTAbFhRNYXN0ZXJDYXJkIFdvcmxkd2lkZTADAgEBGoGNVGhlIE1hc3RlckNhcmQg"
            "V29ybGR3aWRlIENlcnRpZmljYXRpb24gUHJhY3RpY2UgU3RhdGVtZW50IGdvdmVybnMgdGhpcyBjZXJ0aWZpY2F0ZS"
            "BhbmQgaXMgaW5jb3Jwb3JhdGVkIGJ5IHJlZmVyZW5jZSBoZXJlaW4uIExpbWl0ZWQgTGlhYmlsaXR5MDwGA1UdHwQ1"
            "MDMwMaAvoC2GK2h0dHA6Ly9jZXJ0aWZpY2F0ZXMubWFzdGVyY2FyZC5jb20vQ1JMX1BVQi8wDgYDVR0PAQH/BAQDA"
            "geAMB0GA1UdDgQWBBTewBdq6vV1ym9QqBv55hE4TjZ1eTANBgkqhkiG9w0BAQUFAAOCAQEAB6+Htrkv7V48OllLzO"
            "hzaaCafuW3PQNFQze2cpH7QGPrKuB+XOQDYMatb8KN887T00GS/GQxdkU7KCxK8CV1Ms6fjpp5atWQqtRTzuyC1kh"
            "F3HvwlvE6zAW6v7UKqHIxAktPPXRmikUU+u5OiXSsIpf3T1rO+20IIWLJY3dl3iGKRgFEe/LRWvrOnXUNMRajSA89"
            "15EVcxWrYDpa8IlNhUdnr+gFDY4cj/YPOr5GtbikinqEr6z5tn/lj0UpIvk9Ab97bA9v7NITVml/9DkjIrQ0DW5q8"
            "cv2gerg47xmsLPHuLIQsKEGlyb9sr9v382gU6pj22n5n7SIwdn6rM7dVw=="
        )

        self.signature = ""

        self.args_list = [
            "ref_num",
            "timestamp",
            "bank_cust_num",
            "trans_id",
            "trans_amt",
            "merch_id",
            "merch_name_loc",
            "trans_date",
            "trans_time",
            "merch_cat_cd",
            "acquirer_ica",
            "wlt_id",
            "token_rqstr_id",
            "ret_cd",
            "digest",
            "signature_value",
            "x509_cert",
        ]

        self.tags_list = [
            "refNum",
            "timestamp",
            "bankCustNum",
            "transId",
            "transAmt",
            "merchId",
            "merchNameLoc",
            "transDate",
            "transTime",
            "merchCatCd",
            "acquirerIca",
            "de48se26sf1WltId",
            "de48se33sf6TokenRqstrId",
            "retCd",
        ]

        for v in range(0, len(args)):
            setattr(self, self.args_list[v], args[v])

        for k, v in kwargs.items():
            setattr(self, k, v)

        super().__init__(self.xml)

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

    def get_signature_from_format(self, signature_value, x509_cert):

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
            <ds:SignatureValue>{signature_value}
            </ds:SignatureValue>
            <ds:KeyInfo>
                <ds:X509Data>
                    <ds:X509Certificate>{x509_cert}
                    </ds:X509Certificate>
                </ds:X509Data>
            </ds:KeyInfo>
        </ds:Signature>
"""


def valid_transaction_xml(xml):
    ret = False
    if "</Transaction>" in xml:
        try:
            etree.fromstring(xml)
            ret = True
        except etree.ParseError:
            pass
    return ret
