import 'package:finflow_app/features/advisory/data/advisory_api.dart';
import 'package:finflow_app/features/advisory/data/models.dart';
import 'package:flutter/material.dart';

class AdvisoryScreen extends StatefulWidget {
  const AdvisoryScreen({
    super.key,
    required this.api,
  });

  final AdvisoryApi api;

  @override
  State<AdvisoryScreen> createState() => _AdvisoryScreenState();
}

class _AdvisoryScreenState extends State<AdvisoryScreen> {
  final TextEditingController _controller = TextEditingController();

  String? _sessionId;
  bool _loading = false;
  String? _error;
  final List<_ChatItem> _items = [];

  Future<void> _ask() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _loading) {
      return;
    }

    _controller.clear();
    setState(() {
      _loading = true;
      _error = null;
      _items.add(_ChatItem.user(text));
    });

    try {
      final result = await widget.api.ask(message: text, sessionId: _sessionId);
      if (!mounted) {
        return;
      }
      setState(() {
        _sessionId = result.sessionId;
        _items.add(_ChatItem.assistant(result));
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

  Future<void> _applySuggestion(AdvisorySuggestion suggestion) async {
    try {
      final result = await widget.api.applySuggestion(suggestion.suggestionId);
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(result.confirmation)));
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
      appBar: AppBar(title: const Text('Ask FinFlow Advisor')),
      body: Column(
        children: [
          if (_loading) const LinearProgressIndicator(),
          if (_error != null)
            Padding(
              padding: const EdgeInsets.all(12),
              child: Text(_error!, style: const TextStyle(color: Colors.redAccent)),
            ),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: _items.length,
              itemBuilder: (context, index) {
                final item = _items[index];
                if (item.kind == _ChatKind.user) {
                  return Align(
                    alignment: Alignment.centerRight,
                    child: Container(
                      padding: const EdgeInsets.all(10),
                      margin: const EdgeInsets.only(bottom: 8),
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.primaryContainer,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(item.userText!),
                    ),
                  );
                }

                final advisory = item.advisory!;
                return Card(
                  margin: const EdgeInsets.only(bottom: 10),
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(advisory.answer),
                        const SizedBox(height: 8),
                        const Text('Reasoning:'),
                        ...advisory.reasoning.map((r) => Text('- $r')),
                        if (advisory.suggestions.isNotEmpty) ...[
                          const SizedBox(height: 10),
                          const Text('Suggestions:'),
                          ...advisory.suggestions.map(
                            (s) => ListTile(
                              contentPadding: EdgeInsets.zero,
                              title: Text(s.title),
                              subtitle: Text(s.summary),
                              trailing: FilledButton(
                                onPressed: () => _applySuggestion(s),
                                child: const Text('Apply'),
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                );
              },
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
                      controller: _controller,
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _ask(),
                      decoration: const InputDecoration(
                        hintText: 'Ask: "Can I buy an \$800 laptop this month?"',
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  FilledButton(
                    onPressed: _loading ? null : _ask,
                    child: const Text('Ask'),
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

enum _ChatKind { user, assistant }

class _ChatItem {
  const _ChatItem._({
    required this.kind,
    this.userText,
    this.advisory,
  });

  final _ChatKind kind;
  final String? userText;
  final AdvisoryAskResult? advisory;

  factory _ChatItem.user(String text) => _ChatItem._(kind: _ChatKind.user, userText: text);

  factory _ChatItem.assistant(AdvisoryAskResult result) =>
      _ChatItem._(kind: _ChatKind.assistant, advisory: result);
}
