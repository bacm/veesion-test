FROM python:3.12-slim

# Installe uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Prépare le répertoire de travail
WORKDIR /app

# Copie d’abord uniquement les fichiers de config
COPY pyproject.toml uv.lock ./

# Installe les dépendances dans le venv géré par `uv`
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv && uv pip install --no-deps .

# Installe les lib système nécessaires à opencv
RUN apt-get update && apt-get install -y --no-install-recommends \
#       curl \
    ffmpeg \
#       libglib2.0-0 \
#       libsm6 \
#       libxrender1 \
#       libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Puis copie le reste du code (après les deps)
COPY app/ ./app/

CMD ["uv", "run", "python", "-u", "app/worker.py"]

