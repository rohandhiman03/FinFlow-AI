import 'package:finflow_app/features/onboarding/data/models.dart';
import 'package:finflow_app/features/onboarding/data/onboarding_api.dart';
import 'package:finflow_app/main.dart';
import 'package:flutter_test/flutter_test.dart';

class FakeOnboardingApi implements OnboardingApi {
  FakeOnboardingApi()
    : _state = const OnboardingSessionState(
        sessionId: 'session-1',
        status: 'active',
        currentStep: 'income',
        provider: 'claude',
        messages: [
          OnboardingMessage(
            role: 'assistant',
            content: 'What is your income and frequency?',
          ),
        ],
      );

  OnboardingSessionState _state;

  @override
  Future<OnboardingSessionState> startSession({bool resetExisting = true}) async {
    return _state;
  }

  @override
  Future<OnboardingSessionState> sendMessage({
    required String sessionId,
    required String message,
  }) async {
    final nextMessages = <OnboardingMessage>[
      ..._state.messages,
      OnboardingMessage(role: 'user', content: message),
      const OnboardingMessage(role: 'assistant', content: 'Thanks, next question.'),
    ];

    _state = OnboardingSessionState(
      sessionId: sessionId,
      status: 'active',
      currentStep: 'fixed_expenses',
      provider: 'claude',
      messages: nextMessages,
    );

    return _state;
  }
}

void main() {
  testWidgets('renders onboarding chat and initial assistant message', (WidgetTester tester) async {
    await tester.pumpWidget(FinFlowApp(api: FakeOnboardingApi()));
    await tester.pumpAndSettle();

    expect(find.text('FinFlow AI - Phase 2 Onboarding'), findsOneWidget);
    expect(find.text('What is your income and frequency?'), findsOneWidget);
  });
}
