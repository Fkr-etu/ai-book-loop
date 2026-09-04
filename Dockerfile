# ==============================================================================
# Dockerfile Production Multi-stage pour GCP Cloud Run (FastAPI Backend)
# ==============================================================================

FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Installer uv pour la gestion rapide des dépendances
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv pip install --system .

# ------------------------------------------------------------------------------
# Image de runtime finale ultra-légère et sécurisée (non-root)
# ------------------------------------------------------------------------------
FROM python:3.12-slim AS runner

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Création d'un utilisateur non-privilégié (Sécurité DevOps)
RUN adduser --disabled-password --gecos "" appuser

# Copier les packages installés depuis l'étape builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copier le code source
COPY book_loop/ ./book_loop/

# Changer le propriétaire des fichiers vers l'utilisateur non-root
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

# Lancement d'Uvicorn optimisé pour production
CMD ["sh", "-c", "uvicorn book_loop.api.app:app --host 0.0.0.0 --port ${PORT} --workers 1 --proxy-headers --forwarded-allow-ips='*'"]
