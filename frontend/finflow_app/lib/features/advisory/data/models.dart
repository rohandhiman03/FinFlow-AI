class AdvisorySuggestion {
  const AdvisorySuggestion({
    required this.suggestionId,
    required this.title,
    required this.summary,
    required this.adjustments,
  });

  final String suggestionId;
  final String title;
  final String summary;
  final List<Map<String, dynamic>> adjustments;

  factory AdvisorySuggestion.fromJson(Map<String, dynamic> json) {
    return AdvisorySuggestion(
      suggestionId: json['suggestion_id'] as String,
      title: json['title'] as String,
      summary: json['summary'] as String,
      adjustments: (json['adjustments'] as List<dynamic>).cast<Map<String, dynamic>>(),
    );
  }
}

class AdvisoryAskResult {
  const AdvisoryAskResult({
    required this.sessionId,
    required this.answer,
    required this.reasoning,
    required this.suggestions,
  });

  final String sessionId;
  final String answer;
  final List<String> reasoning;
  final List<AdvisorySuggestion> suggestions;

  factory AdvisoryAskResult.fromJson(Map<String, dynamic> json) {
    return AdvisoryAskResult(
      sessionId: json['session_id'] as String,
      answer: json['answer'] as String,
      reasoning: (json['reasoning'] as List<dynamic>).map((e) => e.toString()).toList(growable: false),
      suggestions: (json['suggestions'] as List<dynamic>)
          .map((s) => AdvisorySuggestion.fromJson(s as Map<String, dynamic>))
          .toList(growable: false),
    );
  }
}

class AdvisoryApplyResult {
  const AdvisoryApplyResult({
    required this.suggestionId,
    required this.status,
    required this.confirmation,
  });

  final String suggestionId;
  final String status;
  final String confirmation;

  factory AdvisoryApplyResult.fromJson(Map<String, dynamic> json) {
    return AdvisoryApplyResult(
      suggestionId: json['suggestion_id'] as String,
      status: json['status'] as String,
      confirmation: json['confirmation'] as String,
    );
  }
}
