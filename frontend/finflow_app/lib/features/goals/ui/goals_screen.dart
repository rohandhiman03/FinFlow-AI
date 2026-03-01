import 'package:finflow_app/features/goals/data/goals_api.dart';
import 'package:finflow_app/features/goals/data/models.dart';
import 'package:flutter/material.dart';

class GoalsScreen extends StatefulWidget {
  const GoalsScreen({
    super.key,
    required this.api,
  });

  final GoalsApi api;

  @override
  State<GoalsScreen> createState() => _GoalsScreenState();
}

class _GoalsScreenState extends State<GoalsScreen> {
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _targetController = TextEditingController();

  List<GoalItem> _goals = const [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadGoals();
  }

  Future<void> _loadGoals() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final goals = await widget.api.listGoals();
      if (!mounted) {
        return;
      }
      setState(() {
        _goals = goals;
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

  Future<void> _createGoal() async {
    final name = _nameController.text.trim();
    final target = double.tryParse(_targetController.text.trim());
    if (name.isEmpty || target == null || target <= 0) {
      return;
    }

    try {
      await widget.api.createGoal(name: name, targetAmount: target, targetDate: '2026-12-31');
      _nameController.clear();
      _targetController.clear();
      await _loadGoals();
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _error = e.toString();
      });
    }
  }

  Future<void> _contribute(GoalItem goal) async {
    try {
      final result = await widget.api.contribute(goalId: goal.goalId, amount: 100);
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(result.confirmation)));
      await _loadGoals();
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
    return Scaffold(
      appBar: AppBar(title: const Text('Goals')),
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
                    controller: _nameController,
                    decoration: const InputDecoration(labelText: 'Goal name'),
                  ),
                ),
                const SizedBox(width: 8),
                SizedBox(
                  width: 120,
                  child: TextField(
                    controller: _targetController,
                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                    decoration: const InputDecoration(labelText: 'Target'),
                  ),
                ),
                const SizedBox(width: 8),
                FilledButton(
                  onPressed: _createGoal,
                  child: const Text('Add'),
                ),
              ],
            ),
          ),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              itemCount: _goals.length,
              itemBuilder: (context, index) {
                final goal = _goals[index];
                return Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(goal.name, style: Theme.of(context).textTheme.titleMedium),
                        const SizedBox(height: 6),
                        Text('\$${goal.currentAmount.toStringAsFixed(2)} / \$${goal.targetAmount.toStringAsFixed(2)}'),
                        const SizedBox(height: 6),
                        LinearProgressIndicator(value: (goal.progressPct / 100).clamp(0.0, 1.0)),
                        const SizedBox(height: 6),
                        Text('Required monthly: \$${goal.requiredMonthly.toStringAsFixed(2)}'),
                        Text(goal.onTrack ? 'On track' : 'Off track'),
                        Align(
                          alignment: Alignment.centerRight,
                          child: TextButton(
                            onPressed: () => _contribute(goal),
                            child: const Text('Contribute \$100'),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
