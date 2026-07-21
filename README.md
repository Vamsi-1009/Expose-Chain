# 🛡️ ExposeChain
### AI-Powered Threat Intelligence & Attack Surface Analysis Platform

🔗 **Live Demo:** [webstocking.com/exposechain](https://webstocking.com/exposechain/)

## ✨ Features

### Core Intelligence Capabilities
- 🔍 **Comprehensive DNS Analysis** - Full DNS record enumeration and analysis
- 📋 **WHOIS Intelligence** - Domain registration and ownership data
- 🌍 **Geolocation Tracking** - IP geolocation and hosting analysis, plotted on an interactive map
- 🔐 **SSL/TLS Certificate Analysis** - Certificate validation and security assessment
- 🤖 **AI Risk Prediction** - Rule-based weighted scoring across domain, SSL, infrastructure, and DNS signals

### Technical Features
- ⚡ **Async/Parallel Scanning** - Fast concurrent API calls
- 🛡️ **SSRF Protection** - Prevents internal network scanning
- 🚦 **Rate Limiting** - Protects API from abuse
- 📊 **Interactive Visualizations** - Leaflet map, animated risk gauges
- 🎨 **Modern UI** - React frontend, light SaaS dashboard theme, no database required (all scans are real-time)

---

## 🏗️ Architecture

Single service, no database:

- **Backend**: FastAPI (Python 3.12) + Uvicorn - see [`src/`](src)
- **Frontend**: React + Vite, built to static files at `frontend/dist/` and served directly by FastAPI - see [`frontend/`](frontend)
- **Process manager**: systemd (`exposechain.service`)
- **Reverse proxy**: Nginx with Let's Encrypt SSL
- **Deployment**: Ubuntu VPS (1 vCPU / 2GB RAM), auto-deployed via GitHub Actions on every push to `main`

## 🚀 Local Development

1. **Backend**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   cp .env.example .env
   uvicorn src.main:app --reload
   ```

2. **Frontend** (only needed if changing the UI - the built output is already committed to `frontend/dist/`)
   ```bash
   cd frontend
   npm install
   npm run dev      # local dev server with hot reload
   npm run build    # produces frontend/dist/, served by FastAPI at "/"
   ```

3. **Access the Platform**
   - Frontend: http://localhost:8000/
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 🔁 Deployment

Every push to `main` auto-deploys to the production VPS via [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) - GitHub Actions SSHs in, pulls the latest code, reinstalls Python dependencies if `requirements.txt` changed, and restarts the `exposechain` systemd service.

Manual deploy configs (Nginx site config, systemd unit) live in [`deploy/`](deploy) for reference.

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
Expose-Chain/
├── src/
│   ├── api/              # API routes and endpoints
│   ├── models/           # Pydantic request/response models
│   ├── services/         # DNS, WHOIS, SSL, geolocation, AI risk scoring
│   ├── utils/            # Rate limiting, logging, validators
│   ├── config/           # Configuration settings
│   └── main.py           # Application entry point
├── frontend/
│   ├── src/              # React components
│   └── dist/             # Built static output (committed, served by FastAPI)
├── deploy/                # Nginx + systemd reference configs
├── .github/workflows/     # Auto-deploy GitHub Actions workflow
├── tests/                 # Test files
├── requirements.txt       # Python dependencies
└── .env.example           # Environment variables template
```

---

## ⚠️ Disclaimer
ExposeChain is built for educational and ethical cybersecurity research. Unauthorized scanning without permission is illegal.

**Version**: 2.0.0
