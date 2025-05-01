# ---------- build stage ----------
    FROM python:3.13-alpine AS builder

    # C compiler & headers for wheels that need compilation
    RUN apk add --no-cache \
        build-base \
        musl-dev

    WORKDIR /app
    COPY requirements.txt .

    # Install Python deps into the builder’s /root/.local
    RUN pip install --user --no-cache-dir -r requirements.txt


    # ---------- runtime stage ----------
    FROM python:3.13-alpine

    # Runtime environment
    ENV PYTHONUNBUFFERED=1 \
        TZ=Europe/Berlin \
        PATH=/home/app/.local/bin:$PATH

    # Create non-root user (Alpine’s adduser)
    RUN adduser -D -h /home/app app
    WORKDIR /home/app

    # Copy installed Python packages from builder
    COPY --from=builder /root/.local /home/app/.local

    # Copy project code
    COPY . .

    USER app

    # Default entrypoint (your loop wrapper)
    CMD ["python", "main_loop.py"]
    