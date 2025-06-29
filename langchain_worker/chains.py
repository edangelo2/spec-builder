from __future__ import annotations

import os
import re
import requests
from typing import List, Dict

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory, ChatMessageHistory
from langchain.schema import SystemMessage, HumanMessage
from langchain.chains import LLMChain, SequentialChain

# ---------------------------------------------------------------------------
# 1️⃣  Prompt template – single source of truth
# ---------------------------------------------------------------------------
TEMPLATE = (
    'You are **Spec‑Builder AI**, an expert technical writer.  Improve the following ' \
    'section of a software specification so that it is:
'
    '* Clear, concise, and active‑voice.
'
    '* Conforms to Lumina’s corporate style.
'
    '* Keeps ALL factual content; do not invent requirements.
'
    '* Adds bullet or numbered lists where it aids readability.

'
    'You may receive helpful context chunks from similar specifications; weave in any relevant details.

'
    '------ CONTEXT START ------
{context}
------ CONTEXT END --------

'
    '------ ORIGINAL TEXT START ------
{input}
------ ORIGINAL TEXT END --------

'
    'Return **only** the refined text.  If you detect any of the following issues, append a line
'
    '`RISK: <code>` at the end for each:
'
    '  * missing_validation   – validation rules appear incomplete
'
    '  * ambiguous_field      – same field named two ways or unclear format
'
    '  * formula_error        – calculation formula seems inconsistent
'
)

PROMPT = PromptTemplate(template=TEMPLATE, input_variables=['input', 'context'])

# ---------------------------------------------------------------------------
# 2️⃣  Vector context helper
# ---------------------------------------------------------------------------
VECTOR_API_URL = os.getenv('VECTOR_API_URL', 'http://vector_api:8000')
TOP_K = int(os.getenv('TOP_K', '5'))

def fetch_context(spec_id: str, section: str, k: int = TOP_K) -> str:
    """Return top‑k context chunks joined by blank lines."""
    try:
        resp = requests.post(
            f'{VECTOR_API_URL}/query',
            json={'spec_id': spec_id, 'section': section, 'k': k},
            timeout=30,
        )
        resp.raise_for_status()
        chunks: List[str] = resp.json().get('chunks', [])
        return '

'.join(chunks)
    except Exception as err:
        print('[VectorAPI] context fetch failed:', err)
        return ''

# ---------------------------------------------------------------------------
# 3️⃣  Post‑processing: risk flag extraction
# ---------------------------------------------------------------------------
RISK_PATTERNS = {
    'missing_validation': re.compile(r'missing validation', re.I),
    'ambiguous_field': re.compile(r'ambiguous field', re.I),
    'formula_error': re.compile(r'formula error', re.I),
}

def extract_risk_flags(text: str) -> List[str]:
    return [code for code, rgx in RISK_PATTERNS.items() if rgx.search(text)]

# ---------------------------------------------------------------------------
# 4️⃣  Chain builder
# ---------------------------------------------------------------------------

def build_chain(llm):
    """Return a LangChain SequentialChain ready to `.invoke()`."""

    def memory_factory(spec_id: str, section: str):
        history_key = f'{spec_id}::{section}'
        history = ChatMessageHistory()
        memory = ConversationBufferMemory(
            memory_key='history',
            chat_memory=history,
            return_messages=True,
        )
        # Seed with system role once per section
        if not history.messages:
            history.add_message(SystemMessage(content='You are Spec‑Builder AI.'))
        return memory

    def refinement_step(inputs: Dict[str, str]):
        spec_id, section, original = inputs['spec_id'], inputs['section'], inputs['input']
        ctx = fetch_context(spec_id, section)
        memory = memory_factory(spec_id, section)

        chain = LLMChain(
            llm=llm,
            prompt=PROMPT,
            memory=memory,
            output_parser=StrOutputParser(),
        )
        refined = chain.run({'input': original, 'context': ctx})
        risks = extract_risk_flags(refined)
        return {'output': refined, 'risk': risks}

    return SequentialChain(
        input_variables=['spec_id', 'section', 'input'],
        output_variables=['output', 'risk'],
        chains=[refinement_step],
        verbose=False,
    )