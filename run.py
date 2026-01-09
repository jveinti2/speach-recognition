import uvicorn
from dotenv import load_dotenv
from app.config import settings

load_dotenv()

if __name__ == "__main__":
    is_dev = settings.ENV == "development"

    reload_dirs = ["app"] if is_dev else None

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=is_dev,
        reload_dirs=reload_dirs,
        log_level="info"
    )
