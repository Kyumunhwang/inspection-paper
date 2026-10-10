"""Server runner script for Inspection Paper."""

import os
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    # Google Cloud Run automatically injects the PORT environment variable
    port_env = os.environ.get("PORT")
    port = int(port_env) if port_env else settings.PORT
    host = os.environ.get("HOST", settings.HOST)
    is_dev = settings.APP_ENV.lower() == "development"

    print(f"Starting {settings.APP_NAME} server on http://{host}:{port} (env: {settings.APP_ENV})")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=is_dev,
    )
