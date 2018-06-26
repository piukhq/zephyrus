from settings import MASTERCARD_TRANSACTION_SIGNING_CERTIFICATE, MASTERCARD_CERTIFICATE_COMMON_NAME
from signxml import XMLVerifier, InvalidCertificate, InvalidSignature, InvalidDigest, InvalidInput
from flask import request
from app.errors import CustomException
import lxml.etree as etree


def mastercard_signed_xml(func):
    """Decorator to map request to standard pattern inserting data into response data
    and replying in standard error format for mastercard

    :param func:
    :return:
    """

    def wrapper(*args, **kwargs):
        print("enter")
        xml_data = request.data.decode("utf-8")
        xml, mc_data, message, code = mastercard_request(xml_data)
        request.data = mc_data
        try:
            ret = func(*args, **kwargs)
            print(ret)
        except CustomException:
            code = 400
        return xml, code

    return wrapper


def get_xml_element(element_tree, element_tag):
    for element in element_tree.iter():
        if element_tag in element.tag:
            return element
    return None


def get_xml_element_tree(element_tree, element_tag):
        return etree.ElementTree(get_xml_element(element_tree, element_tag))


def remove_xml_element_tree(element_tree, element_tag):
        element = get_xml_element(element_tree, element_tag)
        parent = element.getparent()
        parent.remove(element)
        return element_tree


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
    try:
        binary_xml = xml_data.encode('utf-8')
        xml_doc = etree.fromstring(binary_xml)
        xml_tree_root = etree.ElementTree(xml_doc)



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

        valid_data_elements = get_valid_signed_data_elements(xml_tree_root,
                                                             signing_certificate_chain,
                                                             certificate_common_name)
        # for element in valid_data_elements.iter():

        mc_data = {conversion_map[element.tag]: element.text
                   for element in valid_data_elements if element.tag in conversion_map}

        # convert money string to integer*100 without rounding errors
        if '.' in mc_data['amount']:
            pounds, pennies = mc_data['amount'].split('.')
            mc_data['amount'] = int(f"{pounds}{pennies:<02}")
        else:
            mc_data['amount'] = int(f"{mc_data['amount']}00")

        mc_data['currency_code'] = 'GBP'
        mc_data['auth_code'] = '.'  # should be optional

        new_tree = remove_xml_element_tree(xml_doc, "Signature")

        return etree.tostring(new_tree).decode('utf8'), mc_data, None, 200

    except etree.ParseError as e:
        return None, mc_data, f'XML Parse Error: {e}', 400
    except (TypeError, IndexError, KeyError, AttributeError, InvalidInput ) as e:
        return None, mc_data, f'Error {e}', 400
    except (InvalidCertificate, InvalidSignature, InvalidDigest) as e:
        return None, mc_data, f'Error {e}', 404
