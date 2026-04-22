import logging
import ipaddress
import re
from flask import Flask, request, jsonify

from tasks import async_host_discovery, async_port_scan, celery

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
    # Regex élargie pour autoriser les options Nmap classiques (--min-rate=1000, etc.)
    if not re.match(r"^[a-zA-Z0-9\-\s\/\.\,\=\:]+$", args_str):
        raise ValueError("The 'advanced_args' field contains invalid characters. Allowed: letters, numbers, spaces, and - / . , = :")
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

    task = async_host_discovery.delay(target, method, safe_args)
    logger.info(f"Discovery task queued: {task.id} for {target}")

    return jsonify({
        "status": "queued",
        "job_id": task.id,
        "message": f"Discovery started. Check /status/{task.id}"
    }), 202


@app.route("/scan", methods=["POST"])
def port_scan():
    """Endpoint pour lancer un scan de ports. Valide les entrées, construit les paramètres et délègue à Celery."""
    data = request.get_json(silent=True)
    if not data: return jsonify({"error": "Invalid JSON"}), 400

    # 1. Extraction des paramètres d'entrée
    target = data.get("target")
    scan_type = data.get("scan_type", "tcp").lower()
    ports = data.get("ports", "")
    timing_template = data.get("timing_template", 4)
    top_ports = data.get("top_ports")
    
    # 2. Validation des paramètres d'entrée
    if not target:
        return jsonify({"error": "Missing 'target'"}), 400
    
    if not is_valid_target(target):
        return jsonify({"error": f"Invalid target IP/CIDR: {target}"}), 400

    if scan_type not in ["tcp", "syn", "udp", "fin"]:
        return jsonify({"error": f"Unsupported scan_type '{scan_type}'"}), 400

    if not isinstance(timing_template, int) or not (0 <= timing_template <= 5):
        return jsonify({"error": "timing_template must be an integer between 0 and 5"}), 400

    if ports and not re.match(r"^[a-zA-Z0-9,\-]+$", ports):
        return jsonify({"error": "Invalid ports format"}), 400
    
    if top_ports and not isinstance(top_ports, int):
        return jsonify({"error": "top_ports must be an integer"}), 400

    try:
        safe_advanced_args = sanitize_nmap_args(data.get("advanced_args", ""))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # 3. Construction des paramètres pour la tâche Celery
    scan_params = {
        "target": target,
        "scan_type": scan_type,
        "ports": ports,
        "top_ports": top_ports,
        "timing_template": timing_template,
        "service_version": bool(data.get("service_version", False)),
        "os_detection": bool(data.get("os_detection", False)),
        "skip_ping": bool(data.get("skip_ping", False)),
        "scripts": data.get("scripts", "none"),
        "advanced_args": safe_advanced_args
    }

    # 4. Délégation à Celery
    task = async_port_scan.delay(scan_params)
    logger.info(f"Scan task queued: {task.id} for {target} (Type: {scan_type})")

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

        # Ajout des états intermédiaires de Celery
        if result.state in ['PENDING', 'STARTED', 'RETRY']:
            response["status"] = "Processing..."
        elif result.state == 'SUCCESS':
            response["result"] = result.result
        elif result.state == 'FAILURE':
            response["error"] = str(result.info)
        else:
            response["status"] = "Unknown state"
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "mode": "async", "version": "2.0"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)