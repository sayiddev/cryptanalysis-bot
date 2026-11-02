FROM python:3.12-slim AS base

RUN groupadd --gid 10001 botgroup \
    && useradd --uid 10001 --gid botgroup --no-create-home --shell /usr/sbin/nologin botuser

WORKDIR /app

COPY pyproject.toml ./
COPY app ./app
COPY scripts ./scripts

RUN pip install --no-cache-dir . \
    && mkdir -p /app/data \
    && chown -R botuser:botgroup /app

USER botuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8080

CMD ["python", "-m", "app.bot.main"]
