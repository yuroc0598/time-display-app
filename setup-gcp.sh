#!/bin/bash
set -e

# Configuration
PROJECT_ID="archie-465300"
ZONE="us-west1-a"
REGION="us-west1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Setting up GCP infrastructure for project: $PROJECT_ID${NC}"

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ Error: You are not authenticated with gcloud. Please run 'gcloud auth login' first.${NC}"
    exit 1
fi

# Set the project
echo -e "${YELLOW}📋 Setting project to $PROJECT_ID${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "📡 Enabling required APIs..."
gcloud services enable container.googleapis.com \
  artifactregistry.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  compute.googleapis.com

# Create Artifact Registry
echo "📦 Creating Artifact Registry..."
gcloud artifacts repositories create archie \
  --repository-format=docker \
  --location=$REGION \
  --description="Docker repository for archie"

# Create static IPs
echo "🌐 Creating static IP addresses..."
gcloud compute addresses create archie-dev-ip --global || echo "Dev IP may already exist"
gcloud compute addresses create archie-staging-ip --global || echo "Staging IP may already exist"
gcloud compute addresses create archie-prod-ip --global || echo "Production IP may already exist"

# Create GKE clusters
echo "☸️  Creating GKE dev cluster..."
gcloud container clusters create archie-dev \
  --zone=$ZONE \
  --num-nodes=2 \
  --machine-type=e2-medium \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=5 \
  --enable-autorepair \
  --enable-autoupgrade \
  --disk-size=20GB

echo "☸️  Creating GKE staging cluster..."
gcloud container clusters create archie-staging \
  --zone=$ZONE \
  --num-nodes=2 \
  --machine-type=e2-medium \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=5 \
  --enable-autorepair \
  --enable-autoupgrade \
  --disk-size=20GB

echo "☸️  Creating GKE production cluster..."
gcloud container clusters create archie-production \
  --zone=$ZONE \
  --num-nodes=3 \
  --machine-type=e2-standard-2 \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=10 \
  --enable-autorepair \
  --enable-autoupgrade \
  --disk-size=30GB \
  --enable-network-policy \
  --enable-autorepair \
  --enable-autoupgrade

# Create service account for GitHub Actions
echo "🔐 Creating service account for GitHub Actions..."
gcloud iam service-accounts create github-actions \
  --description="Service account for GitHub Actions" \
  --display-name="GitHub Actions"

# Grant necessary permissions
echo "🔐 Granting permissions to service account..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/container.developer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/container.admin"

# Create SSL certificates (managed certificates)
echo "🔐 Creating SSL certificates..."
gcloud compute ssl-certificates create archie-dev-ssl-cert \
  --domains=dev.archie.example.com \
  --global || echo "Dev SSL certificate may already exist"

gcloud compute ssl-certificates create archie-staging-ssl-cert \
  --domains=staging.archie.example.com \
  --global || echo "Staging SSL certificate may already exist"

gcloud compute ssl-certificates create archie-prod-ssl-cert \
  --domains=archie.example.com \
  --global || echo "Production SSL certificate may already exist"

# Create and download service account key
echo "🔑 Creating service account key..."
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions@$PROJECT_ID.iam.gserviceaccount.com

echo "✅ GCP infrastructure setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Add these secrets to your GitHub repository:"
echo "   - GCP_SA_KEY: <contents of github-actions-key.json>"
echo ""
echo "2. Update domain names in k8s/*/ingress-patch.yaml files to match your actual domains"
echo ""
echo "3. Get cluster credentials:"
echo "   gcloud container clusters get-credentials archie-dev --zone=$ZONE"
echo "   gcloud container clusters get-credentials archie-staging --zone=$ZONE"
echo "   gcloud container clusters get-credentials archie-production --zone=$ZONE"
echo ""
echo "4. Deploy namespaces and monitoring:"
echo "   kubectl apply -f k8s/setup-namespaces.yaml"
echo "   kubectl apply -f k8s/monitoring/"
echo ""
echo "5. Configure DNS for your domains to point to the static IPs:"
echo "   $(gcloud compute addresses describe archie-dev-ip --global --format='value(address)') -> dev.archie.example.com"
echo "   $(gcloud compute addresses describe archie-staging-ip --global --format='value(address)') -> staging.archie.example.com"
echo "   $(gcloud compute addresses describe archie-prod-ip --global --format='value(address)') -> archie.example.com"
echo ""
echo "6. Set up GitHub environments:"
echo "   - Create 'development', 'staging', and 'production' environments in GitHub"
echo "   - Add approval requirements for production environment"
echo ""
echo "7. Infrastructure created:"
echo "   - GKE clusters: archie-dev, archie-staging, archie-production"
echo "   - Static IPs: archie-dev-ip, archie-staging-ip, archie-prod-ip"
echo "   - SSL certificates: archie-dev-ssl-cert, archie-staging-ssl-cert, archie-prod-ssl-cert"
echo "   - Artifact registry: archie"
echo "   - Service account: github-actions"