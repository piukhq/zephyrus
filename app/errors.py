from flask import jsonify

CLIENT_DOES_NOT_EXIST = 'CLIENT_DOES_NOT_EXIST'
INVALID_CLIENT_SECRET = 'CLIENT_SECRET_DOES_NOT_MATCH'
CONNECTION_ERROR = 'CONNECTION_ERROR'
MISSING_PARAMS = 'MISSING_PARAMS'


errors = {
    MISSING_PARAMS: {
        'name': 'MISSING_PARAMS',
        'message': 'The following required parameters were missing from the request: {}',
        'code': 400,
    },
    CLIENT_DOES_NOT_EXIST: {
        'name': 'CLIENT_DOES_NOT_EXIST',
        'message': 'The client ID provided does not match any of those in our records',
        'code': 401,
    },
    INVALID_CLIENT_SECRET: {
        'name': 'INVALID_CLIENT_SECRET',
        'message': 'The client secret provided seems to be invalid',
        'code': 401,
    },
    CONNECTION_ERROR: {
        'name': 'CONNECTION_ERROR',
        'message': 'There was a problem connecting to one of our services',
        'code': 545,
    }
}


def error_response(name, *format_args):
    error = errors[name]
    return jsonify({
        'error': name,
        'message': error['message'].format(*format_args)
    }), error['code']


class CustomException(Exception):
    """Exception raised for errors in the input.
    """

    def __init__(self, name, *format_args, message=None, payload=None):
        self.name = errors[name]['name']
        self.message = errors[name]['message']
        self.code = errors[name]['code']
        self.message = message or errors[name]['message'].format(*format_args)
        self.payload = payload

    def __str__(self):
        return f"{self.name}: {self.message} code: {self.code}"

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['name'] = self.name
        rv['message'] = self.message
        rv['code'] = self.code
        return rv


class AuthException(CustomException):
    pass

