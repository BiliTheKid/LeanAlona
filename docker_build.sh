#!/bin/bash

# Set default Docker image name if not provided
IMAGE_NAME=${1:-alona-bot}

# Check if .env file exists in the current directory
if [ ! -f .env ]; then
  echo ".env file not found! Please make sure the .env file exists in the current directory."
  exit 1
fi

# Load environment variables from .env
echo "Using .env file for build arguments."

# Build the Docker image
echo "Building Docker image '$IMAGE_NAME'..."

docker build \
  --build-arg INTERNAL_URL="$(grep -v '^#' .env | grep INTERNAL_URL | cut -d '=' -f2)" \
  --build-arg DATABASE_URL="$(grep -v '^#' .env | grep DATABASE_URL | cut -d '=' -f2)" \
  --build-arg API_KEY="$(grep -v '^#' .env | grep API_KEY | cut -d '=' -f2)" \
  --build-arg PHONE="$(grep -v '^#' .env | grep PHONE | cut -d '=' -f2)" \
  --build-arg API_BRIDGE="$(grep -v '^#' .env | grep API_BRIDGE | cut -d '=' -f2)" \
  -t "$IMAGE_NAME" .

# Check if the build was successful
if [ $? -eq 0 ]; then
  echo "Docker image '$IMAGE_NAME' built successfully!"
else
  echo "Failed to build Docker image."
  exit 1
fi
