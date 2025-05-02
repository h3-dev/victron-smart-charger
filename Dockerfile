FROM node:23-alpine AS frontend
WORKDIR /ui

# nur Lock/Manifest kopieren → sauberes Layer-Caching
COPY charger-ui/package.json charger-ui/package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY charger-ui .
RUN npm run build

# ---------- python build stage ----------
FROM python:3.13-alpine AS builder
RUN apk add --no-cache build-base musl-dev
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# ---------- runtime stage ----------
FROM python:3.13-alpine
ENV PYTHONUNBUFFERED=1 TZ=Europe/Berlin
RUN adduser -D -h /home/app app
WORKDIR /home/app

# copy Python deps and source
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /home/app

# copy built frontend to /home/app/static
COPY --from=frontend /ui/dist /home/app/static

USER app
EXPOSE 8000
CMD ["python", "main_loop.py"]
