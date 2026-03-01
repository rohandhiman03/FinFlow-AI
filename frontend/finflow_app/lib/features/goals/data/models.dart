class GoalItem {
  const GoalItem({
    required this.goalId,
    required this.name,
    required this.targetAmount,
    required this.currentAmount,
    required this.progressPct,
    required this.targetDate,
    required this.requiredMonthly,
    required this.onTrack,
  });

  final String goalId;
  final String name;
  final double targetAmount;
  final double currentAmount;
  final double progressPct;
  final String targetDate;
  final double requiredMonthly;
  final bool onTrack;

  factory GoalItem.fromJson(Map<String, dynamic> json) {
    return GoalItem(
      goalId: json['goal_id'] as String,
      name: json['name'] as String,
      targetAmount: (json['target_amount'] as num).toDouble(),
      currentAmount: (json['current_amount'] as num).toDouble(),
      progressPct: (json['progress_pct'] as num).toDouble(),
      targetDate: json['target_date'] as String,
      requiredMonthly: (json['required_monthly'] as num).toDouble(),
      onTrack: json['on_track'] as bool,
    );
  }
}

class GoalContributeResult {
  const GoalContributeResult({
    required this.goalId,
    required this.currentAmount,
    required this.progressPct,
    required this.confirmation,
  });

  final String goalId;
  final double currentAmount;
  final double progressPct;
  final String confirmation;

  factory GoalContributeResult.fromJson(Map<String, dynamic> json) {
    return GoalContributeResult(
      goalId: json['goal_id'] as String,
      currentAmount: (json['current_amount'] as num).toDouble(),
      progressPct: (json['progress_pct'] as num).toDouble(),
      confirmation: json['confirmation'] as String,
    );
  }
}
