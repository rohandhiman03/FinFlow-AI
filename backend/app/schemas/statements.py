from pydantic import BaseModel


class StatementUploadResponse(BaseModel):
    statement_id: str
    account_name: str
    filename: str
    source_type: str
    status: str
    transactions_found: int
    needs_attention_count: int


class StatementListItem(BaseModel):
    statement_id: str
    account_name: str
    filename: str
    source_type: str
    status: str
    transactions_found: int
    needs_attention_count: int
    created_at: str


class ReconciliationEntry(BaseModel):
    entry_id: str
    amount: float
    merchant: str
    description: str
    entry_date: str
    suggested_category: str
    confidence: float
    matched_transaction_id: str | None = None


class ReconciliationResponse(BaseModel):
    statement_id: str
    matched: list[ReconciliationEntry]
    gaps: list[ReconciliationEntry]
    orphans: list[dict[str, str | float]]


class ConfirmGapRequest(BaseModel):
    category_name: str | None = None


class ConfirmGapResponse(BaseModel):
    entry_id: str
    status: str
    created_transaction_id: str
    confirmation: str
