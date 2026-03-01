import 'package:finflow_app/features/advisory/data/advisory_api.dart';
import 'package:finflow_app/features/advisory/ui/advisory_screen.dart';
import 'package:finflow_app/features/dashboard/data/dashboard_api.dart';
import 'package:finflow_app/features/dashboard/ui/dashboard_screen.dart';
import 'package:finflow_app/features/digest/data/digest_api.dart';
import 'package:finflow_app/features/digest/ui/digest_screen.dart';
import 'package:finflow_app/features/goals/data/goals_api.dart';
import 'package:finflow_app/features/goals/ui/goals_screen.dart';
import 'package:finflow_app/features/onboarding/data/onboarding_api.dart';
import 'package:finflow_app/features/onboarding/ui/onboarding_chat_screen.dart';
import 'package:finflow_app/features/reports/data/reports_api.dart';
import 'package:finflow_app/features/reports/ui/reports_screen.dart';
import 'package:finflow_app/features/statements/data/statements_api.dart';
import 'package:finflow_app/features/statements/ui/statements_screen.dart';
import 'package:finflow_app/theme/app_theme.dart';
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
    this.advisoryApi,
    this.digestApi,
    this.onboardingApi,
    this.dashboardApi,
    this.goalsApi,
    this.statementsApi,
    this.reportsApi,
  });

  final AdvisoryApi? advisoryApi;
  final DigestApi? digestApi;
  final OnboardingApi? onboardingApi;
  final DashboardApi? dashboardApi;
  final GoalsApi? goalsApi;
  final StatementsApi? statementsApi;
  final ReportsApi? reportsApi;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FinFlow AI',
      debugShowCheckedModeBanner: false,
      theme: FinFlowTheme.light(),
      home: FinFlowAppShell(
        advisoryApi: advisoryApi ?? BackendAdvisoryApi(),
        digestApi: digestApi ?? BackendDigestApi(),
        onboardingApi: onboardingApi ?? BackendOnboardingApi(),
        dashboardApi: dashboardApi ?? BackendDashboardApi(),
        goalsApi: goalsApi ?? BackendGoalsApi(),
        statementsApi: statementsApi ?? BackendStatementsApi(),
        reportsApi: reportsApi ?? BackendReportsApi(),
      ),
    );
  }
}

class FinFlowAppShell extends StatefulWidget {
  const FinFlowAppShell({
    super.key,
    required this.advisoryApi,
    required this.digestApi,
    required this.onboardingApi,
    required this.dashboardApi,
    required this.goalsApi,
    required this.statementsApi,
    required this.reportsApi,
  });

  final AdvisoryApi advisoryApi;
  final DigestApi digestApi;
  final OnboardingApi onboardingApi;
  final DashboardApi dashboardApi;
  final GoalsApi goalsApi;
  final StatementsApi statementsApi;
  final ReportsApi reportsApi;

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
      onOpenAdvisory: () {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => AdvisoryScreen(api: widget.advisoryApi),
          ),
        );
      },
      onOpenDigest: () {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => DigestScreen(api: widget.digestApi),
          ),
        );
      },
      onOpenGoals: () {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => GoalsScreen(api: widget.goalsApi),
          ),
        );
      },
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
      onOpenReports: () {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => ReportsScreen(api: widget.reportsApi),
          ),
        );
      },
    );
  }
}
