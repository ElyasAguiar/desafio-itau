"""Application lifecycle management."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from app.services.db_service import MongoDBService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    logger.info("🚀 Application starting up...")

    # Inicializa e conecta ao MongoDB
    db_service = MongoDBService()
    connected = await db_service.connect()
    if connected:
        logger.info("✅ MongoDB conectado com sucesso!")
    else:
        logger.error("❌ Falha ao conectar ao MongoDB")

    # Armazena o serviço no estado da aplicação para uso posterior
    app.state.db_service = db_service

    yield

    # Desconecta do MongoDB
    if hasattr(app.state, "db_service"):
        await app.state.db_service.disconnect()

    logger.info("👋 Application shutting down...")
