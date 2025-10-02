import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';

/// ApiClient centralizes HTTP calls to the FastAPI backend.
/// Uses Dart `http` package to POST user messages to `/chat` and
/// returns the bot response text.
class ApiClient {
  ApiClient({http.Client? httpClient}) : _http = httpClient ?? http.Client();

  final http.Client _http;

  Uri _buildUri(String path) {
    final normalizedBase = AppConfig.apiBaseUrl.endsWith('/')
        ? AppConfig.apiBaseUrl.substring(0, AppConfig.apiBaseUrl.length - 1)
        : AppConfig.apiBaseUrl;
    final normalizedPath = path.startsWith('/') ? path : '/$path';
    return Uri.parse('$normalizedBase$normalizedPath');
  }

  /// Sends the user's message to FastAPI `/api/v1/tone/analyze-tone` and returns the tone analysis.
  ///
  /// Request: { "text": "user text" }
  /// Response: { "tone": "...", "improved_text": "..." }
  Future<Map<String, String>> analyzeTone(String message) async {
    final uri = _buildUri('/api/v1/tone/analyze-tone');

    final response = await _http
        .post(
          uri,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: jsonEncode({
            'text': message,
          }),
        )
        .timeout(const Duration(seconds: 30));

    if (response.statusCode >= 200 && response.statusCode < 300) {
      try {
        final decoded = jsonDecode(response.body) as Map<String, dynamic>;
        return {
          'tone': decoded['tone']?.toString() ?? 'friendly',
          'improved_text': decoded['improved_text']?.toString() ?? message,
        };
      } catch (e) {
        throw Exception('Failed to parse server response: $e');
      }
    }

    // Attempt to extract error message from backend
    try {
      final decoded = jsonDecode(response.body);
      final errorMsg = decoded is Map<String, dynamic>
          ? (decoded['detail']?.toString() ?? decoded['message']?.toString())
          : decoded.toString();
      throw Exception('Server error (${response.statusCode}): $errorMsg');
    } catch (_) {
      throw Exception('Server error (${response.statusCode})');
    }
  }
}
