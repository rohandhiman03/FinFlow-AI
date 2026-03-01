from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.goals import GoalContributeRequest, GoalContributeResponse, GoalCreateRequest, GoalItem
from app.services.goals import contribute_to_goal, create_goal, list_goals

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("", response_model=GoalItem)
def create_goal_route(
    payload: GoalCreateRequest,
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
) -> GoalItem:
    user_id = x_user_id or "demo-user"
    return create_goal(
        db=db,
        user_id=user_id,
        name=payload.name,
        target_amount=payload.target_amount,
        target_date=payload.target_date,
    )


@router.get("", response_model=list[GoalItem])
def list_goals_route(
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
) -> list[GoalItem]:
    user_id = x_user_id or "demo-user"
    return list_goals(db=db, user_id=user_id)


@router.post("/{goal_id}/contribute", response_model=GoalContributeResponse)
def contribute_goal_route(
    goal_id: str,
    payload: GoalContributeRequest,
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
) -> GoalContributeResponse:
    user_id = x_user_id or "demo-user"
    try:
        return contribute_to_goal(db=db, user_id=user_id, goal_id=goal_id, amount=payload.amount)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
