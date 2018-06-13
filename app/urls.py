from flask_restplus import Api

from app.views import Amex, MasterCard, Auth

api = Api()

api.add_resource(Auth, '/authorize', endpoint='api.authorize')

api.add_resource(Amex, '/amex', endpoint='api.amex')
api.add_resource(MasterCard, '/mastercard', endpoint='api.mastercard')

