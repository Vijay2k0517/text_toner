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

  void addBotMessage(String text, {String? detectedTone, String? improvedText}) {
    final message = Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      text: text,
      timestamp: DateTime.now(),
      type: MessageType.bot,
      detectedTone: detectedTone,
      improvedText: improvedText,
    );
    addMessage(message);
  }

  void setTyping(bool typing) {
    _isTyping = typing;
    notifyListeners();
  }

  /// Sends the user message to the backend and appends the tone analysis response.
  /// Returns null on success, or an error message string on failure.
  Future<String?> sendMessageToBackend(String userMessage) async {
    // Add user message to UI immediately
    addUserMessage(userMessage);

    // Show typing indicator
    setTyping(true);

    try {
      final analysis = await _apiClient.analyzeTone(userMessage);
      
      // Create a comprehensive response message
      final responseText = _formatToneAnalysisResponse(analysis, userMessage);
      addBotMessage(responseText, 
        detectedTone: analysis['tone'],
        improvedText: analysis['improved_text']
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

  String _formatToneAnalysisResponse(Map<String, String> analysis, String originalText) {
    final detectedTone = analysis['tone'] ?? 'friendly';
    final improvedText = analysis['improved_text'] ?? originalText;
    
    return '''🎯 **Analysis Complete!**

**Original Text:**
$originalText

**Detected Tone:** ${_formatTone(detectedTone)}

**Improved Text:**
$improvedText''';
  }

  String _formatTone(String tone) {
    switch (tone.toLowerCase()) {
      case 'sad':
        return '😢 Sad';
      case 'angry':
        return '😠 Angry';
      case 'friendly':
        return '😊 Friendly';
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
