#!/bin/bash

kubectl delete deployments --all
kubectl delete services --all

docker build -t service:latest ./service-app
docker build -t tracker:latest ./tracking-api
docker build -t sidecar:latest ./sidecar-app

kubectl apply -f "k8s/services/neo4j-pvc.yaml"
kubectl apply -f "k8s/deployments/neo4j-deployment.yaml"
kubectl apply -f "k8s/deployments/tracker-deployment.yaml"
kubectl apply -f "k8s/services/tracker-service.yaml"
kubectl apply -f "k8s/services/neo4j-service.yaml"

for file in k8s/deployments/service*-deployment.yaml; do
    kubectl apply -f "$file"
done

for file in k8s/services/service*-service.yaml; do
    kubectl apply -f "$file"
done

