from fastapi import FastAPI
from app.modules.content.router import router as contenido_router

app = FastAPI(title="CTech API")
app.include_router(contenido_router)

@app.get("/")
def read_root():
    return {"message": "Hola desde API de CTech funcionando 🚀"}

