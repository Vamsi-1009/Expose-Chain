# 🚀 ExposeChain Quick Start Guide

## Choose Your Path

### 🌐 Path 1: Deploy to Production (10 minutes)
**Best for**: Going live immediately with zero infrastructure setup

```bash
1. Create Supabase account → Run migration SQL
2. Click "Deploy to Vercel" button in README
3. Add DATABASE_URL environment variable
4. Deploy! ✅
```

📖 **Full Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
✅ **Checklist**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

---

### 💻 Path 2: Run Locally (2 minutes)
**Best for**: Testing and development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your database URL (or use default PostgreSQL)

# 3. Run the app
uvicorn src.main:app --reload

# 4. Open browser
# → Frontend: http://localhost:8000/
# → API Docs: http://localhost:8000/docs
```

---

## Production Deployment

### Step 1: Supabase (5 minutes)

```bash
1. Go to supabase.com → Create account
2. Create new project: "exposechain"
3. Go to SQL Editor → New Query
4. Copy/paste contents from: migrations/supabase_migration.sql
5. Click "Run"
6. Settings → Database → Copy connection string (URI format)
```

Your connection string looks like:
```
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

### Step 2: Vercel (5 minutes)

```bash
1. Go to vercel.com → Connect GitHub
2. Import your Expose-Chain repository
3. Add Environment Variables:
   - DATABASE_URL = (your Supabase connection string)
   - CORS_ORIGINS = https://your-app.vercel.app
4. Click "Deploy"
5. Wait ~2 minutes
6. Done! 🎉
```

After deployment, update `CORS_ORIGINS` with your actual Vercel URL and redeploy.

---

## Quick Commands

### Development
```bash
# Start server with auto-reload
uvicorn src.main:app --reload

# Run with custom port
uvicorn src.main:app --port 3000

# Start with debug logging
uvicorn src.main:app --reload --log-level debug
```

### Testing
```bash
# Health check
curl http://localhost:8000/health

# Scan a domain
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "example.com", "scan_type": "full"}'

# Get scan history
curl http://localhost:8000/api/history
```

### Git
```bash
# Check status
git status

# Commit changes
git add .
git commit -m "Your message"
git push

# View recent commits
git log --oneline -5
```

---

## Environment Variables

### Required
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### Optional
```bash
CORS_ORIGINS=http://localhost:3000,https://yourapp.com
ENVIRONMENT=production
DEBUG=False
RATE_LIMIT_ENABLED=true
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api` | GET | API documentation |
| `/api/scan` | POST | Full security scan |
| `/api/dns/{domain}` | GET | DNS lookup only |
| `/api/whois/{domain}` | GET | WHOIS lookup only |
| `/api/ssl/{domain}` | GET | SSL certificate check |
| `/api/geo/{ip}` | GET | IP geolocation |
| `/api/history` | GET | Scan history |
| `/api/report/{scan_id}` | GET | Get scan report |

---

## Project Structure

```
Expose-Chain/
├── src/
│   ├── api/
│   │   └── routes.py           # API endpoints
│   ├── config/
│   │   └── settings.py         # Configuration
│   ├── models/
│   │   ├── database.py         # Supabase models
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── dns_service.py      # DNS analysis
│   │   ├── whois_service.py    # WHOIS lookups
│   │   ├── ssl_service.py      # SSL checks
│   │   ├── geolocation_service.py  # Geolocation
│   │   └── ai_service.py       # AI risk analysis
│   ├── utils/
│   │   ├── validators.py       # Input validation
│   │   └── rate_limiter.py     # Rate limiting
│   └── main.py                 # FastAPI app
├── templates/
│   └── index.html              # Frontend UI
├── migrations/
│   └── supabase_migration.sql  # Database schema
├── requirements.txt            # Python dependencies
├── vercel.json                 # Vercel config
└── .env.example                # Environment template
```

---

## Troubleshooting

### Database Connection Failed
```bash
# Check your DATABASE_URL is correct
echo $DATABASE_URL

# Test connection
python -c "from src.models.database import engine; engine.connect()"
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python version (need 3.9+)
python --version
```

### CORS Errors
```bash
# Ensure CORS_ORIGINS includes your frontend URL
# Format: https://yourapp.com (no trailing slash)
# Update in Vercel → Settings → Environment Variables
```

### Port Already in Use
```bash
# Use different port
uvicorn src.main:app --port 8001

# Or kill process using port 8000
# Windows: netstat -ano | findstr :8000
# Linux/Mac: lsof -ti:8000 | xargs kill
```

---

## Key Features

✅ **DNS Analysis** - A, AAAA, MX, NS, TXT, CNAME records
✅ **WHOIS Lookup** - Domain registration info
✅ **SSL/TLS Check** - Certificate validation & security
✅ **Geolocation** - IP location tracking
✅ **AI Risk Scoring** - Multi-factor threat analysis
✅ **Rate Limiting** - API protection
✅ **Caching** - Fast repeated lookups (5-min TTL)
✅ **SSRF Protection** - Prevents internal network scanning
✅ **Scan History** - Persistent storage in Supabase

---

## Performance Tips

1. **Enable Caching**: Already enabled with 5-minute TTL
2. **Use Connection Pooling**: Configured for Supabase
3. **Rate Limiting**: Protects from abuse (10 scans/min)
4. **Parallel Execution**: DNS, WHOIS, SSL run concurrently
5. **Async Routes**: All endpoints use async/await

---

## Security Features

- ✅ SSRF protection (blocks internal IPs)
- ✅ Input validation (domain/IP format)
- ✅ Rate limiting (per-IP)
- ✅ CORS configuration
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ No API keys in code (environment variables)

---

## Next Steps After Deployment

1. ✅ Test all API endpoints
2. ✅ Verify scans saving to Supabase
3. ⬜ Set up custom domain (optional)
4. ⬜ Configure monitoring/alerts
5. ⬜ Add more threat intelligence sources
6. ⬜ Implement user authentication (future)

---

## Useful Links

- **Supabase Dashboard**: https://supabase.com/dashboard
- **Vercel Dashboard**: https://vercel.com/dashboard
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/

---

## Support & Documentation

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview & features |
| `DEPLOYMENT_GUIDE.md` | Detailed deployment instructions |
| `DEPLOYMENT_CHECKLIST.md` | Step-by-step verification |
| `MIGRATION_SUMMARY.md` | Architecture migration details |
| `QUICK_START.md` | This file - quick reference |

---

## Common Tasks

### Add New Environment Variable
```bash
# 1. Add to .env.example
# 2. Add to src/config/settings.py
# 3. Update Vercel → Settings → Environment Variables
# 4. Redeploy
```

### Update Dependencies
```bash
pip install <package>
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

### View Logs
```bash
# Local
# Logs appear in terminal

# Production (Vercel)
# Dashboard → Deployments → View Function Logs
```

---

**You're ready to deploy! 🚀**

Start with: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
