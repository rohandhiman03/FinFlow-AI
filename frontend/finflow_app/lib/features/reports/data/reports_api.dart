import 'dart:convert';

import 'package:finflow_app/config/app_config.dart';
import 'package:finflow_app/features/reports/data/models.dart';
import 'package:http/http.dart' as http;

abstract class ReportsApi {
  Future<FinancialReport> generateReport();

  Future<FinancialReport> getLatestReport();

  Future<List<FinancialReport>> getReportHistory();
}

class BackendReportsApi implements ReportsApi {
  BackendReportsApi({
    http.Client? client,
    String? userId,
  }) : _client = client ?? http.Client(),
       _userId = userId ?? 'demo-user';

  final http.Client _client;
  final String _userId;

  String get _baseUrl => '${AppConfig.apiBaseUrl}/api/v1/reports';

  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'X-User-Id': _userId,
  };

  @override
  Future<FinancialReport> generateReport() async {
    final response = await _client.post(Uri.parse('$_baseUrl/generate'), headers: _headers);
    if (response.statusCode != 200) {
      throw Exception('Failed to generate report (${response.statusCode})');
    }
    return FinancialReport.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  @override
  Future<FinancialReport> getLatestReport() async {
    final response = await _client.get(Uri.parse('$_baseUrl/latest'), headers: _headers);
    if (response.statusCode != 200) {
      throw Exception('Failed to load latest report (${response.statusCode})');
    }
    return FinancialReport.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  @override
  Future<List<FinancialReport>> getReportHistory() async {
    final response = await _client.get(Uri.parse('$_baseUrl/history'), headers: _headers);
    if (response.statusCode != 200) {
      throw Exception('Failed to load report history (${response.statusCode})');
    }
    final data = jsonDecode(response.body) as List<dynamic>;
    return data.map((e) => FinancialReport.fromJson(e as Map<String, dynamic>)).toList(growable: false);
  }
}
