
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS backend-build
WORKDIR /app/backend
RUN pip install --no-cache-dir uv
COPY backend/pyproject.toml backend/uv.lock* ./
RUN uv sync --frozen --no-install-project --no-dev
COPY backend/ ./
COPY .env /app/backend/.env
RUN uv sync --no-dev

FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    gettext-base \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/log/supervisor /var/log/nginx

COPY --from=frontend-build /app/frontend/dist /usr/share/nginx/html

WORKDIR /app/backend
COPY --from=backend-build /app/backend/.venv /app/backend/.venv
COPY --from=backend-build /app/backend /app/backend
ENV PATH="/app/backend/.venv/bin:$PATH"

COPY nginx/nginx.conf /etc/nginx/nginx.conf.template
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENV PORT=10000
EXPOSE 10000

CMD ["/bin/sh", "-c", "envsubst '$PORT' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf"]
