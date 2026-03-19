"""
M.A.N.T.I.S. — FastAPI Server
HTTP + WebSocket server for the dashboard.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from mantis.agent.runtime import get_runtime
from mantis.api.routes import router
from mantis.config import get_settings
from mantis.logging import get_agent_logger, register_ws_client, unregister_ws_client

logger = get_agent_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start the agent loop when the server starts; stop on shutdown."""
    runtime = get_runtime()
    logger.info("Server: Starting M.A.N.T.I.S. agent runtime...")
    runtime.start()
    yield
    logger.info("Server: Shutting down agent runtime...")
    runtime.stop()


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="M.A.N.T.I.S. Backend",
        description="Market Analysis & Network Tactical Integration System — Agent API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # REST routes
    app.include_router(router)

    # WebSocket for real-time log streaming
    @app.websocket("/ws/logs")
    async def websocket_logs(ws: WebSocket):
        await ws.accept()
        register_ws_client(ws)
        logger.info("WebSocket: Dashboard client connected")
        try:
            while True:
                # Keep the connection alive; we send data via broadcast_log
                await ws.receive_text()
        except WebSocketDisconnect:
            logger.info("WebSocket: Dashboard client disconnected")
        finally:
            unregister_ws_client(ws)

    return app
