# Start with a specific version of Python that is 3.10.2 or higher
FROM python:3.11-slim

#argument for build time
ARG INTERNAL_URL
ARG DATABASE_URL
ARG API_KEY
ARG PHONE
ARG API_BRIDGE

#Argument for runtime and build time
ENV INTERNAL_URL=${INTERNAL_URL}
ENV DATABASE_URL=${DATABASE_URL}
ENV API_KEY=${API_KEY}
ENV PHONE=${PHONE}
ENV API_BRIDGE=${API_BRIDGE}

# Set environment variables to prevent the creation of .pyc files and buffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install necessary build dependencies for production (only minimal required tools are installed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a directory for the application code
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Check if .env file exists and copy it
#RUN cat .env && test -f /app/.env || (echo ".env file not found!" && exit 1)

# Copy the rest of the application code
COPY . /app/

RUN rm -rf /app/venv && \
    python -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt && \
    prisma generate
# Install Python dependencies

# Expose the application's port (adjust according to your app)
EXPOSE 8000

# Optionally, set the entry point script to run at container startup (if applicable)
# Ensure you use 'exec' form to allow proper signal handling
RUN pip install --ignore-installed uvicorn==0.20.0

CMD . venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000
