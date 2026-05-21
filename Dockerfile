# Stage 1: Build Next.js static frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: FastAPI backend
FROM python:3.12-slim
WORKDIR /app/backend

RUN pip install --no-cache-dir uv

# Install dependencies first for layer caching
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-install-project

# Copy source and finalize
COPY backend/ .
RUN uv sync --frozen

# Copy legal document templates (needed at runtime by the templates router)
COPY templates/ /app/templates/

# Copy static frontend build into backend serving directory
COPY --from=frontend-builder /app/frontend/out ./static

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
