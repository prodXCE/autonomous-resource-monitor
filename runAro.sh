#!/bin/bash

# ==============================================================================
# Autonomous Resource Optimizer | Project Control Script
#
# Description:
# This script manages the full lifecycle of the ARO application stack.
# It stops and cleans up old containers, rebuilds the necessary images from
# the latest source code, and starts all services in the correct order.
#
# Usage:
# 1. Place this script in the root of your 'autonomous-resource-optimizer' project.
# 2. Make it executable: chmod +x run_project.sh
# 3. Run it from the root directory: ./run_project.sh
# ==============================================================================

# --- Configurataion ---
# Set the script to exit immediately if any command fails
set -e

# --- Step 1: Stop and Clean Up All Existing Containers ---
echo "--- Stopping and removing old containers... ---"
# We use '|| true' to prevent the script from failing if a container doesn't exist.
sudo podman stop aro-backend-app postgres-db prometheus grafana || true
sudo podman rm aro-backend-app postgres-db prometheus || true
echo "Cleanup complete."
echo ""


# --- Step 2: Rebuild Application Images ---
echo "--- Rebuilding aro-backend image... ---"
(cd backend && sudo podman build -t aro-backend:latest .)
echo "Backend image rebuilt."
echo ""

echo "--- Rebuilding aro-ml-worker image... ---"
(cd ml-worker && sudo podman build -t aro-ml-worker:latest .)
echo "ML worker image rebuilt."
echo ""


# --- Step 3: Start Services in Correct Dependency Order ---
echo "--- Starting all project services... ---"

# 1. Start the PostgreSQL Database
echo "Starting postgres-db..."
sudo podman run -d \
  --name postgres-db \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=akash6101 \
  -e POSTGRES_DB=optimizer_db \
  -p 5432:5432 \
  --network private-net \
  postgres:16

# 2. IMPORTANT: Wait for the database to initialize before starting the backend
echo "Waiting 10 seconds for the database to initialize..."
sleep 10

# 3. Start the ARO Backend Application
echo "Starting aro-backend-app..."
sudo podman run -d \
  --name aro-backend-app \
  --network private-net \
  -p 8080:8080 \
  aro-backend:latest

# 4. Start the Prometheus Monitoring Service
echo "Starting prometheus..."
sudo podman run -d \
  --name prometheus \
  -p 9090:9090 \
  --network private-net \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml:z \
  prom/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --web.enable-admin-api

# 5. Start the Grafana Visualization Service
echo "Starting grafana..."
sudo podman run -d \
  --name grafana --replace\
  -p 3000:3000 \
  --network private-net \
  grafana/grafana

echo ""
echo "--- All services are starting up. ---"


# --- Step 4: Final Status Check ---
echo "Waiting 5 seconds for services to stabilize..."
sleep 5
echo "Current status of all running containers:"
sudo podman ps

echo ""
echo "--- Project startup complete! ---"
echo "Your services are available at:"
echo " - Grafana Dashboard: http://<your-vm-ip>:3000"
echo " - Prometheus UI:     http://<your-vm-ip>:9090"
echo " - Backend API:       http://<your-vm-ip>:8080/api/metrics"

