class BudgetCategorySummary {
  const BudgetCategorySummary({
    required this.categoryId,
    required this.name,
    required this.categoryType,
    required this.plannedAmount,
    required this.spentAmount,
    required this.remainingAmount,
    required this.utilizationPct,
    required this.status,
  });

  final String categoryId;
  final String name;
  final String categoryType;
  final double plannedAmount;
  final double spentAmount;
  final double remainingAmount;
  final double utilizationPct;
  final String status;

  factory BudgetCategorySummary.fromJson(Map<String, dynamic> json) {
    return BudgetCategorySummary(
      categoryId: json['category_id'] as String,
      name: json['name'] as String,
      categoryType: json['category_type'] as String,
      plannedAmount: (json['planned_amount'] as num).toDouble(),
      spentAmount: (json['spent_amount'] as num).toDouble(),
      remainingAmount: (json['remaining_amount'] as num).toDouble(),
      utilizationPct: (json['utilization_pct'] as num).toDouble(),
      status: json['status'] as String,
    );
  }
}

class BudgetSummary {
  const BudgetSummary({
    required this.budgetId,
    required this.month,
    required this.totalPlanned,
    required this.totalSpent,
    required this.totalRemaining,
    required this.daysLeftInCycle,
    required this.projectedEndOfMonthPosition,
    required this.categories,
  });

  final String budgetId;
  final String month;
  final double totalPlanned;
  final double totalSpent;
  final double totalRemaining;
  final int daysLeftInCycle;
  final double projectedEndOfMonthPosition;
  final List<BudgetCategorySummary> categories;

  factory BudgetSummary.fromJson(Map<String, dynamic> json) {
    return BudgetSummary(
      budgetId: json['budget_id'] as String,
      month: json['month'] as String,
      totalPlanned: (json['total_planned'] as num).toDouble(),
      totalSpent: (json['total_spent'] as num).toDouble(),
      totalRemaining: (json['total_remaining'] as num).toDouble(),
      daysLeftInCycle: json['days_left_in_cycle'] as int,
      projectedEndOfMonthPosition: (json['projected_end_of_month_position'] as num).toDouble(),
      categories: (json['categories'] as List<dynamic>)
          .map((entry) => BudgetCategorySummary.fromJson(entry as Map<String, dynamic>))
          .toList(growable: false),
    );
  }
}

class ExpenseLogResult {
  const ExpenseLogResult({
    required this.confirmation,
    required this.amount,
    required this.categoryName,
  });

  final String confirmation;
  final double amount;
  final String categoryName;

  factory ExpenseLogResult.fromJson(Map<String, dynamic> json) {
    final txn = json['transaction'] as Map<String, dynamic>;
    return ExpenseLogResult(
      confirmation: json['confirmation'] as String,
      amount: (txn['amount'] as num).toDouble(),
      categoryName: txn['category_name'] as String,
    );
  }
}
