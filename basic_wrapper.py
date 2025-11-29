from flask import Flask, request, jsonify
import nmap
import json
import os

app = Flask(__name__)

# ============================================================
#  Helper DNS options builder
# ============================================================
def build_dns_opts(dns_cfg):
    opts = []

    if not dns_cfg:
        return opts

    if dns_cfg.get("no_dns"):
        opts.append("-n")
    if dns_cfg.get("reverse"):
        opts.append("-R")
    if dns_cfg.get("server"):
        opts.append(f"--dns-server {dns_cfg['server']}")

    return opts


# ============================================================
#  LIVE HOST DISCOVERY
# ============================================================
DISCOVERY_METHODS = {
    "arp": "-PR -sn",
    "icmp_echo": "-PE -sn",
    "icmp_timestamp": "-PP -sn",
    "icmp_netmask": "-PM -sn",
    "tcp_syn_ping": "-PS -sn",
    "tcp_ack_ping": "-PA -sn",
    "udp_ping": "-PU -sn",
}


@app.route("/discover", methods=["POST"])
def discover_hosts():
    data = request.get_json(force=True)

    targets = data.get("targets")
    method = data.get("method")

    if not targets:
        return jsonify({"error": f"targets field required"}), 400

    if method not in DISCOVERY_METHODS:
        return jsonify({"error": f"Unknown discovery method: {method}"}), 400

    nm = nmap.PortScanner()

    # Base options
    options = DISCOVERY_METHODS[method]

    # Add DNS options
    dns_opts = build_dns_opts(data.get("dns"))
    if dns_opts:
        options += " " + " ".join(dns_opts)

    try:
        nm.scan(hosts=targets, arguments=options)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Extract live hosts
    results = {}
    for host in nm.all_hosts():
        results[host] = {
            "state": nm[host].state(),
            "addresses": nm[host].get("addresses", {})
        }

    return jsonify({"method": method, "results": results})


# ============================================================
#  PORT SCANNING
# ============================================================
SCAN_TECHNIQUES = {
    "connect": "-sT",
    "syn": "-sS",
    "null": "-sN",
    "fin": "-sF",
    "xmas": "-sX",
    "udp": "-sU",
}


@app.route("/scan", methods=["POST"])
def port_scan():
    data = request.get_json(force=True)

    target = data.get("target")
    ports = data.get("ports", "1-1024")
    techniques = data.get("techniques", ["syn"])

    if not target:
        return jsonify({"error": "target is required"}), 400

    nm = nmap.PortScanner()

    results = {}

    for tech in techniques:
        if tech not in SCAN_TECHNIQUES:
            results[tech] = {"error": "unknown technique"}
            continue

        options = SCAN_TECHNIQUES[tech]

        try:
            nm.scan(hosts=target, ports=ports, arguments=options)
        except Exception as e:
            results[tech] = {"error": str(e)}
            continue

        # Check if scan returned hosts
        try:
            host = list(nm.all_hosts())[0]
        except:
            results[tech] = {"error": "no hosts found"}
            continue

        # Extract ports
        scan_data = {}
        for proto in nm[host].all_protocols():
            scan_data[proto] = nm[host][proto]

        results[tech] = scan_data

    return jsonify({
        "target": target,
        "ports": ports,
        "results": results
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
