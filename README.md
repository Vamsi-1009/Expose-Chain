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
   - API Docs: http://localhost:8000/docs (requires `DEBUG=True` in `.env` - disabled by default)
   - Health Check: http://localhost:8000/health

## 🔁 Deployment

Every push to `main` auto-deploys to the production VPS via [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) - GitHub Actions SSHs in, pulls the latest code, reinstalls Python dependencies if `requirements.txt` changed, and restarts the `exposechain` systemd service.

Manual deploy configs (Nginx site config, systemd unit) live in [`deploy/`](deploy) for reference.

---

## 🔒 Security Hardening

ExposeChain scans arbitrary user-supplied domains, so its own attack surface has been hardened against the OWASP Top 10:

- **SSRF protection on every lookup endpoint** - `/api/scan`, `/api/dns`, `/api/whois`, and `/api/ssl` all resolve the target and reject private/loopback/link-local/reserved IPs (including the cloud metadata address) before making any outbound connection.
- **DNS-rebinding safe** - the SSL certificate check connects to the IP it just validated instead of re-resolving the hostname at connect time, closing the TOCTOU gap between validation and connection.
- **TLS-only port allowlist** - `/api/ssl/{domain}` only accepts standard TLS ports, so it can't be used to port-scan internal services.
- **Locked-down production config** - `/docs`, `/redoc`, and `/openapi.json` are disabled unless `DEBUG=True`; rate limiting keys on the real client IP behind the Nginx reverse proxy instead of collapsing to one shared bucket.
- **Deploy-time build gate** - CI verifies the app still imports cleanly before restarting the production service, so a broken push can't take the site down.
- **systemd sandboxing** - the service runs as an unprivileged user with `ProtectSystem`, `ProtectHome`, and `PrivateTmp` restricting filesystem access.

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
