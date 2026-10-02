#!/usr/bin/env sh
set -eu

IMAGE_NAME="ai-guru-54-dockerize-ai-fastapi:latest"
CONTAINER_NAME="ai-guru-54-app"

docker build --tag "$IMAGE_NAME" .
docker rm --force "$CONTAINER_NAME" >/dev/null 2>&1 || true
docker run --detach \
  --name "$CONTAINER_NAME" \
  --publish 8000:8000 \
  "$IMAGE_NAME"

printf '%s\n' "Ứng dụng đang khởi động tại http://localhost:8000"
printf '%s\n' "Xem log bằng: docker logs --follow $CONTAINER_NAME"
printf '%s\n' "Dừng bằng: docker stop $CONTAINER_NAME"