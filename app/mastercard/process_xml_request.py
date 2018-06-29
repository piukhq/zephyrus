from settings import MASTERCARD_TRANSACTION_SIGNING_CERTIFICATE, MASTERCARD_CERTIFICATE_COMMON_NAME
from signxml import XMLVerifier, InvalidCertificate, InvalidSignature, InvalidDigest, InvalidInput
from flask import request
from app.errors import CustomException
import lxml.etree as etree
import arrow


def mastercard_signed_xml_response(func):
    """Decorator to map request to standard pattern inserting data into response data
    and replying in standard error format for mastercard
    """

    def wrapper(*args, **kwargs):
        xml, mc_data, message, code = mastercard_request(request.data)
        # message is currently not used but mastercard might in future want this in the xml reponse
        try:
            request.transaction_data = mc_data
            ret = func(*args, **kwargs)
            if not ret['success'] and code == 200:
                code = 400
                # might need in future to set and return message = "Data processing error" but currently not used

        except CustomException as e:
            if e.name == "CONNECTION_ERROR":
                code = e.code
            # error code returned by XML processing should be used unless 200
            elif code == 200:
                code = 400
        except BaseException:
            code = 500
        return xml, code

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


def get_valid_signed_data_elements(binary_xml, root_cert, cert_subject_name):
    assertion_data_elements = XMLVerifier().verify(binary_xml,
                                                   x509_cert=root_cert,
                                                   cert_subject_name=cert_subject_name).signed_xml
    return assertion_data_elements


def get_certificate_details():
    return MASTERCARD_TRANSACTION_SIGNING_CERTIFICATE, MASTERCARD_CERTIFICATE_COMMON_NAME


def mastercard_request(xml_data):
    mc_data = {}
    signing_certificate_chain, certificate_common_name = get_certificate_details()
    response_xml = ""
    try:
        # To ensure we always return an identical format we can remove the signature from the document
        # using string methods:
        response_xml = remove_from_xml_string(xml_data.decode('utf8'), "<ds:Signature", "/ds:Signature>")

        xml_doc = etree.fromstring(xml_data)
        xml_tree_root = etree.ElementTree(xml_doc)
        valid_data_elements = get_valid_signed_data_elements(xml_tree_root,
                                                             signing_certificate_chain,
                                                             certificate_common_name)

        # need for hermes 'time', 'amount', 'mid', 'third_party_id', 'auth_code', 'currency_code', 'payment_card_token'
        # map mastercard tags to bink hermes naming convention then tidy up bespoke discrepancies such as time

        conversion_map = {
            'merchId': 'mid',
            'transAmt': 'amount',
            'bankCustNum': 'payment_card_token',
            'refNum': 'third_party_id',
            'transDate': 'mc_date',
            'transTime': 'mc_time'
        }

        mc_data = {conversion_map[element.tag]: element.text
                   for element in valid_data_elements if element.tag in conversion_map}

        mc_data['currency_code'] = 'GBP'

        time_obj = arrow.get(mc_data['mc_time'] + mc_data['mc_date'], "HHmmssMMDDYYYY")
        mc_data['time'] = time_obj.format("YYYY-MM-DD HH:mm:ss")

        del(mc_data['mc_date'])
        del(mc_data['mc_time'])

        return response_xml, mc_data, None, 200

    except etree.ParseError as e:
        return response_xml, mc_data, f'XML Parse Error: {e}', 400
    except (TypeError, IndexError, KeyError, AttributeError, ValueError, InvalidInput) as e:
        return response_xml, mc_data, f'Error {e}', 400
    except (InvalidCertificate, InvalidSignature, InvalidDigest) as e:
        return response_xml, mc_data, f'Error {e}', 404
