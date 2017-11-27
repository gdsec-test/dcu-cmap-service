# CMAP Service

CMAP Service is a GraphQL Service that retrieves a wide range of information about domains and GoDaddy accounts.

## Cloning
To clone the repository via SSH perform the following
```
git clone git@github.secureserver.net:ITSecurity/cmap_service.git
```
It is recommended that you clone this project into a pyvirtualenv or equivalent virtual enviornment.

## Installing Dependencies
You can install the required dependencies via
```
pip install -r requirements.txt
```

## Building
In order to build the project locally you can run the following commands
```
make dev
```
```
make ote
```
```
make prod
```

## Deploying
Deploying CMAP Service to Kubernetes can be achieved via
```
make dev-deploy
```
```
make ote-deploy
```
```
make prod-deploy
```

## Testing
In order to run the tests you must first install the required dependencies via
```
pip install -r test_requirements.txt
```

After this you may run the tests via
```
nosetests tests/ --cover-package=service/
```
Optionally, you may provide the flag `--with-coverage` to `nosetests` to determine the test coverage of this project.

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
