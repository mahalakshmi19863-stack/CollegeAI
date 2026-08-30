from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import logging
import sys
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .admin.routes import router as admin_router
from .auth.routes import router as auth_router
from .auth.service import auth_service
from .chat.routes import router as chat_router
from .config import settings
from .database.mongodb import db_manager
from .documents.routes import router as documents_router
from .documents.service import document_service
from .feedback.routes import router as feedback_router
from .utils.errors import AppException
from .utils.responses import error_response, success_response

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("college_ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}...")
    await db_manager.connect_to_database()
    stale_before = datetime.now(timezone.utc) - timedelta(
        minutes=settings.PROCESSING_STALE_MINUTES
    )
    recovered = await document_service.recover_stale_processing_documents(stale_before)
    if recovered:
        logger.warning(
            "Marked %s stale document jobs as FAILED for manual reprocessing.",
            recovered,
        )
    if settings.ADMIN_INITIAL_PASSWORD:
        configured = await auth_service.apply_initial_admin_password_if_configured()
        if configured:
            logger.info("Initial admin password reset applied for configured admin email.")
        else:
            logger.warning("Initial admin password reset was not applied because the admin account was not found.")
    yield
    # Shutdown: Close database connection
    logger.info("Shutting down CollegeAI...")
    await db_manager.close_database_connection()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade RAG-based College Information Assistant API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
origins = list(
    set(
        settings.ALLOWED_ORIGINS
        + [settings.FRONTEND_URL]
        + [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://localhost:8001",
            "http://127.0.0.1:8001",
        ]
    )
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.code, exc.message),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = []
    for err in exc.errors():
        loc = " -> ".join([str(l) for l in err.get("loc", [])])
        error_messages.append(f"{loc}: {err.get('msg')}")
    message = "; ".join(error_messages)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response("VALIDATION_ERROR", message),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code = "HTTP_ERROR"
    message = str(exc.detail)
    if isinstance(exc.detail, dict):
        code = exc.detail.get("code", "HTTP_ERROR")
        message = exc.detail.get("message", str(exc.detail))

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(code, message),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled internal server error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            "INTERNAL_SERVER_ERROR",
            "An unexpected error occurred. Please try again later.",
        ),
    )


# Health Endpoint
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint providing status of API, Database, and RAG components."""
    db_status = "connected" if db_manager.is_connected else "offline_buffered"
    return success_response(
        {
            "status": "ok",
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "components": {
                "database": db_status,
                "vector_search": "ready",
                "embeddings": settings.EMBEDDING_PROVIDER,
                "llm": settings.LLM_PROVIDER,
            },
        }
    )


# Mount API Routers
app.include_router(auth_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")
app.include_router(admin_router, prefix="/api")


@app.get("/", tags=["Root"])
async def root():
    return success_response(
        {
            "message": "Welcome to CollegeAI RAG Assistant API",
            "docs": "/docs",
            "health": "/api/health",
        }
    )
