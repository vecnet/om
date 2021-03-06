FROM python:2.7
# OpenMalaria-specific
RUN apt-get update && apt-get install -y \
	g++ \
	git \
	cmake \
	libgsl0-dev \
	libboost-all-dev \
	libxerces-c-dev \
	xsdcxx \
&& rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/SwissTPH/openmalaria
RUN cd openmalaria \
  && git checkout schema-32 \
  && git pull
RUN cd openmalaria && mkdir build \
  && cd build \
  && cmake -DCMAKE_CXX_COMPILER=/usr/bin/g++ -DCMAKE_BUILD_TYPE=Release .. \
  && make
# Dockerize for waiting on postgres being ready.
#  https://github.com/jwilder/dockerize
RUN wget https://github.com/jwilder/dockerize/releases/download/v0.2.0/dockerize-linux-amd64-v0.2.0.tar.gz
RUN tar -C /usr/local/bin -xzvf dockerize-linux-amd64-v0.2.0.tar.gz
RUN rm dockerize-linux-amd64-v0.2.0.tar.gz
# Setup Django.
RUN mkdir /app
ENV PYTHONUNBUFFERED 1
ADD . /app/
RUN pip install -r /app/requirements/local.txt
ENV SECRET_KEY=docker
ENV DJANGO_SETTINGS_MODULE=website.settings.docker
RUN cp openmalaria/build/openMalaria /app/binaries/om/
WORKDIR /app
