### Zephyrus
Microservice to process auth transactions.


#### Local Setup

- Clone the project and run:

  `pipenv install`

- Create a .env file for local development with the following:

  FLASK_APP=zephyrus

  FLASK_ENV=development


- To run the server:
`flask run` or
`python manage.py runserver`

  This should run the server in development mode with Debug set to True.
  
- Install on azure the Mastercard Signing certificate (required to use auth transaction messages from mastercard)
  - A signing certificate in pem format should be uploaded to the defined location 
  
  - The default for dev-media container is "zephyrus/certificates/mc_pem_cert".
  
  The signing certificate and a master key is used by MasterCard to create the certificate contained in each 
  signed XML message from them.  We require only the signing certificate to verify the certificate and signature
  in each message.
  
  A valid signing certificate should look like this:
  
~~~~
-----BEGIN CERTIFICATE-----
MIIDXjCCAkagAwIBAgIUDDz0uGn7QhAyTBcB+xVSg53i4AswDQYJKoZIhvcNAQEL
BQAwXDELMAkGA1UEBhMCVVMxCzAJBgNVBAgMAkNBMRYwFAYDVQQHDA1TYW4gRnJh
bmNpc2NvMRMwEQYDVQQKDApNeSBDb21wYW55MRMwEQYDVQQDDApteXNpdGUuY29t
MB4XDTE4MDcwMzA5NDMwMVoXDTE4MDcwNTA5NDMwMVowXDELMAkGA1UEBhMCVVMx
CzAJBgNVBAgMAkNBMRYwFAYDVQQHDA1TYW4gRnJhbmNpc2NvMRMwEQYDVQQKDApN
eSBDb21wYW55MRMwEQYDVQQDDApteXNpdGUuY29tMIIBIjANBgkqhkiG9w0BAQEF
AAOCAQ8AMIIBCgKCAQEAxzZ3rQq5mOD8vRAEVDPMIsRHREZXi71eHmC41LKCqa2Q
BuzKzwlsPAK/hBTDhBiPnN3pByICsBb+jgyEBO5SEJ7MQHgbqxVk0HUHaUnDZibo
8uovXXzhiiicg5VHcEuBYgoCDn15kuIX129DOsitdk/5RNP5pGuRpgzPN1cUyhpN
g8kLQBpz4OIeUOwXmfbps0i6IGdx0rcrXv6KVHivXaoCm4tXnyhY+j7P3XudEKr1
W7uvXFV3fPL5xJbCxbujALGeby/HG3yIAs9QqNJcapFuH50ndSWZ5yi/KiqON2DI
YSLeA9rmKgOET0Ld2dwTjCvisENYzStQXa+akgoTXwIDAQABoxgwFjAUBgNVHREE
DTALgglsb2NhbGhvc3QwDQYJKoZIhvcNAQELBQADggEBAEQoIMs7L4pUj2pyWk4r
f5FWUjB2wtKZL2/bK7/JQBeokWDUoVh7XJ7B00fEmrPyQ0Z9JuOZxdo++uOEm763
2HdsSWoedHmtOOMa6tcmnVSFfFi4zUQz3GlumxZ7GhzJz7jybRDqG/wg3/HHLRYa
gbdPqv0kzFPHmNcyYeUsbB/ugKZvvC0fFT28Cvf40z4c0cpoz88FXQALmkCcS/1w
+/PiDb223vfbzGblnhMSuCSJNaKJ4ucuJAbDEVJbhfkU0CbHC0RhHKCZ3MD4auHQ
Lpap25Wk9tNe6KWqgggrxscUjV1ArCxgoZmXPj3ndLZwDeKMgiPz6p+h2spTYhPa
Iaw=
-----END CERTIFICATE-----
~~~~
 
  
#### Environment Variables

- `SERVICE_API_KEY`
  - String Value, Auth API Key for communication between services.
- `HERMES_URL`
  - String Value, URL for Hermes
- `CLIENT_INFO_STORAGE_TIMEOUT`
  - Integer Value, Minimum number of minutes before redis cache should be updated by hermes
- `AZURE_ACCOUNT_NAME`
  - Azure Account Name defaults to "bink"
- `AZURE_ACCOUNT_KEY` 
  - Azure account key must be set in environment
- `AZURE_CONTAINER`
  - The container name defaults to "dev-media"
- `AZURE_CERTIFICATE_FOLDER`  
  - The path to certificates defaults to "zephyrus/certificates/"
  - This is the first part of the Azure path which when combined with the MASTERCARD_CERTIFICATE_BLOB_NAME provides the full path to the location the certificate must be uploaded.
- `MASTERCARD_CERTIFICATE_BLOB_NAME`
  - The file name or end part of path specific to Mastercard defaults to "mc_perm_cert"
- `VAULT_URL`
  - String value, URL to Hashicorp Vault
- `VAULT_TOKEN`
  - String value, Access token for Hashicorp Vault. Obtained from Kubernetes secrets.

