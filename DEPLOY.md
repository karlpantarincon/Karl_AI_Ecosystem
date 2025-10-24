# 🚀 Karl AI Ecosystem - Render.com Deployment Guide

## 📋 Overview

This guide will help you deploy the Karl AI Ecosystem to Render.com for 24/7 cloud operation.

## 🏗️ Architecture on Render

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Service   │    │  Background     │    │   PostgreSQL   │
│   (CoreHub API) │    │   Worker        │    │   Database      │
│                 │    │  (DevAgent)     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Service   │    │   Scheduled     │    │   Persistent    │
│   (Dashboard)  │    │   Tasks          │    │   Storage       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Deploy

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Connect your repository

### Step 2: Deploy Services
1. **CoreHub API** (Web Service)
2. **Dashboard** (Web Service) 
3. **DevAgent** (Background Worker)
4. **PostgreSQL** (Database)

### Step 3: Configure Environment Variables

```bash
# CoreHub API
ENVIRONMENT=production
DATABASE_URL=<from-postgresql-service>
CORS_ORIGINS=https://your-dashboard.onrender.com

# DevAgent Worker
COREHUB_URL=https://your-api.onrender.com
DATABASE_URL=<from-postgresql-service>

# Dashboard
NEXT_PUBLIC_API_URL=https://your-api.onrender.com
```

## 📁 File Structure

```
Karl_AI_Ecosystem/
├── render.yaml              # Render configuration
├── requirements.txt         # Python dependencies
├── Procfile                 # Heroku alternative
├── Dockerfile              # Container configuration
├── .dockerignore           # Docker ignore
├── configs/
│   └── env.production      # Production environment
├── scripts/
│   └── deploy-render.sh    # Deployment script
└── DEPLOY.md               # This guide
```

## 🔧 Services Configuration

### 1. CoreHub API (Web Service)
- **Type**: Web Service
- **Build Command**: `poetry install --no-dev`
- **Start Command**: `poetry run uvicorn corehub.api.main:app --host 0.0.0.0 --port $PORT`
- **Health Check**: `/health`

### 2. Dashboard (Web Service)
- **Type**: Web Service
- **Build Command**: `cd dashboard && npm install`
- **Start Command**: `cd dashboard && npm run build && npm start`
- **Health Check**: `/`

### 3. DevAgent (Background Worker)
- **Type**: Background Worker
- **Build Command**: `poetry install --no-dev`
- **Start Command**: `poetry run python agents/devagent/app/main.py loop --interval 300`

### 4. PostgreSQL Database
- **Type**: PostgreSQL
- **Plan**: Free
- **Region**: Oregon

## 🌐 URLs After Deploy

- **API**: `https://karl-ai-corehub.onrender.com`
- **Dashboard**: `https://karl-ai-dashboard.onrender.com`
- **API Docs**: `https://karl-ai-corehub.onrender.com/docs`
- **Health**: `https://karl-ai-corehub.onrender.com/health`

## 🔍 Monitoring

### Health Checks
- **API**: `/health` endpoint
- **Dashboard**: Root path `/`
- **Worker**: Logs in Render dashboard

### Logs
- View logs in Render dashboard
- Each service has separate log streams
- Real-time log monitoring

## 🚨 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check `requirements.txt`
   - Verify Python version (3.11)
   - Check build logs

2. **Database Connection**
   - Verify `DATABASE_URL` environment variable
   - Check PostgreSQL service status
   - Run database migrations

3. **Worker Not Running**
   - Check worker logs
   - Verify `COREHUB_URL` environment variable
   - Check worker service status

### Debug Commands

```bash
# Check service status
curl https://your-api.onrender.com/health

# Check database connection
curl https://your-api.onrender.com/admin/database

# Check worker logs (in Render dashboard)
```

## 📊 Performance Optimization

### Free Plan Limits
- **750 hours/month** per service
- **512MB RAM** per service
- **PostgreSQL**: 1GB storage

### Optimization Tips
1. **Reduce worker interval** if needed
2. **Optimize database queries**
3. **Use caching** for frequent requests
4. **Monitor resource usage**

## 🔄 Updates and Maintenance

### Deploy Updates
```bash
git add .
git commit -m "Update: Description of changes"
git push origin main
# Render will auto-deploy
```

### Database Migrations
```bash
# Run migrations on Render
poetry run alembic upgrade head
```

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Render Support**: https://render.com/support
- **Project Issues**: GitHub Issues

## 🎯 Success Criteria

✅ **API responding** at `/health`
✅ **Dashboard accessible** at root URL
✅ **Worker processing** tasks (check logs)
✅ **Database connected** and working
✅ **SSL certificates** active
✅ **24/7 operation** confirmed

---

**🎉 Congratulations! Your Karl AI Ecosystem is now running 24/7 in the cloud!**
