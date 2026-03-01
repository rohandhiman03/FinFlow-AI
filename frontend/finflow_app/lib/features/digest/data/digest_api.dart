import 'dart:convert';

import 'package:finflow_app/config/app_config.dart';
import 'package:finflow_app/features/digest/data/models.dart';
import 'package:http/http.dart' as http;

abstract class DigestApi {
  Future<DigestSettings> getSettings();

  Future<DigestSettings> updateSettings({
    required String frequency,
    required String day,
    required String time,
  });

  Future<WeeklyDigest> getWeeklyDigest();
}

class BackendDigestApi implements DigestApi {
  BackendDigestApi({
    http.Client? client,
    String? userId,
  }) : _client = client ?? http.Client(),
       _userId = userId ?? 'demo-user';

  final http.Client _client;
  final String _userId;

  String get _baseUrl => '${AppConfig.apiBaseUrl}/api/v1/digest';

  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'X-User-Id': _userId,
  };

  @override
  Future<DigestSettings> getSettings() async {
    final response = await _client.get(Uri.parse('$_baseUrl/settings'), headers: _headers);
    if (response.statusCode != 200) {
      throw Exception('Failed to load digest settings (${response.statusCode})');
    }
    return DigestSettings.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  @override
  Future<DigestSettings> updateSettings({required String frequency, required String day, required String time}) async {
    final response = await _client.put(
      Uri.parse('$_baseUrl/settings'),
      headers: _headers,
      body: jsonEncode({'frequency': frequency, 'day': day, 'time': time}),
    );
    if (response.statusCode != 200) {
      throw Exception('Failed to update digest settings (${response.statusCode})');
    }
    return DigestSettings.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  @override
  Future<WeeklyDigest> getWeeklyDigest() async {
    final response = await _client.get(Uri.parse('$_baseUrl/weekly'), headers: _headers);
    if (response.statusCode != 200) {
      throw Exception('Failed to load weekly digest (${response.statusCode})');
    }
    return WeeklyDigest.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }
}
