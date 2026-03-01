import re
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Budget, BudgetCategory, Goal, OnboardingMessage, OnboardingSession, User
from app.schemas.onboarding import BudgetProposal, ChatMessage, OnboardingResponse

STEP_SEQUENCE = ["income", "fixed_expenses", "variable_spending", "goals", "review", "completed"]


def _extract_amounts(text: str) -> list[float]:
    matches = re.findall(r"\$?([0-9]+(?:\.[0-9]{1,2})?)", text)
    return [float(x) for x in matches]


def _infer_monthly_income(text: str) -> float:
    amounts = _extract_amounts(text)
    if not amounts:
        return 0.0

    base = amounts[0]
    lowered = text.lower()
    if "biweekly" in lowered or "bi-weekly" in lowered:
        return round(base * 26 / 12, 2)
    if "weekly" in lowered:
        return round(base * 52 / 12, 2)
    if "annual" in lowered or "year" in lowered:
        return round(base / 12, 2)
    return round(base, 2)


def _build_budget_proposal(data: dict) -> BudgetProposal:
    monthly_income = _infer_monthly_income(data.get("income", ""))

    fixed_amounts = _extract_amounts(data.get("fixed_expenses", ""))
    variable_amounts = _extract_amounts(data.get("variable_spending", ""))

    fixed_total = round(sum(fixed_amounts), 2)
    variable_total = round(sum(variable_amounts), 2)

    if monthly_income <= 0 and (fixed_total + variable_total) > 0:
        monthly_income = round((fixed_total + variable_total) * 1.2, 2)

    if variable_total == 0 and monthly_income > 0:
        variable_total = round(monthly_income * 0.30, 2)

    if fixed_total == 0 and monthly_income > 0:
        fixed_total = round(monthly_income * 0.35, 2)

    suggested_savings = max(0.0, round(monthly_income - fixed_total - variable_total, 2))

    categories = [
        {"name": "Housing", "type": "fixed", "planned_amount": round(fixed_total * 0.45, 2)},
        {"name": "Utilities", "type": "fixed", "planned_amount": round(fixed_total * 0.20, 2)},
        {"name": "Transport", "type": "fixed", "planned_amount": round(fixed_total * 0.15, 2)},
        {"name": "Groceries", "type": "variable", "planned_amount": round(variable_total * 0.40, 2)},
        {"name": "Dining", "type": "variable", "planned_amount": round(variable_total * 0.25, 2)},
        {"name": "Lifestyle", "type": "variable", "planned_amount": round(variable_total * 0.35, 2)},
        {"name": "Savings", "type": "goal", "planned_amount": suggested_savings},
    ]

    return BudgetProposal(
        estimated_monthly_income=monthly_income,
        monthly_fixed_total=fixed_total,
        monthly_variable_total=variable_total,
        suggested_savings=suggested_savings,
        categories=categories,
    )


def _assistant_prompt_for_step(step: str, provider: str, proposal: BudgetProposal | None = None) -> str:
    if step == "income":
        return (
            f"Hi, I'm FinFlow running on {provider}. Let's build your budget in 5 minutes. "
            "What's your income source, amount, and frequency (monthly/biweekly/weekly)?"
        )
    if step == "fixed_expenses":
        return "Great. Now list your fixed monthly expenses (rent, phone, insurance, etc.) with rough amounts."
    if step == "variable_spending":
        return "Got it. What do you usually spend on groceries, dining, transport, and fun each month?"
    if step == "goals":
        return "Perfect. What money goals should we plan for (emergency fund, debt payoff, travel), with target amounts?"
    if step == "review" and proposal is not None:
        return (
            "I drafted your baseline monthly budget:\n"
            f"- Income: ${proposal.estimated_monthly_income:.2f}\n"
            f"- Fixed: ${proposal.monthly_fixed_total:.2f}\n"
            f"- Variable: ${proposal.monthly_variable_total:.2f}\n"
            f"- Savings: ${proposal.suggested_savings:.2f}\n"
            "Reply 'confirm' to save this budget, or tell me what to adjust."
        )
    if step == "completed":
        return "Budget saved. You're ready for the dashboard and daily expense logging."
    return "Tell me more."


def _next_step(current_step: str) -> str:
    idx = STEP_SEQUENCE.index(current_step)
    return STEP_SEQUENCE[min(idx + 1, len(STEP_SEQUENCE) - 1)]


def _append_message(db: Session, session_id: str, role: str, content: str) -> OnboardingMessage:
    msg = OnboardingMessage(session_id=session_id, role=role, content=content)
    db.add(msg)
    return msg


def _ensure_user(db: Session, user_id: str) -> User:
    user = db.get(User, user_id)
    if user is None:
        user = User(id=user_id)
        db.add(user)
        db.flush()
    return user


def _persist_budget(db: Session, user_id: str, proposal: BudgetProposal, goals_text: str) -> None:
    budget = Budget(user_id=user_id, name="Primary Budget")
    db.add(budget)
    db.flush()

    for category in proposal.categories:
        db.add(
            BudgetCategory(
                budget_id=budget.id,
                name=str(category["name"]),
                category_type=str(category["type"]),
                planned_amount=float(category["planned_amount"]),
            )
        )

    goal_amounts = _extract_amounts(goals_text)
    if goal_amounts:
        db.add(
            Goal(
                user_id=user_id,
                name="Primary Goal",
                target_amount=float(goal_amounts[0]),
                target_date="",
                current_amount=0.0,
            )
        )


def start_onboarding_session(db: Session, user_id: str, provider: str, reset_existing: bool = False) -> OnboardingResponse:
    _ensure_user(db, user_id)

    existing = db.execute(
        select(OnboardingSession)
        .where(OnboardingSession.user_id == user_id, OnboardingSession.status == "active")
        .order_by(OnboardingSession.created_at.desc())
    ).scalars().first()

    if existing is not None and not reset_existing:
        msgs = [ChatMessage(role=m.role, content=m.content) for m in existing.messages]
        proposal = None
        if existing.current_step in {"review", "completed"}:
            proposal = _build_budget_proposal(existing.collected_data or {})
        return OnboardingResponse(
            session_id=existing.id,
            status=existing.status,
            current_step=existing.current_step,
            provider=provider,
            messages=msgs,
            budget_proposal=proposal,
        )

    if existing is not None and reset_existing:
        existing.status = "cancelled"

    session = OnboardingSession(user_id=user_id, status="active", current_step="income", collected_data={})
    db.add(session)
    db.flush()

    assistant_text = _assistant_prompt_for_step("income", provider)
    _append_message(db, session.id, "assistant", assistant_text)
    db.commit()
    db.refresh(session)

    return OnboardingResponse(
        session_id=session.id,
        status=session.status,
        current_step=session.current_step,
        provider=provider,
        messages=[ChatMessage(role="assistant", content=assistant_text)],
    )


def handle_onboarding_message(db: Session, user_id: str, provider: str, session_id: str, message: str) -> OnboardingResponse:
    session = db.execute(
        select(OnboardingSession).where(OnboardingSession.id == session_id, OnboardingSession.user_id == user_id)
    ).scalars().first()

    if session is None:
        raise ValueError("Session not found for user")

    if session.status != "active":
        raise ValueError("Session is not active")

    _append_message(db, session.id, "user", message)

    data = dict(session.collected_data or {})
    step = session.current_step

    if step == "income":
        data["income"] = message
        step = _next_step(step)
        assistant_text = _assistant_prompt_for_step(step, provider)
    elif step == "fixed_expenses":
        data["fixed_expenses"] = message
        step = _next_step(step)
        assistant_text = _assistant_prompt_for_step(step, provider)
    elif step == "variable_spending":
        data["variable_spending"] = message
        step = _next_step(step)
        assistant_text = _assistant_prompt_for_step(step, provider)
    elif step == "goals":
        data["goals"] = message
        step = _next_step(step)
        proposal = _build_budget_proposal(data)
        assistant_text = _assistant_prompt_for_step(step, provider, proposal)
    elif step == "review":
        lowered = message.lower()
        if any(token in lowered for token in ("confirm", "save", "yes", "looks good", "done")):
            proposal = _build_budget_proposal(data)
            _persist_budget(db, user_id, proposal, data.get("goals", ""))
            step = _next_step(step)
            session.status = "completed"
            assistant_text = _assistant_prompt_for_step(step, provider, proposal)
        else:
            # Lightweight adjustment capture for now.
            data["adjustment_notes"] = message
            proposal = _build_budget_proposal(data)
            assistant_text = _assistant_prompt_for_step("review", provider, proposal)
    else:
        assistant_text = "This onboarding session is complete."

    session.collected_data = data
    session.current_step = step
    session.updated_at = datetime.now(timezone.utc)

    _append_message(db, session.id, "assistant", assistant_text)
    db.commit()
    db.refresh(session)

    proposal = _build_budget_proposal(session.collected_data) if session.current_step in {"review", "completed"} else None
    msgs = [ChatMessage(role=m.role, content=m.content) for m in session.messages]

    return OnboardingResponse(
        session_id=session.id,
        status=session.status,
        current_step=session.current_step,
        provider=provider,
        messages=msgs,
        budget_proposal=proposal,
    )
