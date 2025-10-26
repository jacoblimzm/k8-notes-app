# CI/CD Setup Guide for GKE Deployment

This guide will help you set up automated deployments to GKE via GitHub Actions.

## Prerequisites

- Google Cloud Project: `mcse-sandbox`
- GKE Cluster: `cluster-jake` in `asia-southeast1-a`
- GitHub repository for this project
- `gcloud` CLI installed locally

## Step 1: Create a Google Cloud Service Account

This service account will be used by GitHub Actions to deploy to your GKE cluster.

```bash
# Set your project ID
export PROJECT_ID=mcse-sandbox

# Create a service account
gcloud iam service-accounts create github-actions-sa \
    --display-name="GitHub Actions Service Account" \
    --project=$PROJECT_ID

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/container.developer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Create and download the key
gcloud iam service-accounts keys create ~/gcp-key.json \
    --iam-account=github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com
```

## Step 2: Add GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secret:

   **Name:** `GCP_SA_KEY`
   
   **Value:** Copy the entire contents of `~/gcp-key.json` file
   
   ```bash
   # Display the key to copy
   cat ~/gcp-key.json
   ```

5. Click **Add secret**

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

# Get service IPs
kubectl get services -n notes-app
```

## Workflow Details

The GitHub Actions workflow will:

1. **Trigger** on pushes to `main` branch or manual workflow dispatch
2. **Build** Docker images for both backend and frontend using `linux/amd64` platform
3. **Tag** images with:
   - Git commit SHA (e.g., `v0.1-abc1234`)
   - `latest` tag
4. **Push** images to your Artifact Registry at `asia-southeast1-docker.pkg.dev/mcse-sandbox/jake-reg/`
5. **Deploy** to GKE by updating the deployments with new images
6. **Wait** for rollout to complete
7. **Verify** the deployment by listing services and pods

## Troubleshooting

### Permission Denied Errors

If you see permission errors, ensure the service account has the correct roles:

```bash
# List current roles
gcloud projects get-iam-policy mcse-sandbox \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:github-actions-sa@mcse-sandbox.iam.gserviceaccount.com"
```

### Image Pull Errors

Make sure the service account can write to Artifact Registry:

```bash
gcloud artifacts repositories add-iam-policy-binding jake-reg \
    --location=asia-southeast1 \
    --member="serviceAccount:github-actions-sa@mcse-sandbox.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"
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

