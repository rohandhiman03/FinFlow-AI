enum AIProvider {
  claude,
  gemini,
  grok;

  static AIProvider fromString(String raw) {
    switch (raw.toLowerCase().trim()) {
      case 'claude':
        return AIProvider.claude;
      case 'gemini':
        return AIProvider.gemini;
      case 'grok':
        return AIProvider.grok;
      default:
        throw ArgumentError(
          "Unsupported AI provider '$raw'. Use: claude, gemini, grok.",
        );
    }
  }
}

class AppConfig {
  AppConfig._();

  static AIProvider get aiProvider {
    final raw = const String.fromEnvironment(
      'AI_PROVIDER',
      defaultValue: 'claude',
    );
    return AIProvider.fromString(raw);
  }

  static String get apiBaseUrl {
    return const String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: 'http://localhost:8000',
    );
  }
}
