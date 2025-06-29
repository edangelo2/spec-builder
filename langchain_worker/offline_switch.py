import os
from langchain_openai import ChatOpenAI

offline = os.getenv("OFFLINE_MODE", "false").lower() == "true"
if offline:
    class LocalOpenAI(ChatOpenAI):
        def __init__(self, *args, **kwargs):
            super().__init__(*args,
                             base_url=os.getenv("OLLAMA_BASE_URL"),
                             api_key="LOCAL", **kwargs)

    def get_llm():
        return LocalOpenAI(model=os.getenv("MODEL_NAME", "mixtral-8x7b"))
else:
    def get_llm():
        return ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o"),
                          api_key=os.getenv("OPENAI_API_KEY"))