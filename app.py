import logging
import ipaddress
import re
from flask import Flask, request, jsonify
from functools import wraps

from tasks import async_host_discovery, async_port_scan, celery

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --------------------------
# Utilitaires de Validation
# --------------------------

def is_valid_target(target):
    try:
        ipaddress.ip_network(target, strict=False)
        return True
    except ValueError:
        regex_domain = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$"
        return re.match(regex_domain, target) is not None

def sanitize_nmap_args(args_str):
    if not args_str: return ""
    if not re.match(r"^[a-zA-Z0-9\-\s\/]+$", args_str):
        raise ValueError("Arguments contiennent des caractères interdits")
    return args_str

# ------------------------------
# Endpoints
# ------------------------------

@app.route("/discover", methods=["POST"])
def discover_hosts():
    data = request.get_json(silent=True)
    if not data: return jsonify({"error": "Invalid JSON"}), 400

    target = data.get("targets")
    method = data.get("method")
    extra_args = data.get("args", "")

    # 1. Validation (Synchron)
    if not target or not method:
        return jsonify({"error": "Missing 'targets' or 'method'"}), 400
    
    if not is_valid_target(target):
        return jsonify({"error": f"Invalid target format: {target}"}), 400

    try:
        safe_args = sanitize_nmap_args(extra_args)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if method not in ["arp", "ping"]:
        return jsonify({"error": f"Unsupported method '{method}'"}), 400

    # 2. Délégation (Asynchrone)
    # On envoie la tâche à Redis via Celery
    task = async_host_discovery.delay(target, method, safe_args)

    logger.info(f"Discovery task queued: {task.id} for {target}")

    return jsonify({
        "status": "queued",
        "job_id": task.id,
        "message": f"Discovery started. Check /status/{task.id}"
    }), 202


@app.route("/scan", methods=["POST"])
def port_scan():
    data = request.get_json(silent=True)
    if not data: return jsonify({"error": "Invalid JSON"}), 400

    target = data.get("targets")
    ports = data.get("ports")
    techniques = data.get("techniques", [])

    # Correction liste
    if isinstance(techniques, str):
        techniques = [techniques]

    extra_args = data.get("args", "")

    # 1. Validation
    if not target or not techniques:
        return jsonify({"error": "Missing 'targets' or 'techniques'"}), 400
    
    if not is_valid_target(target):
        return jsonify({"error": f"Invalid target IP/CIDR: {target}"}), 400
    
    if ports and not re.match(r"^[0-9,\-]+$", ports):
        return jsonify({"error": "Invalid ports format"}), 400

    try:
        safe_args = sanitize_nmap_args(extra_args)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # 2. Délégation
    task = async_port_scan.delay(target, ports, techniques, safe_args)
    
    logger.info(f"Scan task queued: {task.id} for {target}")

    return jsonify({
        "status": "queued",
        "job_id": task.id,
        "message": f"Scan started. Check /status/{task.id}"
    }), 202


@app.route("/status/<job_id>", methods=["GET"])
def get_status(job_id):
    """Récupérer le résultat d'une tâche via son ID"""
    try:
        result = celery.AsyncResult(job_id)
        
        response = {
            "job_id": job_id,
            "state": result.state
        }

        if result.state == 'PENDING':
            response["status"] = "Processing..."
        elif result.state == 'SUCCESS':
            response["result"] = result.result
        elif result.state == 'FAILURE':
            response["error"] = str(result.info)
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "mode": "async"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)