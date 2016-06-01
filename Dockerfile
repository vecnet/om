FROM python:2.7
# Dockerize for waiting on postgres being ready.
#  https://github.com/jwilder/dockerize
RUN wget https://github.com/jwilder/dockerize/releases/download/v0.2.0/dockerize-linux-amd64-v0.2.0.tar.gz
RUN tar -C /usr/local/bin -xzvf dockerize-linux-amd64-v0.2.0.tar.gz
RUN rm dockerize-linux-amd64-v0.2.0.tar.gz
# Setup Django.
RUN mkdir /app
ENV PYTHONUNBUFFERED 1
COPY . /app/
RUN pip install -r /app/requirements/local.txt
ENV SECRET_KEY=docker
ENV DJANGO_SETTINGS_MODULE=website.settings.docker
# OpenMalaria-specific
RUN apt-get --yes update && apt-get --yes upgrade
RUN apt-get install -y g++ git cmake libgsl0-dev libboost-all-dev libxerces-c-dev xsdcxx
RUN git clone https://github.com/SwissTPH/openmalaria
RUN cd openmalaria \
  && git checkout schema-32 \
  && git pull
RUN cd openmalaria && mkdir build \
  && cd build \
  && cmake -DCMAKE_CXX_COMPILER=/usr/bin/g++ -DCMAKE_BUILD_TYPE=Release .. \
  && make -j4
RUN cp openmalaria/build/openMalaria /app/binaries/om/
WORKDIR /app
