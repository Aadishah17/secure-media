FROM node:22-bookworm-slim AS frontend-build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY index.html vite.config.js ./
COPY src ./src
RUN npm run build


FROM python:3.10-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
COPY backend/requirements-google.txt backend/requirements-google.txt
COPY backend/requirements-web3.txt backend/requirements-web3.txt
RUN python -m pip install --no-cache-dir \
    -r backend/requirements.txt \
    -r backend/requirements-google.txt

COPY backend ./backend
COPY contracts ./contracts
COPY --from=frontend-build /app/dist ./dist

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "backend.run:app"]
