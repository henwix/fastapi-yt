FROM python:3.14-alpine AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_VERSION="0.12.13" \
    LIBMAGIC_VERSION="5.47-r2" \
    APP_PATH="/src" \
    USER="fastapi-yt-user"

ENV VIRTUAL_ENV="$APP_PATH/.venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR $APP_PATH


FROM base AS builder

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir "uv==$UV_VERSION" && \
    uv sync --frozen --no-dev --no-install-project


FROM base AS runner

RUN apk add --no-cache "libmagic==$LIBMAGIC_VERSION" && \
    adduser --disabled-password $USER

COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV
COPY --chown=$USER:$USER . .

USER $USER

EXPOSE 8000
