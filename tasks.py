import os
import nmap3
from celery import Celery
from celery.utils.log import get_task_logger

# Configuration Logger pour Celery
logger = get_task_logger(__name__)

# Configuration Celery
REDIS_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
celery = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)

# Instanciation des moteurs Nmap (Se fait au démarrage du Worker)
try:
    host_discovery = nmap3.NmapHostDiscovery()
    scan_engine = nmap3.NmapScanTechniques()
except Exception as e:
    logger.critical(f"Erreur init nmap3 dans le worker: {e}")

@celery.task(bind=True)
def async_host_discovery(self, target, method, safe_args):
    """Tâche pour /discover"""
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
def async_port_scan(self, target, ports, techniques, safe_args):
    """Tâche pour /scan (Gère la boucle des techniques)"""
    logger.info(f"START Port Scan: {target} techniques={techniques}")
    
    results = {}
    
    # Construction de l'argument de port global si présent
    # (Note: on l'ajoute dynamiquement dans la boucle pour gérer le --privileged)
    
    for tech in techniques:
        try:
            current_args = safe_args

            # Logique Privilégiée (déplacée ici)
            if tech in ["syn", "udp", "fin"]:
                current_args = f"{current_args} --privileged"

            # Ajout des ports
            if ports:
                arg_string = f"-p {ports} {current_args}".strip()
            else:
                arg_string = current_args
            
            # Mapping exécution
            if tech == "tcp":
                res = scan_engine.nmap_tcp_scan(target, args=arg_string)
            elif tech == "syn":
                res = scan_engine.nmap_syn_scan(target, args=arg_string)
            elif tech == "fin":
                res = scan_engine.nmap_fin_scan(target, args=arg_string)
            elif tech == "udp":
                res = scan_engine.nmap_udp_scan(target, args=arg_string)
            else:
                results[tech] = {"error": "Unsupported technique"}
                continue
            
            results[tech] = res

        except Exception as e:
            logger.error(f"Error executing {tech} scan: {e}")
            results[tech] = {"error": str(e)}

    return {
        "target": target,
        "scan_results": results
    }