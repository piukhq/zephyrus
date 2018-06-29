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
  
#### Environment Variables

- `SERVICE_API_KEY`
  - String Value, Auth API Key for communication between services.
- `REDIS_HOST`
  - String Value, IP or FQDN of REDIS
- `REDIS_PORT`
  - String Value, Port for REDIS
- `REDIS_PASSWORD`
  - String Value, Password for REDIS
- `HERMES_URL`
  - String Value, URL for Hermes
- `CLIENT_INFO_STORAGE_TIMEOUT`
  - Integer Value, Minimum number of minutes before redis cache should be updated by hermes
