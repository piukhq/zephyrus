from flask_restplus import Resource, Api

api = Api()


@api.route('/amex')
class Amex(Resource):
    def post(self):
        return {'success': True}


@api.route('/mastercard')
class MasterCard(Resource):
    def post(self):
        return {'success': True}
