from fastapi import FastAPI
from app.api import endpoints

app = FastAPI(title="DocuFill AI API", version="1.0.0")

app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "DocuFill AI Service is running"}
