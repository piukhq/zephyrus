from flask_restplus import Resource

from app.authentication.amex import jwt_auth


class Amex(Resource):
    @jwt_auth
    def post(self):
        return {'success': True}


class MasterCard(Resource):
    def post(self):
        return {'success': True}
