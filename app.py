from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    session_id: str
    query: str
    approved: bool

@app.post("/run")   # ✅ MUST be POST
async def run_agent(q: Query):

    async def fake_stream():
        yield "Here are 5 countries:\n"
        yield "1. India\n"
        yield "2. USA\n"
        yield "3. Japan\n"
        yield "4. Germany\n"
        yield "5. Brazil\n"

    return StreamingResponse(fake_stream(), media_type="text/plain")
