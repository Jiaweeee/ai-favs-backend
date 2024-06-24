from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.database import get_db_session
from app.db.models import User

def get_current_user(request: Request, db_session: Session = Depends(get_db_session)):
    user_id = request.headers.get("X-USER-ID")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID header missing"
        )
    user = User.get(session=db_session, id_=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID"
        )
    return user