#!/bin/bash

if [[ $TRAVIS_OS_NAME == "osx" ]]; then
	psql -c 'create database om;' -U postgres
else
  if [[ $USE_DOCKER == "yes" ]]; then
	echo "OK"
  else
	  psql -c 'create database om;' -U postgres
  fi
fi
