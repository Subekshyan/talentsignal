# Build from the repo root:  docker build -f backend/Dockerfile -t talentsignal-backend .
FROM python:3.12-slim
WORKDIR /app

COPY matching /matching
RUN pip install --no-cache-dir /matching

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
