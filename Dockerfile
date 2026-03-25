# Image de base légère (Python 3.11 sur Debian Slim)
FROM python:3.11-slim

# Variables d'environnement pour optimiser Python dans Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Installation des dépendances système
# - nmap : Le scanner réseau
# - libcap2-bin : Pour la commande 'setcap' (gestion des capabilities)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    libcap2-bin \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Création d'un utilisateur non-root pour la sécurité
RUN useradd -m -s /bin/bash scanner

# Configuration du répertoire de travail
WORKDIR /scanner

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Étape 8 : GESTION DES CAPABILITIES (Le point critique)
# Au lieu de lancer en root, on donne à nmap les droits spécifiques :
# - cap_net_raw : Pour envoyer des paquets bruts (TCP scan, OS detection)
# - cap_net_admin : Pour configurer les interfaces réseaux si besoin
# - cap_net_bind_service : Pour utiliser les ports privilégiés (<1024)

USER root

RUN setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip /usr/bin/nmap

# Changement de propriétaire des fichiers vers l'utilisateur non-root
RUN chown -R scanner:scanner /scanner

# Passage à l'utilisateur non-root
USER scanner

# Exposition du port
EXPOSE 5000

# Lancement avec Gunicorn (Serveur de production)
# 4 workers pour gérer plusieurs requêtes en parallèle
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:5000", "--timeout=120", "app:app"]