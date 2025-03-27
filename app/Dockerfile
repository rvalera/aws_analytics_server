# Use official Python runtime as a parent image
FROM python:3.12

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && apt-get install -y redis-server \
    && apt-get install -y poppler-utils \
    && apt-get clean \ 
    && rm -rf /var/lib/apt/lists/* \
    && redis-server --daemonize yes


# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
# RUN redis-server --daemonize yes
# CMD ["fastapi", "run", "main.py", "--port", "8000"]

COPY entrypoint.sh .
RUN chmod a+x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]