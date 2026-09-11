from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
import jwt
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.config import settings
from app.database import db_session
from app.models import User

ph=PasswordHasher()
def hash_password(value): return ph.hash(value)
def verify_password(hash_value, value):
    try: return ph.verify(hash_value, value)
    except Exception: return False
def issue_token(user):
    now=datetime.now(timezone.utc); return jwt.encode({'sub':str(user.id),'iat':now,'exp':now+timedelta(minutes=settings.jwt_ttl_minutes)},settings.jwt_secret,algorithm='HS256')
def current_user(authorization: str|None = Header(default=None), db: Session=Depends(db_session)):
    if not authorization or not authorization.startswith('Bearer '): raise HTTPException(401, detail={'code':'authentication_required','message':'Bearer token required'})
    try: payload=jwt.decode(authorization[7:],settings.jwt_secret,algorithms=['HS256'])
    except jwt.ExpiredSignatureError: raise HTTPException(401, detail={'code':'invalid_token','message':'Token expired'})
    except jwt.PyJWTError: raise HTTPException(401, detail={'code':'invalid_token','message':'Token invalid'})
    user=db.get(User,payload.get('sub'))
    if not user or not user.active: raise HTTPException(401, detail={'code':'invalid_token','message':'User inactive'})
    return user

