from fastapi import FastAPI

app = FastAPI()

@app.get("/api")
@app.get("/api/health")
async def root():
    return {"message": "Hello from Vercel Serverless!", "status": "ok"}
