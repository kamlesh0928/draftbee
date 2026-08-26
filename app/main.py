from fastapi import FastAPI

app = FastAPI(
    title="AI Content Engine",
    version="1.0.0"
)

@app.get("/")
async def root():
    return { "message": "Hello" }

@app.get("/health")
async def health():
    return { "status": "ok" }
