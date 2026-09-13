# Stage 1

FROM python:3.14-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /src

COPY pyproject.toml uv.lock /src/
RUN pip install --no-cache-dir --upgrade pip && \
  pip install --no-cache-dir uv && \
  uv sync --frozen --no-dev --no-install-project

# Stage 2

FROM python:3.14-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/src/.venv/bin:$PATH"

RUN apk add --no-cache libmagic

WORKDIR /src

RUN adduser --disabled-password fastapi-yt-user

COPY --from=builder /src/.venv /src/.venv
COPY --chown=fastapi-yt-user:fastapi-yt-user . /src/

USER fastapi-yt-user

EXPOSE 8000
