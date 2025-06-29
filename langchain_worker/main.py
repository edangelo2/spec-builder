from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from chains import build_chain
from offline_switch import get_llm

app = FastAPI(title="LangChain Worker")
llm = get_llm()
chain = build_chain(llm)

class ChatBody(BaseModel):
    spec_id: str
    section: str
    text: str

@app.post("/chat")
async def chat(body: ChatBody):
    try:
        response = chain.invoke({"input": body.text,
                                 "spec_id": body.spec_id,
                                 "section": body.section})
        return {"refined_text": response["output"],
                "risk_flags": response.get("risk", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))