# MasterCard Endpoint

The MasterCard endpoint is `/auth_transactions/mastercard`. Test it with the following cURL.

## Auth transaction

MasterCard uses nasty signed XML evilness:

```shell
curl --url http://localhost:9000/auth_transactions/mastercard \
  --header 'Content-Type: text/xml' \
  --data '<?xml version="1.0" encoding="UTF-8"?><Transaction xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <refNum>MNWF2MDNQ</refNum>
  <timestamp>2021-09-29T08:50:23.0000152-05:00</timestamp>
  <bankCustNum>ZDkzrv5eCZxgt5aGDLjC3PnrR67</bankCustNum>
  <transId>17932322049</transId>
  <transAmt>5.10</transAmt>
  <merchNameLoc>WASABI</merchNameLoc>
  <transDate>09292021</transDate>
  <transTime>145000</transTime>
  <merchCatCd>5812</merchCatCd>
  <acquirerIca>012216</acquirerIca>
  <retCd/>
  <merchId>1510540</merchId>
<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#"><ds:SignedInfo><ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/><ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/><ds:Reference URI=""><ds:Transforms><ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/><ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"><ec:InclusiveNamespaces xmlns:ec="http://www.w3.org/2001/10/xml-exc-c14n#" PrefixList="code ds kind rw samlp saml typens #default xsd xsi"/></ds:Transform></ds:Transforms><ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/><ds:DigestValue>JfDWYZvewxEpB9RmwiS0ve1RuGU=</ds:DigestValue></ds:Reference></ds:SignedInfo><ds:SignatureValue>G8t6ouUQJu2FNY8/5nbral/vUrEnc/MxnBae0Mr2J0po+YDckEPIxdQqZ2y5lC08+wnTWnLhD4QM&#13;
DVaNH4DE3OWpYvpSvjYFhJmP80ZbRi9HczW+JZ4t0zQo2sZh8RgFTJEzMJp8KnuiNXTkoSL2uS84&#13;
BTHzo1TDyQYa0f/m+XnQGpfTjcHHwQ34J/DJ1AEZzgGE2tGlDRG6uxbHiiUy795ZaRO+B0iPESkP&#13;
pZxOmvvYR1JpdCDOPopi087T6r2GmTxD9q3iAxbo1jBr3rE99SlKA3EaEPdYJl5950t+8G3+utAN&#13;
9nh0uYu7xTDIiPTy6Bk+XLbHOXZQgGkvDhg0Ww==</ds:SignatureValue><ds:KeyInfo><ds:X509Data><ds:X509Certificate>MIIHWzCCBkOgAwIBAgIRAL8BPxuUxfl0AAAAAFD7pZMwDQYJKoZIhvcNAQELBQAwgboxCzAJBgNV&#13;
BAYTAlVTMRYwFAYDVQQKEw1FbnRydXN0LCBJbmMuMSgwJgYDVQQLEx9TZWUgd3d3LmVudHJ1c3Qu&#13;
bmV0L2xlZ2FsLXRlcm1zMTkwNwYDVQQLEzAoYykgMjAxMiBFbnRydXN0LCBJbmMuIC0gZm9yIGF1&#13;
dGhvcml6ZWQgdXNlIG9ubHkxLjAsBgNVBAMTJUVudHJ1c3QgQ2VydGlmaWNhdGlvbiBBdXRob3Jp&#13;
dHkgLSBMMUswHhcNMTkxMjExMjExODU0WhcNMjIwMzEwMjE0ODUzWjCBijELMAkGA1UEBhMCQkUx&#13;
ETAPBgNVBAcTCFdhdGVybG9vMS4wLAYDVQQKEyVNYXN0ZXJDYXJkIEludGVybmF0aW9uYWwgSW5j&#13;
b3Jwb3JhdGVkMRUwEwYDVQQLEwxTQU1MIFNpZ25pbmcxITAfBgNVBAMTGHNpZ25pbmcud3MubWNy&#13;
ZXdhcmRzLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALC318aHrpW6uHBxPRpH&#13;
G/Tz9+gRj5Zx5+yRT5xh7+kF86bUnKQEit3ZYm5U2JreySJ4ylPm/7lVVMETycRD87hiWm+LtW6M&#13;
WZXn8M/qR1G0nuAme+/CCO6OyegRwPH+gbbtFggI/SXe6SJ2u4lwGEZqbtWrKJWeFcGYRmgoVZgT&#13;
Sr2j09I9xl7zjxetWofDXOrZqSEpF7SIRURN/era3xpZvkTBc8jlZs866Ko7i3SSt7jTuzvonTHI&#13;
dKObIYGQggp0fGuvtfHhMJ0juPETWCKRugo3AedSBz4l9IMwO3xmD7SHO3xRf6z7qm6bqTwECtGg&#13;
j7VJgARYHqn1i2JTET8CAwEAAaOCA4gwggOEMCMGA1UdEQQcMBqCGHNpZ25pbmcud3MubWNyZXdh&#13;
cmRzLmNvbTCCAfUGCisGAQQB1nkCBAIEggHlBIIB4QHfAHYAh3W/51l8+IxDmV+9827/Vo1HVjb/&#13;
SrVgwbTq/16ggw8AAAFu9u+33AAABAMARzBFAiAv5Ffq8wC/aQEJG9tUHb7bAhx9UYCzNqLzdg+0&#13;
zM1O1QIhAOgTP4OawLwP/GhtB8awFwQL6q7n2eaLor5y+HzRIRQ/AHYAVhQGmi/XwuzT9eG9RLI+&#13;
x0Z2ubyZEVzA75SYVdaJ0N0AAAFu9u+37gAABAMARzBFAiEAjw5m5L9xd1scyPCADiq5PymU9C78&#13;
8H5R/AIwtzdpHzICIDBTHo5fQwwHpvLYDGmQsqdbzk8L2wgCirKF4nJbRScLAHUAVYHUwhaQNgFK&#13;
6gubVzxT8MDkOHhwJQgXL6OqHQcT0wwAAAFu9u+3+wAABAMARjBEAiAInXZWfmXhhRmILAPfRT7m&#13;
FtLGzMGPT6H8LUBWydD/PAIgY/N5tgVKsOifsopZ8cumGgFIU4qeCpsVlhiKN6lHJYoAdgCkuQmQ&#13;
tBhYFIe7E6LMZ3AKPDWYBPkb37jjd80OyA3cEAAAAW7277gpAAAEAwBHMEUCICaxeLSeyXdy+iPh&#13;
ffZo9iZyr6SKdOO6hZ4YjqzIx22qAiEAvrkMohRZxYRz5/C+abImgrmt7HhzvYRah2TCAZN19Lkw&#13;
DgYDVR0PAQH/BAQDAgWgMB0GA1UdJQQWMBQGCCsGAQUFBwMBBggrBgEFBQcDAjAzBgNVHR8ELDAq&#13;
MCigJqAkhiJodHRwOi8vY3JsLmVudHJ1c3QubmV0L2xldmVsMWsuY3JsMEsGA1UdIAREMEIwNgYK&#13;
YIZIAYb6bAoBBTAoMCYGCCsGAQUFBwIBFhpodHRwOi8vd3d3LmVudHJ1c3QubmV0L3JwYTAIBgZn&#13;
gQwBAgIwaAYIKwYBBQUHAQEEXDBaMCMGCCsGAQUFBzABhhdodHRwOi8vb2NzcC5lbnRydXN0Lm5l&#13;
dDAzBggrBgEFBQcwAoYnaHR0cDovL2FpYS5lbnRydXN0Lm5ldC9sMWstY2hhaW4yNTYuY2VyMB8G&#13;
A1UdIwQYMBaAFIKicHTdvFM/z3vU981/p2DGCky/MB0GA1UdDgQWBBQ4ASDcmAYdAiYm9xSmopEJ&#13;
EPXEuzAJBgNVHRMEAjAAMA0GCSqGSIb3DQEBCwUAA4IBAQCQEmUUR1oPIQGkavvJtBYxb4aX/RbX&#13;
OO3GcpUtWPl1MlKNwg0mu6rl9bX7Bu8JYlZ3XQd9Qn+yImah/bRsqSUlq8/qeM6M0SWuJarzZEIu&#13;
b1Q1Txp5mo9o3Pzniq9GPmmL5ECKs1X4n6Vi3WyKIBCE4SFjTWGp2uOrh7w7p9VMp1fd12x7jmZ7&#13;
QWmAyOw/Tq/oGvPNSHm8bo9rH1lHUPXxbxfDEc4SpbCYigG8tMhjxAQDnkrxYdc38SUEntFX+Pp3&#13;
SZX4gtSjMxv9LP+Fpg5s5tKOEFWuBJlw8pFXhrMebeilFJNOfyZhUllQoKEjpYx73X6gnaA0upi3&#13;
RsxLjRZw</ds:X509Certificate></ds:X509Data></ds:KeyInfo></ds:Signature></Transaction>'
```

Response:
```
"<?xml version=\"1.0\" encoding=\"UTF-8\"?><Transaction xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n  <refNum>MNWF2MDNQ</refNum>\n  <timestamp>2021-09-29T08:50:23.0000152-05:00</timestamp>\n  <bankCustNum>ZDkzrv5eCZxgt5aGDLjC3PnrR67</bankCustNum>\n  <transId>17932322049</transId>\n  <transAmt>5.10</transAmt>\n  <merchNameLoc>WASABI</merchNameLoc>\n  <transDate>09292021</transDate>\n  <transTime>145000</transTime>\n  <merchCatCd>5812</merchCatCd>\n  <acquirerIca>012216</acquirerIca>\n  <retCd/>\n  <merchId>1510540</merchId>\n</Transaction>"
```
Currently it looks like a JSON string because the content type is not text/xml