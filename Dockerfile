FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml LICENSE /app
COPY src/ /app/src/

RUN pip install --no-cache-dir .

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

LABEL org.opencontainers.image.source="https://github.com/TheArqsz/bashdog"
LABEL org.opencontainers.image.description="A modern, configurable, and easy-to-use documentation generator for Bash frameworks."
LABEL org.opencontainers.image.licenses="MIT"

ENTRYPOINT ["bashdog"]

CMD ["--help"]
