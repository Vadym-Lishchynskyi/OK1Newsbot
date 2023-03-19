# App
FROM python:3.10 as BotBack

WORKDIR /app/

ENV POETRY_VERSION=1.4.0
RUN pip3 install poetry==$POETRY_VERSION
RUN poetry config virtualenvs.create false

ADD ./poetry.lock .
ADD ./pyproject.toml .

RUN poetry install

ADD . .

RUN chmod +x ./entrypoint.sh

EXPOSE 8000

CMD ["/app/entrypoint.sh"]