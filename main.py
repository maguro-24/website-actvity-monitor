from supabase import create_client
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(url, key)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #later add domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Event(BaseModel):
    event_type: str
    page_url: str
    metadata: dict = {}

class UserSignup(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

'''
----------------
signs user up
user(UserSignup) - the user
returns status
----------------
'''
@app.post("/signup")
def signup(user: UserSignup):
    response = supabase.auth.sign_up({
        "email": user.email,
        "password": user.password
    })
    if response.user:
        return {"status": "ok", "user_id": response.user.id}
    else:
        raise HTTPException(status_code=400, detail=str(response))


'''
--------------------
login for the user
user(UserLogin) - the user
returns status
--------------------
'''
@app.post("/login")
def login(user: UserLogin):
    response = supabase.auth.sign_in_with_password({
        "email": user.email,
        "password": user.password
    })
    if response.user:
        return {"status": "ok", "access_token": response.session.access_token}
    else:
        raise HTTPException(status_code=400, detail=str(response))


'''
-----------------------------------------------------------------------
verifies that user has loged in before getting token
authorization(str) - reads the Authorization header from the request
                     checks that the token is valid with Supabase
returns user id if vaild, else 401
----------------------------------------------------------------------
'''
def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    
    token = authorization.split(" ")[1]
    
    # Verify token with Supabase
    try:
        user = supabase.auth.get_user(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user.user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")


'''
----------------------------
adds event to the data base
event(Event) - event to be added
returns status
----------------------------
'''
@app.post("/track")
def track_event(event: Event, user_id: str = Depends(verify_token)):
    # Add user_id from verified token
    data = event.dict()
    data["user_id"] = user_id
    
    supabase.table("web_log").insert(data).execute()
    return {"status": "ok"}

