# CMAP Service

CMAP Service is a GraphQL Service that retrieves a wide range of information about domains and GoDaddy accounts such as
1. Host Information (Product, Shopper ID, VIP, Hostname, etc.)
2. Registrar Information (Registrar Name, Abuse Contacts, Domain Create Date, etc.)
3. Shopper Information (Shopper ID, VIP, Shopper Create Date, Domain Count, etc.)

## Cloning
To clone the repository via SSH perform the following
```
git clone git@github.secureserver.net:ITSecurity/cmap_service.git
```
It is recommended that you clone this project into a pyvirtualenv or equivalent virtual enviornment.

## Installing Dependencies
You can install the required private dependencies via
```
pip install -r private_pips.txt
```
Followed by installing public dependencies via
```
pip install -r requirements.txt
```

## Building
In order to build the project locally you can run the following commands
```
make [dev, ote, prod]
```

## Deploying
Deploying CMAP Service to Kubernetes can be achieved via
```
make [dev, ote, prod]-deploy
```

## Testing
In order to run the tests you must first install the required dependencies via
```
pip install -r test_requirements.txt
```

After this you may run the tests via
```
nosetests tests/
```
Optionally, you may provide the flags `--with-coverage --cover-package=service/` to `nosetests` to determine the test coverage of this project.

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
8. `VERTIGOUSER` (User for Vertigo API)
9. `VERTIGOPASS` (Password for Vertigo API)
10. `DIABLOUSER` (User for Diablo API)
11. `DIABLOPASS` (Password for Diablo)
12. `ANGELOUSER` (User for Angelo API)
13. `ANGELOPASS` (Password for Angelo API)
14. `SMDBUSER` (User for SMDB WSDL)
15. `SMDBPASS` (Password for SMDB WSDL)
16. `MWPONEUSER` (User for Managed Wordpress API)
17. `MWPONEPASS` (Password for Managed Wordpress API)
18. `ACCESS_ID` (Access ID for Alexa API)
19. `SECRET_ACCESS_KEY` (Access key for Alexa API)

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
