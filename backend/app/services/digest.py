from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Budget, BudgetCategory, Transaction, UserPreference
from app.schemas.digest import DigestSettingsResponse, WeeklyDigestResponse


def _find_budget_for_user(db: Session, user_id: str) -> Budget:
    budget = db.execute(
        select(Budget).where(Budget.user_id == user_id).order_by(Budget.created_at.desc())
    ).scalars().first()
    if budget is None:
        raise ValueError("No budget found. Complete onboarding first.")
    return budget


def _get_or_create_pref(db: Session, user_id: str) -> UserPreference:
    pref = db.get(UserPreference, user_id)
    if pref is None:
        pref = UserPreference(user_id=user_id, digest_frequency="weekly", digest_day="Sunday", digest_time="09:00")
        db.add(pref)
        db.flush()
    return pref


def get_digest_settings(db: Session, user_id: str) -> DigestSettingsResponse:
    pref = _get_or_create_pref(db, user_id)
    db.commit()
    return DigestSettingsResponse(frequency=pref.digest_frequency, day=pref.digest_day, time=pref.digest_time)


def update_digest_settings(db: Session, user_id: str, frequency: str, day: str, time: str) -> DigestSettingsResponse:
    pref = _get_or_create_pref(db, user_id)
    pref.digest_frequency = frequency
    pref.digest_day = day
    pref.digest_time = time
    db.commit()
    return DigestSettingsResponse(frequency=pref.digest_frequency, day=pref.digest_day, time=pref.digest_time)


def generate_weekly_digest(db: Session, user_id: str) -> WeeklyDigestResponse:
    budget = _find_budget_for_user(db, user_id)

    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
    end = now

    weekly_spent = db.execute(
        select(func.sum(Transaction.amount)).where(
            Transaction.user_id == user_id,
            Transaction.budget_id == budget.id,
            Transaction.transaction_date >= start,
            Transaction.transaction_date <= end,
        )
    ).scalar()
    weekly_spent = round(float(weekly_spent or 0.0), 2)

    categories = db.execute(
        select(BudgetCategory).where(BudgetCategory.budget_id == budget.id)
    ).scalars().all()

    monthly_planned = sum(c.planned_amount for c in categories if c.category_type != "goal")
    weekly_income_proxy = round(monthly_planned / 4.0, 2) if monthly_planned > 0 else 1.0
    savings_rate = round(max(0.0, (weekly_income_proxy - weekly_spent) / max(weekly_income_proxy, 1.0) * 100), 2)

    variable = [c for c in categories if c.category_type == "variable"]
    category_to_watch = variable[0].name if variable else (categories[0].name if categories else "Spending")

    upcoming_fixed = [c for c in categories if c.category_type == "fixed"]
    upcoming_expenses = [
        {"name": c.name, "amount": round(c.planned_amount / 4.0, 2), "window": "next 7 days"}
        for c in sorted(upcoming_fixed, key=lambda x: x.planned_amount, reverse=True)[:3]
    ]

    digest_text = (
        f"This week you spent ${weekly_spent:.2f}. "
        f"Your estimated weekly savings rate is {savings_rate:.1f}%. "
        f"Watch {category_to_watch} closely. "
        f"You have {len(upcoming_expenses)} expected fixed expenses in the next 7 days."
    )

    return WeeklyDigestResponse(
        period_start=start.date().isoformat(),
        period_end=end.date().isoformat(),
        weekly_spent=weekly_spent,
        weekly_income_proxy=weekly_income_proxy,
        savings_rate_pct=savings_rate,
        category_to_watch=category_to_watch,
        upcoming_expenses=upcoming_expenses,
        digest_text=digest_text,
    )
