class Message {
  final String id;
  final String text;
  final MessageType type;
  final DateTime timestamp;
  final bool isTyping;
  final String? detectedTone;
  final String? improvedText;

  Message({
    required this.id,
    required this.text,
    required this.type,
    required this.timestamp,
    this.isTyping = false,
    this.detectedTone,
    this.improvedText,
  });

  Message copyWith({
    String? id,
    String? text,
    MessageType? type,
    DateTime? timestamp,
    bool? isTyping,
    String? detectedTone,
    String? improvedText,
  }) {
    return Message(
      id: id ?? this.id,
      text: text ?? this.text,
      type: type ?? this.type,
      timestamp: timestamp ?? this.timestamp,
      isTyping: isTyping ?? this.isTyping,
      detectedTone: detectedTone ?? this.detectedTone,
      improvedText: improvedText ?? this.improvedText,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'text': text,
      'type': type.name,
      'timestamp': timestamp.toIso8601String(),
      'isTyping': isTyping,
      'detectedTone': detectedTone,
      'improvedText': improvedText,
    };
  }

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'],
      text: json['text'],
      type: MessageType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => MessageType.bot,
      ),
      timestamp: DateTime.parse(json['timestamp']),
      isTyping: json['isTyping'] ?? false,
      detectedTone: json['detectedTone'],
      improvedText: json['improvedText'],
    );
  }
}

enum MessageType {
  user,
  bot,
  typing,
}
