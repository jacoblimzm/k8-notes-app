# Quick Start - CI/CD Pipeline Setup

## ✅ What's Already Done

- [x] Docker images pushed to Docker Hub
- [x] Kubernetes deployments updated with Docker Hub images
- [x] GitHub Actions workflow configured
- [x] Manual deployment verified

## 🚀 Next Steps (Takes ~5 minutes)

### 1. Create Docker Hub Access Token

Go to [Docker Hub Security Settings](https://hub.docker.com/settings/security):
1. Click **New Access Token**
2. Name: `github-actions-token`
3. Permissions: **Read & Write**
4. Click **Generate** and **copy the token**

### 2. Create GCP Service Account

Run these commands in your terminal:

```bash
export PROJECT_ID=mcse-sandbox

# Create service account
gcloud iam service-accounts create github-actions-sa \
    --display-name="GitHub Actions Service Account" \
    --project=$PROJECT_ID

# Grant deployment permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/container.developer"

# Create key
gcloud iam service-accounts keys create ~/gcp-key.json \
    --iam-account=github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com

# Display key to copy
cat ~/gcp-key.json
```

### 3. Add GitHub Secrets

Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these two secrets:

**Secret 1:**
- Name: `DOCKERHUB_TOKEN`
- Value: Paste the Docker Hub token from Step 1

**Secret 2:**
- Name: `GCP_SA_KEY`
- Value: Paste the entire JSON content from `cat ~/gcp-key.json`

### 4. Test the Pipeline

```bash
# Push to GitHub to trigger the pipeline
git add .
git commit -m "Enable CI/CD pipeline"
git push origin main
```

Or manually trigger:
1. Go to GitHub repo → **Actions** tab
2. Click **Build and Deploy to GKE**
3. Click **Run workflow** → **Run workflow**

### 5. Monitor

Watch the deployment in real-time:
- GitHub: **Actions** tab → Click on the running workflow
- Terminal: `kubectl get pods -n notes-app -w`

## 🎯 What Happens Automatically

Every time you push to `main`:
1. ✅ Builds backend, frontend, and nginx images
2. ✅ Pushes images to Docker Hub (tagged with commit SHA + latest)
3. ✅ Updates GKE deployments with new images
4. ✅ Waits for rollout to complete
5. ✅ Verifies all pods are running

## 📊 Check Deployment Status

```bash
# View all resources
kubectl get all -n notes-app

# Check specific deployments
kubectl rollout status deployment/backend -n notes-app
kubectl rollout status deployment/frontend -n notes-app
kubectl rollout status deployment/nginx-proxy -n notes-app

# View logs
kubectl logs -f deployment/backend -n notes-app
kubectl logs -f deployment/frontend -n notes-app
```

## 🔗 Current Images

Your deployments are using:
- Backend: `jacoblimzm/notes-backend-amd:v1.0.1`
- Frontend: `jacoblimzm/notes-frontend-amd:v1.0`
- Nginx: `jacoblimzm/nginx-proxy-amd:v0.8`

After CI/CD runs, they will update to use commit SHA tags.

## 🆘 Need Help?

See the detailed guide: [CICD-SETUP.md](./CICD-SETUP.md)

## 🧹 Clean Up (Optional)

After successful setup, delete the local service account key:

```bash
rm ~/gcp-key.json
```

**Never commit this file to git!** (It's already in `.gitignore`)

