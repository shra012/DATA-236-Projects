#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="mysql"
MYSQL_DATABASE="data236-mysql"
HOST_PORT="3306"
IMAGE="mysql:8"

# Start a MySQL 8 container for local development.
docker run \
  --name "${CONTAINER_NAME}" \
  -e "MYSQL_ALLOW_EMPTY_PASSWORD=yes" \
  -e "MYSQL_DATABASE=${MYSQL_DATABASE}" \
  -p "${HOST_PORT}:3306" \
  -d "${IMAGE}"
