import 'package:finflow_app/main.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('shows foundation status content', (WidgetTester tester) async {
    await tester.pumpWidget(const FinFlowApp());

    expect(find.text('FinFlow AI - Phase 1'), findsOneWidget);
    expect(find.textContaining('Active AI provider:'), findsOneWidget);
  });
}
