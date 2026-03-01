from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Budget, BudgetCategory, FinancialReport, Goal, Transaction
from app.schemas.reports import CategoryPerformanceItem, FinancialReportResponse, ScoreDimension
from app.services.transactions import get_budget_summary


def _find_budget_for_user(db: Session, user_id: str) -> Budget:
    budget = db.execute(
        select(Budget).where(Budget.user_id == user_id).order_by(Budget.created_at.desc())
    ).scalars().first()
    if budget is None:
        raise ValueError("No budget found. Complete onboarding first.")
    return budget


def _score_by_threshold(value: float, good_max: float, warn_max: float, reverse: bool = False) -> float:
    if reverse:
        if value >= good_max:
            return 95.0
        if value >= warn_max:
            return 75.0
        if value > 0:
            return 55.0
        return 40.0

    if value <= good_max:
        return 95.0
    if value <= warn_max:
        return 75.0
    return 50.0


def _grade(score: float) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def _build_dimensions(
    estimated_income: float,
    total_spent: float,
    total_planned: float,
    goal_planned: float,
    debt_ratio: float,
    emergency_months: float,
    discretionary_ratio: float,
    adherence_delta_pct: float,
) -> list[ScoreDimension]:
    savings_rate = ((estimated_income - total_spent) / estimated_income * 100) if estimated_income > 0 else 0.0
    savings_score = _score_by_threshold(savings_rate, good_max=20.0, warn_max=15.0, reverse=True)

    debt_score = _score_by_threshold(debt_ratio, good_max=36.0, warn_max=45.0, reverse=False)

    emergency_score = _score_by_threshold(emergency_months, good_max=6.0, warn_max=3.0, reverse=True)

    discretionary_score = _score_by_threshold(discretionary_ratio, good_max=30.0, warn_max=40.0, reverse=False)

    adherence_score = _score_by_threshold(adherence_delta_pct, good_max=10.0, warn_max=20.0, reverse=False)

    return [
        ScoreDimension(
            name="Savings Rate",
            score=savings_score,
            value=round(savings_rate, 2),
            ideal_range="15-20%+",
            explanation=f"You saved {savings_rate:.1f}% of estimated income this month.",
        ),
        ScoreDimension(
            name="Debt-to-Income",
            score=debt_score,
            value=round(debt_ratio, 2),
            ideal_range="Below 36%",
            explanation=f"Estimated debt burden is {debt_ratio:.1f}% of income.",
        ),
        ScoreDimension(
            name="Emergency Fund",
            score=emergency_score,
            value=round(emergency_months, 2),
            ideal_range="3-6 months",
            explanation=f"Current emergency runway estimate is {emergency_months:.1f} months.",
        ),
        ScoreDimension(
            name="Discretionary Spend",
            score=discretionary_score,
            value=round(discretionary_ratio, 2),
            ideal_range="Below 30%",
            explanation=f"Discretionary spending is {discretionary_ratio:.1f}% of income.",
        ),
        ScoreDimension(
            name="Budget Adherence",
            score=adherence_score,
            value=round(adherence_delta_pct, 2),
            ideal_range="Within 10%",
            explanation=f"Actual spending variance is {adherence_delta_pct:.1f}% vs plan.",
        ),
    ]


def _top_insights(category_items: list[CategoryPerformanceItem]) -> list[str]:
    sorted_items = sorted(category_items, key=lambda c: c.delta)
    insights: list[str] = []

    overspent = [c for c in category_items if c.delta > 0]
    underspent = [c for c in category_items if c.delta < 0]

    if overspent:
        top = max(overspent, key=lambda c: c.delta)
        insights.append(f"{top.category_name} is over budget by ${top.delta:.2f}.")
    if underspent:
        top = min(underspent, key=lambda c: c.delta)
        insights.append(f"{top.category_name} is under budget by ${abs(top.delta):.2f}.")
    if len(sorted_items) >= 2:
        insights.append("Your largest spending swings are concentrated in 1-2 categories.")

    return insights[:4]


def _recommendation(category_items: list[CategoryPerformanceItem]) -> str:
    overspent = [c for c in category_items if c.delta > 0]
    if not overspent:
        return "Keep current allocations and move surplus into savings this month."

    top = max(overspent, key=lambda c: c.delta)
    return (
        f"Reduce {top.category_name} by ${top.delta:.2f} next month and redirect it to your savings target."
    )


def _to_response(report: FinancialReport) -> FinancialReportResponse:
    dimensions = [ScoreDimension(**item) for item in report.dimensions.get("items", [])]
    category_performance = [CategoryPerformanceItem(**item) for item in report.category_performance.get("items", [])]
    insights = list(report.insights.get("items", []))

    return FinancialReportResponse(
        report_id=report.id,
        month=report.month,
        overall_score=report.overall_score,
        grade=report.grade,
        narrative=report.narrative,
        dimensions=dimensions,
        category_performance=category_performance,
        insights=insights,
        recommendation=report.recommendation,
        created_at=report.created_at.isoformat(),
    )


def generate_financial_report(db: Session, user_id: str) -> FinancialReportResponse:
    budget = _find_budget_for_user(db, user_id)
    summary = get_budget_summary(db, user_id)

    month = summary.month
    categories = db.execute(
        select(BudgetCategory).where(BudgetCategory.budget_id == budget.id).order_by(BudgetCategory.created_at.asc())
    ).scalars().all()

    goal_planned = sum(float(c.planned_amount) for c in categories if c.category_type == "goal")
    estimated_income = max(1.0, summary.total_planned + goal_planned)

    debt_planned = sum(
        float(c.planned_amount)
        for c in categories
        if any(keyword in c.name.lower() for keyword in ("debt", "loan", "credit"))
    )
    debt_ratio = (debt_planned / estimated_income) * 100 if estimated_income > 0 else 0.0

    essential = [c for c in summary.categories if c.category_type == "fixed"]
    essential_spend = sum(c.spent_amount for c in essential)

    goals = db.execute(select(Goal).where(Goal.user_id == user_id)).scalars().all()
    emergency_goal = next((g for g in goals if "emergency" in g.name.lower()), None)
    emergency_current = emergency_goal.current_amount if emergency_goal else 0.0
    monthly_essential = max(1.0, essential_spend if essential_spend > 0 else sum(c.planned_amount for c in essential))
    emergency_months = emergency_current / monthly_essential

    discretionary = [c for c in summary.categories if c.category_type == "variable"]
    discretionary_spend = sum(c.spent_amount for c in discretionary)
    discretionary_ratio = (discretionary_spend / estimated_income) * 100 if estimated_income > 0 else 0.0

    adherence_delta_pct = (
        abs(summary.total_spent - summary.total_planned) / summary.total_planned * 100
        if summary.total_planned > 0
        else 0.0
    )

    dimensions = _build_dimensions(
        estimated_income=estimated_income,
        total_spent=summary.total_spent,
        total_planned=summary.total_planned,
        goal_planned=goal_planned,
        debt_ratio=debt_ratio,
        emergency_months=emergency_months,
        discretionary_ratio=discretionary_ratio,
        adherence_delta_pct=adherence_delta_pct,
    )

    category_items: list[CategoryPerformanceItem] = []
    for cat in summary.categories:
        delta = round(cat.spent_amount - cat.planned_amount, 2)
        comment = "Over plan" if delta > 0 else "Under plan" if delta < 0 else "On plan"
        category_items.append(
            CategoryPerformanceItem(
                category_name=cat.name,
                planned_amount=cat.planned_amount,
                actual_amount=cat.spent_amount,
                delta=delta,
                comment=comment,
            )
        )

    insights = _top_insights(category_items)
    recommendation = _recommendation(category_items)

    overall_score = round(sum(d.score for d in dimensions) / len(dimensions), 2)
    grade = _grade(overall_score)

    narrative = (
        f"This month you spent ${summary.total_spent:.2f} against a plan of ${summary.total_planned:.2f}. "
        f"Your financial health score is {overall_score:.0f} ({grade})."
    )

    report = FinancialReport(
        user_id=user_id,
        budget_id=budget.id,
        month=month,
        overall_score=overall_score,
        grade=grade,
        narrative=narrative,
        dimensions={"items": [d.model_dump() for d in dimensions]},
        category_performance={"items": [item.model_dump() for item in category_items]},
        insights={"items": insights},
        recommendation=recommendation,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return _to_response(report)


def get_latest_financial_report(db: Session, user_id: str) -> FinancialReportResponse:
    report = db.execute(
        select(FinancialReport).where(FinancialReport.user_id == user_id).order_by(FinancialReport.created_at.desc())
    ).scalars().first()

    if report is None:
        return generate_financial_report(db, user_id)

    return _to_response(report)


def list_financial_reports(db: Session, user_id: str) -> list[FinancialReportResponse]:
    rows = db.execute(
        select(FinancialReport).where(FinancialReport.user_id == user_id).order_by(FinancialReport.created_at.desc())
    ).scalars().all()
    return [_to_response(row) for row in rows]
