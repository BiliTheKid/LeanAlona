#!/bin/bash
# Set default Docker image name if not provided
IMAGE_NAME=${1:-alona-bot}
DATABASE_URL=$(grep DATABASE_URL .env |grep -v '^#' | cut -d '=' -f2)
docker run --env-file .env --env DATABASE_URL="$(grep DATABASE_URL .env |grep -v '^#' | cut -d '=' -f2)"  -p 8000:8000 -d "$IMAGE_NAME"
#docker run --env-file .env --env DATABASE_URL="$DATABASE_URL"  -p 8000:8000 -d "$IMAGE_NAME"
#docker run --env-file .env -p 8000:8000 -d "$IMAGE_NAME"
