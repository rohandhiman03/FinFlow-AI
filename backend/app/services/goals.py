from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Goal
from app.schemas.goals import GoalContributeResponse, GoalItem


def _months_until_target(target_date: str) -> int:
    try:
        parsed = date.fromisoformat(target_date)
        today = date.today()
        months = (parsed.year - today.year) * 12 + (parsed.month - today.month)
        return max(1, months)
    except ValueError:
        return 12


def _to_goal_item(goal: Goal) -> GoalItem:
    progress = 0.0
    if goal.target_amount > 0:
        progress = min(100.0, round((goal.current_amount / goal.target_amount) * 100, 2))

    months_left = _months_until_target(goal.target_date or "")
    required_monthly = round(max(0.0, goal.target_amount - goal.current_amount) / months_left, 2)
    on_track = progress >= 100.0 or required_monthly <= (goal.target_amount * 0.12)

    return GoalItem(
        goal_id=goal.id,
        name=goal.name,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        progress_pct=progress,
        target_date=goal.target_date,
        required_monthly=required_monthly,
        on_track=on_track,
    )


def create_goal(db: Session, user_id: str, name: str, target_amount: float, target_date: str | None) -> GoalItem:
    goal = Goal(
        user_id=user_id,
        name=name,
        target_amount=target_amount,
        target_date=target_date or "",
        current_amount=0.0,
        created_at=datetime.now(timezone.utc),
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return _to_goal_item(goal)


def list_goals(db: Session, user_id: str) -> list[GoalItem]:
    rows = db.execute(select(Goal).where(Goal.user_id == user_id).order_by(Goal.created_at.desc())).scalars().all()
    return [_to_goal_item(g) for g in rows]


def contribute_to_goal(db: Session, user_id: str, goal_id: str, amount: float) -> GoalContributeResponse:
    goal = db.execute(select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)).scalars().first()
    if goal is None:
        raise ValueError("Goal not found")

    goal.current_amount = round(goal.current_amount + amount, 2)
    db.commit()
    db.refresh(goal)

    progress = min(100.0, round((goal.current_amount / goal.target_amount) * 100, 2)) if goal.target_amount > 0 else 0.0
    return GoalContributeResponse(
        goal_id=goal.id,
        current_amount=goal.current_amount,
        progress_pct=progress,
        confirmation=f"Added ${amount:.2f} to {goal.name}.",
    )
