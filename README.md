# CMAP Service

CMAP Service is a GraphQL Service that retrieves a wide range of information about domains and GoDaddy accounts such as
1. Host Information (Product, Shopper ID, VIP, Hostname, etc.)
2. Registrar Information (Registrar Name, Abuse Contacts, Domain Create Date, etc.)
3. Shopper Information (Shopper ID, VIP, Shopper Create Date, Domain Count, etc.)

## Cloning
To clone the repository via SSH perform the following
```
git clone git@github.secureserver.net:digital-crimes/cmap_service.git
```

It is recommended that you clone this project into a pyvirtualenv or equivalent virtual environment. For this project, be sure to create a virtual environment with Python 3.6.

This is achievable via `mkproject --python=/usr/local/bin/python3.6 cmap`.

## Installing Dependencies
To install all dependencies for development and testing simply run `make`.

## Building
Building a local Docker image for the respective development environments can be achieved by
```
make [dev, ote, prod]
```

## Deploying
Deploying the Docker image to Kubernetes can be achieved via
```
make [dev, ote, prod]-deploy
```
You must also ensure you have the proper push permissions to Artifactory or you may experience a `Forbidden` message.

## Testing
```
make test     # runs all unit tests
make testcov  # runs tests with coverage
```

## Style and Standards
All deploys must pass Flake8 linting and all unit tests which are baked into the [Makefile](Makfile).

There are a few commands that might be useful to ensure consistent Python style:

```
make flake8  # Runs the Flake8 linter
make isort   # Sorts all imports
make tools   # Runs both Flake8 and isort
```

## Built With
CMAP Service is built utilizing the following key technologies

1. Graphene (GraphQL for Python)
2. Flask
3. Redis


## Running Locally
If you would like to run CMAP Service locally, you will need to specify the following environment variables
1. `sysenv` (dev, ote, prod)
2. `DB_PASS` (Password for MongoDB)
3. `REDIS` (Local instance of REDIS)
4. `BRAND_DETECTION_URL` (Local instance of Brand Detection)
5. `CMAP_PROXY_USER` (User for CMAP Proxy)
6. `CMAP_PROXY_PASS` (Password for CMAP Proxy)
7. `CMAP_PROXY_CERT` (Certificate for connecting to CMAP Proxy)
8. `CMAP_PROXY_KEY` (Key for connecting to CMAP Proxy)
9. `VERTIGO_USER` (User for Vertigo API)
10. `VERTIGO_PASS` (Password for Vertigo API)
11. `DIABLO_USER` (User for Diablo API)
12. `DIABLO_PASS` (Password for Diablo)
13. `ANGELO_USER` (User for Angelo API)
14. `ANGELO_PASS` (Password for Angelo API)
15. `SMDB_USER` (User for SMDB WSDL)
16. `SMDB_PASS` (Password for SMDB WSDL)
17. `MWP_ONE_USER` (User for Managed Wordpress API)
18. `MWP_ONE_PASS` (Password for Managed Wordpress API)
19. `ALEXA_ACCESS_ID` (Access ID for Alexa API)
20. `ALEXA_ACCESS_KEY` (Access key for Alexa API)
21. `CMAP_API_CERT` (Certificate for connecting to CRM SOAP API)
22. `CMAP_API_KEY` (Key for connecting to CRM SOAP API)
23. `WITHOUT_SSO` (flag is set to True for local environments. Defaults to False so as to avoid SSO redirect logic)

CMAP Service can then be run locally by running `python run.py`


# Examples

Curl basic hosting and registrar information
```
curl -X POST -H 'Content-Type:application/graphql' 'https://cmapservice.int.godaddy.com/graphql' -d '{domainQuery(domain:"godaddy.com"){host{ hostingCompanyName ip } registrar{ registrarName domainCreateDate }}}'
```
Output
```
{"data":{"domainQuery":{"host":{"hostingCompanyName":"GoDaddy.com LLC","ip":"208.109.192.70"},"registrar":{"registrarName":"GoDaddy.com, LLC","domainCreateDate":"1999-03-02"}}}}
```

Enter basic hosting and registrar query into web GUI

  1. Navigate to https://cmapservice.int.godaddy.com/graphql
  2. Enter the following into the left pane and press the Play button
```
  {
    domainQuery(domain:"godaddy.com"){
    host{
      hostingCompanyName
      ip
    }
    registrar{
      registrarName
      domainCreateDate
    }
   }
  }
```
  
Hint: pressing Ctrl-Space while your cursor is on the left pane will provide you with possible items to add to your query such as Alexa ranking, ip addresses abuse contacts etc. Be sure to visit the Docs link in the upper right corner to get a sense of all the possible data that can be gathered.
  
A more complex web page example

```
{
  domainQuery(domain:"godaddy.com"){
    host{
      hostingCompanyName
      ip
      dataCenter
      guid
      hostingAbuseEmail
      os
    }
    registrar{
      registrarName
      domainCreateDate
      registrarAbuseEmail
    }
    
    alexaRank
    shopperInfo{
      domainCount
      shopperCreateDate
      shopperId
      vip{
        portfolioType
      }
    }
  }
}
```
  Output
```
  {
  "data": {
    "domainQuery": {
      "host": {
        "hostingCompanyName": "GoDaddy.com LLC",
        "ip": "208.109.192.70",
        "dataCenter": "P3",
        "guid": "28fa828c-5500-11e4-b427-14feb5d40b65",
        "hostingAbuseEmail": [
          "abuse@godaddy.com"
        ],
        "os": "Linux"
      },
      "registrar": {
        "registrarName": "GoDaddy.com, LLC",
        "domainCreateDate": "1999-03-02",
        "registrarAbuseEmail": [
          "abuse@godaddy.com"
        ]
      },
      "alexaRank": 186,
      "shopperInfo": {
        "domainCount": 665,
        "shopperCreateDate": "2002-09-06",
        "shopperId": "1001700",
        "vip": {
          "portfolioType": "CN"
        }
      }
    }
  }
}
```
