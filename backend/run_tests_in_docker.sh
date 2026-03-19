#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
IMAGE_NAME="todos-backend-test:latest"

echo "Building Docker image ${IMAGE_NAME} (this may take a few minutes)..."
docker build -t ${IMAGE_NAME} -f "${ROOT_DIR}/Dockerfile.test" "${ROOT_DIR}"

echo "Running tests inside container..."
docker run --rm ${IMAGE_NAME}

echo "Container tests finished." 
