FROM tiangolo/uwsgi-nginx-flask:python2.7

COPY ./app /app
COPY systems.json /app/
COPY *.csv /app/

COPY requirements.txt /tmp/
RUN pip install -U pip
RUN pip install -r /tmp/requirements.txt

WORKDIR /app
