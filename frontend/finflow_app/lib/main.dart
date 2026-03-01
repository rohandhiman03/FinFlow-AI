import 'package:finflow_app/features/onboarding/data/onboarding_api.dart';
import 'package:finflow_app/features/onboarding/ui/onboarding_chat_screen.dart';
import 'package:flutter/material.dart';

void main() {
  runApp(const FinFlowApp());
}

class FinFlowApp extends StatelessWidget {
  const FinFlowApp({super.key, this.api});

  final OnboardingApi? api;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FinFlow AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF6C63FF)),
      ),
      home: OnboardingChatScreen(api: api ?? BackendOnboardingApi()),
    );
  }
}
