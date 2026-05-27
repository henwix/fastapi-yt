# Stage 1

FROM python:3.14-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /src

COPY pyproject.toml poetry.lock /src/
RUN pip install --upgrade pip && \
  pip install poetry && \
  poetry config virtualenvs.create false && \
  poetry install --no-root --no-interaction --no-ansi

# Stage 2

FROM python:3.14-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /src

RUN adduser --disabled-password fastapi-yt-user

COPY --from=builder --chown=fastapi-yt-user:fastapi-yt-user /usr/local/lib/python3.14/site-packages/ /usr/local/lib/python3.14/site-packages/
COPY --from=builder --chown=fastapi-yt-user:fastapi-yt-user /usr/local/bin/ /usr/local/bin/
COPY --chown=fastapi-yt-user:fastapi-yt-user . /src/

USER fastapi-yt-user

EXPOSE 8000
