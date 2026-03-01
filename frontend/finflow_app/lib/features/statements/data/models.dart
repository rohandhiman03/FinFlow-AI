class StatementListItem {
  const StatementListItem({
    required this.statementId,
    required this.accountName,
    required this.filename,
    required this.sourceType,
    required this.status,
    required this.transactionsFound,
    required this.needsAttentionCount,
    required this.createdAt,
  });

  final String statementId;
  final String accountName;
  final String filename;
  final String sourceType;
  final String status;
  final int transactionsFound;
  final int needsAttentionCount;
  final String createdAt;

  factory StatementListItem.fromJson(Map<String, dynamic> json) {
    return StatementListItem(
      statementId: json['statement_id'] as String,
      accountName: json['account_name'] as String,
      filename: json['filename'] as String,
      sourceType: json['source_type'] as String,
      status: json['status'] as String,
      transactionsFound: json['transactions_found'] as int,
      needsAttentionCount: json['needs_attention_count'] as int,
      createdAt: json['created_at'] as String,
    );
  }
}

class ReconciliationEntry {
  const ReconciliationEntry({
    required this.entryId,
    required this.amount,
    required this.merchant,
    required this.description,
    required this.entryDate,
    required this.suggestedCategory,
    required this.confidence,
    this.matchedTransactionId,
  });

  final String entryId;
  final double amount;
  final String merchant;
  final String description;
  final String entryDate;
  final String suggestedCategory;
  final double confidence;
  final String? matchedTransactionId;

  factory ReconciliationEntry.fromJson(Map<String, dynamic> json) {
    return ReconciliationEntry(
      entryId: json['entry_id'] as String,
      amount: (json['amount'] as num).toDouble(),
      merchant: json['merchant'] as String,
      description: json['description'] as String,
      entryDate: json['entry_date'] as String,
      suggestedCategory: json['suggested_category'] as String,
      confidence: (json['confidence'] as num).toDouble(),
      matchedTransactionId: json['matched_transaction_id'] as String?,
    );
  }
}

class ReconciliationData {
  const ReconciliationData({
    required this.statementId,
    required this.matched,
    required this.gaps,
    required this.orphans,
  });

  final String statementId;
  final List<ReconciliationEntry> matched;
  final List<ReconciliationEntry> gaps;
  final List<Map<String, dynamic>> orphans;

  factory ReconciliationData.fromJson(Map<String, dynamic> json) {
    return ReconciliationData(
      statementId: json['statement_id'] as String,
      matched: (json['matched'] as List<dynamic>)
          .map((e) => ReconciliationEntry.fromJson(e as Map<String, dynamic>))
          .toList(growable: false),
      gaps: (json['gaps'] as List<dynamic>)
          .map((e) => ReconciliationEntry.fromJson(e as Map<String, dynamic>))
          .toList(growable: false),
      orphans: (json['orphans'] as List<dynamic>).cast<Map<String, dynamic>>(),
    );
  }
}

class StatementUploadResult {
  const StatementUploadResult({
    required this.statementId,
    required this.transactionsFound,
    required this.needsAttentionCount,
  });

  final String statementId;
  final int transactionsFound;
  final int needsAttentionCount;

  factory StatementUploadResult.fromJson(Map<String, dynamic> json) {
    return StatementUploadResult(
      statementId: json['statement_id'] as String,
      transactionsFound: json['transactions_found'] as int,
      needsAttentionCount: json['needs_attention_count'] as int,
    );
  }
}
