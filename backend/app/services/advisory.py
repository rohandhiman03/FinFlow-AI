import re
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AdvisoryMessage, AdvisorySession, AdvisorySuggestion, Budget, BudgetCategory
from app.schemas.advisory import AdvisoryApplyResponse, AdvisoryAskResponse, AdvisorySuggestionItem
from app.services.transactions import get_budget_summary


def _extract_first_amount(text: str) -> float | None:
    match = re.search(r"\$?([0-9]+(?:\.[0-9]{1,2})?)", text)
    if not match:
        return None
    return float(match.group(1))


def _find_budget_for_user(db: Session, user_id: str) -> Budget:
    budget = db.execute(
        select(Budget).where(Budget.user_id == user_id).order_by(Budget.created_at.desc())
    ).scalars().first()
    if budget is None:
        raise ValueError("No budget found. Complete onboarding first.")
    return budget


def _get_or_create_session(db: Session, user_id: str, budget_id: str, session_id: str | None) -> AdvisorySession:
    if session_id:
        session = db.execute(
            select(AdvisorySession).where(AdvisorySession.id == session_id, AdvisorySession.user_id == user_id)
        ).scalars().first()
        if session is None:
            raise ValueError("Advisory session not found")
        return session

    existing = db.execute(
        select(AdvisorySession)
        .where(AdvisorySession.user_id == user_id, AdvisorySession.status == "active")
        .order_by(AdvisorySession.updated_at.desc())
    ).scalars().first()
    if existing:
        return existing

    session = AdvisorySession(user_id=user_id, budget_id=budget_id, status="active")
    db.add(session)
    db.flush()
    return session


def _create_rebalance_suggestion(
    db: Session,
    session: AdvisorySession,
    user_id: str,
    budget_id: str,
    shortfall: float,
) -> AdvisorySuggestion:
    categories = db.execute(
        select(BudgetCategory).where(BudgetCategory.budget_id == budget_id).order_by(BudgetCategory.planned_amount.desc())
    ).scalars().all()

    variable = [c for c in categories if c.category_type == "variable"]
    if not variable:
        variable = categories

    remaining = round(shortfall, 2)
    adjustments: list[dict[str, float | str]] = []

    for category in variable:
        if remaining <= 0:
            break
        reduction = round(min(remaining, max(25.0, category.planned_amount * 0.2)), 2)
        if reduction <= 0:
            continue
        adjustments.append({"category_name": category.name, "delta": -reduction})
        remaining = round(remaining - reduction, 2)

    savings_category = next((c for c in categories if c.name.lower() == "savings"), None)
    if savings_category is not None:
        total_cut = round(sum(abs(float(a["delta"])) for a in adjustments), 2)
        if total_cut > 0:
            adjustments.append({"category_name": savings_category.name, "delta": total_cut})

    suggestion = AdvisorySuggestion(
        session_id=session.id,
        user_id=user_id,
        budget_id=budget_id,
        title="Rebalance monthly budget",
        summary="Shift budget from discretionary categories to fund this goal/purchase.",
        adjustments={"items": adjustments},
        status="proposed",
    )
    db.add(suggestion)
    db.flush()
    return suggestion


def ask_advisory_question(db: Session, user_id: str, session_id: str | None, message: str) -> AdvisoryAskResponse:
    budget = _find_budget_for_user(db, user_id)
    session = _get_or_create_session(db, user_id, budget.id, session_id)

    db.add(AdvisoryMessage(session_id=session.id, role="user", content=message))

    summary = get_budget_summary(db, user_id)
    amount = _extract_first_amount(message)
    lowered = message.lower()

    reasoning: list[str] = [
        f"Current month remaining budget is ${summary.total_remaining:.2f}.",
        f"Projected end-of-month position is ${summary.projected_end_of_month_position:.2f}.",
    ]

    suggestions: list[AdvisorySuggestion] = []
    answer = "Based on your current budget, here is what I recommend."

    if amount is not None and any(token in lowered for token in ("can i", "swing", "buy", "purchase")):
        if summary.total_remaining >= amount:
            answer = (
                f"Yes, you can likely afford ${amount:.2f} this month. "
                f"You would still have about ${summary.total_remaining - amount:.2f} remaining."
            )
            reasoning.append("Requested amount is below current remaining budget.")
        else:
            shortfall = round(amount - summary.total_remaining, 2)
            answer = (
                f"Not with your current allocation. You are short by about ${shortfall:.2f}. "
                "I prepared a rebalance option below."
            )
            reasoning.append("Requested amount is above remaining budget, requiring reallocation.")
            suggestions.append(_create_rebalance_suggestion(db, session, user_id, budget.id, shortfall))
    elif amount is not None and any(token in lowered for token in ("how long", "save")):
        monthly_savings = max(1.0, summary.total_remaining)
        months = int((amount + monthly_savings - 1) // monthly_savings)
        answer = (
            f"At your current pace of roughly ${monthly_savings:.2f}/month, "
            f"you can reach ${amount:.2f} in about {months} month(s)."
        )
        reasoning.append("Estimated timeline is amount divided by current monthly surplus.")
    elif any(token in lowered for token in ("should i", "or")):
        answer = (
            "Given your current spending profile, prioritize reducing high-variance discretionary categories first, "
            "then allocate freed cash to the higher-confidence goal this month."
        )
        reasoning.append("Recommendation prioritizes volatility reduction before long-term allocation.")
    else:
        over_budget = [c for c in summary.categories if c.utilization_pct >= 85 and c.category_type == "variable"]
        if over_budget:
            top = sorted(over_budget, key=lambda c: c.utilization_pct, reverse=True)[0]
            answer = (
                f"Your {top.name} category is at {top.utilization_pct:.1f}% utilization. "
                f"Consider trimming it by about ${max(20.0, top.spent_amount - top.planned_amount):.2f} next month."
            )
            reasoning.append("Top advisory signal is current over-budget category utilization.")
        else:
            answer = "You are broadly on track this month. Maintain current allocations and keep logging consistently."
            reasoning.append("No critical overspend signal detected in current category utilization.")

    db.add(AdvisoryMessage(session_id=session.id, role="assistant", content=answer))
    session.updated_at = datetime.now(timezone.utc)

    db.commit()

    suggestion_items = [
        AdvisorySuggestionItem(
            suggestion_id=s.id,
            title=s.title,
            summary=s.summary,
            adjustments=list(s.adjustments.get("items", [])),
        )
        for s in suggestions
    ]

    return AdvisoryAskResponse(
        session_id=session.id,
        answer=answer,
        reasoning=reasoning,
        suggestions=suggestion_items,
    )


def apply_suggestion(db: Session, user_id: str, suggestion_id: str) -> AdvisoryApplyResponse:
    suggestion = db.execute(
        select(AdvisorySuggestion).where(AdvisorySuggestion.id == suggestion_id, AdvisorySuggestion.user_id == user_id)
    ).scalars().first()

    if suggestion is None:
        raise ValueError("Suggestion not found")

    if suggestion.status == "applied":
        return AdvisoryApplyResponse(
            suggestion_id=suggestion.id,
            status="applied",
            applied_adjustments=list(suggestion.adjustments.get("items", [])),
            confirmation="Suggestion was already applied.",
        )

    categories = db.execute(
        select(BudgetCategory).where(BudgetCategory.budget_id == suggestion.budget_id)
    ).scalars().all()
    categories_by_name = {c.name.lower(): c for c in categories}

    applied: list[dict[str, float | str]] = []
    for item in suggestion.adjustments.get("items", []):
        category_name = str(item.get("category_name", "")).lower()
        delta = float(item.get("delta", 0.0))

        category = categories_by_name.get(category_name)
        if category is None:
            continue

        new_value = max(0.0, round(category.planned_amount + delta, 2))
        category.planned_amount = new_value
        applied.append({"category_name": category.name, "delta": delta, "new_planned_amount": new_value})

    suggestion.status = "applied"
    db.commit()

    return AdvisoryApplyResponse(
        suggestion_id=suggestion.id,
        status="applied",
        applied_adjustments=applied,
        confirmation="Applied the recommended budget changes.",
    )
