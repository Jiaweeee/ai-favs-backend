from fastapi import APIRouter, status as HttpStatus, Depends
from pydantic import BaseModel
from app.apis.schemas import BaseResponse
from app.db.models import User
from app.db.database import get_db_session
from app.apis.dependencies import get_current_user
from .agent_runner import AgentRunner
from .agent import CollectionAgent
from sqlalchemy.orm import Session

router = APIRouter()

class AssistantQueryBody(BaseModel):
    query: str

@router.post("/assistant/query", response_model=BaseResponse)
def assistant_query(
    body: AssistantQueryBody,
    current_user: User = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    query = body.query
    agent_runner = AgentRunner(
        goal=query,
        agent=CollectionAgent(db_session=db_session),
        user=current_user,
        completed_actions=[]
    )
    result = agent_runner.run()
    return BaseResponse(
        code=HttpStatus.HTTP_200_OK,
        msg="success",
        data=result
    )


__all__ = ["router"]