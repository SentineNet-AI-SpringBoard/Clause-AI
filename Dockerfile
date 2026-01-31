# Single-container deployment: FastAPI backend (milestone3) + Streamlit UI (milestone4)
#
# Why: platforms like Render/Fly/Azure can run one container service, while Netlify cannot host this stack.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Minimal OS deps (kept small). Add build tools only if your pip installs require compilation.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates bash \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first for better layer caching.
COPY deploy/requirements-docker.txt /app/deploy/requirements-docker.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /app/deploy/requirements-docker.txt

# Copy only the runtime code (keeps build context small).
COPY deploy /app/deploy
COPY milestone3/backend /app/milestone3/backend
COPY milestone4/UI/UI /app/milestone4/UI/UI

# Normalize line endings and ensure scripts are executable.
RUN sed -i 's/\r$//' /app/deploy/start.sh \
    && chmod +x /app/deploy/start.sh

# Default Streamlit port for many PaaS providers is provided via $PORT.
ENV PORT=8501 \
    BACKEND_URL=http://127.0.0.1:8000 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8501

CMD ["bash", "deploy/start.sh"]
