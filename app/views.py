from flask_restplus import Resource


class Amex(Resource):
    def post(self):
        return {'success': True}


class MasterCard(Resource):
    def post(self):
        return {'success': True}
