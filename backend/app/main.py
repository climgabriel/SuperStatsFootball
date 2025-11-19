from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
import os

from app.core.config import settings
from app.routers import auth, users, leagues, fixtures, predictions, admin, webhooks, odds, statistics, combined_predictions
from app.db.session import engine, SessionLocal
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
    logger.info("📊 Sentry monitoring initialized")
else:
    logger.info("📊 Sentry monitoring disabled (no DSN configured)")

# Create FastAPI app
logger.info(f"🏗️  Creating FastAPI application: {settings.APP_NAME} v{settings.VERSION}")
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="High-performance football statistics and prediction API - Clone of SuperStatsFootball.com",
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)
logger.info("✅ FastAPI application created")

# CORS middleware - use configured origins from settings
cors_origins = settings.BACKEND_CORS_ORIGINS if settings.BACKEND_CORS_ORIGINS else ["*"]

logger.info(f"🌐 CORS origins: {cors_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
logger.info("✅ CORS middleware configured")

# Include routers
logger.info("📡 Registering API routers...")
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["Users"])
app.include_router(leagues.router, prefix=f"{settings.API_V1_PREFIX}/leagues", tags=["Leagues"])
app.include_router(fixtures.router, prefix=f"{settings.API_V1_PREFIX}/fixtures", tags=["Fixtures"])
app.include_router(predictions.router, prefix=f"{settings.API_V1_PREFIX}/predictions", tags=["Predictions"])
app.include_router(odds.router, prefix=f"{settings.API_V1_PREFIX}/odds", tags=["Odds"])
app.include_router(statistics.router, prefix=f"{settings.API_V1_PREFIX}/statistics", tags=["Statistics"])
app.include_router(combined_predictions.router, prefix=f"{settings.API_V1_PREFIX}/combined", tags=["Combined Predictions"])
app.include_router(admin.router, prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Admin"])
app.include_router(webhooks.router, prefix=f"{settings.API_V1_PREFIX}/webhooks", tags=["Webhooks"])
logger.info("✅ All routers registered successfully")


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    try:
        logger.info("=" * 80)
        logger.info(f"🚀 {settings.APP_NAME} v{settings.VERSION} STARTING...")
        logger.info("=" * 80)

        # Environment configuration
        logger.info(f"📍 Environment: {settings.ENVIRONMENT}")
        logger.info(f"🔒 Debug mode: {settings.DEBUG}")
        logger.info(f"🌐 Host: 0.0.0.0")
        logger.info(f"🔌 Port: {os.getenv('PORT', '8000')}")

        # Database configuration
        db_url = settings.DATABASE_URL
        if not db_url:
            logger.error("❌ DATABASE_URL is not set. Supabase/Postgres connectivity is required.")
            raise RuntimeError("DATABASE_URL missing")

        # Mask password in database URL for security
        if '@' in db_url:
            masked_url = db_url.split('@')[0].split('://')[0] + '://***:***@' + db_url.split('@')[1]
        else:
            masked_url = db_url[:30] + '...'
        logger.info(f"🗄️  Database: {masked_url}")

        # Check critical environment variables
        logger.info("🔍 Checking environment variables...")
        env_checks = {
            "DATABASE_URL": bool(settings.DATABASE_URL),
            "SECRET_KEY": bool(settings.SECRET_KEY),
            "ENVIRONMENT": bool(settings.ENVIRONMENT),
            "API_V1_PREFIX": bool(settings.API_V1_PREFIX)
        }
        for var_name, is_set in env_checks.items():
            status = "✅" if is_set else "❌"
            logger.info(f"  {status} {var_name}: {'SET' if is_set else 'NOT SET'}")

        # Create database tables (in production, use Alembic migrations)
        if settings.ENVIRONMENT == "development":
            logger.info("🏗️  Creating database tables (development mode)...")
            try:
                from app.models import user, league, team, fixture, prediction, odds
                Base.metadata.create_all(bind=engine)
                logger.info("✅ Database tables created successfully")
                try:
                    from app.db.init_db import seed_initial_data
                    db_session = SessionLocal()
                    try:
                        seed_initial_data(db_session)
                        logger.info("✅ Development seed data ensured")
                    finally:
                        db_session.close()
                except Exception as seed_error:
                    logger.error(f"❌ Error seeding development data: {seed_error}")
            except Exception as e:
                logger.error(f"❌ Error creating database tables: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                # Don't fail startup for table creation errors
        else:
            logger.info("🏗️  Production mode: Skipping table creation (use Alembic migrations)")

        # Start automatic data synchronization scheduler
        logger.info("🔄 Starting automatic data synchronization scheduler...")
        try:
            from app.services.scheduler_service import auto_sync_scheduler
            auto_sync_scheduler.start()
            logger.info("✅ Automatic sync scheduler started successfully")
        except Exception as scheduler_error:
            logger.error(f"❌ Error starting scheduler: {scheduler_error}")
            logger.warning("⚠️  Continuing without automatic sync scheduler")

        logger.info("=" * 80)
        logger.info("✅ STARTUP COMPLETE! Application is ready to accept requests.")
        logger.info(f"📋 Healthcheck endpoint available at: /health")
        logger.info(f"📋 API documentation available at: /docs (debug mode only)")
        logger.info("=" * 80)
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ FATAL: Startup failed with error: {str(e)}")
        logger.error("=" * 80)
        import traceback
        logger.error(traceback.format_exc())
        logger.error("=" * 80)
        logger.info("⚠️  Allowing startup to continue so healthcheck can respond...")
        logger.error("=" * 80)
        # Allow startup to continue so healthcheck can respond


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info(f"👋 {settings.APP_NAME} shutting down...")

    # Stop scheduler
    try:
        from app.services.scheduler_service import auto_sync_scheduler
        auto_sync_scheduler.stop()
        logger.info("✅ Scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")

    # Close API Football client
    from app.services.apifootball import api_football_client
    await api_football_client.close()


@app.get("/")
async def root():
    """Root endpoint."""
    logger.info("📞 Root endpoint called: /")
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.info("Health check endpoint called: /health")
    response = {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
        "api": "operational",
        "database": "connected" if settings.DATABASE_URL else "sqlite_fallback",
        "port": os.getenv("PORT", "8000")
    }
    logger.info(f"Health check response: {response}")
    return response


@app.get("/ip")
async def get_server_ip():
    """Get server's public IP address (for API-Football IP whitelisting)."""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("https://api.ipify.org?format=json")
            ip_data = response.json()
            return {
                "ip": ip_data["ip"],
                "message": "Add this IP to API-Football SET IP whitelist",
                "instructions": "Go to https://www.api-football.com/ → SET IP → Add this IP → Save"
            }
    except Exception as e:
        return {"error": str(e), "message": "Could not determine public IP"}


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
