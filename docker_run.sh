#!/bin/bash
# Set default Docker image name if not provided
IMAGE_NAME=${1:-alona-bot}
#docker run "$(grep -v '^#' .env | grep -v '^$' | sed 's/^/--env /')" -p 8000:8000 -d "$IMAGE_NAME"
docker run --env-file .env -p 8000:8000 -d "$IMAGE_NAME"

