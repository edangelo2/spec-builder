"""chains.py – LangChain refinement chain (compatible with LangChain ≥ 0.2)"""
from __future__ import annotations

import os, requests
from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

VECTOR_API = os.getenv("VECTOR_API_URL", "http://vector_api:8000")
TOP_K = int(os.getenv("TOP_K", 5))

# -------------------------------------------------------------
# Helpers
# -------------------------------------------------------------

def fetch_vector_context(spec_id: str, section: str, k: int = TOP_K) -> List[str]:
    """Return k similar chunks via Vector API."""
    try:
        r = requests.post(f"{VECTOR_API}/query", json={"spec_id": spec_id, "section": section, "k": k}, timeout=30)
        r.raise_for_status()
        return [c["text"] for c in r.json().get("chunks", [])]
    except Exception as e:
        return [f"<vector retrieval failed: {e}>"]

# -------------------------------------------------------------
# Prompt template
# -------------------------------------------------------------
PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You are an expert technical writer. Rewrite the provided *raw* section of a software specification so that it is:
• Clear, active‑voice English
• Consistent with Lumina's BFS/EIS style guide
• Free of typos and duplicated statements
• Correctly formatted in Markdown (headings, tables, lists)
If you detect BUSINESS or TECHNICAL ambiguities, flag them in a list called RISK FLAGS at the end.
Previous approved revisions and similar specs (for context) are provided below.
"""),
    ("user", """
### Context chunks
{context}

### Raw section text
{input}
"""),
])

# -------------------------------------------------------------
# Chain builder
# -------------------------------------------------------------

def build_chain(llm: ChatOpenAI):
    output = StrOutputParser()
    return PROMPT | llm | output