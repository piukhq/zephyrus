import lxml.etree as etree
from signxml import XMLVerifier


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


def get_valid_signed_data(binary_xml, root_cert, cert_subject_name):
    assertion_data = XMLVerifier().verify(binary_xml, x509_cert=root_cert, cert_subject_name=cert_subject_name)\
        .signed_xml
    return assertion_data


def mastercard_request(xml_data):
    try:
        binary_xml = xml_data.encode('utf-8')
        xml_doc = etree.fromstring(binary_xml)
        element_tree = etree.ElementTree(xml_doc)

        mc_data = {}
        xml_doc = etree.fromstring(binary_xml)
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

        new_tree = remove_xml_element_tree(xml_doc, "Signature")

        return etree.tostring(new_tree).decode('utf8'), mc_data, True, None

    except etree.ParseError as e:
        return None, mc_data, False, f'XML Parse Error: {e}'
    except (TypeError, IndexError, KeyError, AttributeError) as e:
        return None, mc_data, False, f'Error {e}'


