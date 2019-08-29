from collections import namedtuple

from app.amex import AmexAuthView, AmexMeView, AmexView
from app.mastercard import MasterCardView
from app.views import HealthCheck
from app.visa import VisaView

url = namedtuple("url", ["uri_template", "resource"])

urlpatterns = [
    url("/healthz", HealthCheck),
    url("/auth_transactions/authorize", AmexAuthView),
    url("/me", AmexMeView),
    url("/auth_transactions/amex", AmexView),
    url("/auth_transactions/mastercard", MasterCardView),
    url("/auth_transactions/visa", VisaView),
]
