# 🛡️ ExposeChain (Advanced Edition)
### AI-Powered Attack Surface & Threat Intelligence Platform

## 📌 Current Status: Phase 1 - Step 1 ✅

### Completed Features
- ✅ Project structure setup
- ✅ FastAPI application with health check
- ✅ Input validation (Domain/IPv4/IPv6 detection)
- ✅ Basic API endpoints
- ✅ Configuration management

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run the Application
```bash
python -m src.main
```

The API will be available at:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Root**: http://localhost:8000/

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
