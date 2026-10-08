@echo off

start cmd /k "cd handler && echo Starting Handler Service && venv\Scripts\activate && fastapi dev --port 8000"
start cmd /k "cd retriever && echo Starting Retriever Service && venv\Scripts\activate && fastapi dev --port 8001"
start cmd /k "cd generator && echo Starting Generator Service && venv\Scripts\activate && celery -A worker worker --loglevel=info --pool=solo"
start cmd /k "cd preprocessor && echo Starting Preprocessor Service && venv\Scripts\activate && celery -A worker worker --loglevel=info --pool=solo"