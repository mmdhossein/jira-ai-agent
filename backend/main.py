# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.database import engine, Base
from app.services.jira_client import JiraClient

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the application."""
    # Startup: Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")
    
    # Test Jira connection
    jira_client = JiraClient()
    if await jira_client.test_connection():
        print("✓ Jira connection successful")
    else:
        print("⚠ Jira connection failed - check credentials")
    
    yield
    
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="AI Project Management Agent",
    description="Backend API for AI-powered Jira analytics and management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "dummy_mode": settings.dummy_mode
    }


from app.api import auth, chat, jira, reports, sessions

app.include_router(auth.router, prefix='/api')
app.include_router(chat.router, prefix='/api')
app.include_router(jira.router, prefix='/api')
app.include_router(reports.router, prefix='/api')
app.include_router(sessions.router, prefix='/api')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
