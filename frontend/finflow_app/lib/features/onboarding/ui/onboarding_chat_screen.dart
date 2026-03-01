import 'package:finflow_app/config/app_config.dart';
import 'package:finflow_app/features/onboarding/data/models.dart';
import 'package:finflow_app/features/onboarding/data/onboarding_api.dart';
import 'package:flutter/material.dart';

class OnboardingChatScreen extends StatefulWidget {
  const OnboardingChatScreen({
    super.key,
    required this.api,
    this.onCompleted,
  });

  final OnboardingApi api;
  final VoidCallback? onCompleted;

  @override
  State<OnboardingChatScreen> createState() => _OnboardingChatScreenState();
}

class _OnboardingChatScreenState extends State<OnboardingChatScreen> {
  final TextEditingController _controller = TextEditingController();

  OnboardingSessionState? _state;
  bool _isLoading = true;
  bool _isSending = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _start();
  }

  Future<void> _start() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final session = await widget.api.startSession(resetExisting: true);
      if (!mounted) {
        return;
      }
      setState(() {
        _state = session;
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
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _send() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _state == null || _isSending) {
      return;
    }

    _controller.clear();
    setState(() {
      _isSending = true;
      _error = null;
    });

    try {
      final session = await widget.api.sendMessage(
        sessionId: _state!.sessionId,
        message: text,
      );
      if (!mounted) {
        return;
      }
      setState(() {
        _state = session;
      });
      if (session.status == 'completed') {
        widget.onCompleted?.call();
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
          _isSending = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final session = _state;

    return Scaffold(
      appBar: AppBar(
        title: const Text('FinFlow AI - Phase 2 Onboarding'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: Center(
              child: Text('AI: ${AppConfig.aiProvider.name}'),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          if (_isLoading) const LinearProgressIndicator(),
          if (session != null)
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 8, 12, 0),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Chip(
                  label: Text('Step: ${session.currentStep} | Status: ${session.status}'),
                ),
              ),
            ),
          if (_error != null)
            Padding(
              padding: const EdgeInsets.all(12),
              child: Text(
                _error!,
                style: const TextStyle(color: Colors.redAccent),
              ),
            ),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: session?.messages.length ?? 0,
              itemBuilder: (context, index) {
                final msg = session!.messages[index];
                final isUser = msg.role == 'user';
                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(10),
                    constraints: const BoxConstraints(maxWidth: 340),
                    decoration: BoxDecoration(
                      color: isUser
                          ? Theme.of(context).colorScheme.primaryContainer
                          : Theme.of(context).colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(msg.content),
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
                      enabled: !_isSending && !_isLoading,
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _send(),
                      decoration: const InputDecoration(
                        hintText: 'Type your answer... (income, expenses, goals)',
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  FilledButton(
                    onPressed: _isSending || _isLoading ? null : _send,
                    child: _isSending
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('Send'),
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
