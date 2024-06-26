import arrow
import falcon
import lxml.etree as etree
import sentry_sdk
from OpenSSL.crypto import FILETYPE_PEM, load_certificate
from signxml import (
    DigestAlgorithm,
    InvalidCertificate,
    InvalidDigest,
    InvalidInput,
    InvalidSignature,
    SignatureConfiguration,
    SignatureMethod,
    XMLVerifier,
)
from signxml.util import add_pem_header

from app.errors import CustomException


def mastercard_signed_xml_response(func):
    """Decorator to map request to standard pattern inserting data into response data
    and replying in standard error format for mastercard
    """

    def wrapper(req: falcon.Request, resp: falcon.Response, *args, **kwargs):
        xml, mc_data, message, code = mastercard_request(req.media)
        if code in (falcon.HTTP_400, falcon.HTTP_403):
            resp.media = xml
            resp.status = code
            return

        # message is currently not used but mastercard might in future want this in the xml reponse
        try:
            req.context.transaction_data = mc_data
            func(func, req, resp, *args, **kwargs)
        except CustomException as e:
            sentry_sdk.capture_exception(e)
            if e.name == "CONNECTION_ERROR":
                code = e.code
            # error code returned by XML processing should be used unless 200
            elif code == falcon.HTTP_200:
                code = falcon.HTTP_400
        except BaseException as e:
            sentry_sdk.capture_exception(e)
            code = falcon.HTTP_500

        resp.media = xml
        resp.status = code

    return wrapper


def remove_from_xml_string(xml_string, start_string, end_string):
    end = 0
    try:
        start = xml_string.index(start_string)
        if 0 < start < len(xml_string):
            end = xml_string.index(end_string, start) + len(end_string)
            if end <= start:
                raise ValueError
        return "{}{}".format(xml_string[:start], xml_string[end:])
    except ValueError:
        return ""


def get_valid_signed_data_elements(binary_xml, pem_signing_cert):
    """Get validated and signed data.  This protects against forged XML which can pass unsigned data.

    signXML implements a best practice which requires us to supply the common name so that the certificate
    can be trusted.  Typically, this might be known shared knowledge such as domain name.  However,
    in our case the certificate will be passed from MasterCard, can be trusted and is handled securely. Also the
    common name might be changed by MasterCard and is not defined in their specification.  Therefore, the best option
    would be to extract the common name from the certificate using the same methods as signXML which will ensure that
    this alone will not cause a failure.  Hence the use of load_certificate and add_pem_header.

    :param binary_xml:
    :param pem_signing_cert:
    :return: Validated Signed data - any unsigned data will be removed for security
    """
    signing_cert = load_certificate(FILETYPE_PEM, add_pem_header(pem_signing_cert))
    cert_subject_name = signing_cert.get_subject().commonName
    assertion_data_elements = (
        XMLVerifier()
        .verify(
            binary_xml,
            x509_cert=pem_signing_cert,
            cert_subject_name=cert_subject_name,
            expect_config=SignatureConfiguration(
                signature_methods={SignatureMethod.RSA_SHA1},
                digest_algorithms={DigestAlgorithm.SHA1},
            ),
        )
        .signed_xml
    )
    return assertion_data_elements


def mastercard_request(xml_data):
    mc_data = {}
    response_xml = ""

    try:
        # To ensure we always return an identical format we can remove the signature from the document
        # using string methods:
        response_xml = remove_from_xml_string(xml_data.decode("utf8"), "<ds:Signature", "/ds:Signature>")
        xml_doc = etree.fromstring(xml_data)
        xml_tree_root = etree.ElementTree(xml_doc)
        pem_signing_cert = get_signing_cert(xml_tree_root)
        valid_data_elements = get_valid_signed_data_elements(xml_tree_root, pem_signing_cert)

        # need for hermes 'time', 'amount', 'mid', 'third_party_id', 'auth_code', 'currency_code', 'payment_card_token'
        # map mastercard tags to bink hermes naming convention then tidy up bespoke discrepancies such as time

        conversion_map = {
            "merchId": "mid",
            "transAmt": "amount",
            "bankCustNum": "payment_card_token",
            "refNum": "third_party_id",
            "transDate": "mc_date",
            "transTime": "mc_time",
        }

        mc_data = {
            conversion_map[element.tag]: element.text
            for element in valid_data_elements
            if element.tag in conversion_map
        }

        mc_data["currency_code"] = "GBP"

        time_obj = arrow.get(mc_data["mc_time"] + mc_data["mc_date"], "HHmmssMMDDYYYY")
        mc_data["time"] = time_obj.format("YYYY-MM-DD HH:mm:ss")

        del mc_data["mc_date"]
        del mc_data["mc_time"]

        return response_xml, mc_data, None, falcon.HTTP_200

    except etree.ParseError as e:
        sentry_sdk.capture_exception(e)
        return response_xml, mc_data, f"XML Parse Error: {e}", falcon.HTTP_400
    except (
        TypeError,
        IndexError,
        KeyError,
        AttributeError,
        ValueError,
        InvalidInput,
    ) as e:
        sentry_sdk.capture_exception(e)
        return response_xml, mc_data, f"Error {e}", falcon.HTTP_400
    except (InvalidCertificate, InvalidSignature, InvalidDigest) as e:
        sentry_sdk.capture_exception(e)
        return response_xml, mc_data, f"Error {e}", falcon.HTTP_403


def get_signing_cert(xml_tree_root):
    namespaces = {"ds": "http://www.w3.org/2000/09/xmldsig#"}
    certificate_xml = xml_tree_root.find("/ds:Signature/ds:KeyInfo/ds:X509Data/ds:X509Certificate", namespaces)
    pem_signing_cert = certificate_xml.text

    return pem_signing_cert
