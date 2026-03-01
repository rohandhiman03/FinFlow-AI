import 'package:finflow_app/features/dashboard/data/dashboard_api.dart';
import 'package:finflow_app/features/dashboard/ui/dashboard_screen.dart';
import 'package:finflow_app/features/onboarding/data/onboarding_api.dart';
import 'package:finflow_app/features/onboarding/ui/onboarding_chat_screen.dart';
import 'package:finflow_app/features/statements/data/statements_api.dart';
import 'package:finflow_app/features/statements/ui/statements_screen.dart';
import 'package:flutter/material.dart';

void main() {
  runApp(const FinFlowApp());
}

enum AppStage {
  loading,
  onboarding,
  dashboard,
}

class FinFlowApp extends StatelessWidget {
  const FinFlowApp({
    super.key,
    this.onboardingApi,
    this.dashboardApi,
    this.statementsApi,
  });

  final OnboardingApi? onboardingApi;
  final DashboardApi? dashboardApi;
  final StatementsApi? statementsApi;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FinFlow AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF6C63FF)),
      ),
      home: FinFlowAppShell(
        onboardingApi: onboardingApi ?? BackendOnboardingApi(),
        dashboardApi: dashboardApi ?? BackendDashboardApi(),
        statementsApi: statementsApi ?? BackendStatementsApi(),
      ),
    );
  }
}

class FinFlowAppShell extends StatefulWidget {
  const FinFlowAppShell({
    super.key,
    required this.onboardingApi,
    required this.dashboardApi,
    required this.statementsApi,
  });

  final OnboardingApi onboardingApi;
  final DashboardApi dashboardApi;
  final StatementsApi statementsApi;

  @override
  State<FinFlowAppShell> createState() => _FinFlowAppShellState();
}

class _FinFlowAppShellState extends State<FinFlowAppShell> {
  AppStage _stage = AppStage.loading;

  @override
  void initState() {
    super.initState();
    _bootstrap();
  }

  Future<void> _bootstrap() async {
    try {
      await widget.dashboardApi.getBudgetSummary();
      if (!mounted) {
        return;
      }
      setState(() {
        _stage = AppStage.dashboard;
      });
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() {
        _stage = AppStage.onboarding;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_stage == AppStage.loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    if (_stage == AppStage.onboarding) {
      return OnboardingChatScreen(
        api: widget.onboardingApi,
        onCompleted: () {
          setState(() {
            _stage = AppStage.dashboard;
          });
        },
      );
    }

    return DashboardScreen(
      api: widget.dashboardApi,
      onRestartOnboarding: () {
        setState(() {
          _stage = AppStage.onboarding;
        });
      },
      onOpenStatements: () {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => StatementsScreen(api: widget.statementsApi),
          ),
        );
      },
    );
  }
}
