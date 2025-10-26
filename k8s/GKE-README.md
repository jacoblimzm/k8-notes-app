# Notes App - GKE Deployment Guide

This guide will help you deploy the Notes App to Google Kubernetes Engine (GKE).

## Prerequisites

1. **Google Cloud SDK** installed and configured
2. **kubectl** installed and configured
3. **Docker** installed
4. **Google Cloud Project** with billing enabled

## Step 1: Set up GKE Cluster

```bash
# Set your project ID
PROJECT_ID=mcse-sandbox

# Create a GKE cluster
gcloud container clusters create notes-app-cluster \
    --zone=us-central1-a \
    --num-nodes=2 \
    --machine-type=e2-medium \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=5

# Get credentials for the cluster and update kubectl config
gcloud container clusters get-credentials cluster-jake --zone=asia-southeast1-a --project mcse-sandbox

# Get kubectl config
kubectl config view
kubectl config current-contexts
```
- See more information about kubectl config and viewing current context of [kubectl](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl#interact_kubectl)

## Step 2: Build and Push Docker Images

```bash
# Configure Docker to use gcloud as a credential helper
gcloud auth configure-docker

# Build and tag images
docker build -t gcr.io/$PROJECT_ID/notes-backend:latest ./backend
docker build -t gcr.io/$PROJECT_ID/notes-frontend:latest ./frontend
docker buildx build --platform linux/amd64 -t asia-southeast1-docker.pkg.dev/mcse-sandbox/jake-reg/notes-backend-amd:v0.1 .

docker tag SOURCE-IMAGE LOCATION-docker.pkg.dev/PROJECT-ID/REPOSITORY/IMAGE:TAG

docker tag notes-frontend-image:latest asia-southeast1-docker.pkg.dev/mcse-sandbox/jake-reg/notes-frontend:v0.1
docker tag notes-backend-image:latest asia-southeast1-docker.pkg.dev/mcse-sandbox/jake-reg/notes-backend:v0.1
docker tag notes-backend-image:latest gcr.io/mcse-sandbox/notes-backend:v0.1

# Push images to Google Container Registry
docker push gcr.io/$PROJECT_ID/notes-backend:latest
docker push gcr.io/$PROJECT_ID/notes-frontend:latest

docker push asia-southeast1-docker.pkg.dev/mcse-sandbox/jake-reg/notes-frontend-amd:v0.1
docker push asia-southeast1-docker.pkg.dev/mcse-sandbox/jake-reg/notes-backend-amd:v0.1
docker push asia-southeast1-docker.pkg.dev/mcse-sandbox/jake-reg/nginx-proxy-amd:v0.1
docker push gcr.io/mcse-sandbox/notes-backend:v0.1
docker push gcr.io/mcse-sandbox/notes-frontend:v0.1
```

## Step 3: Update Kubernetes Manifests

Update the image references in your deployment files:

**backend-deployment.yaml:**
```yaml
image: gcr.io/YOUR-PROJECT-ID/notes-backend:latest
```

**frontend-deployment.yaml:**
```yaml
image: gcr.io/YOUR-PROJECT-ID/notes-frontend:latest
```

### Database Initialization
The database will be automatically initialized with:
- Notes table creation
- Sample data insertion
- Scripts located in `init-db/` folder

## Step 4: Deploy to GKE

```bash
# Create namespace
kubectl apply -f namespace.yaml

# Create secrets
kubectl apply -f secrets.yaml

# Create database init script
kubectl apply -f postgres-init-configmap.yaml

# Deploy PostgreSQL
kubectl apply -f postgres-deployment.yaml
kubectl apply -f postgres-service.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n notes-app --timeout=300s

# Deploy backend
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml

# Deploy frontend
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
```

## Step 5: Access Your Application

```bash
# Get the external IP of the frontend service
kubectl get svc frontend-service -n notes-app

# The output will show something like:
# NAME               TYPE           CLUSTER-IP      EXTERNAL-IP      PORT(S)        AGE
# frontend-service   LoadBalancer   10.0.123.456    34.123.456.789   3000:30000/TCP 2m
```

Access your application at: `http://EXTERNAL-IP:3000`

## Step 6: Monitor Your Deployment

```bash
# Check pod status
kubectl get pods -n notes-app

# Check services
kubectl get svc -n notes-app

# View logs
kubectl logs -f deployment/backend -n notes-app
kubectl logs -f deployment/frontend -n notes-app
kubectl logs -f deployment/postgres -n notes-app
```

## GKE-Specific Considerations

### Load Balancer
- GKE automatically provisions a Google Cloud Load Balancer
- External IP assignment may take 1-2 minutes
- Load balancer incurs additional costs

### Storage
- Consider using Google Cloud Storage or Cloud SQL for production
- Current setup uses ephemeral storage (data lost on pod restart)
- Database schema is automatically initialized via init scripts in `init-db/` folder

### Security
- Update secrets with strong passwords for production
- Consider using Google Secret Manager for sensitive data
- Enable network policies for pod-to-pod communication

### Scaling
- Cluster autoscaling is enabled
- Consider horizontal pod autoscaling (HPA) for the backend

## Cleanup

```bash
# Delete the deployment
kubectl delete namespace notes-app

# Delete the cluster (optional)
gcloud container clusters delete notes-app-cluster --zone=us-central1-a
```

## Troubleshooting

### Common Issues:

1. **Image pull errors**: Ensure images are pushed to GCR and accessible
2. **Load balancer pending**: Wait 1-2 minutes for IP assignment
3. **Database connection issues**: Check if PostgreSQL pod is ready and init scripts completed
4. **Permission errors**: Ensure proper IAM roles are assigned

### Useful Commands:

```bash
# Describe resources for debugging
kubectl describe pod <pod-name> -n notes-app
kubectl describe svc <service-name> -n notes-app

# Port forward for local debugging
kubectl port-forward svc/frontend-service 8080:3000 -n notes-app

# Execute commands in pods
kubectl exec -it <pod-name> -n notes-app -- /bin/bash

# Check database initialization
kubectl logs <postgres-pod-name> -n notes-app | grep "database system is ready"
```

## Cost Optimization

- Use preemptible nodes for development
- Set appropriate resource limits
- Monitor usage with Cloud Console
- Consider using Cloud Run for serverless deployment 