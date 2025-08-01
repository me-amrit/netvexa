#!/bin/bash

echo "🧹 Cleaning up existing containers and volumes..."
docker-compose down -v

echo "🚀 Starting fresh..."
./start-dev.sh