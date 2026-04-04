FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PostgreSQL/AlloyDB
RUN apt-get update && apt-get install -y libpq-dev gcc

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run uses Port 8080 by default
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
