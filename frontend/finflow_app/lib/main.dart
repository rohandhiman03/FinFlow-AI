import 'package:flutter/material.dart';
import 'package:finflow_app/config/app_config.dart';

void main() {
  runApp(const FinFlowApp());
}

class FinFlowApp extends StatelessWidget {
  const FinFlowApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FinFlow AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF6C63FF)),
      ),
      home: const FoundationStatusScreen(),
    );
  }
}

class FoundationStatusScreen extends StatelessWidget {
  const FoundationStatusScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = AppConfig.aiProvider.name;
    final apiBaseUrl = AppConfig.apiBaseUrl;

    return Scaffold(
      appBar: AppBar(title: const Text('FinFlow AI - Phase 1')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Foundation ready',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 12),
            Text('Active AI provider: $provider'),
            Text('API base URL: $apiBaseUrl'),
            const SizedBox(height: 20),
            const Text('Switch provider at launch time:'),
            const SizedBox(height: 8),
            const SelectableText(
              'flutter run --dart-define=AI_PROVIDER=gemini '
              '--dart-define=API_BASE_URL=http://localhost:8000',
            ),
          ],
        ),
      ),
    );
  }
}
