FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for SQLite
RUN mkdir -p /app/data

# Set default env vars
ENV PYTHONUNBUFFERED=1
ENV DB_PATH=/app/data/startups.db

CMD ["python", "main.py"]
