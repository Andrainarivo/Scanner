# Scanner 🚀

A high-performance, secure REST API for performing Nmap scans asynchronously using **Flask**, **Celery**, and **Redis**.

## 🌟 Key Features

* **Asynchronous Architecture**: Long-running scans do not block the API, thanks to Celery workers.
* **Enhanced Security**: Runs as a non-root user (`scanner`) while retaining necessary network privileges via **Linux Capabilities**.
* **Multi-Technique Support**: Supports SYN (Stealth), TCP Connect, UDP, and FIN scans.
* **Host Discovery**: Dedicated modules for ARP and Ping discovery.
* **Dockerized**: Ready-to-deploy stack with Docker Compose.

---

## 🏗️ Architecture

The application is split into three main services:

1. **API (Flask)**: Entry point for submitting scan requests and checking task status.
2. **Broker (Redis)**: The message queue that transports tasks to workers.
3. **Worker (Celery)**: Executes the actual Nmap commands and stores the results.

---

## 🚀 Getting Started

### Prerequisites

* Docker
* Docker Compose

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

## 🔒 Security & Privileges

This project follows the **Principle of Least Privilege**. Instead of running containers as root, we use `setcap` in the Dockerfile to grant specific networking permissions:

```dockerfile
RUN setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip /usr/bin/nmap
```

These capabilities are then enabled in the `docker-compose.yml` file:

```yaml
cap_add:
  - NET_RAW
  - NET_ADMIN
```

**Note on SYN Scans**: For scans requiring raw sockets (like SYN), the `--privileged` flag is automatically handled internally by the worker to bypass Nmap's identity checks but `still not working`.

---

## 🛠️ Tech Stack

* **Language**: Python 3.12
* **Framework**: Flask
* **Task Queue**: Celery + Redis
* **Scanner**: Nmap (via python-nmap3)
* **Container**: Docker (Debian Slim)
