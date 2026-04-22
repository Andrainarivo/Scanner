import os
import nmap3
from celery import Celery
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

REDIS_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
celery = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)

try:
    host_discovery = nmap3.NmapHostDiscovery()
    scan_engine = nmap3.NmapScanTechniques()
except Exception as e:
    logger.critical(f"Error initializing Nmap engines: {e}")

# ----------------------------------------------------------
# FONCTIONS UTILITAIRES POUR LA CONSTRUCTION D'ARGUMENTS
# ----------------------------------------------------------

def build_nmap_args(params):
    """Construit dynamiquement la chaîne d'arguments Nmap pour un scan optimal"""
    args = []

    scan_type = params.get("scan_type", "tcp").lower()
    os_detection = params.get("os_detection", False)

    # Scan SYN, UDP, FIN ou TCP classique ? (SYN, UDP et FIN nécessitent des privilèges élevés)
    if scan_type in ["syn", "udp", "fin"] or os_detection:
        args.append("--privileged")

    # Vitesse (Timing template : 0-5)
    timing = params.get("timing_template", 4)
    args.append(f"-T{timing}")

    # Ping ou pas ( -Pn pour ignorer la découverte d'hôte )
    if params.get("skip_ping"):
        args.append("-Pn")

    # Détection de version et d'OS
    if params.get("service_version"):
        args.append("-sV")
    if os_detection:
        args.append("-O")

    # Moteur de Scripts (NSE)
    scripts = params.get("scripts")
    if scripts == "default":
        args.append("-sC")
    elif scripts and scripts != "none":
        args.append(f"--script={scripts}")

    # Filtrage des Ports (soit par liste, soit par top ports)
    top_ports = params.get("top_ports")
    ports = params.get("ports")

    if top_ports:
        # Si top_ports est défini, on ignore l'argument ports classique
        args.append(f"--top-ports {top_ports}")
    elif ports:
        args.append(f"-p {ports}")

    # Injection d'arguments bruts ( ex: --min-rate=1000 pour accélérer les scans rapides )
    advanced = params.get("advanced_args")
    if advanced:
        args.append(advanced)

    return " ".join(args)

# ----------------------------------------------------------
# FONCTION DE FORMATAGE DES RÉSULTATS DE SCAN
# ----------------------------------------------------------

def format_scan_results(raw_results, target_requested, scan_type):
    """Transforme le résultat brut de Nmap en un JSON propre et standardisé"""
    
    # Validation de base du format de résultat
    if not isinstance(raw_results, dict):
        return {"error": "Nmap failed or returned no data", "raw": str(raw_results)}

    processed_hosts = []
    
    # Nmap retourne souvent des métadonnées (runtime, stats) en plus des hôtes scannés. On les sépare pour un traitement propre.
    meta_keys = ["runtime", "stats", "task_results"]
    host_keys = [k for k in raw_results.keys() if k not in meta_keys]

    for ip in host_keys:
        host_data = raw_results[ip]
        if not isinstance(host_data, dict):
            continue

        # État de l'hôte (up/down/unknown)
        status = host_data.get("state", {}).get("state", "unknown")

        # Détection d'OS (si disponible)
        os_match = "unknown"
        os_matches = host_data.get("osmatch", [])
        if os_matches:
            os_match = os_matches[0].get("name", "unknown")

        # Ports ouverts et services associés
        open_ports = []
        for port in host_data.get("ports", []):
            if port.get("state") == "open":
                service_info = port.get("service", {})
                product = service_info.get("product", "")
                version = service_info.get("version", "")
                full_version = f"{product} {version}".strip()

                open_ports.append({
                    "port": int(port.get("portid", 0)),
                    "protocol": port.get("protocol", "tcp"),
                    "service": service_info.get("name", "unknown"),
                    "version": full_version if full_version else "unknown"
                })

        processed_hosts.append({
            "ip": ip,
            "status": status,
            "os_match": os_match,
            "open_ports": open_ports
        })

    # Durée du scan (si disponible)
    runtime = raw_results.get("runtime", {})
    duration = runtime.get("elapsed", "0")

    return {
        "summary": {
            "target": target_requested,
            "scan_type": scan_type,
            "hosts_up": len(processed_hosts),
            "duration_seconds": duration
        },
        "hosts": processed_hosts
    }


# ----------------------------------------------------------
# TÂCHES ASYNCHRONES CELERY
# ----------------------------------------------------------

@celery.task(bind=True)
def async_host_discovery(self, target, method, safe_args):
    """ Tâche de découverte d'hôtes unifiée (ARP ou Ping) """
    logger.info(f"START Discovery: {method} on {target}")
    discovery_map = {
        "arp": host_discovery.nmap_arp_discovery,
        "ping": host_discovery.nmap_no_portscan
    }
    try:
        if method not in discovery_map:
            return {"error": f"Unsupported method '{method}'"}
        result = discovery_map[method](target, args=safe_args)
        return {"status": "success", "method": method, "data": result}
    except Exception as e:
        logger.error(f"Discovery Failed: {e}")
        return {"error": str(e)}


@celery.task(bind=True)
def async_port_scan(self, scan_params):
    """ Tâche de scan de ports unifiée pour tous les types de scans (TCP, SYN, UDP, FIN) avec arguments optimisés """
    target = scan_params.get("target")
    scan_type = scan_params.get("scan_type", "tcp").lower()
    
    # Construction de la chaîne d'arguments Nmap à partir des paramètres
    arg_string = build_nmap_args(scan_params)
    logger.info(f"EXECUTE Scan: {scan_type} on {target} with args: {arg_string}")
    
    try:
        # Initialisation de l'engine de scan (on le fait ici pour éviter les problèmes de sérialisation avec Celery)
        engine = nmap3.NmapScanTechniques()
        
        # Exécution du scan selon le type demandé
        if scan_type == "tcp":
            raw_res = engine.nmap_tcp_scan(target, args=arg_string)
        elif scan_type == "syn":
            raw_res = engine.nmap_syn_scan(target, args=arg_string)
        elif scan_type == "udp":
            raw_res = engine.nmap_udp_scan(target, args=arg_string)
        elif scan_type == "fin":
            raw_res = engine.nmap_fin_scan(target, args=arg_string)
        else:
            return {"error": f"Unsupported scan type: {scan_type}", "target": target}
        
        # Vérification de la présence d'erreurs dans le résultat brut de Nmap
        if "error" in raw_res:
            logger.error(f"Nmap Scan Error: {raw_res['error']}")
            return {"error": raw_res["error"], "target": target}
            
        return format_scan_results(raw_res, target, scan_type)

    except Exception as e:
        logger.error(f"Error executing scan: {e}")
        return {"error": str(e), "target": target}