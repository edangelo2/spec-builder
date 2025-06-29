# Upsert (called by Activepieces after refinement)
curl -X POST http://vector_api:8000/upsert \ 
  -H "Content-Type: application/json" \
  -d '{"spec_id":"ABC123","section":"1.2 Scope", "text":"original paragraph ..."}'

# Query (called by LangChain Worker)
curl -X POST http://vector_api:8000/query \ 
  -H "Content-Type: application/json" \
  -d '{"spec_id":"ABC123","section":"1.2 Scope", "k":3}'