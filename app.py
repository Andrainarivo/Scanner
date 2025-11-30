import logging
import ipaddress
import re
from flask import Flask, request, jsonify
from functools import wraps
import nmap3

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Instanciation des moteurs Nmap
try:
    host_discovery = nmap3.NmapHostDiscovery()
    scan_engine = nmap3.NmapScanTechniques()
except Exception as e:
    logger.critical(f"Erreur lors de l'initialisation de nmap3: {e}")
    exit(1)

# ------------------------------
# Décorateurs & Utilitaires
# ------------------------------

def require_api_key(f):
    """(Optionnel) Sécurisation basique par API Key."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # En prod, utilisez une variable d'environnement ou un gestionnaire de secrets
        api_key = request.headers.get('X-API-KEY')
        if api_key != "votre-super-secret-key": 
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

def is_valid_target(target):
    """Valide si la cible est une IP, un sous-réseau CIDR ou un domaine valide."""
    try:
        # Vérifie IP v4/v6 ou CIDR
        ipaddress.ip_network(target, strict=False)
        return True
    except ValueError:
        # Vérification simple de nom de domaine (regex basique)
        regex_domain = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$"
        return re.match(regex_domain, target) is not None

def sanitize_nmap_args(args_str):
    """
    Nettoie les arguments pour éviter l'injection de commandes.
    N'autorise que certains caractères sûrs.
    """
    if not args_str:
        return ""
    # Autorise seulement alphanumérique, tirets, espaces et slash
    if not re.match(r"^[a-zA-Z0-9\-\s\/]+$", args_str):
        raise ValueError("Arguments contiennent des caractères interdits")
    return args_str

# ------------------------------
# Endpoints
# ------------------------------

@app.route("/discover", methods=["POST"])
# @require_api_key # Décommentez pour activer la sécurité
def discover_hosts():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    target = data.get("targets")
    method = data.get("method")
    extra_args = data.get("args", "")

    # Validation stricte
    if not target or not method:
        return jsonify({"error": "Missing 'targets' or 'method'"}), 400
    
    if not is_valid_target(target):
        return jsonify({"error": f"Invalid target format: {target}"}), 400

    try:
        safe_args = sanitize_nmap_args(extra_args)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    logger.info(f"Discovery scan requested: {method} on {target}")

    discovery_map = {
        "arp": host_discovery.nmap_arp_discovery,
        "ping": host_discovery.nmap_no_portscan
    }

    if method not in discovery_map:
        return jsonify({"error": f"Unsupported method '{method}'"}), 400

    try:
        # Exécution du scan
        result = discovery_map[method](target, args=safe_args)
        return jsonify({
            "status": "success",
            "method": method,
            "data": result
        })
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        return jsonify({"error": "Internal Scan Error", "details": str(e)}), 500


@app.route("/scan", methods=["POST"])
def port_scan():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    target = data.get("targets")
    ports = data.get("ports") # Peut être None pour défaut
    techniques = data.get("techniques", [])

    # Si l'utilisateur envoie "tcp" au lieu de ["tcp"], on convertit la chaine en liste
    if isinstance(techniques, str):
        techniques = [techniques]

    extra_args = data.get("args", "")

    # Validations
    if not target or not techniques:
        return jsonify({"error": "Missing 'targets' or 'techniques'"}), 400
    
    if not is_valid_target(target):
        return jsonify({"error": f"Invalid target IP/CIDR: {target}"}), 400
    
    # Validation basique des ports (ex: "80" ou "1-100" ou "80,443")
    if ports and not re.match(r"^[0-9,\-]+$", ports):
        return jsonify({"error": "Invalid ports format"}), 400

    try:
        safe_args = sanitize_nmap_args(extra_args)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    results = {}
    
    # Construction des arguments globaux
    base_args = safe_args
    if ports:
        base_args = f"-p {ports} {safe_args}".strip()

    logger.info(f"Port scan requested on {target} techniques={techniques}")

    for tech in techniques:
        try:
            if tech == "tcp":
                res = scan_engine.nmap_tcp_scan(target, args=base_args)
            elif tech == "syn":
                # Note: SYN scan requiert des privilèges root (sudo ou capabilities)
                res = scan_engine.nmap_syn_scan(target, args=base_args)
            elif tech == "fin":
                res = scan_engine.nmap_fin_scan(target, args=base_args)
            elif tech == "udp":
                # UDP est lent et requiert root
                res = scan_engine.nmap_udp_scan(target, args=base_args)
            else:
                results[tech] = {"error": "Unsupported technique"}
                continue
            
            results[tech] = res

        except Exception as e:
            logger.error(f"Error executing {tech} scan: {e}")
            results[tech] = {"error": str(e)}

    return jsonify({
        "target": target,
        "scan_results": results
    })

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "version": "1.1.0"})

if __name__ == "__main__":
    # Désactiver le debug en prod !
    app.run(host="0.0.0.0", port=5000, debug=False)