import falcon

CLIENT_DOES_NOT_EXIST = "CLIENT_DOES_NOT_EXIST"
INVALID_CLIENT_SECRET = "CLIENT_SECRET_DOES_NOT_MATCH"
CONNECTION_ERROR = "CONNECTION_ERROR"
CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
MISSING_PARAMS = "MISSING_PARAMS"
MISSING_AUTH = "MISSING_AUTH"
INVALID_AUTH_FORMAT = "INVALID_AUTH_FORMAT"
INVALID_AUTH_TYPE = "INVALID_AUTH_TYPE"
INVALID_AUTH_TOKEN = "INVALID_AUTH_TOKEN"
AUTH_EXPIRED = "AUTH_EXPIRED"
INVALID_DATA_FORMAT = "INVALID_DATA"
INVALID_AUTH_SETTINGS = "INVALID_AUTH_SETTINGS"


errors = {
    MISSING_PARAMS: {
        "name": "MISSING_PARAMS",
        "message": "The following required parameters were missing from the request: {}",
        "code": falcon.HTTP_400,
    },
    INVALID_DATA_FORMAT: {"name": "INVALID_DATA_FORMAT", "message": "{}", "code": falcon.HTTP_400},
    MISSING_AUTH: {"name": "MISSING_AUTH", "message": "Missing Authorization header.", "code": falcon.HTTP_401},
    INVALID_AUTH_FORMAT: {
        "name": "INVALID_AUTH_FORMAT",
        "message": 'Authorization header must be of the format "Authorization: <type> <credentials>".',
        "code": falcon.HTTP_401,
    },
    INVALID_AUTH_TYPE: {
        "name": "INVALID_AUTH_TYPE",
        "message": 'Authorization type "{}" is invalid. Valid options: Token.',
        "code": falcon.HTTP_401,
    },
    INVALID_AUTH_TOKEN: {
        "name": "INVALID_AUTH_TOKEN",
        "message": "Authorization token is invalid.",
        "code": falcon.HTTP_401,
    },
    AUTH_EXPIRED: {
        "name": "AUTH_EXPIRED",
        "message": "Authentication token has expired. Please request a new one.",
        "code": falcon.HTTP_401,
    },
    CLIENT_DOES_NOT_EXIST: {
        "name": "CLIENT_DOES_NOT_EXIST",
        "message": "The client ID provided does not match any of those in our records",
        "code": falcon.HTTP_401,
    },
    INVALID_CLIENT_SECRET: {
        "name": "INVALID_CLIENT_SECRET",
        "message": "The client secret provided seems to be invalid",
        "code": falcon.HTTP_401,
    },
    CONNECTION_ERROR: {
        "name": "CONNECTION_ERROR",
        "message": "There was a problem connecting to one of our services",
        "code": "545 Connection Error",
    },
    INVALID_AUTH_SETTINGS: {
        "name": "INVALID_AUTH_SETTINGS",
        "message": "Authorisation settings have not been configured.",
        "code": falcon.HTTP_500,
    },
    CONFIGURATION_ERROR: {
        "name": "Configuration error",
        "message": "There is an error with the configuration or it was not possible to retrieve.",
        "code": "536",
    },
}


class CustomException(Exception):
    "Exception raised for errors in the input."

    def __init__(self, name, *format_args, message=None, payload=None):
        self.name = errors[name]["name"]
        self.message = errors[name]["message"]
        self.code = errors[name]["code"]
        self.message = message or errors[name]["message"].format(*format_args)
        self.payload = payload

    def __str__(self):
        return f"{self.name}: {self.message} code: {self.code}"

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["name"] = self.name
        rv["message"] = self.message
        rv["code"] = self.code
        return rv


class AuthException(CustomException):
    pass
