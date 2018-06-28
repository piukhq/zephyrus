from flask_restplus import Api

from app.authentication.token_utils import Auth, Me
from app.views import Amex, MasterCard

api = Api()

api.add_resource(Auth, '/authorize', endpoint='api.authorize')
api.add_resource(Me, '/me', endpoint='api.me')


api.add_resource(Amex, '/amex', endpoint='api.amex')
api.add_resource(MasterCard, '/mastercard', endpoint='api.mastercard')
