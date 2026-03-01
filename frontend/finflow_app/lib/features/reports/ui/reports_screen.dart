import 'package:finflow_app/features/reports/data/models.dart';
import 'package:finflow_app/features/reports/data/reports_api.dart';
import 'package:flutter/material.dart';

class ReportsScreen extends StatefulWidget {
  const ReportsScreen({
    super.key,
    required this.api,
  });

  final ReportsApi api;

  @override
  State<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends State<ReportsScreen> {
  FinancialReport? _report;
  bool _loading = true;
  bool _generating = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadLatest();
  }

  Future<void> _loadLatest() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final report = await widget.api.getLatestReport();
      if (!mounted) {
        return;
      }
      setState(() {
        _report = report;
      });
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

  Future<void> _generateNow() async {
    setState(() {
      _generating = true;
      _error = null;
    });

    try {
      final report = await widget.api.generateReport();
      if (!mounted) {
        return;
      }
      setState(() {
        _report = report;
      });
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Report generated.')));
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
          _generating = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final report = _report;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Financial Health Report'),
        actions: [
          FilledButton(
            onPressed: _generating ? null : _generateNow,
            child: _generating
                ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                : const Text('Generate'),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: Column(
        children: [
          if (_loading) const LinearProgressIndicator(),
          if (_error != null)
            Padding(
              padding: const EdgeInsets.all(12),
              child: Text(_error!, style: const TextStyle(color: Colors.redAccent)),
            ),
          Expanded(
            child: report == null
                ? const Center(child: Text('No report yet. Generate one.'))
                : ListView(
                    padding: const EdgeInsets.all(12),
                    children: [
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(12),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Month ${report.month}', style: Theme.of(context).textTheme.titleMedium),
                              const SizedBox(height: 6),
                              Text('Score: ${report.overallScore.toStringAsFixed(0)} (${report.grade})'),
                              const SizedBox(height: 6),
                              Text(report.narrative),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(12),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Dimensions', style: Theme.of(context).textTheme.titleMedium),
                              const SizedBox(height: 8),
                              ...report.dimensions.map(
                                (d) => ListTile(
                                  contentPadding: EdgeInsets.zero,
                                  title: Text('${d.name}: ${d.score.toStringAsFixed(0)}'),
                                  subtitle: Text(d.explanation),
                                  trailing: Text(d.idealRange),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(12),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Recommendation', style: Theme.of(context).textTheme.titleMedium),
                              const SizedBox(height: 6),
                              Text(report.recommendation),
                              const SizedBox(height: 10),
                              Text('Insights', style: Theme.of(context).textTheme.titleSmall),
                              ...report.insights.map((i) => Padding(
                                    padding: const EdgeInsets.only(top: 4),
                                    child: Text('- $i'),
                                  )),
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

