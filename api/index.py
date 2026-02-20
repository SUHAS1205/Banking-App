from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/api")
@app.get("/api/health")
async def root():
    return {"message": "Hello from Vercel!", "status": "ok"}

handler = Mangum(app)
