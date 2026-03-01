import 'package:finflow_app/features/digest/data/digest_api.dart';
import 'package:finflow_app/features/digest/data/models.dart';
import 'package:flutter/material.dart';

class DigestScreen extends StatefulWidget {
  const DigestScreen({
    super.key,
    required this.api,
  });

  final DigestApi api;

  @override
  State<DigestScreen> createState() => _DigestScreenState();
}

class _DigestScreenState extends State<DigestScreen> {
  WeeklyDigest? _digest;
  DigestSettings? _settings;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final settings = await widget.api.getSettings();
      final digest = await widget.api.getWeeklyDigest();
      if (!mounted) {
        return;
      }
      setState(() {
        _settings = settings;
        _digest = digest;
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

  Future<void> _saveSettings(String frequency) async {
    final current = _settings;
    if (current == null) {
      return;
    }

    try {
      final updated = await widget.api.updateSettings(
        frequency: frequency,
        day: current.day,
        time: current.time,
      );
      if (!mounted) {
        return;
      }
      setState(() {
        _settings = updated;
      });
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Digest settings saved.')));
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
    final digest = _digest;
    final settings = _settings;

    return Scaffold(
      appBar: AppBar(title: const Text('Weekly Digest')),
      body: Column(
        children: [
          if (_loading) const LinearProgressIndicator(),
          if (_error != null)
            Padding(
              padding: const EdgeInsets.all(12),
              child: Text(_error!, style: const TextStyle(color: Colors.redAccent)),
            ),
          if (settings != null)
            Padding(
              padding: const EdgeInsets.all(12),
              child: Row(
                children: [
                  const Text('Frequency:'),
                  const SizedBox(width: 8),
                  DropdownButton<String>(
                    value: settings.frequency,
                    items: const [
                      DropdownMenuItem(value: 'daily', child: Text('Daily')),
                      DropdownMenuItem(value: 'weekly', child: Text('Weekly')),
                      DropdownMenuItem(value: 'monthly', child: Text('Monthly')),
                    ],
                    onChanged: (value) {
                      if (value != null) {
                        _saveSettings(value);
                      }
                    },
                  ),
                ],
              ),
            ),
          Expanded(
            child: digest == null
                ? const Center(child: Text('No digest data available.'))
                : ListView(
                    padding: const EdgeInsets.all(12),
                    children: [
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(12),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Period ${digest.periodStart} -> ${digest.periodEnd}'),
                              const SizedBox(height: 6),
                              Text('Weekly spent: \$${digest.weeklySpent.toStringAsFixed(2)}'),
                              Text('Savings rate: ${digest.savingsRatePct.toStringAsFixed(1)}%'),
                              Text('Watch: ${digest.categoryToWatch}'),
                              const SizedBox(height: 8),
                              Text(digest.digestText),
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
                              const Text('Upcoming Expenses'),
                              const SizedBox(height: 6),
                              ...digest.upcomingExpenses.map(
                                (e) => Text('${e['name']}: \$${(e['amount'] as num).toStringAsFixed(2)} (${e['window']})'),
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
