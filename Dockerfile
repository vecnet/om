FROM python:2.7
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements/ /app/requirements/
RUN pip install -r requirements/dev.txt
COPY . /app/
