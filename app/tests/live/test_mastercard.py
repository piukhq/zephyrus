import datetime

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography import x509
from cryptography.x509.oid import NameOID
from signxml import XMLSigner, methods as sign_methods
import requests

from app.tests.test_helpers.signed_xml import SignedXML, MockMastercardAuthTransaction


class Certificate:
    def __init__(self):
        self.common_name = "mysite.com"
        self.cert_subject = self.issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My Company"),
                x509.NameAttribute(NameOID.COMMON_NAME, self.common_name),
            ]
        )

        self.private_key = self.make_private_key()
        self.public_key = self.private_key.public_key()
        self.root_cert = self.make_root_certificate()

    @staticmethod
    def make_private_key():
        key = b"""-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCvjjonH7Gmc1+T
aHZvyj8vGSgcIIOrbw0C8oAgKqJYSNylg0T2yyiMplT/7ys5flb63Cw3X4xDZzZj
Ys3KHIBfY/dQx5BQ96mXYY8fMlaAhfcJqvOWjrG/tSu8NxuR+W0prnaMxFJxdyFk
J3OSX2/1M+hdzS1i/lKrFZVYBfvvoyiXLvCAMLGDs9z7pDJ0WeBLIMRaLCuUkLAH
rNmNnqN7gqTOotlXf3rtS2O+Etz1e3pfP8bE2ikx9eSK5sGJD5Iods2Ngi0KWSnp
ylWZmcDXl48XbJRbsNtNfuYdYIlVWRojEZzt7GGSlPoKsXhHzsr5XU+XoOSrbAwW
FpXxBt0pAgMBAAECggEAPqklWJGXdzH3C0Zd/8jQhJ8WEfQJC0e3/TVRRinxiFF5
cBpKo0wgTRORg0h6xSqzIRc1MQ6JogVVBGRfz6Qcre+gdtTETiIYBlBsJVZySa2H
X4wFJdgI2cRwt91zmcbNj/MVnWj1hEphQL5UIgqui3bbmZ+Cc7MTDr3FcIWyRvX+
HJtLKy5zwxXK/dkTOlmZXbNXmf2DNK4my7/jz4J/Lmd9PL9srFkBWKH+rhsbCFnZ
Wtv5y1m4V9V5IsyRmP25oHiq2OYt7KCwUUsjlKP6wSb54NB5HmPNZebts8S6q7fZ
I3DoQMtsy1KOAr7Iis7qiUu4fbk9NNB5m2cegFtwAQKBgQDfSC8F68WQ+V+oBZkj
C5JTS6NUfG6YF/Rjjq/qQJDNUVeQJWFJBRtSkovYNkAPe/t5VhTVIP7gK6IzwHge
YM/ItAWvRSo2ZFe75zpEe/K8oGGMjleQdT5EWYq7ei//c2BuWDzHHN9lyFht6OY7
4qtPUWeNyXmkQSZyopGC2fgFsQKBgQDJR7ewX/UemO7X8RiIBHr9glPhL87EUP7B
ggUrXiUjua3uF5t2oMZqWak6G1Ptp9lJpuB5cINX5DSv0x/32JW70QvI/ZBFlslu
KdXhI9+Uy1Quk3mXLIW40Q+eQ2HCb5oQAKcuOYv1lmnL/Ig5I2S84SZqgDa3VMJ3
AEtbgC+U+QKBgQCB/vjBrb9c5JN4s6mw6a/LpyH0sm2BR5EV1aE99VFY+J7OYbT+
WmbJ8GBTBWLOoRSMVD3UyF0cDstk7g4BQcQ3yff1T4OAH3OlBr652KA+ifHBb64z
gM875BYNiNohE/90vxLDql+2VqqFcy94dkPe7jooJsEXjIbh/xxQ3q60QQKBgQCn
TliuX6S1ETP/BOV6Mhc1X75vQLjiz9xiZrv7R18hqfacIL1VxuAGiI60wQBrXAiu
Qur1poNWbFcrCxfYgQw9OM9N+w6P+X1nd5jTcmknGjfYGzeHZDem3wfXanT5FKD/
yjssniLrOWKpbzigHf5fTdsLzZUtoGOgXPtGjG+AqQKBgDWi4J4f7Y1jM2feZgrr
ly5PtA5aiCqq+Y1eq/PzvmjD9dzATOeAFNppx6RXiF9us7oAdN3253CeUMpsZ+SO
aAG+jyCgkD+KLThilZZ2hr8FohXt7UFKFx69MQdIudd9wn0MXpu8LDR6ri8mcjA6
3YtRy2cjeC/w5lSaJybtiwfF
-----END PRIVATE KEY-----
"""
        return serialization.load_pem_private_key(key, password=None, backend=default_backend())

    @property
    def private_pem_key(self):
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(b"passphrase"),
        ).decode("utf-8")

    def make_root_certificate(self):
        # Various details about who we are. For a self-signed certificate the
        # subject and issuer are always the same.
        return (
            x509.CertificateBuilder()
            .subject_name(self.cert_subject)
            .issuer_name(self.issuer)
            .public_key(self.public_key)
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=2))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False)
            .sign(self.private_key, hashes.SHA256(), default_backend())
        )

    @property
    def root_pem_certificate(self):
        return self.root_cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

    def sign(self, xml):
        return XMLSigner(
            method=sign_methods.enveloped,
            signature_algorithm="rsa-sha1",
            digest_algorithm="sha1",
            c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#",
        ).sign(xml, key=self.private_key, cert=self.root_pem_certificate)


cert = Certificate()
signed_xml = SignedXML(MockMastercardAuthTransaction(), signing_cert=cert)
resp = requests.post(
    "https://api.dev.gb.bink.com/auth_transactions/mastercard",
    headers={"Content-Type": "application/xml"},
    data=signed_xml.xml,
)
print(resp.text)
