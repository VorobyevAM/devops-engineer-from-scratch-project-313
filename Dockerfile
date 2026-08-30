FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy
ENV PORT=8080

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md main.py ./
COPY src ./src
RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8080

CMD ["sh", "-c", ".venv/bin/gunicorn --bind 0.0.0.0:${PORT} main:app"]
