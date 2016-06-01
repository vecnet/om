#!/bin/bash

if [[ $TRAVIS_OS_NAME == "osx" ]]; then
	pip install --upgrade pip
	pip install -r requirements/staging.txt
else
  if [[ $USE_DOCKER == "yes" ]]; then
	  sudo rm /usr/local/bin/docker-compose
	  curl -L https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-`uname -s`-`uname -m` > docker-compose
	  chmod +x docker-compose
	  sudo mv docker-compose /usr/local/bin
	  sudo apt-get -qq update
	  sudo apt-get purge -y docker-engine
	  sudo apt-get install -y docker-engine
  else
	  pip install --upgrade pip
	  pip install -r requirements/staging.txt
  fi
fi
