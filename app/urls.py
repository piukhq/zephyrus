from collections import namedtuple

from app.authentication.token_utils import Auth, Me
from app.views import Amex, MasterCard, HealthCheck, Visa

url = namedtuple("url", ["uri_template", "resource"])

urlpatterns = [
    url('/healthz', HealthCheck),
    url('/auth_transactions/authorize', Auth),
    url('/me', Me),
    url('/auth_transactions/amex', Amex),
    url('/auth_transactions/mastercard', MasterCard),
    url('/auth_transactions/visa', Visa)
]
