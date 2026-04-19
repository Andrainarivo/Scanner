# Scanner

A high-performance REST API for performing Nmap scans asynchronously using **python3-nmap**, **Flask**, **Celery**/**Redis**.

## Key Features

* **Asynchronous Architecture**: Long-running scans do not block the API.
* **Enhanced Security**: Runs as a non-root user while retaining necessary network privileges via **Linux Capabilities**.
* **Multi-Technique Support**: Supports SYN Scan, TCP Connect, UDP, and FIN scans.
* **Host Discovery**: Dedicated modules for ARP and Ping discovery.
* **Dockerized**: Ready-to-deploy stack with Docker Compose.

---

## Getting Started

### Prerequisites

* Docker CE

### Installation & Run

```bash
# Clone the repository
git clone https://github.com/Andrainarivo/Scanner.git
cd Scanner

# Build and start the stack
docker compose up -d --build
```

The API will be available at: `http://0.0.0.0:5000`

---

## 📖 API Documentation

### 1. Host Discovery

`POST /discover`

```json
{
    "targets": "192.168.1.0/24",
    "method": "arp",
    "args": "--min-rate 1000"
}
```

### 2. Port Scanning

`POST /scan`

```json
{
    "targets": "scanme.nmap.org",
    "ports": "80,443,22",
    "techniques": ["syn", "tcp"],
    "args": "-A"
}
```

### 3. Check Status/Result

`GET /status/<job_id>`

### 4. Health Check

`GET /health`

---

## Tech Stack

* **Language**: Python 3.12
* **Framework**: Flask
* **Job Queue**: Celery + Redis
* **Scanner**: Nmap
* **Container**: Docker
