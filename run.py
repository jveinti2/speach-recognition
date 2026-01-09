import uvicorn
import sys

if __name__ == "__main__":
    reload = sys.platform != "win32"

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=reload,
        log_level="info"
    )
