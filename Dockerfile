FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY app ./app

# Expose the port uvicorn will listen on
EXPOSE 8123

# Run uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8123", "--workers", "4", "--log-level", "info", "--access-log"]