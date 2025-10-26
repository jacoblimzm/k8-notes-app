# Notes App - Kubernetes Deployment

A simple Kubernetes setup for the Notes App with PostgreSQL, Flask backend, and Next.js frontend.

## Quick Start

1. **Build and tag your Docker images:**
   ```bash
   # Build backend image
   docker build -t notes-backend:latest ./backend
   
   # Build frontend image  
   docker build -t notes-frontend:latest ./frontend
   ```

2. **Deploy to Kubernetes:**
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
   
   # Deploy backend
   kubectl apply -f backend-deployment.yaml
   kubectl apply -f backend-service.yaml
   
   # Deploy frontend
   kubectl apply -f frontend-deployment.yaml
   kubectl apply -f frontend-service.yaml
   ```

3. **Access the application:**
   - Frontend: Check the external IP with `kubectl get svc frontend-service -n notes-app`
   - Backend API: `http://backend-service:5000` (internal)

## Notes

- PostgreSQL data is ephemeral (no persistent storage)
- Database table is automatically created on startup via init script
- Database passwords are stored in Kubernetes secrets
- Frontend connects to backend via internal service name
- No ingress controller required - using LoadBalancer for external access

## Security

- Update the passwords in `secrets.yaml` before deploying to production
- Use `echo -n "your-password" | base64` to encode new passwords 