from fastapi import FastAPI  # type: ignore[reportMissingImports]
from fastapi.middleware.cors import CORSMiddleware  # type: ignore[reportMissingImports]

try:
    from backend.routes import router
except ModuleNotFoundError as exc:
    if exc.name != "backend":
        raise
    from routes import router


app = FastAPI(
    title="LegalEase API",
    description="AI-powered legal document generation API",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"]
)


@app.get("/")
def root():

    return {
        "application": "LegalEase",
        "status": "running",
        "version": "1.0.0",
        "health": "/health",
        "documentation": "/docs"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


app.include_router(router)