# Railway.com Dockerfile for Django deployment
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=eshop.settings.production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --clear

# Expose port
EXPOSE $PORT

# Start command
CMD python manage.py migrate && \
    gunicorn --bind 0.0.0.0:$PORT --timeout 60 --workers 2 eshop.wsgi:application