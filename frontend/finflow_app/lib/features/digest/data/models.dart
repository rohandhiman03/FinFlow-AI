class DigestSettings {
  const DigestSettings({
    required this.frequency,
    required this.day,
    required this.time,
  });

  final String frequency;
  final String day;
  final String time;

  factory DigestSettings.fromJson(Map<String, dynamic> json) {
    return DigestSettings(
      frequency: json['frequency'] as String,
      day: json['day'] as String,
      time: json['time'] as String,
    );
  }
}

class WeeklyDigest {
  const WeeklyDigest({
    required this.periodStart,
    required this.periodEnd,
    required this.weeklySpent,
    required this.weeklyIncomeProxy,
    required this.savingsRatePct,
    required this.categoryToWatch,
    required this.upcomingExpenses,
    required this.digestText,
  });

  final String periodStart;
  final String periodEnd;
  final double weeklySpent;
  final double weeklyIncomeProxy;
  final double savingsRatePct;
  final String categoryToWatch;
  final List<Map<String, dynamic>> upcomingExpenses;
  final String digestText;

  factory WeeklyDigest.fromJson(Map<String, dynamic> json) {
    return WeeklyDigest(
      periodStart: json['period_start'] as String,
      periodEnd: json['period_end'] as String,
      weeklySpent: (json['weekly_spent'] as num).toDouble(),
      weeklyIncomeProxy: (json['weekly_income_proxy'] as num).toDouble(),
      savingsRatePct: (json['savings_rate_pct'] as num).toDouble(),
      categoryToWatch: json['category_to_watch'] as String,
      upcomingExpenses: (json['upcoming_expenses'] as List<dynamic>).cast<Map<String, dynamic>>(),
      digestText: json['digest_text'] as String,
    );
  }
}
