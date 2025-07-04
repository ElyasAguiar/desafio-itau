from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from loki_logger_handler.loki_logger_handler import LokiLoggerHandler
from loki_logger_handler.formatters.loguru_formatter import LoguruFormatter
from loguru import logger

from app.core.lifespan import lifespan
from app.routers import api_routers
from app.core.config import settings


def configure_logs(app: FastAPI) -> None:
    custom_handler = LokiLoggerHandler(
        url=settings.LOKI_URL,
        labels={"application": "Test", "environment": "Develop"},
        label_keys={},
        timeout=10,
        default_formatter=LoguruFormatter(),
    )

    logger.configure(handlers=[{"sink": custom_handler, "serialize": True}])


def configure_routes(app: FastAPI) -> None:
    """Configure API routes."""
    app.include_router(api_routers)


def configure_metrics(app: FastAPI) -> None:
    """Instrument and expose Prometheus metrics."""
    Instrumentator(
        excluded_handlers=[],
    ).instrument(
        app
    ).expose(app, endpoint="/metrics", include_in_schema=True)


def build_app():
    # Criação do app FastAPI
    app = FastAPI(
        title="Desafio Itaú API",
        description="API instrumentada com Prometheus",
        version=settings.RELEASE_VERSION,
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
    configure_logs(app)

    return app


app = build_app()
