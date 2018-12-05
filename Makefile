PROJECT=ddr
APP=ddrexplorer
USER=ddr
SHELL = /bin/bash

APP_VERSION := $(shell cat VERSION)
GIT_SOURCE_URL=https://github.com/densho/ddr-explorer

PYTHON_VERSION=python3.5

# Release name e.g. jessie
DEBIAN_CODENAME := $(shell lsb_release -sc)
# Release numbers e.g. 8.10
DEBIAN_RELEASE := $(shell lsb_release -sr)
# Sortable major version tag e.g. deb8
DEBIAN_RELEASE_TAG = deb$(shell lsb_release -sr | cut -c1)

# current branch name minus dashes or underscores
PACKAGE_BRANCH := $(shell git rev-parse --abbrev-ref HEAD | tr -d _ | tr -d -)
# current commit hash
PACKAGE_COMMIT := $(shell git log -1 --pretty="%h")
# current commit date minus dashes
PACKAGE_TIMESTAMP := $(shell git log -1 --pretty="%ad" --date=short | tr -d -)

INSTALL_BASE=/opt
INSTALL_PUBLIC=$(INSTALL_BASE)/ddr-explorer
REQUIREMENTS=./requirements.txt
PIP_CACHE_DIR=$(INSTALL_BASE)/pip-cache

VIRTUALENV=./venv/ddrexplorer
SETTINGS=./ddrexplorer/ddrexplorer/settings.py

CONF_BASE=/etc/ddr
CONF_PRODUCTION=$(CONF_BASE)/ddrexplorer.cfg
CONF_LOCAL=$(CONF_BASE)/ddrexplorer-local.cfg

LOG_BASE=/var/log/ddr

SUPERVISOR_GUNICORN_CONF=/etc/supervisor/conf.d/ddrexplorer.conf
NGINX_CONF=/etc/nginx/sites-available/ddrexplorer.conf
NGINX_CONF_LINK=/etc/nginx/sites-enabled/ddrexplorer.conf

DEB_BRANCH := $(shell git rev-parse --abbrev-ref HEAD | tr -d _ | tr -d -)
DEB_ARCH=amd64
DEB_NAME_STRETCH=$(APP)-$(DEB_BRANCH)
# Application version, separator (~), Debian release tag e.g. deb8
# Release tag used because sortable and follows Debian project usage.
DEB_VERSION_STRETCH=$(APP_VERSION)~deb9
DEB_FILE_STRETCH=$(DEB_NAME_STRETCH)_$(DEB_VERSION_STRETCH)_$(DEB_ARCH).deb
DEB_VENDOR=Densho.org
DEB_MAINTAINER=<geoffrey.jost@densho.org>
DEB_DESCRIPTION=REST back-end for Brian Yamasaki app
DEB_BASE=opt/ddr-explorer


.PHONY: help


help:
	@echo "ddr-explorer Install Helper"
	@echo ""
	@echo "install - Does a complete install. Idempotent, so run as many times as you like."
	@echo "          IMPORTANT: Run 'adduser ddr' first to install ddr user and group."
	@echo "          Installation instructions: make howto-install"
	@echo "Subcommands:"
	@echo "    install-prep    - Various preperatory tasks"
	@echo "    install-daemons - Installs Nginx, Redis"
	@echo "    get-app         - Runs git-clone or git-pull on ddr-explorer"
	@echo "    install-app     - Just installer tasks for ddr-explorer"
	@echo ""
	@echo ""
	@echo "migrate - Initialize or update Django app's database tables."
	@echo ""
	@echo "branch BRANCH=[branch] - Switches ddr-explorer and supporting repos to [branch]."
	@echo ""
	@echo "reload  - Reloads supervisord and nginx configs"
	@echo "reload-nginx"
	@echo "reload-supervisors"
	@echo ""
	@echo "restart - Restarts all servers"
	@echo "restart-redis"
	@echo "restart-nginx"
	@echo "restart-supervisord"
	@echo ""
	@echo "status  - Server status"
	@echo ""
	@echo "uninstall - Deletes 'compiled' Python files. Leaves build dirs and configs."
	@echo "clean   - Deletes files created by building the program. Leaves configs."
	@echo ""
	@echo "More install info: make howto-install"

help-all:
	@echo "install - Do a fresh install"
	@echo "install-prep    - git-config, add-user, apt-update, install-misc-tools"
	@echo "install-daemons - install-nginx install-redis install-elasticsearch"
	@echo "install-ddr     - install-ddr-explorer"
	@echo "install-static  - "
	@echo "update  - Do an update"
	@echo "restart - Restart servers"
	@echo "status  - Server status"
	@echo "install-configs - "
	@echo "update-ddr - "
	@echo "uninstall - "
	@echo "clean - "


get: get-ddr-explorer

install: install-prep get-app install-app install-daemons install-static install-configs

uninstall: uninstall-app uninstall-configs

clean: clean-app


install-prep: apt-update install-core git-config install-misc-tools

apt-update:
	@echo ""
	@echo "Package update ---------------------------------------------------------"
	apt-get --assume-yes update

apt-upgrade:
	@echo ""
	@echo "Package upgrade --------------------------------------------------------"
	apt-get --assume-yes upgrade

install-core:
	apt-get --assume-yes install bzip2 curl gdebi-core git-core logrotate ntp python3

git-config:
	git config --global alias.st status
	git config --global alias.co checkout
	git config --global alias.br branch
	git config --global alias.ci commit

install-misc-tools:
	@echo ""
	@echo "Installing miscellaneous tools -----------------------------------------"
	apt-get --assume-yes install ack-grep byobu elinks htop mg multitail


install-daemons: install-nginx install-redis

install-nginx:
	@echo ""
	@echo "Nginx ------------------------------------------------------------------"
	apt-get --assume-yes install nginx

install-redis:
	@echo ""
	@echo "Redis ------------------------------------------------------------------"
	apt-get --assume-yes install redis-server


install-virtualenv:
	@echo ""
	@echo "install-virtualenv -----------------------------------------------------"
	apt-get --assume-yes install python-pip python-virtualenv
	test -d $(VIRTUALENV) || virtualenv --python=python3 $(VIRTUALENV)


get-app: get-ddr-explorer

install-app: install-virtualenv install-ddr-explorer install-configs install-daemon-configs

uninstall-app: uninstall-ddr-explorer uninstall-configs uninstall-daemon-configs

clean-app: clean-ddr-explorer


get-ddr-explorer:
	@echo ""
	@echo "get-ddr-explorer ---------------------------------------------------------"
	git pull

install-ddr-explorer: clean-ddr-explorer
	@echo ""
	@echo "install-ddr-explorer -----------------------------------------------------"
	apt-get --assume-yes install imagemagick sqlite3 supervisor
	source $(VIRTUALENV)/bin/activate; \
	pip3 install -U -r $(INSTALL_PUBLIC)/requirements.txt
# logs dir
	-mkdir $(LOG_BASE)
	chown -R ddr.root $(LOG_BASE)
	chmod -R 755 $(LOG_BASE)
# sqlite db dir
	-mkdir $(SQLITE_BASE)
	-chown -R ddr.root $(SQLITE_BASE)
	-chmod -R 755 $(SQLITE_BASE)

uninstall-ddr-explorer:
	@echo ""
	@echo "uninstall-ddr-explorer ---------------------------------------------------"
	source $(VIRTUALENV)/bin/activate; \
	cd $(INSTALL_PUBLIC)/ddrexplorer && pip3 uninstall -y -r $(INSTALL_PUBLIC)/requirements.txt

clean-ddr-explorer:
	-rm -Rf $(INSTALL_PUBLIC)/ddrexplorer/src


migrate:
	source $(VIRTUALENV)/bin/activate; \
	cd $(INSTALL_PUBLIC)/ddrexplorer && python manage.py migrate --noinput
	-chown -R ddr.root $(SQLITE_BASE)
	-chmod -R 750 $(SQLITE_BASE)
	chown -R ddr.root $(LOG_BASE)
	chmod -R 755 $(LOG_BASE)


install-configs:
	@echo ""
	@echo "configuring ddr-explorer -------------------------------------------------"
# base settings file
# /etc/ddr/ddrexplorer.cfg must be readable by all
# /etc/ddr/ddrexplorer-local.cfg must be readable by ddr but contains sensitive info
	-mkdir /etc/ddr
	cp $(INSTALL_PUBLIC)/conf/ddrexplorer.cfg $(CONF_PRODUCTION)
	chown root.root $(CONF_PRODUCTION)
	chmod 644 $(CONF_PRODUCTION)
	touch $(CONF_LOCAL)
	chown ddr.root $(CONF_LOCAL)
	chmod 640 $(CONF_LOCAL)
# web app settings
	cp $(INSTALL_PUBLIC)/conf/settings.py $(SETTINGS)
	chown root.root $(SETTINGS)
	chmod 644 $(SETTINGS)

uninstall-configs:
	-rm $(SETTINGS)
	-rm $(CONF_PRODUCTION)
	-rm $(CONF_SECRET)


install-daemon-configs:
	@echo ""
	@echo "install-daemon-configs -------------------------------------------------"
# nginx settings
	cp $(INSTALL_PUBLIC)/conf/nginx.conf $(NGINX_CONF)
	chown root.root $(NGINX_CONF)
	chmod 644 $(NGINX_CONF)
	-ln -s $(NGINX_CONF) $(NGINX_CONF_LINK)
	-rm /etc/nginx/sites-enabled/default
# supervisord
	cp $(INSTALL_PUBLIC)/conf/supervisor.conf $(SUPERVISOR_GUNICORN_CONF)
	chown root.root $(SUPERVISOR_GUNICORN_CONF)
	chmod 644 $(SUPERVISOR_GUNICORN_CONF)

uninstall-daemon-configs:
	-rm $(NGINX_CONF)
	-rm $(NGINX_CONF_LINK)


reload: reload-nginx reload-supervisor

reload-nginx:
	/etc/init.d/nginx reload

reload-supervisor:
	supervisorctl reload

reload-app: reload-supervisor


stop: stop-redis stop-nginx stop-supervisor

stop-redis:
	/etc/init.d/redis-server stop

stop-nginx:
	/etc/init.d/nginx stop

stop-supervisor:
	/etc/init.d/supervisor stop

stop-app:
	supervisorctl stop ddrexplorer


restart: restart-redis restart-nginx restart-supervisor

restart-redis:
	/etc/init.d/redis-server restart

restart-nginx:
	/etc/init.d/nginx restart

restart-supervisor:
	/etc/init.d/supervisor restart

restart-app:
	supervisorctl restart ddrexplorer


# just Redis and Supervisor
restart-minimal: restart-redis stop-nginx restart-supervisor


status:
	@echo "------------------------------------------------------------------------"
	-/etc/init.d/redis-server status
	@echo " - - - - -"
	-/etc/init.d/nginx status
	@echo " - - - - -"
	-supervisorctl status
	@echo ""

git-status:
	@echo "------------------------------------------------------------------------"
	cd $(INSTALL_PUBLIC) && git status


# http://fpm.readthedocs.io/en/latest/
install-fpm:
	@echo "install-fpm ------------------------------------------------------------"
	apt-get install ruby ruby-dev rubygems build-essential
	gem install --no-ri --no-rdoc fpm

# https://stackoverflow.com/questions/32094205/set-a-custom-install-directory-when-making-a-deb-package-with-fpm
# https://brejoc.com/tag/fpm/
deb: deb-stretch

deb-stretch:
	@echo ""
	@echo "DEB packaging (stretch) ------------------------------------------------"
	-rm -Rf $(DEB_FILE_STRETCH)
	virtualenv --python=python3 --relocatable $(VIRTUALENV)  # Make venv relocatable
	fpm   \
	--verbose   \
	--input-type dir   \
	--output-type deb   \
	--name $(DEB_NAME_STRETCH)   \
	--version $(DEB_VERSION_STRETCH)   \
	--package $(DEB_FILE_STRETCH)   \
	--url "$(GIT_SOURCE_URL)"   \
	--vendor "$(DEB_VENDOR)"   \
	--maintainer "$(DEB_MAINTAINER)"   \
	--description "$(DEB_DESCRIPTION)"   \
	--depends "nginx"   \
	--depends "python3"   \
	--depends "redis-server"   \
	--depends "sqlite3"  \
	--depends "supervisor"   \
	--after-install "bin/fpm-mkdir-log.sh"   \
	--chdir $(INSTALL_PUBLIC)   \
	conf/ddrexplorer.cfg=etc/ddr/ddrexplorer.cfg   \
	bin=$(DEB_BASE)   \
	conf=$(DEB_BASE)   \
	COPYRIGHT=$(DEB_BASE)   \
	ddrexplorer=$(DEB_BASE)   \
	.git=$(DEB_BASE)   \
	.gitignore=$(DEB_BASE)   \
	INSTALL=$(DEB_BASE)   \
	LICENSE=$(DEB_BASE)   \
	Makefile=$(DEB_BASE)   \
	README.rst=$(DEB_BASE)   \
	requirements.txt=$(DEB_BASE)   \
	venv=$(DEB_BASE)   \
	venv/ddrexplorer/lib/$(PYTHON_VERSION)/site-packages/rest_framework/static/rest_framework=$(STATIC_ROOT)  \
	VERSION=$(DEB_BASE)
