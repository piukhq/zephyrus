#import xml.etree.ElementTree as etree
import io
import lxml.etree as etree
#from lxml import etree
import hashlib
import base64
from signxml import VerifyResult, XMLVerifier


class BasicSoap:

    def __init__(self, xml=None, element=None):
        self.xml = None
        self.xml_doc = None
        self.tree = None
        if xml:
            self.xml = xml.encode('utf-8')
            if not element:
                element = etree.ElementTree(etree.fromstring(self.xml))
        if element:
            self.tree = element

    def remove(self, element_tag):
        element = self.get_xml_element(element_tag)
        parent = element.getparent()
        parent.remove(element)

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
        b_str = str(base64.b64encode(hash_object.digest()), 'utf-8')
        return b_str

    @staticmethod
    def canonicalize_xml(xml_part):
        canonicalized_xml = io.BytesIO()
        xml_part.write_c14n(canonicalized_xml, exclusive=True)
        return canonicalized_xml


class Signature(BasicSoap):

    def __init__(self, element):
        super().__init__(element=element)


class UnsignedXML(BasicSoap):

    def __init__(self, xml):
        super().__init__(xml=xml)


class SignedXML(BasicSoap):

    def __init__(self, xml, root_cert=None):
        self.root_cert = root_cert
        self.signature_value = None
        self.digest_value = None
        self.computed_digest_value = None
        self.X509_value = None
        super().__init__(xml=xml)


    def sign(self):
        pass

    def verify_signature(self):
        """
        Uses signxml to verify signature and return only verified data checked by
        signature.  Much safer to use as it contains security measures against XML
        attacks.  Also supports other methods.
        A root certificate must be supplied to verify the X509 certificate in the
        XML signature - this is an in built security measure.
        However, requires more dev ops support to install system libraries etc.

        :return:
        """

        assertion_data = XMLVerifier().verify(self.xml, x509_cert=self.root_cert).signed_xml
        print (assertion_data)
        return assertion_data

    def process_signed_envelope(self):
        """
        Manual method not using signxml and assuming envelope, sha1, and c14n
        Requires XML security measures to be added

        Note built in xml.etree can be used but exclusive is not supported

        :return:
        """
        signature = Signature(self.get_xml_element_tree("Signature"))

        # Remove signature section as envelope method signs the rest of the document
        self.remove("Signature")
        # Canonicalize the document to be hashed
        f2 = self.canonicalize_xml(self.tree)

        print(f2.getvalue())

        self.computed_digest_value = self.get_hash(f2.getvalue())
        print(self.computed_digest_value)

        signature_value_element = signature.get_xml_element('SignatureValue')
        self.signature_value = signature_value_element.text
        print(self.signature_value)

        digest_value_element = signature.get_xml_element('DigestValue')
        self.digest_value = digest_value_element.text
        print(self.digest_value)

        X509_value_element = signature.get_xml_element('X509Certificate')
        self.X509_value = X509_value_element.text
        print(self.X509_value)

        print(base64.b64decode(self.X509_value))

        #signature_value = self.canonicalize_xml(signature_value)
        #signature_value_str = signature_value.getvalue().decode("utf-8")


def mastercard_request(xml_data):
    try:
        mc_data = {}

        xml_doc = etree.fromstring(xml_data.encode('utf8'))
        # need ('time', 'amount', 'mid', 'third_party_id', 'auth_code', 'currency_code', 'payment_card_token')
        # get client by client id gets ('client_id', 'secret', 'organisation') may not be useful

        conversion_map = {
            'merchId': 'mid',
            'transAmt': 'amount',
            'bankCustNum': 'payment_card_token',
            'refNum': 'third_party_id',
            'transDate': 'date',
            'transTime': 'time'
        }

        mc_data = {conversion_map[child.tag]: child.text for child in xml_doc if child.tag in conversion_map}
        # convert money string to integer*100 without rounding errors
        if '.' in mc_data['amount']:
            pounds, pennies = mc_data['amount'].split('.')
            mc_data['amount'] = int(f"{pounds}{pennies:<02}")
        else:
            mc_data['amount'] = int(f"{mc_data['amount']}00")

        mc_data['currency_code'] = 'GBP'
        mc_data['auth_code'] = '.'  # should be optional

        return mc_data, True, None

    except etree.ParseError as e:
        return mc_data, False, f'XML Parse Error: {e}'
    except (TypeError, IndexError, KeyError, AttributeError) as e:
        return mc_data, False, f'Error {e}'


