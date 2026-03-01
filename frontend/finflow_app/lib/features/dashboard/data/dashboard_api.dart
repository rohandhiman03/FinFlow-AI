import 'dart:convert';

import 'package:finflow_app/config/app_config.dart';
import 'package:finflow_app/features/dashboard/data/models.dart';
import 'package:http/http.dart' as http;

class NoBudgetException implements Exception {
  const NoBudgetException(this.message);
  final String message;

  @override
  String toString() => message;
}

abstract class DashboardApi {
  Future<BudgetSummary> getBudgetSummary();

  Future<ExpenseLogResult> logExpense(String message);
}

class BackendDashboardApi implements DashboardApi {
  BackendDashboardApi({
    http.Client? client,
    String? userId,
  }) : _client = client ?? http.Client(),
       _userId = userId ?? 'demo-user';

  final http.Client _client;
  final String _userId;

  String get _baseUrl => '${AppConfig.apiBaseUrl}/api/v1/transactions';

  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'X-User-Id': _userId,
  };

  @override
  Future<BudgetSummary> getBudgetSummary() async {
    final response = await _client.get(
      Uri.parse('$_baseUrl/budget-summary'),
      headers: _headers,
    );

    if (response.statusCode == 404) {
      throw const NoBudgetException('No budget found. Complete onboarding first.');
    }

    if (response.statusCode != 200) {
      throw Exception('Failed to load budget summary (${response.statusCode})');
    }

    return BudgetSummary.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  @override
  Future<ExpenseLogResult> logExpense(String message) async {
    final response = await _client.post(
      Uri.parse('$_baseUrl/log'),
      headers: _headers,
      body: jsonEncode({'message': message}),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to log expense (${response.statusCode})');
    }

    return ExpenseLogResult.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }
}
