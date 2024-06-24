from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.apis.schemas import BaseResponse
from app.db import models, database
from app.apis.user.schemas import UserInfo

router = APIRouter()

@router.post("/user/signup", response_model=BaseResponse)
async def signup(db_session: Session = Depends(database.get_db_session)):
    new_user = models.User().save(session=db_session)
    return BaseResponse(
        code=200,
        msg="success",
        data=UserInfo(id=new_user.id)
    )

__all__ = ["router"]