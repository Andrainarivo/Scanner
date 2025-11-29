"""
REST API for network scanning using python3-nmap (nmap3).
Includes:
- Live Host Discovery (ARP, Ping, etc.)
- TCP/UDP port scanning techniques (connect, SYN, FIN, UDP, etc.)

This API is intended for DevSecOps projects focusing on security, 
automation and containerized deployments.
"""

from flask import Flask, request, jsonify
import nmap3

app = Flask(__name__)

# Instantiate host discovery and scan technique engines
host_discovery = nmap3.NmapHostDiscovery()
scan_engine = nmap3.NmapScanTechniques()


# ------------------------------
# Utility Functions
# ------------------------------

def validate_json(required_fields, data):
    """
    Validate that required fields exist in the JSON payload.

    Args:
        required_fields (list): List of required keys.
        data (dict): Parsed JSON payload.

    Returns:
        tuple: (bool, message) where bool indicates success, message contains error.
    """
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: '{field}'"
    return True, None


# ------------------------------
# Live Host Discovery Endpoint
# ------------------------------

@app.route("/discover", methods=["POST"])
def discover_hosts():
    """
    Perform host discovery using ARP scan, ICMP ping, etc.
    Methods supported depend on python3-nmap capabilities.

    Expected JSON:
    {
        "targets": "192.168.1.0/24",
        "method": "arp" | "ping",
        "args": "-n" (optional extra nmap arguments)
    }
    """
    data = request.get_json(force=True)
    ok, msg = validate_json(["targets", "method"], data)
    if not ok:
        return jsonify({"error": msg}), 400

    targets = data["targets"]
    method = data["method"]
    args = data.get("args", "")

    # Map method to internal nmap3 function
    discovery_map = {
        "arp": host_discovery.nmap_arp_discovery,
        "ping": host_discovery.nmap_no_portscan   # ICMP ping discovery
    }

    if method not in discovery_map:
        return jsonify({"error": f"Unsupported discovery method '{method}'"}), 400

    try:
        result = discovery_map[method](targets, args=args)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "method": method,
        "targets": targets,
        "results": result
    })


# ------------------------------
# Port Scanning Endpoint
# ------------------------------

@app.route("/scan", methods=["POST"])
def port_scan():
    """
    Perform TCP/UDP port scanning using different techniques.
    Supports connect scan, SYN scan, FIN scan, UDP scan, etc.

    Expected JSON:
    {
        "target": "192.168.1.10",
        "ports": "1-1000" OR "22,80,443",
        "techniques": ["tcp", "syn", "fin", "udp"],
        "args": "-n" (optional)
    }
    """
    data = request.get_json(force=True)
    ok, msg = validate_json(["target", "techniques"], data)
    if not ok:
        return jsonify({"error": msg}), 400

    target = data["target"]
    ports = data.get("ports")
    techniques = data["techniques"]
    extra_args = data.get("args", "")

    results = {}

    for tech in techniques:
        try:
            # Construct argument string
            arg_string = ""
            if ports:
                arg_string = f"-p {ports} {extra_args}".strip()
            else:
                arg_string = extra_args

            # Technique mapping
            if tech == "tcp":
                result = scan_engine.nmap_tcp_scan(target, args=arg_string)
            elif tech == "syn":
                result = scan_engine.nmap_syn_scan(target, args=arg_string)
            elif tech == "fin":
                result = scan_engine.nmap_fin_scan(target, args=arg_string)
            elif tech == "udp":
                result = scan_engine.nmap_udp_scan(target, args=arg_string)
            else:
                results[tech] = {"error": f"Unsupported scan technique '{tech}'"}
                continue

            results[tech] = result

        except Exception as e:
            results[tech] = {"error": str(e)}

    return jsonify({
        "target": target,
        "ports": ports,
        "results": results
    })


# ------------------------------
# Root (Health Check)
# ------------------------------

@app.route("/", methods=["GET"])
def root():
    """Simple health check endpoint."""
    return jsonify({"status": "ok", "message": "Nmap API running"})


# ------------------------------
# Main
# ------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
