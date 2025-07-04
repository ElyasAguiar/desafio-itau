import uvicorn
from loguru import logger

from app.core.config import settings

def calculate_worker_count() -> int:
    """Calculate optimal worker count: 2 * CPU cores + 1"""
    return 1

def main():
    worker_count = calculate_worker_count()
    logger.info(f"🚀 Starting application with {worker_count} worker(s)")
    uvicorn.run(
        app="app.server:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=worker_count,
        reload=settings.ENVIRONMENT == "development",
    )


if __name__ == "__main__":
    main()
