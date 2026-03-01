class OnboardingMessage {
  const OnboardingMessage({
    required this.role,
    required this.content,
  });

  final String role;
  final String content;

  factory OnboardingMessage.fromJson(Map<String, dynamic> json) {
    return OnboardingMessage(
      role: json['role'] as String,
      content: json['content'] as String,
    );
  }
}

class OnboardingSessionState {
  const OnboardingSessionState({
    required this.sessionId,
    required this.status,
    required this.currentStep,
    required this.provider,
    required this.messages,
    this.budgetProposal,
  });

  final String sessionId;
  final String status;
  final String currentStep;
  final String provider;
  final List<OnboardingMessage> messages;
  final Map<String, dynamic>? budgetProposal;

  factory OnboardingSessionState.fromJson(Map<String, dynamic> json) {
    return OnboardingSessionState(
      sessionId: json['session_id'] as String,
      status: json['status'] as String,
      currentStep: json['current_step'] as String,
      provider: json['provider'] as String,
      messages: (json['messages'] as List<dynamic>)
          .map((m) => OnboardingMessage.fromJson(m as Map<String, dynamic>))
          .toList(growable: false),
      budgetProposal: json['budget_proposal'] as Map<String, dynamic>?,
    );
  }
}
