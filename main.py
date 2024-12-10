import logging
import asyncio
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from app.handler.utils.log import logger
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from contextlib import asynccontextmanager

from app.handler.jobs import stop_scheduler, start_scheduler
from app.handler.routers import sub
from fastapi_responses import custom_openapi
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.handler.utils.config import (
    UVICORN_HOST,
    UVICORN_PORT,
    UVICORN_UDS,
    UVICORN_SSL_CERTFILE,
    UVICORN_SSL_KEYFILE,
    DOCS,
)

__version__ = "0.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events."""
    await start_scheduler()
    logger.info("Application started successfully.")
    yield  # App will be running during this period
    await stop_scheduler()
    logger.info("Application shut down successfully.")


def create_app() -> FastAPI:
    """Create and configure FastAPI application instance."""
    app = FastAPI(
        title="Migration",
        description="API to proxy sub requests between users and backend system",
        version=__version__,
        docs_url="/docs" if DOCS else None,
        redoc_url="/redoc" if DOCS else None,
        lifespan=lifespan,  # Set the lifespan context manager
    )

    app.openapi = custom_openapi(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request, exc):
        logger.error(f"An HTTP error!: {repr(exc)}")
        return await http_exception_handler(request, exc)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        logger.error(f"The client sent invalid data!: {exc}")
        return await request_validation_exception_handler(request, exc)

    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name

    # Include the router
    app.include_router(sub.router)

    return app


async def main():
    """Main function to run the application."""
    app = create_app()

    config = uvicorn.Config(
        app,
        host=UVICORN_HOST,
        port=UVICORN_PORT,
        uds=UVICORN_UDS,
        ssl_certfile=UVICORN_SSL_CERTFILE,
        ssl_keyfile=UVICORN_SSL_KEYFILE,
        workers=1,
        log_level=logging.INFO,
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    file_path = Path("exceptions.json")

    if not file_path.exists():
        logger.error(f"Marzban exceptions data file not found at: {file_path}")
    else:
        try:
            asyncio.run(main())
        except FileNotFoundError as e:
            logger.error(f"FileNotFoundError: {e}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
