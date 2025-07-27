#!/usr/bin/env bash
set -e

NAMESPACE="alertsystem"
VIDEOS_SRC="./nginx/videos"
VIDEOS_DEST="/mnt/data/videos"

# --- Couleurs ---
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== 0. Nettoyage du cluster existant ===${NC}"
if kubectl get namespace ${NAMESPACE} &>/dev/null; then
    echo -e "${GREEN}--> Suppression du namespace ${NAMESPACE}...${NC}"
    kubectl delete namespace ${NAMESPACE} --wait
    echo -e "${GREEN}--> Namespace supprimé.${NC}"
else
    echo "--> Aucun namespace ${NAMESPACE} existant."
fi

echo -e "${GREEN}=== 1. Vérification de Minikube ===${NC}"
if ! command -v minikube &> /dev/null; then
    echo "❌ Minikube n'est pas installé. Installe-le avant de lancer ce script."
    exit 1
fi

if ! minikube status &>/dev/null; then
    echo -e "${GREEN}--> Minikube non démarré, démarrage en cours...${NC}"
    minikube start --driver=docker
else
    echo -e "${GREEN}--> Minikube est déjà en cours d'exécution.${NC}"
fi

echo -e "${GREEN}=== 2. Montage du répertoire local des vidéos ===${NC}"
if [ ! -d "$VIDEOS_SRC" ]; then
    echo "❌ Le répertoire $VIDEOS_SRC n'existe pas. Crée-le avant de continuer."
    exit 1
fi

# Lancer minikube mount en arrière-plan
if ! pgrep -f "minikube mount $VIDEOS_SRC:$VIDEOS_DEST" > /dev/null; then
    echo "--> Montage de $VIDEOS_SRC sur $VIDEOS_DEST dans Minikube..."
    nohup minikube mount $VIDEOS_SRC:$VIDEOS_DEST >/dev/null 2>&1 &
    sleep 3
else
    echo "--> Montage déjà actif."
fi

echo -e "${GREEN}=== 3. Construction des images Docker ===${NC}"
# Utiliser l'environnement Docker de Minikube
eval $(minikube docker-env)

echo "--> Build de nginx-local"
docker build -t nginx-local:latest ./nginx

echo "--> Build de alert-service"
docker build -t alert-service:latest ./alert-service

echo "--> Build de alert-worker"
docker build -t alert-worker:latest ./alert-worker

echo -e "${GREEN}=== 4. Application du manifest Kubernetes ===${NC}"
kubectl apply -f k8s-alertsystem.yml

echo -e "${GREEN}=== 5. Attente du déploiement des pods ===${NC}"
if ! kubectl wait --for=condition=available --timeout=120s deployment --all -n ${NAMESPACE}; then
    echo "❌ Certains pods ne sont pas prêts."
    kubectl get pods -n ${NAMESPACE}
fi

echo -e "${GREEN}=== 6. État final ===${NC}"
kubectl get pods -n ${NAMESPACE}
kubectl get svc -n ${NAMESPACE}

echo -e "${GREEN}✅ Déploiement terminé !${NC}"
echo "FastAPI (alert-service): http://$(minikube ip):30000"
echo "RabbitMQ Management: http://$(minikube ip):31672"
echo "Nginx (vidéos): http://$(minikube ip):30080"
