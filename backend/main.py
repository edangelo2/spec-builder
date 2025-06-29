from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from routers import ingestion, refine

app = FastAPI(title="Spec‑Builder API")
app.include_router(ingestion.router)
app.include_router(refine.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health")
async def health():
    return {"status": "ok"}