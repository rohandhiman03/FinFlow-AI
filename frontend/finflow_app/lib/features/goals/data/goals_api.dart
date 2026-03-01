import 'dart:convert';

import 'package:finflow_app/config/app_config.dart';
import 'package:finflow_app/features/goals/data/models.dart';
import 'package:http/http.dart' as http;

abstract class GoalsApi {
  Future<List<GoalItem>> listGoals();

  Future<GoalItem> createGoal({
    required String name,
    required double targetAmount,
    String? targetDate,
  });

  Future<GoalContributeResult> contribute({
    required String goalId,
    required double amount,
  });
}

class BackendGoalsApi implements GoalsApi {
  BackendGoalsApi({
    http.Client? client,
    String? userId,
  }) : _client = client ?? http.Client(),
       _userId = userId ?? 'demo-user';

  final http.Client _client;
  final String _userId;

  String get _baseUrl => '${AppConfig.apiBaseUrl}/api/v1/goals';

  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'X-User-Id': _userId,
  };

  @override
  Future<List<GoalItem>> listGoals() async {
    final response = await _client.get(Uri.parse(_baseUrl), headers: _headers);
    if (response.statusCode != 200) {
      throw Exception('Failed to list goals (${response.statusCode})');
    }
    final data = jsonDecode(response.body) as List<dynamic>;
    return data.map((e) => GoalItem.fromJson(e as Map<String, dynamic>)).toList(growable: false);
  }

  @override
  Future<GoalItem> createGoal({required String name, required double targetAmount, String? targetDate}) async {
    final response = await _client.post(
      Uri.parse(_baseUrl),
      headers: _headers,
      body: jsonEncode({
        'name': name,
        'target_amount': targetAmount,
        'target_date': targetDate,
      }),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to create goal (${response.statusCode})');
    }
    return GoalItem.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  @override
  Future<GoalContributeResult> contribute({required String goalId, required double amount}) async {
    final response = await _client.post(
      Uri.parse('$_baseUrl/$goalId/contribute'),
      headers: _headers,
      body: jsonEncode({'amount': amount}),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to contribute (${response.statusCode})');
    }

    return GoalContributeResult.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }
}
