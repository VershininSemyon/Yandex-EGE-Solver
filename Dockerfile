
# ==========================================
# Stage 1: Сборка Frontend (React + Vite)
# ==========================================
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ==========================================
# Stage 2: Сборка Backend (Python + Uv)
# ==========================================
FROM python:3.12-slim AS backend-build
WORKDIR /app/backend
RUN pip install --no-cache-dir uv
COPY backend/pyproject.toml backend/uv.lock* ./
RUN uv sync --frozen --no-install-project --no-dev
COPY backend/ ./
RUN uv sync --no-dev

# ==========================================
# Stage 3: Финальный образ (Nginx + Uvicorn)
# ==========================================
FROM python:3.12-slim

# Устанавливаем Nginx, Supervisor и gettext-base (для envsubst)
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    gettext-base \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/log/supervisor /var/log/nginx

# Копируем собранный фронтенд
COPY --from=frontend-build /app/frontend/dist /usr/share/nginx/html

# Копируем бэкенд и виртуальное окружение
WORKDIR /app/backend
COPY --from=backend-build /app/backend/.venv /app/backend/.venv
COPY --from=backend-build /app/backend /app/backend
ENV PATH="/app/backend/.venv/bin:$PATH"

# Копируем конфигурации
COPY nginx/nginx.conf /etc/nginx/nginx.conf.template
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Render передает порт через переменную PORT. По умолчанию 10000.
ENV PORT=10000
EXPOSE 10000

# Подставляем $PORT в конфиг Nginx и запускаем Supervisor
CMD ["/bin/sh", "-c", "envsubst '$PORT' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf"]
