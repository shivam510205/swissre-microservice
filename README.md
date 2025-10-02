# SwissRe Medical Summarization Microservice

Production-ready SwissRe microservice for medical data summarization with Streamlit dashboard.

## 🏗️ Architecture
- **SwissRe API Service**: FastAPI microservice calling SwissRe summarization API
- **Streamlit Dashboard**: Interactive UI for viewing summarization results
- **Medical Data Processing**: JSON to text conversion and clinical summarization

## 📁 Structure
```
swissre-microservice/
├── src/                    # SwissRe backend code
├── ui/                     # Streamlit frontend dashboard
├── docker/                 # Production Dockerfiles
├── helm/                   # Kubernetes Helm chart
├── build-images.sh         # Build and push Docker images
├── deploy.sh              # Deploy to Kubernetes
└── DEPLOYMENT-GUIDE.md    # Complete deployment instructions
```

## 🚀 Quick Deploy

### Prerequisites
- ✅ IAM Role: `SFGAppSwissReServiceRole`
- ✅ EKS Cluster with OIDC provider
- ✅ SwissRe API Token in AWS Secrets Manager
- ✅ JFrog Artifactory access

### Deploy Commands
```bash
# 1. Login to container registry
docker login securian-docker-all.jfrog.io

# 2. Build and push images
./build-images.sh

# 3. Deploy to Kubernetes
./deploy.sh dev
```

### Access Applications
```bash
# Streamlit Dashboard
kubectl port-forward -n is-mlops svc/swissre-dev-frontend 8501:8501

# Backend API
kubectl port-forward -n is-mlops svc/swissre-dev-backend 8080:8080
```

## 📊 Features
- **Medical Data Processing**: JSON to plain text conversion
- **SwissRe API Integration**: Clinical summarization via SwissRe API
- **Interactive Dashboard**: View and manage summarization results
- **Secure Token Management**: SwissRe API token via AWS Secrets Manager
- **Production Ready**: Security, monitoring, and scaling built-in

## 🔗 URLs
- **Streamlit UI**: http://localhost:8501
- **Backend API**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health
