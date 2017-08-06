#!/bin/bash

if [[ $TRAVIS_OS_NAME == "osx" ]]; then
	python manage.py migrate
	python manage.py test -v 2
else
  if [[ $USE_DOCKER == "yes" ]]; then
	  docker-compose up -d
	  docker-compose run web /bin/sh -c "exec python manage.py migrate"
	  docker-compose run web /bin/sh -c "exec python manage.py test -v 2"
	  docker-compose down
  else
	  ./binaries/om/openMalaria -v
#	  python manage.py migrate
	  coverage run --source='.' manage.py test -v 2
  fi
fi
