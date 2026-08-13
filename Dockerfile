# Single Dockerfile to serve Flask API and static index.html
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (minimal)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY app/backend/requirements.txt ./
RUN pip install -r requirements.txt

# App code (API + static frontend) — flattened into /app so Flask
# (static_folder='.') serves the frontend from the working directory.
COPY app/backend/maze_simulator_backend.py ./
COPY app/frontend/index.html ./
COPY app/frontend/styles.css ./

# Expose default port (Render puede usar otro; se respeta $PORT)
EXPOSE 5000
ENV PORT=5000

# Use gunicorn and bind to $PORT (Render define PORT)
CMD ["sh", "-c", "gunicorn -w 2 -k gthread -b 0.0.0.0:${PORT:-5000} maze_simulator_backend:app"]
