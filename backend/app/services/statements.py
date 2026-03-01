import csv
import io
import re
from datetime import datetime, timedelta, timezone

from pypdf import PdfReader
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.db.models import Budget, BudgetCategory, StatementEntry, StatementUpload, Transaction
from app.schemas.statements import (
    ConfirmGapResponse,
    ReconciliationEntry,
    ReconciliationResponse,
    StatementListItem,
    StatementUploadResponse,
)


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


def _suggest_category(text: str, categories: list[BudgetCategory]) -> tuple[str, float]:
    lowered = text.lower()
    key_map = _category_keywords()

    for cat in categories:
        cat_name = cat.name.lower().strip()
        if cat_name in key_map and any(keyword in lowered for keyword in key_map[cat_name]):
            return cat.name, 0.86

    for cat in categories:
        if cat.category_type == "variable":
            return cat.name, 0.62

    return categories[0].name, 0.55


def _extract_amount(text: str) -> float:
    match = re.search(r"[-+]?\$?([0-9]+(?:\.[0-9]{1,2})?)", text)
    if not match:
        raise ValueError("Unable to parse amount")
    return float(match.group(1))


def _parse_date(value: str) -> datetime:
    cleaned = value.strip()
    formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%b %d %Y", "%d %b %Y"]
    for fmt in formats:
        try:
            return datetime.strptime(cleaned, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return datetime.now(timezone.utc)


def _normalize_row(row: dict[str, str]) -> tuple[datetime, str, float, str]:
    normalized = {k.lower().strip(): (v or "").strip() for k, v in row.items()}

    date_val = normalized.get("date") or normalized.get("transaction_date") or normalized.get("posted_date") or ""
    desc = normalized.get("description") or normalized.get("merchant") or normalized.get("details") or ""

    amount_raw = normalized.get("amount") or normalized.get("debit") or normalized.get("value") or ""
    if not amount_raw and normalized.get("credit"):
        amount_raw = normalized["credit"]

    amount = _extract_amount(amount_raw)
    merchant = (normalized.get("merchant") or desc.split(" ")[0] or "Expense").strip().title()

    return _parse_date(date_val), merchant, amount, desc or merchant


def _parse_csv_entries(content: bytes) -> list[tuple[datetime, str, float, str]]:
    text = content.decode("utf-8-sig", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))
    entries: list[tuple[datetime, str, float, str]] = []
    for row in reader:
        if not row:
            continue
        try:
            entries.append(_normalize_row(row))
        except ValueError:
            continue
    return entries


def _parse_pdf_entries(content: bytes) -> list[tuple[datetime, str, float, str]]:
    reader = PdfReader(io.BytesIO(content))
    lines: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        lines.extend([ln.strip() for ln in text.splitlines() if ln.strip()])

    entries: list[tuple[datetime, str, float, str]] = []
    pattern = re.compile(r"(?P<date>\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}).*?(?P<amount>[-+]?\$?[0-9]+(?:\.[0-9]{1,2})?)$")

    for line in lines:
        match = pattern.search(line)
        if not match:
            continue
        date_val = _parse_date(match.group("date"))
        amount = _extract_amount(match.group("amount"))
        description = line.replace(match.group("date"), "").replace(match.group("amount"), "").strip(" -")
        merchant = description.split(" ")[0].strip().title() if description else "Expense"
        entries.append((date_val, merchant, amount, description or merchant))

    return entries


def upload_statement(
    db: Session,
    user_id: str,
    account_name: str,
    filename: str,
    content: bytes,
) -> StatementUploadResponse:
    budget = _find_budget_for_user(db, user_id)
    categories = db.execute(select(BudgetCategory).where(BudgetCategory.budget_id == budget.id)).scalars().all()
    if not categories:
        raise ValueError("Budget exists but has no categories.")

    lowered_name = filename.lower()
    if lowered_name.endswith(".csv"):
        source_type = "csv"
        entries = _parse_csv_entries(content)
    elif lowered_name.endswith(".pdf"):
        source_type = "pdf"
        entries = _parse_pdf_entries(content)
    else:
        raise ValueError("Unsupported file type. Upload CSV or PDF.")

    statement = StatementUpload(
        user_id=user_id,
        budget_id=budget.id,
        account_name=account_name or "Primary Account",
        filename=filename,
        source_type=source_type,
        status="processed",
        transactions_found=len(entries),
    )
    db.add(statement)
    db.flush()

    for entry_date, merchant, amount, description in entries:
        suggested_category, confidence = _suggest_category(f"{merchant} {description}", categories)
        db.add(
            StatementEntry(
                statement_id=statement.id,
                amount=amount,
                merchant=merchant,
                description=description,
                entry_date=entry_date,
                suggested_category=suggested_category,
                confidence=confidence,
                status="unmatched",
            )
        )

    db.flush()
    reconciliation = get_reconciliation(db, user_id=user_id, statement_id=statement.id)
    statement.needs_attention_count = len(reconciliation.gaps)
    db.commit()

    return StatementUploadResponse(
        statement_id=statement.id,
        account_name=statement.account_name,
        filename=statement.filename,
        source_type=statement.source_type,
        status=statement.status,
        transactions_found=statement.transactions_found,
        needs_attention_count=statement.needs_attention_count,
    )


def list_statements(db: Session, user_id: str) -> list[StatementListItem]:
    rows = db.execute(
        select(StatementUpload).where(StatementUpload.user_id == user_id).order_by(StatementUpload.created_at.desc())
    ).scalars().all()

    return [
        StatementListItem(
            statement_id=row.id,
            account_name=row.account_name,
            filename=row.filename,
            source_type=row.source_type,
            status=row.status,
            transactions_found=row.transactions_found,
            needs_attention_count=row.needs_attention_count,
            created_at=row.created_at.isoformat(),
        )
        for row in rows
    ]


def _as_entry_payload(entry: StatementEntry) -> ReconciliationEntry:
    return ReconciliationEntry(
        entry_id=entry.id,
        amount=entry.amount,
        merchant=entry.merchant,
        description=entry.description,
        entry_date=entry.entry_date.isoformat(),
        suggested_category=entry.suggested_category,
        confidence=entry.confidence,
        matched_transaction_id=entry.matched_transaction_id,
    )


def get_reconciliation(db: Session, user_id: str, statement_id: str) -> ReconciliationResponse:
    statement = db.execute(
        select(StatementUpload).where(StatementUpload.id == statement_id, StatementUpload.user_id == user_id)
    ).scalars().first()
    if statement is None:
        raise ValueError("Statement not found for user")

    entries = db.execute(
        select(StatementEntry).where(StatementEntry.statement_id == statement_id).order_by(StatementEntry.entry_date.asc())
    ).scalars().all()

    matched: list[ReconciliationEntry] = []
    gaps: list[ReconciliationEntry] = []
    matched_transaction_ids: set[str] = set()

    for entry in entries:
        matched_txn = None
        if entry.matched_transaction_id:
            matched_txn = db.get(Transaction, entry.matched_transaction_id)

        if matched_txn is None:
            candidate = db.execute(
                select(Transaction)
                .where(
                    Transaction.user_id == user_id,
                    Transaction.budget_id == statement.budget_id,
                    Transaction.amount == entry.amount,
                    Transaction.transaction_date >= (entry.entry_date - timedelta(days=2)),
                    Transaction.transaction_date <= (entry.entry_date + timedelta(days=2)),
                )
                .order_by(Transaction.created_at.desc())
            ).scalars().first()

            if candidate is not None:
                entry.matched_transaction_id = candidate.id
                entry.status = "matched"
                matched_txn = candidate
            else:
                entry.matched_transaction_id = None
                entry.status = "gap"

        if matched_txn is not None:
            matched_transaction_ids.add(matched_txn.id)
            matched.append(_as_entry_payload(entry))
        else:
            gaps.append(_as_entry_payload(entry))

    db.flush()

    start_date = min((e.entry_date for e in entries), default=datetime.now(timezone.utc) - timedelta(days=31))
    end_date = max((e.entry_date for e in entries), default=datetime.now(timezone.utc)) + timedelta(days=1)

    orphan_query = select(Transaction).where(
        Transaction.user_id == user_id,
        Transaction.budget_id == statement.budget_id,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date,
    )
    if matched_transaction_ids:
        orphan_query = orphan_query.where(Transaction.id.not_in(list(matched_transaction_ids)))
    orphan_rows = db.execute(orphan_query.order_by(Transaction.transaction_date.desc())).scalars().all()

    orphans = [
        {
            "transaction_id": txn.id,
            "amount": txn.amount,
            "merchant": txn.merchant,
            "description": txn.description,
            "transaction_date": txn.transaction_date.isoformat(),
        }
        for txn in orphan_rows
    ]

    statement.needs_attention_count = len(gaps)
    db.commit()

    return ReconciliationResponse(
        statement_id=statement.id,
        matched=matched,
        gaps=gaps,
        orphans=orphans,
    )


def confirm_gap(
    db: Session,
    user_id: str,
    statement_id: str,
    entry_id: str,
    category_name: str | None,
) -> ConfirmGapResponse:
    statement = db.execute(
        select(StatementUpload).where(StatementUpload.id == statement_id, StatementUpload.user_id == user_id)
    ).scalars().first()
    if statement is None:
        raise ValueError("Statement not found for user")

    entry = db.execute(
        select(StatementEntry).where(StatementEntry.id == entry_id, StatementEntry.statement_id == statement_id)
    ).scalars().first()
    if entry is None:
        raise ValueError("Statement entry not found")

    budget_categories = db.execute(
        select(BudgetCategory).where(BudgetCategory.budget_id == statement.budget_id)
    ).scalars().all()
    if not budget_categories:
        raise ValueError("Budget has no categories")

    target_category = None
    if category_name:
        target_category = next((c for c in budget_categories if c.name.lower() == category_name.lower()), None)
    if target_category is None:
        suggested = entry.suggested_category.lower()
        target_category = next((c for c in budget_categories if c.name.lower() == suggested), None)
    if target_category is None:
        target_category = budget_categories[0]

    txn = Transaction(
        user_id=user_id,
        budget_id=statement.budget_id,
        category_id=target_category.id,
        amount=entry.amount,
        merchant=entry.merchant,
        description=entry.description,
        source_text=f"statement:{statement.filename}",
        transaction_date=entry.entry_date,
    )
    db.add(txn)
    db.flush()

    entry.matched_transaction_id = txn.id
    entry.status = "matched"

    gap_count = db.execute(
        select(func.count()).select_from(StatementEntry).where(
            and_(StatementEntry.statement_id == statement_id, StatementEntry.status.in_(["gap", "unmatched"]))
        )
    ).scalar_one()
    statement.needs_attention_count = int(gap_count)

    db.commit()

    return ConfirmGapResponse(
        entry_id=entry.id,
        status=entry.status,
        created_transaction_id=txn.id,
        confirmation=f"Logged ${entry.amount:.2f} -> {target_category.name}",
    )
