FROM python:3.13-alpine AS builder
RUN apk add --no-cache build-base musl-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

FROM python:3.13-alpine
ENV PYTHONUNBUFFERED=1 TZ=Europe/Berlin
RUN adduser -D -h /home/app app
WORKDIR /home/app

COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /home/app

USER app
EXPOSE 8000
CMD ["python", "main_loop.py"]