#!/bin/bash

if [[ $TRAVIS_OS_NAME == "osx" ]]; then
	python manage.py migrate
	python manage.py test --liveserver=localhost:8082
else
  if [[ $USE_DOCKER == "yes" ]]; then
	  docker-compose up -d
	  docker-compose run web /bin/sh -c "exec python manage.py migrate"
	  docker-compose run web /bin/sh -c "exec python manage.py test --liveserver=localhost:8082"
	  docker-compose down
  else
	  ./binaries/om/openMalaria -v
	  python manage.py migrate
	  python manage.py test --liveserver=localhost:8082
  fi
fi
