FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY Backend/ ./Backend/
COPY Frontend/ ./Frontend/

# Cloud platforms like Render, Cloud Run, and Railway pass the PORT env var
ENV PORT=5000
EXPOSE 5000

CMD ["sh", "-c", "gunicorn --chdir Backend app:app --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120"]
