"""
ExposeChain - Main Application
AI-Powered Attack Surface & Threat Intelligence Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import router
from src.config import settings

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-Powered Attack Surface & Threat Intelligence Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║               🛡️  ExposeChain v{settings.VERSION}                  ║
    ║                                                          ║
    ║     AI-Powered Attack Surface & Threat Intelligence      ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    
    🚀 Starting server...
    📍 API Docs: http://{settings.HOST}:{settings.PORT}/docs
    🔗 Health Check: http://{settings.HOST}:{settings.PORT}/health
    """)
    
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
