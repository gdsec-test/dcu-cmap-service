REPONAME=digital-crimes/cmap_service
BUILDROOT=$(HOME)/dockerbuild/$(REPONAME)
DOCKERREPO=gdartifactory1.jfrog.io/docker-dcu-local/cmap_service
DATE=$(shell date)
COMMIT=
BUILD_BRANCH=origin/main
SHELL=/bin/bash

define deploy_k8s
	docker push $(DOCKERREPO):$(2)
	cd k8s/$(1) && kustomize edit set image $$(docker inspect --format='{{index .RepoDigests 0}}' $(DOCKERREPO):$(2))
	kubectl --context $(3) apply -k k8s/$(1)
	cd k8s/$(1) && kustomize edit set image $(DOCKERREPO):$(1)
endef

all: init

init:
	pip3 install -r test_requirements.txt --use-pep517
	pip3 install -r requirements.txt --use-pep517
	pip3 install -r gddy-requirements.txt --use-pep517

.PHONY: lint
lint:
	isort --atomic .
	flake8 --config ./.flake8 .

.PHONY: unit-test
unit-test: lint
	@echo "----- Running tests -----"
	sysenv=dev python -m unittest discover tests "*_tests.py"

.PHONY: testcov
testcov:
	@echo "----- Running tests with coverage -----"
	@coverage run --source=service -m unittest discover tests "*_tests.py"
	@coverage xml
	@coverage report


.PHONY: prep
prep: unit-test
	@echo "----- preparing $(REPONAME) build -----"
	# stage pips we will need to install in Docker build
	mkdir -p $(BUILDROOT)
	cp -rp ./* $(BUILDROOT)
	cp -rp ~/.pip $(BUILDROOT)/pip_config

.PHONY: dev
dev: prep
	@echo "----- building $(REPONAME) dev -----"
	docker build -t $(DOCKERREPO):dev $(BUILDROOT)

.PHONY: test-env
test-env: prep
	@echo "----- building $(REPONAME) test -----"
	docker build -t $(DOCKERREPO):test $(BUILDROOT)

.PHONY: ote
ote: prep
	@echo "----- building $(REPONAME) ote -----"
	docker build -t $(DOCKERREPO):ote $(BUILDROOT)

.PHONY: stg
stg: prep
	@echo "----- building $(REPONAME) stg -----"
	docker build -t $(DOCKERREPO):stg $(BUILDROOT)

.PHONY: prod
prod: prep
	@echo "----- building $(REPONAME) prod -----"
	read -p "About to build production image from main branch. Are you sure? (Y/N): " response ; \
	if [[ $$response == 'N' || $$response == 'n' ]] ; then exit 1 ; fi
	if [[ `git status --porcelain | wc -l` -gt 0 ]] ; then echo "You must stash your changes before proceeding" ; exit 1 ; fi
	git fetch && git checkout $(BUILD_BRANCH)
	$(eval COMMIT:=$(shell git rev-parse --short HEAD))
	docker build -t $(DOCKERREPO):$(COMMIT) $(BUILDROOT)
	git checkout -

.PHONY: dev-deploy
dev-deploy: dev
	@echo "----- deploying $(REPONAME) dev -----"
	$(call deploy_k8s,dev,dev,dev-cset)

.PHONY: test-deploy
test-deploy: test-env
	@echo "----- deploying $(REPONAME) test -----"
	$(call deploy_k8s,test,test,test-cset)

.PHONY: ote-deploy
ote-deploy: ote
	@echo "----- deploying $(REPONAME) ote -----"
	$(call deploy_k8s,ote,ote,ote-cset)

.PHONY: stg-deploy
stg-deploy: stg
	@echo "----- deploying $(REPONAME) stg -----"
	$(call deploy_k8s,stg,stg,prod-cset)

.PHONY: prod-deploy
prod-deploy: prod
	@echo "----- deploying $(REPONAME) prod -----"
	$(call deploy_k8s,prod,$(COMMIT),prod-cset)

.PHONY: clean
clean:
	@echo "----- cleaning $(REPONAME) app -----"
	rm -rf $(BUILDROOT)
