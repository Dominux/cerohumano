FROM python:3.12-slim as base

# Building stage
FROM base AS builder

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

WORKDIR /src
COPY ./requirements.txt ./
RUN pip install --prefix=/runtime --force-reinstall -r requirements.txt

# Runtime stage
FROM base AS runtime
COPY --from=builder /runtime /usr/local

WORKDIR /src
COPY ./alembic.ini ./
COPY ./services/server/main.py ./
COPY ./services/server/run.sh ./
COPY ./migrations ./migrations
COPY ./app ./app
RUN chmod +x run.sh

CMD ["sh", "./run.sh"]
