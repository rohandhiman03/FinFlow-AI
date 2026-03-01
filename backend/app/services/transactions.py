import calendar
import re
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Budget, BudgetCategory, Transaction
from app.schemas.transactions import (
    BudgetCategorySummary,
    BudgetSummaryResponse,
    ExpenseLogResponse,
    LoggedTransaction,
)


def _extract_amount(text: str) -> float:
    matches = re.findall(r"\$?([0-9]+(?:\.[0-9]{1,2})?)", text)
    if not matches:
        raise ValueError("Couldn't parse an amount. Include something like '$12.50'.")
    return float(matches[0])


def _extract_merchant(text: str) -> str:
    lowered = text.lower()
    at_match = re.search(r"\bat\s+([a-zA-Z0-9&'\- ]{2,40})", text, flags=re.IGNORECASE)
    if at_match:
        return at_match.group(1).strip().split("$")[0].strip().title()

    cleaned = re.sub(r"\$?[0-9]+(?:\.[0-9]{1,2})?", "", text).strip()
    tokens = [t for t in cleaned.split() if t.lower() not in {"paid", "spent", "for", "my", "the", "today"}]
    return " ".join(tokens[:3]).strip().title() if tokens else "Expense"


def _find_budget_for_user(db: Session, user_id: str) -> Budget:
    budget = db.execute(
        select(Budget).where(Budget.user_id == user_id).order_by(Budget.created_at.desc())
    ).scalars().first()
    if budget is None:
        raise ValueError("No budget found. Complete onboarding first.")
    return budget


def _category_keywords() -> dict[str, tuple[str, ...]]:
    return {
        "housing": ("rent", "mortgage", "landlord", "condo"),
        "utilities": ("phone", "internet", "hydro", "electric", "gas bill", "water", "rogers", "bell"),
        "transport": ("uber", "lyft", "transit", "bus", "train", "fuel", "gas", "parking"),
        "groceries": ("grocery", "groceries", "costco", "walmart", "loblaws", "metro", "nofrills"),
        "dining": ("coffee", "cafe", "restaurant", "dinner", "lunch", "breakfast", "food delivery", "ubereats"),
        "lifestyle": ("amazon", "shopping", "netflix", "spotify", "entertainment", "subscription", "movie", "gym"),
        "savings": ("savings", "investment", "tfsa", "rrsp"),
    }


def _map_category(text: str, categories: list[BudgetCategory]) -> BudgetCategory:
    lowered = text.lower()
    key_map = _category_keywords()

    for cat in categories:
        cat_name = cat.name.lower().strip()
        if cat_name in key_map and any(keyword in lowered for keyword in key_map[cat_name]):
            return cat

    # Fallback: choose first variable category; otherwise first category.
    for cat in categories:
        if cat.category_type == "variable":
            return cat

    return categories[0]


def log_expense(db: Session, user_id: str, message: str) -> ExpenseLogResponse:
    budget = _find_budget_for_user(db, user_id)
    categories = db.execute(
        select(BudgetCategory).where(BudgetCategory.budget_id == budget.id).order_by(BudgetCategory.created_at.asc())
    ).scalars().all()

    if not categories:
        raise ValueError("Budget exists but has no categories.")

    amount = _extract_amount(message)
    merchant = _extract_merchant(message)
    category = _map_category(message, categories)

    txn = Transaction(
        user_id=user_id,
        budget_id=budget.id,
        category_id=category.id,
        amount=amount,
        merchant=merchant,
        description=message,
        source_text=message,
        transaction_date=datetime.now(timezone.utc),
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)

    confirmation = f"Added ${amount:.2f} -> {category.name}"
    return ExpenseLogResponse(
        confirmation=confirmation,
        parsed_input={
            "amount": amount,
            "merchant": merchant,
            "category": category.name,
        },
        transaction=LoggedTransaction(
            id=txn.id,
            amount=txn.amount,
            merchant=txn.merchant,
            category_name=category.name,
            transaction_date=txn.transaction_date.isoformat(),
        ),
    )


def get_budget_summary(db: Session, user_id: str) -> BudgetSummaryResponse:
    budget = _find_budget_for_user(db, user_id)

    categories = db.execute(
        select(BudgetCategory).where(BudgetCategory.budget_id == budget.id).order_by(BudgetCategory.created_at.asc())
    ).scalars().all()

    if not categories:
        raise ValueError("Budget exists but has no categories.")

    now = datetime.now(timezone.utc)
    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    if now.month == 12:
        month_end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        month_end = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)

    rows = db.execute(
        select(Transaction.category_id, func.sum(Transaction.amount))
        .where(
            Transaction.user_id == user_id,
            Transaction.budget_id == budget.id,
            Transaction.transaction_date >= month_start,
            Transaction.transaction_date < month_end,
        )
        .group_by(Transaction.category_id)
    ).all()

    spent_map = {category_id: float(total or 0.0) for category_id, total in rows}

    category_summaries: list[BudgetCategorySummary] = []
    total_planned = 0.0
    total_spent = 0.0

    for category in categories:
        planned = float(category.planned_amount)
        spent = round(float(spent_map.get(category.id, 0.0)), 2)
        remaining = round(planned - spent, 2)
        utilization = round((spent / planned) * 100, 2) if planned > 0 else 0.0
        status = "green" if utilization < 60 else "amber" if utilization < 85 else "red"

        category_summaries.append(
            BudgetCategorySummary(
                category_id=category.id,
                name=category.name,
                category_type=category.category_type,
                planned_amount=planned,
                spent_amount=spent,
                remaining_amount=remaining,
                utilization_pct=utilization,
                status=status,
            )
        )

        if category.category_type != "goal":
            total_planned += planned
            total_spent += spent

    total_planned = round(total_planned, 2)
    total_spent = round(total_spent, 2)
    total_remaining = round(total_planned - total_spent, 2)

    days_in_month = calendar.monthrange(now.year, now.month)[1]
    days_left = max(0, days_in_month - now.day)

    projected = total_remaining
    if now.day > 0:
        daily_spend = total_spent / now.day
        projected = round(total_planned - (daily_spend * days_in_month), 2)

    return BudgetSummaryResponse(
        budget_id=budget.id,
        month=f"{now.year}-{now.month:02d}",
        total_planned=total_planned,
        total_spent=total_spent,
        total_remaining=total_remaining,
        days_left_in_cycle=days_left,
        projected_end_of_month_position=projected,
        categories=category_summaries,
    )
