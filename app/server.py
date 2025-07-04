from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app.core.lifespan import lifespan
from app.routers import api_routers
from app.core.config import settings


def configure_routes(app: FastAPI) -> None:
    """Configure API routes."""
    app.include_router(api_routers)


def configure_metrics(app: FastAPI) -> None:
    """Instrument and expose Prometheus metrics."""
    Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        excluded_handlers=[],
    ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=True)


def build_app():
    # Criação do app FastAPI
    app = FastAPI(
        title="Desafio Itaú API",
        description="API instrumentada com Prometheus",
        version=settings.RELEASE_VERSION,
        docs_url=None if settings.ENVIRONMENT == "production" else "/docs",
        redoc_url=None if settings.ENVIRONMENT == "production" else "/redoc",
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        ],
        lifespan=lifespan,
    )

    configure_routes(app)
    configure_metrics(app)

    return app


app = build_app()
