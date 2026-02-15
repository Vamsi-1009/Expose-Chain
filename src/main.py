"""
ExposeChain - Main Application
AI-Powered Attack Surface & Threat Intelligence Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from src.api import router
from src.config import settings
from src.utils.logging_config import setup_logging
from src.utils.rate_limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Setup logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-Powered Attack Surface & Threat Intelligence Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Register rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Mount static files if directory exists
static_path = Path("static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")


# Include API routes
app.include_router(router)


# Serve the frontend
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_frontend():
    """Serve the web interface"""
    template_path = Path("templates/index.html")
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>ExposeChain API</h1><p>Frontend template not found. Visit <a href='/docs'>/docs</a> for API documentation.</p>"


if __name__ == "__main__":
    import uvicorn

    print(f"""
    ==========================================================
    |                                                          |
    |              ExposeChain v{settings.VERSION}                       |
    |                                                          |
    |     AI-Powered Attack Surface & Threat Intelligence      |
    |                                                          |
    ==========================================================

    Starting server...
    Web Interface: http://{settings.HOST}:{settings.PORT}/
    API Docs:      http://{settings.HOST}:{settings.PORT}/docs
    Health Check:  http://{settings.HOST}:{settings.PORT}/health
    """)

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
