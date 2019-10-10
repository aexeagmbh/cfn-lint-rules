FROM python:3.7-buster

RUN pip install pipenv
WORKDIR /tmp
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system --dev
RUN rm Pipfile Pipfile.lock

RUN useradd uid1000 --home-dir /home/uid1000 --uid 1000
RUN mkdir -p /home/uid1000 && chown uid1000: /home/uid1000
USER uid1000

WORKDIR /usr/src/app
COPY ./ .
