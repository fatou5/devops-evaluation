# Projet d'évaluation DevOps

Ce projet met en place une chaîne DevOps complète : développement, tests, build, publication, déploiement et supervision.

L'application est une API développée avec FastAPI et conteneurisée avec Docker. Les tests sont réalisés avec Pytest. L'image Docker est publiée sur GitHub Container Registry (GHCR) puis déployée automatiquement grâce à GitHub Actions et un self-hosted runner.

La supervision est assurée avec Prometheus.

## 1. Technologies utilisées

* Python 3.12
* FastAPI / Uvicorn
* Redis
* Docker / Docker Compose
* GitHub Actions
* GitHub Container Registry
* Pytest / Pytest-Cov
* Ruff
* yamllint
* Prometheus

## 2. Structure du projet

Le projet contient principalement :

* `app/` : code de l'application
* `tests/` : tests automatisés
* `prometheus/` : règles d'alertes
* `.github/workflows/` : workflows CI/CD
* `.github/actions/` : action réutilisable pour Python
* `Dockerfile` : construction de l'image
* `docker-compose.yml` : environnement local
* `docker-compose.prod.yml` : environnement de production
* `prometheus.yml` : configuration Prometheus
* `requirements.txt` et `requirements-dev.txt` : dépendances
* `VERSION` : version de l'application

## 3. Application

L'API possède plusieurs endpoints :

* `/` : endpoint principal
* `/health` : vérification de l'application et de Redis
* `/metrics` : métriques Prometheus
* `/test-error` : génère volontairement une erreur HTTP 500
* `/test-slow` : génère volontairement une latence

curl http://localhost:8000/


## 4. Lancement en local

Les prérequis sont Docker, Docker Compose et Python 3.11 ou 3.12.

Pour démarrer le projet :

docker compose up -d --build


Vérifier les conteneurs :

docker compose ps


L'application est disponible sur :

http://localhost:8000


Prometheus est accessible sur :

http://localhost:9091


Le port 9091 est utilisé pour éviter un conflit avec une autre instance Prometheus.

Pour vérifier l'application :

curl http://localhost:8000/health


## 5. Tests et qualité

Les tests sont réalisés avec Pytest et vérifient notamment le fonctionnement de `/health`, Redis, les métriques Prometheus et l'endpoint de latence.

Installation de l'environnement :

python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt


Les tests peuvent ensuite être lancés avec :

python -m pytest -v


Le projet utilise également Ruff :

python -m ruff check .
python -m ruff format --check .


Les fichiers YAML sont vérifiés avec :

yamllint .


## 6. Docker

Le Dockerfile utilise une construction multi-stage afin de limiter le contenu de l'image finale.

L'application utilise une image `python:3.12-slim` et s'exécute avec un utilisateur non privilégié nommé `appuser`.

Un healthcheck Docker vérifie régulièrement l'endpoint `/health`.

Les fichiers inutiles ou sensibles comme `.git`, `.venv`, `.env` et les caches Python sont exclus grâce au `.dockerignore`.

## 7. CI avec GitHub Actions

La CI est lancée lors des `push` sur `main` et lors des Pull Requests.

Elle permet de vérifier :

* le lint et le formatage avec Ruff ;
* les tests avec Python 3.11 et 3.12 ;
* le fonctionnement avec Redis ;
* la construction de l'image Docker.

Les rapports de tests et de couverture sont également conservés comme artefacts GitHub Actions.

Une action réutilisable située dans `.github/actions/setup-python/` permet de préparer l'environnement Python et d'utiliser le cache pip.

## 8. Publication et déploiement

Après une CI réussie sur `main`, le workflow CD construit l'image et la publie dans GitHub Container Registry :

ghcr.io/fatou5/devops-evaluation


Plusieurs tags sont utilisés, notamment :

* `latest`
* le SHA court du commit
* la version du projet, actuellement `1.0.0`

Le déploiement est effectué sur une machine équipée d'un GitHub Actions self-hosted runner.

Le workflow utilise le `GITHUB_TOKEN` pour s'authentifier auprès de GHCR.

## 9. Vérification du déploiement

Après le déploiement, un healthcheck est effectué avec :

curl --fail --silent --show-error http://localhost:8000/health


Le contrôle est réalisé plusieurs fois afin de laisser le temps à l'application de démarrer.

Si le nouveau déploiement ne fonctionne pas, le workflow peut récupérer l'image correspondant à la version précédente et effectuer un **rollback**.

## 10. Supervision avec Prometheus

L'application expose ses métriques sur :

http://localhost:8000/metrics


Prometheus récupère les métriques régulièrement.

Les principales métriques utilisées sont :

* `http_requests_total` : nombre de requêtes HTTP ;
* `http_request_duration_seconds` : durée des requêtes ;
* `app_version_info` : version actuellement déployée.

Les métriques de latence permettent notamment de calculer le p95 et le p99.

## 11. Alertes

Deux alertes principales ont été mises en place.

### HighHTTP5xxRatio

Cette alerte surveille le taux de réponses HTTP 5xx.

Elle se déclenche lorsque le taux d'erreurs dépasse 5% pendant la durée définie dans la configuration.

### HighHTTPP95Latency

Cette alerte surveille le temps de réponse de l'application.

Elle se déclenche lorsque le p95 dépasse 500 ms pendant la durée configurée.

Les endpoints `/test-error` et `/test-slow` permettent de tester le fonctionnement des alertes.

for i in $(seq 1 100); do
  curl -s -o /dev/null http://localhost:8000/test-error
done


Pour tester la latence :

for i in $(seq 1 30); do
  curl -s -o /dev/null http://localhost:8000/test-slow
done


## 12. Sécurité

Quelques mesures de sécurité sont appliquées au projet :

* utilisation d'une image Python versionnée ;
* construction Docker multi-stage ;
* utilisation d'un utilisateur non root ;
* exclusion des secrets et fichiers `.env` du dépôt ;
* permissions GitHub Actions limitées au nécessaire ;
* utilisation du `GITHUB_TOKEN` pour GHCR ;
* absence de secrets directement dans le code ;
* healthchecks applicatifs et Docker ;
* possibilité de rollback.

## 13. Commandes utiles

Vérifier l'application :

curl -i http://localhost:8000/
curl -i http://localhost:8000/health
curl -i http://localhost:8000/metrics


Vérifier les conteneurs :

docker compose ps


Arrêter l'environnement :

docker compose down


Pour supprimer également les conteneurs orphelins :

docker compose down --remove-orphans


## 14. Version et dépôt

La version actuelle du projet est :

1.0.0


Le projet est disponible sur GitHub :

`https://github.com/fatou5/devops-evaluation`

Ce dépôt contient les éléments nécessaires pour mettre en place la CI/CD, construire et déployer l'application avec Docker et assurer sa supervision avec Prometheus.
