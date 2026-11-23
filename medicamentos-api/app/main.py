# app/main.py
from fastapi import FastAPI
from app.medicamentos import router

app = FastAPI(title="API de Farmacia", version="1.0.0")
app.include_router(router)

@app.get("/")
def raiz() -> dict:
    return {"api": "medicamentos", "docs": "/docs"}