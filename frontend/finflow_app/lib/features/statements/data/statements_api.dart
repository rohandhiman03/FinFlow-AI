import 'dart:convert';
import 'dart:typed_data';

import 'package:finflow_app/config/app_config.dart';
import 'package:finflow_app/features/statements/data/models.dart';
import 'package:http/http.dart' as http;

abstract class StatementsApi {
  Future<StatementUploadResult> uploadStatement({
    required String filename,
    required Uint8List bytes,
    required String accountName,
  });

  Future<List<StatementListItem>> listStatements();

  Future<ReconciliationData> getReconciliation(String statementId);

  Future<void> confirmGap({
    required String statementId,
    required String entryId,
    String? categoryName,
  });
}

class BackendStatementsApi implements StatementsApi {
  BackendStatementsApi({
    http.Client? client,
    String? userId,
  }) : _client = client ?? http.Client(),
       _userId = userId ?? 'demo-user';

  final http.Client _client;
  final String _userId;

  String get _baseUrl => '${AppConfig.apiBaseUrl}/api/v1/statements';

  Map<String, String> get _headers => {
    'X-User-Id': _userId,
  };

  @override
  Future<StatementUploadResult> uploadStatement({
    required String filename,
    required Uint8List bytes,
    required String accountName,
  }) async {
    final request = http.MultipartRequest('POST', Uri.parse('$_baseUrl/upload'));
    request.headers.addAll(_headers);
    request.fields['account_name'] = accountName;
    request.files.add(http.MultipartFile.fromBytes('file', bytes, filename: filename));

    final streamed = await request.send();
    final response = await http.Response.fromStream(streamed);

    if (response.statusCode != 200) {
      throw Exception('Failed to upload statement (${response.statusCode})');
    }

    return StatementUploadResult.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  @override
  Future<List<StatementListItem>> listStatements() async {
    final response = await _client.get(Uri.parse(_baseUrl), headers: _headers);
    if (response.statusCode != 200) {
      throw Exception('Failed to list statements (${response.statusCode})');
    }

    final payload = jsonDecode(response.body) as List<dynamic>;
    return payload
        .map((entry) => StatementListItem.fromJson(entry as Map<String, dynamic>))
        .toList(growable: false);
  }

  @override
  Future<ReconciliationData> getReconciliation(String statementId) async {
    final response = await _client.get(
      Uri.parse('$_baseUrl/$statementId/reconciliation'),
      headers: _headers,
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to load reconciliation (${response.statusCode})');
    }

    return ReconciliationData.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  @override
  Future<void> confirmGap({
    required String statementId,
    required String entryId,
    String? categoryName,
  }) async {
    final response = await _client.post(
      Uri.parse('$_baseUrl/$statementId/gaps/$entryId/confirm'),
      headers: {
        ..._headers,
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'category_name': categoryName}),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to confirm reconciliation gap (${response.statusCode})');
    }
  }
}
