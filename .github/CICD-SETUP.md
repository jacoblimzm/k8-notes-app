# CI/CD Setup Guide for GKE Deployment with Docker Hub

This guide will help you set up automated deployments to GKE via GitHub Actions using Docker Hub for container images.

## Prerequisites

- Docker Hub account (username: `jacoblimzm`)
- Google Cloud Project: `mcse-sandbox`
- GKE Cluster: `cluster-jake` in `asia-southeast1-a`
- GitHub repository for this project
- `gcloud` CLI installed locally

## Step 1: Create Docker Hub Access Token

1. Go to [Docker Hub](https://hub.docker.com/)
2. Log in with your account
3. Click on your username (top right) → **Account Settings**
4. Go to **Security** → **New Access Token**
5. Give it a name: `github-actions-token`
6. Select **Read & Write** permissions
7. Click **Generate**
8. **Copy the token immediately** (you won't be able to see it again)

## Step 2: Create Google Cloud Service Account

This service account will be used by GitHub Actions to deploy to your GKE cluster.

```bash
# Set your project ID
export PROJECT_ID=mcse-sandbox

# Create a service account
gcloud iam service-accounts create github-actions-sa \
    --display-name="GitHub Actions Service Account" \
    --project=$PROJECT_ID

# Grant necessary permissions (only container.developer needed for deployment)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/container.developer"

# Create and download the key
gcloud iam service-accounts keys create ~/gcp-key.json \
    --iam-account=github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com
```

## Step 3: Add GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

### Secret 1: DOCKERHUB_TOKEN
   **Name:** `DOCKERHUB_TOKEN`
   
   **Value:** Paste the Docker Hub access token you created in Step 1

### Secret 2: GCP_SA_KEY
   **Name:** `GCP_SA_KEY`
   
   **Value:** Copy the entire contents of `~/gcp-key.json` file
   
   ```bash
   # Display the key to copy
   cat ~/gcp-key.json
   ```

5. Click **Add secret** for each one

## Step 3: Ensure Your Kubernetes Resources Exist

Make sure your namespace and other resources are already deployed:

```bash
# Connect to your cluster
gcloud container clusters get-credentials cluster-jake \
    --zone=asia-southeast1-a \
    --project=mcse-sandbox

# Create namespace if it doesn't exist
kubectl apply -f k8s/namespace.yaml

# Apply other resources (secrets, postgres, services, etc.)
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres-init-configmap.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# If you have nginx ingress
kubectl apply -f k8s/nginx-deployment.yaml
kubectl apply -f k8s/nginx-service.yaml
kubectl apply -f k8s/nginx-ingress.yaml
```

## Step 4: Test the Workflow

### Automatic Trigger (Push to main)
```bash
# Make a change and push to main
git add .
git commit -m "Test CI/CD pipeline"
git push origin main
```

### Manual Trigger
1. Go to your GitHub repository
2. Click on **Actions** tab
3. Select **Build and Deploy to GKE** workflow
4. Click **Run workflow**
5. Select the branch and click **Run workflow**

## Step 5: Monitor the Deployment

1. Go to the **Actions** tab in your GitHub repository
2. Click on the running workflow
3. Watch the progress of each step
4. Check for any errors in the logs

Once complete, verify the deployment:

```bash
# Check if new pods are running
kubectl get pods -n notes-app

# Check deployment status
kubectl rollout status deployment/backend -n notes-app
kubectl rollout status deployment/frontend -n notes-app
kubectl rollout status deployment/nginx-proxy -n notes-app

# Get service IPs
kubectl get services -n notes-app
```

## Workflow Details

The GitHub Actions workflow will:

1. **Trigger** on pushes to `main` branch or manual workflow dispatch
2. **Login** to Docker Hub using your access token
3. **Build** Docker images for backend, frontend, and nginx using `linux/amd64` platform
4. **Tag** images with:
   - Git commit SHA (e.g., `jacoblimzm/notes-backend-amd:abc1234`)
   - `latest` tag (e.g., `jacoblimzm/notes-backend-amd:latest`)
5. **Push** images to Docker Hub at `docker.io/jacoblimzm/`
6. **Deploy** to GKE by updating the deployments with new images
7. **Wait** for rollout to complete
8. **Verify** the deployment by listing services and pods

## Troubleshooting

### Docker Hub Authentication Errors

If you see Docker Hub login errors:

1. Verify your Docker Hub token is correct in GitHub Secrets
2. Ensure the token has **Read & Write** permissions
3. Check if the token is still valid (they can expire)

```bash
# Test Docker Hub login locally
docker login -u jacoblimzm
# Enter your token when prompted
```

### Image Push Errors

If images fail to push to Docker Hub:

1. Verify your repositories exist on Docker Hub
2. Check if your Docker Hub plan has enough storage/bandwidth
3. Ensure the image names match your username: `jacoblimzm/*`

### GKE Permission Errors

If you see GKE deployment permission errors:

```bash
# List current roles
gcloud projects get-iam-policy mcse-sandbox \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:github-actions-sa@mcse-sandbox.iam.gserviceaccount.com"
```

### Cluster Connection Issues

Verify your cluster is accessible:

```bash
gcloud container clusters describe cluster-jake \
    --zone=asia-southeast1-a \
    --project=mcse-sandbox
```

### Namespace Not Found

Create the namespace if it doesn't exist:

```bash
kubectl create namespace notes-app
```

## Security Best Practices

1. **Rotate Service Account Keys** regularly
2. **Use Workload Identity** instead of service account keys for production (more secure but more complex)
3. **Limit permissions** to only what's needed
4. **Review audit logs** regularly
5. **Never commit** the `gcp-key.json` file to your repository

## Clean Up

After successful testing, delete the local key file:

```bash
rm ~/gcp-key.json
```

## Optional: Use Workload Identity (More Secure)

For production, consider using Workload Identity Federation instead of service account keys. This eliminates the need to store long-lived credentials. See [Google's documentation](https://cloud.google.com/blog/products/identity-security/enabling-keyless-authentication-from-github-actions) for details.

## Next Steps

- Set up separate workflows for dev, staging, and production environments
- Add automated testing before deployment
- Implement blue-green or canary deployments
- Add Slack/email notifications for deployment status
- Set up monitoring and alerting with Datadog or Cloud Monitoring

