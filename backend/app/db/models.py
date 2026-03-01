from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OnboardingSession(Base):
    __tablename__ = "onboarding_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    current_step: Mapped[str] = mapped_column(String(32), default="income")
    collected_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    messages: Mapped[list["OnboardingMessage"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="OnboardingMessage.created_at"
    )


class OnboardingMessage(Base):
    __tablename__ = "onboarding_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("onboarding_sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    session: Mapped[OnboardingSession] = relationship(back_populates="messages")


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(80), default="Primary Budget")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class BudgetCategory(Base):
    __tablename__ = "budget_categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    budget_id: Mapped[str] = mapped_column(String(36), ForeignKey("budgets.id"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    category_type: Mapped[str] = mapped_column(String(20))
    planned_amount: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    target_amount: Mapped[float] = mapped_column(Float)
    target_date: Mapped[str] = mapped_column(String(30), default="")
    current_amount: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), index=True)
    budget_id: Mapped[str] = mapped_column(String(36), ForeignKey("budgets.id"), index=True)
    category_id: Mapped[str] = mapped_column(String(36), ForeignKey("budget_categories.id"), index=True)
    amount: Mapped[float] = mapped_column(Float)
    merchant: Mapped[str] = mapped_column(String(120), default="")
    description: Mapped[str] = mapped_column(Text)
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    source_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class StatementUpload(Base):
    __tablename__ = "statement_uploads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), index=True)
    budget_id: Mapped[str] = mapped_column(String(36), ForeignKey("budgets.id"), index=True)
    account_name: Mapped[str] = mapped_column(String(120), default="Primary Account")
    filename: Mapped[str] = mapped_column(String(255), default="")
    source_type: Mapped[str] = mapped_column(String(20), default="csv")
    status: Mapped[str] = mapped_column(String(20), default="processed")
    transactions_found: Mapped[int] = mapped_column(Integer, default=0)
    needs_attention_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class StatementEntry(Base):
    __tablename__ = "statement_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    statement_id: Mapped[str] = mapped_column(String(36), ForeignKey("statement_uploads.id"), index=True)
    amount: Mapped[float] = mapped_column(Float)
    merchant: Mapped[str] = mapped_column(String(160), default="")
    description: Mapped[str] = mapped_column(Text)
    entry_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    suggested_category: Mapped[str] = mapped_column(String(80), default="Lifestyle")
    confidence: Mapped[float] = mapped_column(Float, default=0.6)
    status: Mapped[str] = mapped_column(String(20), default="unmatched")
    matched_transaction_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("transactions.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class FinancialReport(Base):
    __tablename__ = "financial_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), index=True)
    budget_id: Mapped[str] = mapped_column(String(36), ForeignKey("budgets.id"), index=True)
    month: Mapped[str] = mapped_column(String(7), index=True)  # YYYY-MM
    overall_score: Mapped[float] = mapped_column(Float)
    grade: Mapped[str] = mapped_column(String(2))
    narrative: Mapped[str] = mapped_column(Text)
    dimensions: Mapped[dict] = mapped_column(JSON, default=dict)
    category_performance: Mapped[dict] = mapped_column(JSON, default=dict)
    insights: Mapped[dict] = mapped_column(JSON, default=dict)
    recommendation: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
