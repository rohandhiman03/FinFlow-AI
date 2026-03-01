import 'dart:convert';

import 'package:finflow_app/config/app_config.dart';
import 'package:finflow_app/features/onboarding/data/models.dart';
import 'package:http/http.dart' as http;

abstract class OnboardingApi {
  Future<OnboardingSessionState> startSession({bool resetExisting = true});

  Future<OnboardingSessionState> sendMessage({
    required String sessionId,
    required String message,
  });
}

class BackendOnboardingApi implements OnboardingApi {
  BackendOnboardingApi({
    http.Client? client,
    String? userId,
  }) : _client = client ?? http.Client(),
       _userId = userId ?? 'demo-user';

  final http.Client _client;
  final String _userId;

  String get _baseUrl => '${AppConfig.apiBaseUrl}/api/v1/onboarding';

  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'X-User-Id': _userId,
  };

  @override
  Future<OnboardingSessionState> startSession({bool resetExisting = true}) async {
    final response = await _client.post(
      Uri.parse('$_baseUrl/start'),
      headers: _headers,
      body: jsonEncode({'reset_existing': resetExisting}),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to start onboarding (${response.statusCode})');
    }

    return OnboardingSessionState.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  @override
  Future<OnboardingSessionState> sendMessage({
    required String sessionId,
    required String message,
  }) async {
    final response = await _client.post(
      Uri.parse('$_baseUrl/message'),
      headers: _headers,
      body: jsonEncode({
        'session_id': sessionId,
        'message': message,
      }),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to send onboarding message (${response.statusCode})');
    }

    return OnboardingSessionState.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }
}
