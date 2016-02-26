FROM python:2.7
RUN apt-get --yes update && apt-get --yes upgrade
RUN apt-get install -y g++ git cmake libgsl0-dev libboost-all-dev libxerces-c-dev xsdcxx
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements/ /app/requirements/
RUN pip install -r requirements/dev.txt
COPY . /app/
RUN git clone https://github.com/SwissTPH/openmalaria
RUN cd openmalaria \
  && git checkout schema-32 \
  && git pull
# Run build steps
RUN cd openmalaria && mkdir build \
  && cd build \
  && cmake -DCMAKE_CXX_COMPILER=/usr/bin/g++ -DCMAKE_BUILD_TYPE=Release .. \
  && make -j4
RUN cp openmalaria/build/openMalaria /app/binaries/om/
ENV DJANGO_SETTINGS_MODULE=website.settings.docker
