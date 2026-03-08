# Dockerfile for ACEest Fitness & Gym API
# Uses a slim Python base image to keep the image small.

FROM python:3.12-slim

# Set a working directory for the app
WORKDIR /app

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy requirements first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the Flask default port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
