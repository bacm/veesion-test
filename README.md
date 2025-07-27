# Description
Ce projet est une plateforme de traitement d’alertes vidéos. Elle permet de :
- Recevoir des alertes via une API FastAPI (alert-service)
- Publier des messages dans RabbitMQ.
- Traiter les alertes via des workers qui traitent les vidéos

# Services principaux
- alert-service : API REST (FastAPI) pour publier des alertes dans RabbitMQ.
- alert-worker : Consommateur RabbitMQ, qui :
    - Télécharge les en-têtes vidéos via aiohttp.
    - Utilise ffprobe pour extraire width et height.
    - Sauvegarde les résultats dans la base PostgreSQL.
- RabbitMQ : File de messages.
- PostgreSQL : Stockage des alertes traitées.
- Nginx : Sert les fichiers vidéos.

# Installation locale
- git clone
- Lancer `setup_local.sh` pour le setup local

# Example de POST d'une alerte
```
curl -X POST "http://$(minikube ip):30000/alert" \
  -H "Content-Type: application/json" \
  -d '{
        "uid": "UID-1234",
        "video": "/videos/test.avi",
        "timestamp": 1720000000,
        "store": "store-42"
      }'
```

Ou pour un test de charge 

```
for i in {1..1000}; do
    curl -X POST "http://$(minikube ip):30000/alert" \
        -H "Content-Type: application/json" \
        -d '{
            "uid": "E00E9901-9246-4869-945A-7A0AABE1C382",
            "video": "/videos/test_1.avi",
            "timestamp": 1748871320.6882,
            "store": "test-store"
        }' &
done
```

# Validation manuelle
Pour valider le contenu en DB en local
```kubectl port-forward svc/postgres 5432:5432 -n alertsystem```
et lancer une shell 
```psql -h localhost -p 5432 -U veesion -d veesion```
pour valider le contenu dans la table videos.