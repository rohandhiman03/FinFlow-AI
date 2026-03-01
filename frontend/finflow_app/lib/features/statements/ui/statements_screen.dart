import 'dart:convert';
import 'dart:typed_data';

import 'package:finflow_app/features/statements/data/models.dart';
import 'package:finflow_app/features/statements/data/statements_api.dart';
import 'package:flutter/material.dart';

class StatementsScreen extends StatefulWidget {
  const StatementsScreen({
    super.key,
    required this.api,
  });

  final StatementsApi api;

  @override
  State<StatementsScreen> createState() => _StatementsScreenState();
}

class _StatementsScreenState extends State<StatementsScreen> {
  final TextEditingController _accountController = TextEditingController(text: 'Primary Account');
  final TextEditingController _csvController = TextEditingController(
    text: 'date,description,amount\n2026-03-01,Coffee Shop,4.75',
  );

  List<StatementListItem> _statements = const [];
  ReconciliationData? _reconciliation;
  String? _selectedStatementId;
  bool _loading = true;
  bool _uploading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadStatements();
  }

  Future<void> _loadStatements() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final items = await widget.api.listStatements();
      if (!mounted) {
        return;
      }
      setState(() {
        _statements = items;
      });

      if (_selectedStatementId != null) {
        await _loadReconciliation(_selectedStatementId!);
      }
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = e.toString();
      });
    } finally {
      if (mounted) {
        setState(() {
          _loading = false;
        });
      }
    }
  }

  Future<void> _uploadCsvText() async {
    setState(() {
      _uploading = true;
      _error = null;
    });

    try {
      final csvText = _csvController.text.trim();
      if (csvText.isEmpty) {
        throw Exception('Paste CSV content before upload.');
      }

      final result = await widget.api.uploadStatement(
        filename: 'manual_statement.csv',
        bytes: Uint8List.fromList(utf8.encode(csvText)),
        accountName: _accountController.text.trim().isEmpty ? 'Primary Account' : _accountController.text.trim(),
      );

      if (!mounted) {
        return;
      }

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Uploaded. ${result.transactionsFound} transactions, ${result.needsAttentionCount} need attention.')),
      );

      _selectedStatementId = result.statementId;
      await _loadStatements();
      await _loadReconciliation(result.statementId);
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = e.toString();
      });
    } finally {
      if (mounted) {
        setState(() {
          _uploading = false;
        });
      }
    }
  }

  Future<void> _loadReconciliation(String statementId) async {
    try {
      final data = await widget.api.getReconciliation(statementId);
      if (!mounted) {
        return;
      }
      setState(() {
        _selectedStatementId = statementId;
        _reconciliation = data;
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = e.toString();
      });
    }
  }

  Future<void> _confirmGap(ReconciliationEntry entry) async {
    final statementId = _selectedStatementId;
    if (statementId == null) {
      return;
    }

    try {
      await widget.api.confirmGap(
        statementId: statementId,
        entryId: entry.entryId,
        categoryName: entry.suggestedCategory,
      );
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Gap confirmed and logged.')));
      await _loadReconciliation(statementId);
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = e.toString();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final rec = _reconciliation;

    return Scaffold(
      appBar: AppBar(title: const Text('Statements & Reconciliation')),
      body: Column(
        children: [
          if (_loading) const LinearProgressIndicator(),
          if (_error != null)
            Padding(
              padding: const EdgeInsets.all(12),
              child: Text(_error!, style: const TextStyle(color: Colors.redAccent)),
            ),
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Expanded(
                    child: TextField(
                      controller: _accountController,
                      decoration: const InputDecoration(
                        labelText: 'Account Name',
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  FilledButton(
                  onPressed: _uploading ? null : _uploadCsvText,
                  child: _uploading
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Text('Upload CSV'),
                  ),
                ],
              ),
            ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: TextField(
              controller: _csvController,
              minLines: 4,
              maxLines: 8,
              decoration: const InputDecoration(
                labelText: 'Paste CSV (date,description,amount)',
                alignLabelWithHint: true,
              ),
            ),
          ),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              children: [
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Uploaded Statements', style: Theme.of(context).textTheme.titleMedium),
                        const SizedBox(height: 8),
                        if (_statements.isEmpty)
                          const Text('No statements uploaded yet.')
                        else
                          ..._statements.map(
                            (item) => ListTile(
                              contentPadding: EdgeInsets.zero,
                              title: Text('${item.accountName} - ${item.filename}'),
                              subtitle: Text('${item.transactionsFound} txns | ${item.needsAttentionCount} need attention'),
                              trailing: TextButton(
                                onPressed: () => _loadReconciliation(item.statementId),
                                child: const Text('View'),
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                if (rec != null)
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Reconciliation', style: Theme.of(context).textTheme.titleMedium),
                          const SizedBox(height: 8),
                          Text('Matched: ${rec.matched.length}'),
                          Text('Gaps: ${rec.gaps.length}'),
                          Text('Orphans: ${rec.orphans.length}'),
                          const SizedBox(height: 8),
                          if (rec.gaps.isEmpty)
                            const Text('No gaps to confirm.')
                          else
                            ...rec.gaps.map(
                              (gap) => ListTile(
                                contentPadding: EdgeInsets.zero,
                                title: Text('${gap.merchant}  \$${gap.amount.toStringAsFixed(2)}'),
                                subtitle: Text('Suggested: ${gap.suggestedCategory}'),
                                trailing: FilledButton(
                                  onPressed: () => _confirmGap(gap),
                                  child: const Text('Confirm'),
                                ),
                              ),
                            ),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
