from flask_restplus import Api

from app.authentication.token_utils import Auth, Me
from app.views import Amex, MasterCard, HealthCheck

api = Api()

api.add_resource(HealthCheck, '/healthz', endpoint='api.healthz')

api.add_resource(Auth, '/auth_transactions/authorize', endpoint='api.authorize')
api.add_resource(Me, '/me', endpoint='api.me')


api.add_resource(Amex, '/auth_transactions/amex', endpoint='api.amex')
api.add_resource(MasterCard, '/auth_transactions/mastercard', endpoint='api.mastercard')
