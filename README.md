# 🛡️ ExposeChain
### AI-Powered Threat Intelligence & Attack Surface Analysis Platform

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Vamsi-1009/Expose-Chain)

## ✨ Features

### Core Intelligence Capabilities
- 🔍 **Comprehensive DNS Analysis** - Full DNS record enumeration and analysis
- 📋 **WHOIS Intelligence** - Domain registration and ownership data
- 🌍 **Geolocation Tracking** - IP geolocation and hosting analysis
- 🔐 **SSL/TLS Certificate Analysis** - Certificate validation and security assessment
- 🤖 **AI Risk Prediction** - Multi-factor threat scoring and recommendations

### Technical Features
- ⚡ **Async/Parallel Scanning** - Fast concurrent API calls
- 🛡️ **SSRF Protection** - Prevents internal network scanning
- 🚦 **Rate Limiting** - Protects API from abuse
- 💾 **Supabase Database** - Persistent scan history with PostgreSQL
- 📊 **Interactive Visualizations** - Maps, charts, and animations
- 🎨 **Modern UI** - Responsive design with 25+ animations

---

## 🚀 Deployment Options

### Option 1: Deploy to Vercel + Supabase (Recommended)

**Perfect for production deployments with zero DevOps**

1. **Setup Supabase Database** (5 minutes)
   - Create account at [supabase.com](https://supabase.com)
   - Create new project
   - Run migration from `migrations/supabase_migration.sql`
   - Copy database connection string

2. **Deploy to Vercel** (5 minutes)
   - Click the "Deploy with Vercel" button above
   - Connect your GitHub account
   - Set environment variables:
     - `DATABASE_URL`: Your Supabase connection string
     - `CORS_ORIGINS`: Your Vercel deployment URL
   - Deploy!

3. **Detailed Instructions**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
4. **Checklist**: Use [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

### Option 2: Local Development

**For testing and development**

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run the Application**
   ```bash
   uvicorn src.main:app --reload
   ```

4. **Access the Platform**
   - Frontend: http://localhost:8000/
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

---

## 📡 API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Scan Target
```bash
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{
    "target": "example.com",
    "scan_type": "quick"
  }'
```

### Supported Inputs
- ✅ Domain names: `example.com`, `subdomain.example.com`
- ✅ IPv4 addresses: `8.8.8.8`
- ✅ IPv6 addresses: `2001:4860:4860::8888`

---

## 📂 Project Structure
```
exposechain/
├── src/
│   ├── api/              # API routes and endpoints
│   ├── models/           # Pydantic models
│   ├── services/         # Business logic (future)
│   ├── utils/            # Utility functions
│   ├── config/           # Configuration settings
│   └── main.py           # Application entry point
├── tests/                # Test files
├── static/               # Static files (future)
├── templates/            # HTML templates (future)
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variables template
```

---

## ⚠️ Disclaimer
ExposeChain is built for educational and ethical cybersecurity research. Unauthorized scanning without permission is illegal.

**Author**: Vamsi Krishna
**Version**: 1.0.0
# Deploy trigger
