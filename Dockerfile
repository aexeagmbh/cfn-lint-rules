FROM python:3.7-buster

COPY requirements.txt /tmp
RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt

RUN useradd uid1000 --home-dir /home/uid1000 --uid 1000
RUN mkdir -p /home/uid1000 && chown uid1000: /home/uid1000
USER uid1000

WORKDIR /usr/src/app
COPY ./ .
