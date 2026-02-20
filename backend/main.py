from fastapi import FastAPI, HTTPException, Response, Cookie, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import database
import auth
import os
from datetime import datetime
import mysql.connector

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup - do not block startup
    import threading
    def safe_init():
        try:
            database.init_db()
            print("Database initialized successfully during lifespan.")
        except Exception as e:
            print(f"DATABASE INIT ERROR: {e}")
            
    thread = threading.Thread(target=safe_init)
    thread.start()
    yield

app = FastAPI(title="KodBank API", lifespan=lifespan)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.get("/health")
async def health_check():
    db_status = "unknown"
    try:
        conn = database.get_db_connection()
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ok", 
        "service": "KodBank API",
        "database": db_status
    }

from fastapi.security import OAuth2PasswordBearer
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

async def get_token(
    access_token_cookie: Optional[str] = Cookie(None, alias="access_token"),
    access_token_header: Optional[str] = Depends(oauth2_scheme)
):
    token = access_token_header or access_token_cookie
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone: str

class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/register")
async def register(user: UserRegister):
    conn = database.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if user already exists
        cursor.execute("SELECT * FROM kodusers WHERE username = %s OR email = %s", (user.username, user.email))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username or Email already registered")
        
        # Hash password and insert user
        hashed_password = auth.get_password_hash(user.password)
        cursor.execute(
            "INSERT INTO kodusers (username, email, password, phone, role) VALUES (%s, %s, %s, %s, 'Customer')",
            (user.username, user.email, hashed_password, user.phone)
        )
        conn.commit()
        return {"message": "User registered successfully", "status": "success"}
    
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        cursor.close()
        conn.close()

@app.post("/login")
async def login(user: UserLogin, response: Response):
    conn = database.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM kodusers WHERE username = %s", (user.username,))
        db_user = cursor.fetchone()
        
        if not db_user or not auth.verify_password(user.password, db_user["password"]):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Generate token
        token_data = {"sub": db_user["username"], "role": db_user["role"]}
        token, expiry = auth.create_access_token(token_data)
        
        # Store token in DB (CJWT)
        cursor.execute(
            "INSERT INTO CJWT (token, uid, expiry) VALUES (%s, %s, %s)",
            (token, db_user["uid"], expiry)
        )
        conn.commit()
        
        # Set cookie (keeping for compatibility)
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            expires=expiry.strftime("%a, %d-%b-%Y %T GMT"),
            samesite="lax",
            secure=False # Set to False for local dev
        )
        
        return {
            "message": "Login successful", 
            "status": "success", 
            "username": db_user["username"], 
            "role": db_user["role"],
            "access_token": token # Return token in body for local file storage
        }
    
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        cursor.close()
        conn.close()

@app.get("/balance")
async def get_balance(access_token: str = Depends(get_token)):
    payload = auth.decode_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    username = payload.get("sub")
    
    conn = database.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verify token exists in DB
        cursor.execute("SELECT * FROM CJWT WHERE token = %s", (access_token,))
        if not cursor.fetchone():
            raise HTTPException(status_code=401, detail="Token not found in session")
            
        # Fetch balance
        cursor.execute("SELECT balance FROM kodusers WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {"balance": float(user_data["balance"]), "username": username}
        
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        cursor.close()
        conn.close()

@app.get("/profile")
async def get_profile(access_token: str = Depends(get_token)):
    payload = auth.decode_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
        
    username = payload.get("sub")
    
    conn = database.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT username, email, phone, role FROM kodusers WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        return user_data
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    import uvicorn
    # Using 8009 to avoid conflicts
    port = int(os.getenv("PORT", 8009))
    uvicorn.run(app, host="0.0.0.0", port=port)
