# Zephyrus

TODO all the badges

Microservice to process auth transactions.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Prerequisites](#prerequisites)
- [Dependencies](#dependencies)
- [Project Setup](#project-setup)
  - [Virtual Environment](#virtual-environment)
  - [Development API Server](#development-api-server)
  - [Unit Tests](#unit-tests)
  - [Inspecting RabbitMQ](#inspecting-rabbitmq)
- [Deployment](#deployment)
    - [Environment Variables](#environment-variables)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Prerequisites

- [poetry](https://python-poetry.org/docs/)

## Dependencies

The following is a list of the important dependencies used in the project. You do not need to install these manually. 
See [project setup](#project-setup) for installation instructions.

- [Falcon](https://falcon.readthedocs.io/en/stable/) - Falcon Python web framework.
- [Sentry SDK](https://docs.sentry.io/quickstart?platform=python) - Client for the Sentry error reporting platform. Includes Flask integration.
- [RabbitMQ](https://www.rabbitmq.com/) - AMQP Message broker.
- [Azure KeyVault Secrets](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets) - Azure KeyVault secrets library.
- [AzureCLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) - Used to magically have credentials to the Dev Azure KeyVault.
- [OpenTracing](https://opentracing.io/) - Enables request level tracing

## Project Setup

Poetry is used for managing project dependencies and execution.

### Virtual Environment

To create a virtualenv and install required software packages:

```bash
poetry install
```

Project configuration is done through environment variables. A convenient way to set these is in a `.env` file in the project root. 
This file will be sourced by Poetry when `poetry run` and `poetry shell` are used. 
See `settings.py` for configuration options that can be set in this file.

To make a `.env` file from the provided example:

```bash
cp .env.example .env
```

The provided example is sufficient as a basic configuration, but modification may be required for specific use-cases.

The `.env` file contains connection parameters for RabbitMQ used in the project; 
The default connection parameters assume a local instance of these services listening on ports 55672 (RabbitMQ)

To quickly create docker containers for the required services:

```bash
scripts/services
```

### Development API Server

The falcon development server is used for running the project locally. 
This should be replaced with a WSGI-compatible server for deployment to a live environment.

To run the Falcon development server:

```bash
scripts/api
```

* VISA request info - [link](./VISA.md)
* AMEX request info - [link](./AMEX.md)
* MasterCard request info - [link](./MASTERCARD.md)

Run the following to generate mastercard certs:
```bash
scripts/send_transaction gen-cert
```

Send random transactions:
```bash
scripts/send_transaction visa
scripts/send_transaction mastercard
scripts/send_transaction amex
```

### Unit Tests

Testing is done with `pytest`.

To execute a full test run:

```bash
scripts/test
```

### Inspecting RabbitMQ

```
http://localhost:55673/
User: guest
Password: guest
```

This will bring up the RabbitMQ management interface which you can see queued transactions in.

## Deployment

There is a Dockerfile provided in the project root. Build an image from this to get a deployment-ready version of the project.

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

- `VAULT_URL`
  - String value, URL to Hashicorp Vault
- `VAULT_TOKEN`
  - String value, Access token for Hashicorp Vault. Obtained from Kubernetes secrets.