# CMAP Service

CMAP Service is a GraphQL Service that retrieves a wide range of information about domains and GoDaddy accounts such as
* Host Information (Product, Shopper ID, VIP, Hostname, etc.)
* Registrar Information (Registrar Name, Abuse Contacts, Domain Create Date, etc.)
* Shopper Information (Shopper ID, VIP, Shopper Create Date, Domain Count, etc.)

## Table of Contents
  1. [Cloning](#cloning)
  2. [Installing Dependencies](#installing-dependencies)
  3. [Building](#building)
  4. [Deploying](#deploying)
  5. [Testing](#testing)
  6. [Style and Standards](#style-and-standards)
  7. [Built With](#built-with)
  8. [Running Locally](#running-locally)
  9. [Examples](#examples)

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
### Unit Tests
```
make test     # runs all unit tests
make testcov  # runs tests with coverage
```
### Wiremock in dev
Due to the lack of a robust dev environment here @ GoDaddy, we needed to mock out our external interfaces in order to test a variety of enrichment scenarios. When testing enrichment we need to be able to determine; Is the domain registered here? Is the domain hosted here? What shopper owns the domain? What shopper owns the hosting product? What are the identifiers for those products? What are the shopper contact details? Rather than hard-code these values, we determined that it would be better to be able to encode them in the domain itself. This allows the tester to specify randomly generated data when they don't care, or create links between things when they do care. Here is the regex that describes how to encode the enrichment data into the domain.

```
      domain here?        shopper       domain id    hosted here?    shopper       guid
^stub(registered|foreign)(\d{9}|random)(\d{9}|random)(diablo|gocentral|mwpone|foreign)(\d{9}|random)([0-9A-Fa-f]{12}|random)-.*\.com$
```
For example, the domain `stubforeignrandomrandomdiablo123456789random-placeholder.com` tells us that we want CMAP to detect this domain as registered elsewhere, but hosted as a diablo product under shopper 123456789 with a random product identifier.

## Style and Standards
All deploys must pass Flake8 linting and all unit tests which are baked into the [Makefile](Makefile).

There are a few commands that might be useful to ensure consistent Python style:

```
make flake8  # Runs the Flake8 linter
make isort   # Sorts all imports
make tools   # Runs both Flake8 and isort
```

## Built With
CMAP Service is built utilizing the following key technologies

* Graphene (GraphQL for Python)
* Flask
* Redis


## Running Locally
If you would like to run CMAP Service locally, you will need to specify the following environment variables
* `sysenv` (Set to `local`. Other values include: `dev`, `ote`, `prod`)
* `ALEXA_ACCESS_ID` (Access ID for Alexa API)
* `ALEXA_ACCESS_KEY` (Access key for Alexa API)
* `ANGELO_USER` (User for Angelo API)
* `ANGELO_PASS` (Password for Angelo API)
* `CMAP_API_CERT` Path to apiuser.cmap.int certificate file (for connecting to CRM SOAP API)
* `CMAP_API_KEY` Path to apiuser.cmap.int key file (for connecting to CRM SOAP API)
* `CMAP_PROXY_CERT` Path to proxyuser.cmap.int.godaddy.com certificate file (for connecting to CMAP Proxy, prod only)
* `CMAP_PROXY_KEY` Path to proxyuser.cmap.int.godaddy.com key file(for connecting to CMAP Proxy, prod only)
* `CMAP_PROXY_USER` (User for CMAP Proxy)
* `CMAP_PROXY_PASS` (Password for CMAP Proxy)
* `CMAP_SERVICE_CERT` Path to cmapservice.int certificate file (for connecting to SUBSCRIPTIONS & GOCENTRAL APIs)
* `CMAP_SERVICE_KEY` Path to cmapservice.int key file (for connecting to SUBSCRIPTIONS & GOCENTRAL APIs)
* `DB_PASS` (Password for MongoDB)
* `DIABLO_USER` (User for Diablo API)
* `DIABLO_PASS` (Password for Diablo API)
* `MWP_ONE_USER` (User for Managed Wordpress API)
* `MWP_ONE_PASS` (Password for Managed Wordpress API)
* `SMDB_USER` (User for SMDB WSDL)
* `SMDB_PASS` (Password for SMDB WSDL)
* `VALUATION_KEY` (Access key for Valuation API)
* `VERTIGO_USER` (User for Vertigo API)
* `VERTIGO_PASS` (Password for Vertigo API)

Steps to run locally:
1. Enter `docker-compose up` from a command line within the _cmap_service_ directory which contains the _docker-compose.yaml_ file
   1. This will launch local instances of _redis_ and _mongodb_ on ports _6379_ and _27017_ respectively
      1. `redis-cli` can be used from a command line to access the _redis_ store
      2. `Robo3T v1.3` or similar Mongo GUI _should_ be able to be configured to access the _mongodb_ instance
2. Configure environment variables above
3. Enter `python run.py` from a command line within the _cmap_service_ directory


## Examples

Curl basic hosting and registrar information using CERT_JWT (view CN_WHITELIST in settings.py to obtain CN cert to use). Visit [this link](https://confluence.godaddy.com/display/ITSecurity/Accessing+Shopper+Locker+Service#AccessingShopperLockerService-ObtainaJWT) to view steps for requesting a cert JWT from a cert/key pair.
```
curl -X POST -H 'Content-Type:application/graphql' --header 'Accept: application/json' --header 'Authorization: sso-jwt CERT_JWT' 'https://cmapservice.int.godaddy.com/graphql' -d '{domainQuery(domain:"godaddy.com"){host{ hostingCompanyName ip } registrar{ registrarName domainCreateDate }}}'
```
Output
```
{"data":{"domainQuery":{"host":{"hostingCompanyName":"GoDaddy.com LLC","ip":"208.109.192.70"},"registrar":{"registrarName":"GoDaddy.com LLC","domainCreateDate":"1999-03-02T00:00:00.000Z"}}}}
```

Enter basic hosting and registrar query into web GUI

  1. Navigate to https://cmapservice.int.godaddy.com/graphql
  2. Enter the following into the left pane and press the Play button
```
{
  domainQuery(domain: "example.com") {
    host {
      hostingCompanyName
      ip
    }
    registrar {
      registrarName
      domainCreateDate
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
        "ip": "64.202.167.129"
      },
      "registrar": {
        "registrarName": "RESERVED-Internet Assigned Numbers Authority",
        "domainCreateDate": "1995-08-14"
      }
    }
  }
}
```
  
Hint: pressing Ctrl-Space while your cursor is on the left pane will provide you with possible items to add to your query such as Alexa ranking, ip addresses abuse contacts etc. Be sure to visit the Docs link in the upper right corner to get a sense of all the possible data that can be gathered.
  
[Click here](https://cmapservice.int.godaddy.com/graphql?query=%7B%0A%20%20domainQuery(domain%3A%20"godaddy.com")%20%7B%0A%20%20%20%20alexaRank%0A%20%20%20%20apiReseller%20%7B%0A%20%20%20%20%20%20parent%0A%20%20%20%20%20%20child%0A%20%20%20%20%7D%0A%20%20%20%20blacklist%0A%20%20%20%20domain%0A%20%20%20%20domainStatus%20%7B%0A%20%20%20%20%20%20statusCode%0A%20%20%20%20%7D%0A%20%20%20%20host%20%7B%0A%20%20%20%20%20%20createdDate%0A%20%20%20%20%20%20dataCenter%0A%20%20%20%20%20%20friendlyName%0A%20%20%20%20%20%20guid%0A%20%20%20%20%20%20containerId%0A%20%20%20%20%20%20brand%0A%20%20%20%20%20%20hostingAbuseEmail%0A%20%20%20%20%20%20hostingCompanyName%0A%20%20%20%20%20%20hostname%0A%20%20%20%20%20%20ip%0A%20%20%20%20%20%20os%0A%20%20%20%20%20%20product%0A%20%20%20%20%20%20shopperId%0A%20%20%20%20%20%20mwpId%0A%20%20%20%20%20%20vip%20%7B%0A%20%20%20%20%20%20%20%20accountRepFirstName%0A%20%20%20%20%20%20%20%20accountRepLastName%0A%20%20%20%20%20%20%20%20accountRepEmail%0A%20%20%20%20%20%20%20%20portfolioType%0A%20%20%20%20%20%20%20%20blacklist%0A%20%20%20%20%20%20%20%20shopperId%0A%20%20%20%20%20%20%7D%0A%20%20%20%20%20%20privateLabelId%0A%20%20%20%20%7D%0A%20%20%20%20registrar%20%7B%0A%20%20%20%20%20%20brand%0A%20%20%20%20%20%20domainCreateDate%0A%20%20%20%20%20%20domainId%0A%20%20%20%20%20%20registrarName%0A%20%20%20%20%20%20registrarAbuseEmail%0A%20%20%20%20%7D%0A%20%20%20%20shopperInfo%20%7B%0A%20%20%20%20%20%20shopperId%0A%20%20%20%20%20%20domainCount%0A%20%20%20%20%20%20shopperCreateDate%0A%20%20%20%20%20%20shopperEmail%0A%20%20%20%20%20%20shopperFirstName%0A%20%20%20%20%20%20shopperLastName%0A%20%20%20%20%20%20shopperAddress1%0A%20%20%20%20%20%20shopperAddress2%0A%20%20%20%20%20%20shopperCity%0A%20%20%20%20%20%20shopperState%0A%20%20%20%20%20%20shopperPostalCode%0A%20%20%20%20%20%20shopperCountry%0A%20%20%20%20%20%20shopperPhoneMobile%0A%20%20%20%20%20%20shopperPhoneHome%0A%20%20%20%20%20%20shopperPhoneWork%0A%20%20%20%20%20%20shopperPhoneWorkExt%0A%20%20%20%20%20%20vip%20%7B%0A%20%20%20%20%20%20%20%20accountRepFirstName%0A%20%20%20%20%20%20%20%20accountRepLastName%0A%20%20%20%20%20%20%20%20accountRepEmail%0A%20%20%20%20%20%20%20%20portfolioType%0A%20%20%20%20%20%20%20%20blacklist%0A%20%20%20%20%20%20%20%20shopperId%0A%20%20%20%20%20%20%7D%0A%20%20%20%20%7D%0A%20%20%20%20securitySubscription%20%7B%0A%20%20%20%20%20%20sucuriProduct%0A%20%20%20%20%7D%0A%20%20%20%20sslSubscriptions%20%7B%0A%20%20%20%20%20%20certCommonName%0A%20%20%20%20%20%20certType%0A%20%20%20%20%20%20createdAt%0A%20%20%20%20%20%20expiresAt%0A%20%20%20%20%7D%0A%20%20%7D%0A%7D) to run a more complex query in the production environment
