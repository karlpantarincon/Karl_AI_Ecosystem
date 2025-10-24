#!/bin/bash
# Karl AI Ecosystem - Render.com Deployment Script

echo "🚀 Deploying Karl AI Ecosystem to Render.com..."

# Check if we're in the right directory
if [ ! -f "render.yaml" ]; then
    echo "❌ Error: render.yaml not found. Run this script from the project root."
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: Karl AI Ecosystem"
fi

# Add all files to git
echo "📝 Adding files to git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Deploy: Configure for Render.com

- Add render.yaml configuration
- Add production environment config
- Add Docker support
- Add requirements.txt
- Optimize for cloud deployment"

# Check if remote exists
if ! git remote | grep -q "render"; then
    echo "🔗 Add your Render.com Git remote:"
    echo "git remote add render https://git.render.com/your-username/karl-ai-ecosystem.git"
    echo ""
    echo "Then run: git push render main"
else
    echo "🚀 Pushing to Render..."
    git push render main
fi

echo "✅ Deployment configuration complete!"
echo ""
echo "📋 Next steps:"
echo "1. Create account at https://render.com"
echo "2. Connect your GitHub repository"
echo "3. Deploy using render.yaml"
echo "4. Configure environment variables"
echo "5. Test your services"
