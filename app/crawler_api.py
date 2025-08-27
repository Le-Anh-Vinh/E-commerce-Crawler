from fastapi import FastAPI, Header, HTTPException
from .crawler_logic import update_and_crawl     # Actual logic in a module
from .config import Config
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

scheduler = BackgroundScheduler()

# Run crawl every 6 hours
scheduler.add_job(update_and_crawl, "interval", hours=6)

@app.on_event("startup")
def startup_event():
    scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

@app.get("/crawl")
def trigger_crawl(x_api_key: str = Header(None)):
    # # Check API key
    # if x_api_key != Config.API_KEY:
    #     raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        result = update_and_crawl()
        return {"status": "success", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}
