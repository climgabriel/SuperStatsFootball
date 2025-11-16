from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings
from app.routers import auth, users, leagues, fixtures, predictions, admin, webhooks, odds, statistics
from app.db.session import engine
from app.db.base import Base
from app.utils.logger import logger

# Initialize Sentry (if configured)
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration()
        ],
        traces_sample_rate=1.0 if settings.ENVIRONMENT == "development" else 0.1,
        environment=settings.ENVIRONMENT
    )

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="High-performance football statistics and prediction API - Clone of SuperStatsFootball.com",
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["Users"])
app.include_router(leagues.router, prefix=f"{settings.API_V1_PREFIX}/leagues", tags=["Leagues"])
app.include_router(fixtures.router, prefix=f"{settings.API_V1_PREFIX}/fixtures", tags=["Fixtures"])
app.include_router(predictions.router, prefix=f"{settings.API_V1_PREFIX}/predictions", tags=["Predictions"])
app.include_router(odds.router, prefix=f"{settings.API_V1_PREFIX}/odds", tags=["Odds"])
app.include_router(statistics.router, prefix=f"{settings.API_V1_PREFIX}/statistics", tags=["Statistics"])
app.include_router(admin.router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Admin"])
app.include_router(webhooks.router, prefix=f"{settings.API_V1_PREFIX}/webhooks", tags=["Webhooks"])


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(f"🚀 {settings.APP_NAME} v{settings.VERSION} starting...")
    logger.info(f"📍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔒 Debug mode: {settings.DEBUG}")

    # Create database tables (in production, use Alembic migrations)
    if settings.ENVIRONMENT == "development":
        try:
            from app.models import user, league, team, fixture, prediction, odds
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created")
        except Exception as e:
            logger.error(f"❌ Error creating database tables: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info(f"👋 {settings.APP_NAME} shutting down...")

    # Close API Football client
    from app.services.apifootball import api_football_client
    await api_football_client.close()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
        "api": "operational"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")

    if settings.DEBUG:
        raise exc

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )
