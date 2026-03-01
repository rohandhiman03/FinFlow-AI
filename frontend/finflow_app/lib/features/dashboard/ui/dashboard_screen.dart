import 'package:finflow_app/features/dashboard/data/dashboard_api.dart';
import 'package:finflow_app/features/dashboard/data/models.dart';
import 'package:flutter/material.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({
    super.key,
    required this.api,
    required this.onRestartOnboarding,
    required this.onOpenStatements,
  });

  final DashboardApi api;
  final VoidCallback onRestartOnboarding;
  final VoidCallback onOpenStatements;

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final TextEditingController _inputController = TextEditingController();

  BudgetSummary? _summary;
  bool _loading = true;
  bool _sending = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadSummary();
  }

  Future<void> _loadSummary() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final summary = await widget.api.getBudgetSummary();
      if (!mounted) {
        return;
      }
      setState(() {
        _summary = summary;
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

  Future<void> _logExpense() async {
    final text = _inputController.text.trim();
    if (text.isEmpty || _sending) {
      return;
    }

    _inputController.clear();
    setState(() {
      _sending = true;
      _error = null;
    });

    try {
      final result = await widget.api.logExpense(text);
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(result.confirmation)));
      await _loadSummary();
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
          _sending = false;
        });
      }
    }
  }

  Color _statusColor(BuildContext context, String status) {
    switch (status) {
      case 'green':
        return Colors.green;
      case 'amber':
        return Colors.orange;
      case 'red':
        return Colors.red;
      default:
        return Theme.of(context).colorScheme.primary;
    }
  }

  @override
  Widget build(BuildContext context) {
    final summary = _summary;

    return Scaffold(
      appBar: AppBar(
        title: const Text('FinFlow AI - Phase 3 Dashboard'),
        actions: [
          TextButton(
            onPressed: widget.onOpenStatements,
            child: const Text('Statements'),
          ),
          TextButton(
            onPressed: widget.onRestartOnboarding,
            child: const Text('Onboarding'),
          ),
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
          if (summary != null) ...[
            Padding(
              padding: const EdgeInsets.all(12),
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Month ${summary.month}', style: Theme.of(context).textTheme.titleMedium),
                      const SizedBox(height: 8),
                      Text('Spent: \$${summary.totalSpent.toStringAsFixed(2)}'),
                      Text('Remaining: \$${summary.totalRemaining.toStringAsFixed(2)}'),
                      Text('Days left: ${summary.daysLeftInCycle}'),
                      Text('Projected EOM: \$${summary.projectedEndOfMonthPosition.toStringAsFixed(2)}'),
                    ],
                  ),
                ),
              ),
            ),
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                itemCount: summary.categories.length,
                itemBuilder: (context, index) {
                  final cat = summary.categories[index];
                  final progress = cat.plannedAmount > 0 ? (cat.spentAmount / cat.plannedAmount).clamp(0.0, 1.0) : 0.0;
                  return Card(
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(cat.name, style: Theme.of(context).textTheme.titleSmall),
                              Text('\$${cat.spentAmount.toStringAsFixed(2)} / \$${cat.plannedAmount.toStringAsFixed(2)}'),
                            ],
                          ),
                          const SizedBox(height: 8),
                          LinearProgressIndicator(
                            value: progress,
                            color: _statusColor(context, cat.status),
                            minHeight: 8,
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          ] else
            const Expanded(
              child: Center(
                child: Text('No budget summary available yet.'),
              ),
            ),
          SafeArea(
            top: false,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _inputController,
                      enabled: !_sending,
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _logExpense(),
                      decoration: const InputDecoration(
                        hintText: 'Log expense: "grabbed coffee \$4.75"',
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  FilledButton(
                    onPressed: _sending ? null : _logExpense,
                    child: _sending
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('Add'),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
