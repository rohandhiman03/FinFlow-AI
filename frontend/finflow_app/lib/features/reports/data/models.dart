class ScoreDimension {
  const ScoreDimension({
    required this.name,
    required this.score,
    required this.value,
    required this.idealRange,
    required this.explanation,
  });

  final String name;
  final double score;
  final double value;
  final String idealRange;
  final String explanation;

  factory ScoreDimension.fromJson(Map<String, dynamic> json) {
    return ScoreDimension(
      name: json['name'] as String,
      score: (json['score'] as num).toDouble(),
      value: (json['value'] as num).toDouble(),
      idealRange: json['ideal_range'] as String,
      explanation: json['explanation'] as String,
    );
  }
}

class CategoryPerformanceItem {
  const CategoryPerformanceItem({
    required this.categoryName,
    required this.plannedAmount,
    required this.actualAmount,
    required this.delta,
    required this.comment,
  });

  final String categoryName;
  final double plannedAmount;
  final double actualAmount;
  final double delta;
  final String comment;

  factory CategoryPerformanceItem.fromJson(Map<String, dynamic> json) {
    return CategoryPerformanceItem(
      categoryName: json['category_name'] as String,
      plannedAmount: (json['planned_amount'] as num).toDouble(),
      actualAmount: (json['actual_amount'] as num).toDouble(),
      delta: (json['delta'] as num).toDouble(),
      comment: json['comment'] as String,
    );
  }
}

class FinancialReport {
  const FinancialReport({
    required this.reportId,
    required this.month,
    required this.overallScore,
    required this.grade,
    required this.narrative,
    required this.dimensions,
    required this.categoryPerformance,
    required this.insights,
    required this.recommendation,
    required this.createdAt,
  });

  final String reportId;
  final String month;
  final double overallScore;
  final String grade;
  final String narrative;
  final List<ScoreDimension> dimensions;
  final List<CategoryPerformanceItem> categoryPerformance;
  final List<String> insights;
  final String recommendation;
  final String createdAt;

  factory FinancialReport.fromJson(Map<String, dynamic> json) {
    return FinancialReport(
      reportId: json['report_id'] as String,
      month: json['month'] as String,
      overallScore: (json['overall_score'] as num).toDouble(),
      grade: json['grade'] as String,
      narrative: json['narrative'] as String,
      dimensions: (json['dimensions'] as List<dynamic>)
          .map((d) => ScoreDimension.fromJson(d as Map<String, dynamic>))
          .toList(growable: false),
      categoryPerformance: (json['category_performance'] as List<dynamic>)
          .map((c) => CategoryPerformanceItem.fromJson(c as Map<String, dynamic>))
          .toList(growable: false),
      insights: (json['insights'] as List<dynamic>).map((e) => e.toString()).toList(growable: false),
      recommendation: json['recommendation'] as String,
      createdAt: json['created_at'] as String,
    );
  }
}
