import 'dart:convert';

import 'package:finflow_app/config/app_config.dart';
import 'package:finflow_app/features/advisory/data/models.dart';
import 'package:http/http.dart' as http;

abstract class AdvisoryApi {
  Future<AdvisoryAskResult> ask({
    required String message,
    String? sessionId,
  });

  Future<AdvisoryApplyResult> applySuggestion(String suggestionId);
}

class BackendAdvisoryApi implements AdvisoryApi {
  BackendAdvisoryApi({
    http.Client? client,
    String? userId,
  }) : _client = client ?? http.Client(),
       _userId = userId ?? 'demo-user';

  final http.Client _client;
  final String _userId;

  String get _baseUrl => '${AppConfig.apiBaseUrl}/api/v1/advisory';

  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'X-User-Id': _userId,
  };

  @override
  Future<AdvisoryAskResult> ask({
    required String message,
    String? sessionId,
  }) async {
    final response = await _client.post(
      Uri.parse('$_baseUrl/ask'),
      headers: _headers,
      body: jsonEncode({
        'message': message,
        'session_id': sessionId,
      }),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to get advisory response (${response.statusCode})');
    }

    return AdvisoryAskResult.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  @override
  Future<AdvisoryApplyResult> applySuggestion(String suggestionId) async {
    final response = await _client.post(
      Uri.parse('$_baseUrl/apply'),
      headers: _headers,
      body: jsonEncode({'suggestion_id': suggestionId}),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to apply advisory suggestion (${response.statusCode})');
    }

    return AdvisoryApplyResult.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }
}
