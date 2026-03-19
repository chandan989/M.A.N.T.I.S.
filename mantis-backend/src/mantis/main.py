"""
M.A.N.T.I.S. — Entry Point
Starts the FastAPI server with Uvicorn, which in turn starts the agent runtime.
"""

from __future__ import annotations

import uvicorn

from mantis.api.server import create_app
from mantis.config import get_settings


app = create_app()


def main() -> None:
    settings = get_settings()
    print(
        "\n"
        "  ╔══════════════════════════════════════════════════════════════╗\n"
        "  ║                                                            ║\n"
        "  ║   M.A.N.T.I.S.                                            ║\n"
        "  ║   Market Analysis & Network Tactical Integration System    ║\n"
        "  ║                                                            ║\n"
       f"  ║   Server   : http://{settings.server_host}:{settings.server_port}                    ║\n"
       f"  ║   Network  : {settings.hedera_network:<10}                                  ║\n"
       f"  ║   Profile  : {settings.risk_profile:<10}                                  ║\n"
       f"  ║   Interval : {settings.sentry_interval_seconds}s                                       ║\n"
        "  ║                                                            ║\n"
        "  ╚══════════════════════════════════════════════════════════════╝\n"
    )
    uvicorn.run(
        app,
        host=settings.server_host,
        port=settings.server_port,
        log_level=settings.log_level,
    )


if __name__ == "__main__":
    main()
