FROM node:26-slim AS frontend

WORKDIR /frontend

COPY package.json package-lock.json ./
RUN npm ci


FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy
ENV PORT=80
ENV APP_PORT=8000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx gettext-base \
    && rm -f /etc/nginx/sites-enabled/default \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md main.py ./
COPY src ./src
RUN uv sync --frozen --no-dev

COPY . .
COPY --from=frontend /frontend/node_modules/@hexlet/project-devops-deploy-crud-frontend/dist/. /app/public/
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY docker/start.sh /start.sh

RUN chmod +x /start.sh

EXPOSE 80

CMD ["/start.sh"]
