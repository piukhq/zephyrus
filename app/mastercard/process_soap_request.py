import xml.etree.ElementTree as ETree


def mastercard_request(xml_data):
    try:
        mc_data = {}
        xml_doc = ETree.fromstring(xml_data)
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

    except ETree.ParseError as e:
        return mc_data, False, f'XML Parse Error: {e}'
    except (TypeError, IndexError, KeyError, AttributeError) as e:
        return mc_data, False, f'Error {e}'
