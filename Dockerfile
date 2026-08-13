# --- Base image ---
FROM python:3.12-slim

# --- Set working directory inside the container ---
WORKDIR /app

# --- Install dependencies first (better layer caching) ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy application code ---
COPY . .

# --- Flask will listen on this port ---
EXPOSE 5000

# --- Run with gunicorn (production-grade WSGI server, not the Flask dev server) ---
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
