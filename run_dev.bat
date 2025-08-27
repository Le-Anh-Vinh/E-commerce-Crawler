@echo off
echo Starting Crawler API (Dev Mode)...
call venv\Scripts\activate
uvicorn app.crawler_api:app --host 0.0.0.0 --port 8000 --reload
