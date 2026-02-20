from fastapi import FastAPI, HTTPException, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add current directory to path for local imports
sys.path.append(os.path.dirname(__file__))

import auth
import database
from typing import Optional

app = FastAPI(title="KodBank API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api")
@app.get("/api/health")
async def health_check():
    db_status = "unknown"
    try:
        # Simple connection test
        conn = database.get_db_connection()
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ok", 
        "database": db_status,
        "env_check": {
            "DB_HOST": "set" if os.getenv("DB_HOST") else "missing",
            "DB_USER": "set" if os.getenv("DB_USER") else "missing",
            "DB_PASS": "set" if os.getenv("DB_PASS") else "missing",
            "DB_NAME": "set" if os.getenv("DB_NAME") else "missing"
        }
    }

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    phone: str

class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/api/register")
async def register(user: UserRegister):
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM kodusers WHERE username = %s OR email = %s", (user.username, user.email))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Username or email already exists")
        
        hashed_password = auth.get_password_hash(user.password)
        cursor.execute("INSERT INTO kodusers (username, email, password, phone) VALUES (%s, %s, %s, %s)", (user.username, user.email, hashed_password, user.phone))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "User registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/login")
async def login(user: UserLogin):
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM kodusers WHERE username = %s", (user.username,))
        db_user = cursor.fetchone()
        
        if not db_user or not auth.verify_password(user.password, db_user["password"]):
            cursor.close()
            conn.close()
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        token, expiry = auth.create_access_token({"sub": db_user["username"]})
        
        cursor.execute("INSERT INTO CJWT (token, uid, expiry) VALUES (%s, %s, %s)", (token, db_user["uid"], expiry))
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"username": db_user["username"], "access_token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/balance")
async def get_balance(token: str = Depends(auth.decode_token)):
    if not token: raise HTTPException(status_code=401)
    
    username = token.get("sub")
    conn = database.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT balance FROM kodusers WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if not user: raise HTTPException(status_code=404)
    return {"balance": user["balance"]}

@app.get("/api/profile")
async def get_profile(token: str = Depends(auth.decode_token)):
    if not token: raise HTTPException(status_code=401)
    
    username = token.get("sub")
    conn = database.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username, email, phone, role FROM kodusers WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if not user: raise HTTPException(status_code=404)
    return user
