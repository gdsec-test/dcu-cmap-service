REPONAME=infosec-dcu/cmap_service
BUILDROOT=$(HOME)/dockerbuild/$(REPONAME)
DOCKERREPO=artifactory.secureserver.net:10014/docker-dcu-local/cmap_service

# libraries we need to stage for pip to install inside Docker build
PRIVATE_PIPS=git@github.secureserver.net:ITSecurity/blindAl.git

.PHONY: prep prod clean

all: prep prod

prep:
	@echo "----- preparing $(REPONAME) build -----"
	# stage pips we will need to install in Docker build
	mkdir -p $(BUILDROOT)/private_pips && rm -rf $(BUILDROOT)/private_pips/*
	for entry in $(PRIVATE_PIPS) ; do \
		cd $(BUILDROOT)/private_pips && git clone $$entry ; \
	done

	# copy the app code to the build root
	cp -rp ./* $(BUILDROOT)

dev: prep
	@echo "----- building $(REPONAME) prod -----"
	DOCKERTAG=dev
	docker build --no-cache=true -t $(DOCKERREPO):prod $(BUILDROOT)

ote: prep
	@echo "----- building $(REPONAME) prod -----"
	DOCKERTAG=ote
	docker build --no-cache=true -t $(DOCKERREPO):prod $(BUILDROOT)

prod: prep
	@echo "----- building $(REPONAME) prod -----"
	DOCKERTAG=prod
	docker build --no-cache=true -t $(DOCKERREPO):prod $(BUILDROOT)

ote: prep
	@echo "----- building $(REPONAME) ote -----"
	DOCKERTAG=ote
	docker build --no-cache=true -t $(DOCKERREPO):ote $(BUILDROOT)

clean:
	@echo "----- cleaning $(REPONAME) app -----"
	rm -rf $(BUILDROOT)
