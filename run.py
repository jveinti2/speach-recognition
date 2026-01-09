import uvicorn
import os

if __name__ == "__main__":
    is_dev = os.getenv("ENV", "production") == "development"

    reload_dirs = ["app"] if is_dev else None

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=is_dev,
        reload_dirs=reload_dirs,
        log_level="info"
    )
