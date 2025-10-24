# Karl AI Ecosystem - Heroku/Procfile Configuration
# Alternative deployment option

# CoreHub API
web: uvicorn corehub.api.main:app --host 0.0.0.0 --port $PORT

# DevAgent Worker (requires Heroku Worker dyno)
worker: python agents/devagent/app/main.py loop --interval 300

# Dashboard (separate app)
# dashboard: cd dashboard && npm run build && npm start
