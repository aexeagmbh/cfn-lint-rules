FROM python:3.8-slim-bullseye

WORKDIR /tmp
COPY requirements requirements
RUN python -m pip install -r ./requirements/dev.txt
RUN rm -rf ./requirements

RUN useradd uid1000 --home-dir /home/uid1000 --uid 1000
RUN mkdir -p /home/uid1000 && chown uid1000: /home/uid1000
USER uid1000

WORKDIR /usr/src/app
COPY ./ .
