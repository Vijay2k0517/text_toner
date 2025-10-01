import 'package:flutter/material.dart';
import '../models/message.dart';
import '../services/api_client.dart';

class ChatProvider extends ChangeNotifier {
  ChatProvider({ApiClient? apiClient}) : _apiClient = apiClient ?? ApiClient();

  final List<Message> _messages = [];
  bool _isTyping = false;
  final ApiClient _apiClient;

  List<Message> get messages => List.unmodifiable(_messages);
  bool get isTyping => _isTyping;

  void addMessage(Message message) {
    _messages.add(message);
    notifyListeners();
  }

  void addUserMessage(String text) {
    final message = Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      text: text,
      type: MessageType.user,
      timestamp: DateTime.now(),
    );
    addMessage(message);
  }

  void addBotMessage(String text, {String? detectedTone, String? improvisedText}) {
    final message = Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      text: text,
      timestamp: DateTime.now(),
      type: MessageType.bot,
      detectedTone: detectedTone,
      improvisedText: improvisedText,
    );
    addMessage(message);
  }

  void setTyping(bool typing) {
    _isTyping = typing;
    notifyListeners();
  }

  /// Sends the user message to the backend and appends the tone analysis response.
  /// Returns null on success, or an error message string on failure.
  Future<String?> sendMessageToBackend(String userMessage, {String? targetTone}) async {
    // Add user message to UI immediately
    addUserMessage(userMessage);

    // Show typing indicator
    setTyping(true);

    try {
      final analysis = await _apiClient.analyzeTone(userMessage, targetTone: targetTone);
      
      // Create a comprehensive response message
      final responseText = _formatToneAnalysisResponse(analysis);
      addBotMessage(responseText, 
        detectedTone: analysis['detected_tone'],
        improvisedText: analysis['improvised_text']
      );
      return null;
    } catch (e) {
      // On error, show a friendly error message as a bot message
      addBotMessage('Sorry, I could not process your request. Please try again.');
      return e.toString();
    } finally {
      setTyping(false);
    }
  }

  String _formatToneAnalysisResponse(Map<String, String> analysis) {
    final detectedTone = analysis['detected_tone'] ?? 'neutral';
    final improvisedText = analysis['improvised_text'] ?? analysis['original_text'] ?? '';
    
    return '''🎯 **Tone Analysis Complete!**

**Detected Tone:** ${_formatTone(detectedTone)}

**Improved Text:**
$improvisedText

*The text has been enhanced while preserving your original meaning.*''';
  }

  String _formatTone(String tone) {
    switch (tone.toLowerCase()) {
      case 'positive':
        return '😊 Positive';
      case 'negative':
        return '😔 Negative';
      case 'neutral':
        return '😐 Neutral';
      default:
        return '🤔 $tone';
    }
  }

  // Keeping for compatibility; replaced by backend call
  void simulateBotResponse(String userMessage) {
    // Prefer sendMessageToBackend in production
    sendMessageToBackend(userMessage);
  }

  void clearMessages() {
    _messages.clear();
    notifyListeners();
  }
}
