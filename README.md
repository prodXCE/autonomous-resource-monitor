## **Autonomous Resource Optimizer (ARO)**

An **autonomous, self-aware infrastructure management platform** designed to monitor system metrics, detect anomalies using statistical analysis, and provide **real-time operational insights** via a professional monitoring stack.

This project demonstrates a **complete microservice ecosystem** built using **modern DevOps and ML practices**, from **data ingestion and analysis** to **visualization and automated lifecycle management**.

---

###  **Core Features**

####  Microservice Architecture

A decoupled system consisting of:

* **Backend Service** (Spring Boot): Handles API logic and data storage.
* **ML Worker Service** (Python): Performs anomaly detection.
* **Monitoring Stack** (Prometheus + Grafana): Provides observability and analytics.

####  Real-Time Metric Ingestion

Spring Boot backend exposes REST APIs for collecting **any time-series metric data**, stored in a **PostgreSQL database**.

#### �Autonomous Anomaly Detection

A continuously running **Python ML worker** fetches recent metrics and applies the **Modified Z-Score** algorithm — a robust statistical method that identifies outliers without assuming a Gaussian distribution.

####  Observability Stack

Integrates **Prometheus** for metrics scraping and **Grafana** for interactive dashboards that visualize:

* System health
* Metric trends
* Detected anomalies

####  Containerized & Automated Deployment

All components — Backend, ML Worker, Database, Prometheus, Grafana — are containerized using **Podman**.
A single **automation script (`run_project.sh`)** manages:

* Environment cleanup
* Image rebuild
* Sequential startup

This ensures **reproducibility, consistency, and zero manual setup**.

---

###  **Technology Stack**

| Layer          | Technology/Tool                                         | Purpose                                             |
| :------------- | :------------------------------------------------------ | :-------------------------------------------------- |
| **Backend**    | Java 17+, Spring Boot, Spring Data JPA, Spring Actuator | API, persistence, and metric exposure               |
| **ML/AI**      | Python, Pandas                                          | Data manipulation and statistical anomaly detection |
| **Database**   | PostgreSQL                                              | Storage for time-series metrics                     |
| **DevOps**     | Podman, Dockerfile, Bash, SELinux                       | Containerization and lifecycle automation           |
| **Monitoring** | Prometheus, Grafana                                     | Metrics collection and dashboard visualization      |
| **OS**         | Rocky Linux                                             | Base runtime environment                            |

---

###  **Getting Started**

#### **Prerequisites**

* Linux VM (tested on Rocky Linux 9)
* `git`, `podman` (or `docker`)
* Internet access for container image pulls

#### **Installation**

```bash
git clone https://github.com/prodXCE/autonomous-resource-optimizer
cd autonomous-resource-optimizer
chmod +x runAro.sh
```

#### **Start the Stack**

```bash
./runAro.sh
```

This script automatically:

* Stops existing containers
* Rebuilds images
* Launches services in order

---

###  **Verification**

#### Check Running Containers

```bash
sudo podman ps
```

You should see:

* `aro-backend-app`
* `postgres-db`
* `aro-ml-worker`
* `prometheus`
* `grafana`

All with **status: Up** ✅

#### Access Dashboards

| Service        | URL                        | Default Credentials |
| -------------- | -------------------------- | ------------------- |
| **Grafana**    | `http://<your-vm-ip>:3000` | `admin / admin`     |
| **Prometheus** | `http://<your-vm-ip>:9090` | —                   |

---

###  **Test the Full System Loop**

#### 1. Start Services

```bash
./runAro.sh
```

#### 2. Post Metric Data

```bash
# Normal Data
curl -X POST -H "Content-Type: application/json" \
  -d '{"source": "vm-prod-01", "metricType": "CPU_USAGE", "value": 0.85}' \
  http://<your-vm-ip>:8080/api/metrics

# Anomaly Data
curl -X POST -H "Content-Type: application/json" \
  -d '{"source": "vm-prod-01", "metricType": "CPU_USAGE", "value": 25.0}' \
  http://<your-vm-ip>:8080/api/metrics
```

#### 3. Observe Anomaly Detection

Monitor the ML worker logs:

```bash
sudo podman run --name aro-ml-worker-run --replace --network private-net aro-ml-worker:latest
sudo podman logs -f aro-ml-worker
```

Within 60 seconds, you should see log entries highlighting the **anomaly detection event**.


