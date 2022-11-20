FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update \
    && apt-get install netcat -y
RUN apt-get upgrade -y && apt-get install sqlite3 gcc python3-dev musl-dev -y
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY pyproject.toml ./poetry.lock* /app/
RUN poetry install

COPY . /app/
COPY ./wsgi-entrypoint.sh ./
RUN chmod 777 ./wsgi-entrypoint.sh
RUN chmod +x ./run-celery.sh
RUN export $(grep -v "^#" .env | xargs)

EXPOSE 8000

ENTRYPOINT ["./wsgi-entrypoint.sh", "./run-celery.sh"]