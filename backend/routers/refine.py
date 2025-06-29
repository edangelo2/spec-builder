from fastapi import APIRouter
import requests, os

router = APIRouter(prefix="/refine", tags=["refine"])
ACTIVEPIECES_URL = os.getenv("ACTIVEPIECES_URL", "http://activepieces")

@router.post("")
async def refine(body: dict):
    r = requests.post(f"{ACTIVEPIECES_URL}/refine", json=body, timeout=60)
    if r.status_code != 200:
        return {"error": r.text}
    return r.json()