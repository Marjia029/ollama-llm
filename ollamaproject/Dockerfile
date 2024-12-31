# Use official Python image as a base
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (for PostgreSQL, etc.)
RUN apt-get update && apt-get install -y \
    iputils-ping \
    dnsutils \
    net-tools \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files into the container
COPY . /app/

# Set environment variables (if needed)
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=ollamaproject.settings

# Expose the port the app will run on
EXPOSE 8000

# Run the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
