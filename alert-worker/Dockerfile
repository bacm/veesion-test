FROM python:3.12-slim

# Installe uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Prépare le répertoire de travail
WORKDIR /app

ENV PYTHONPATH=/app

# Copie d’abord uniquement les fichiers de config
COPY pyproject.toml uv.lock ./

# Installe les dépendances dans le venv géré par `uv`
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv && uv pip install --no-deps .

# Installe les lib système nécessaires à opencv
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Puis copie le reste du code (après les deps)
COPY app/ ./app/

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]

