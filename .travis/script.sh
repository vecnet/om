#!/bin/bash

if [[ $TRAVIS_OS_NAME == "osx" ]]; then
	python manage.py migrate
	python manage.py test
else
  if [[ $USE_DOCKER == "yes" ]]; then
	  docker-compose up -d
	  docker-compose run web /bin/sh -c "exec python manage.py migrate"
	  docker-compose run web /bin/sh -c "exec python manage.py test"
	  docker-compose down
  else
	  python manage.py migrate
	  python manage.py test
  fi
fi
