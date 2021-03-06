#!/bin/bash

if [ "$TRAVIS_OS_NAME" == "linux" ]; then
	echo "OK"
	pip install coverage
	pip install coveralls
elif [ "$TRAVIS_OS_NAME" == "osx" ]; then
	pip install virtualenv
	virtualenv -p $PYTHON /tmp/venv
	source /tmp/venv/bin/activate
	pip install -U pytest
	pip install coverage
	pip install coveralls
fi

cp .travis/openMalaria binaries/om/
