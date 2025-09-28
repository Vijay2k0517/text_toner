import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import '../providers/chat_provider.dart';
import '../widgets/message_bubble.dart';
import '../widgets/input_field.dart';
import '../theme/app_theme.dart';
import '../models/message.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _addWelcomeMessage();
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _addWelcomeMessage() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final chatProvider = Provider.of<ChatProvider>(context, listen: false);
      if (chatProvider.messages.isEmpty) {
        chatProvider.addBotMessage(
          "Welcome to Text Toner! 🎨\n\nI'm here to help you improve your text by adjusting tone, enhancing clarity, and making it more engaging. Just share your text and tell me what you'd like to improve!",
        );
      }
    });
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          // Custom App Bar with gradient
          _buildAppBar(),
          
          // Chat messages area
          Expanded(
            child: Consumer<ChatProvider>(
              builder: (context, chatProvider, child) {
                // Scroll to bottom when new messages are added
                WidgetsBinding.instance.addPostFrameCallback((_) {
                  _scrollToBottom();
                });

                return ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  itemCount: chatProvider.messages.length + (chatProvider.isTyping ? 1 : 0),
                  itemBuilder: (context, index) {
                    if (index < chatProvider.messages.length) {
                      final message = chatProvider.messages[index];
                      return MessageBubble(
                        message: message,
                        showAvatar: _shouldShowAvatar(chatProvider.messages, index),
                      );
                    } else {
                      // Typing indicator
                      return MessageBubble(
                        message: Message(
                          id: 'typing',
                          text: '',
                          type: MessageType.typing,
                          timestamp: DateTime.now(),
                          isTyping: true,
                        ),
                        showAvatar: true,
                      );
                    }
                  },
                );
              },
            ),
          ),
          
          // Input field
          Consumer<ChatProvider>(
            builder: (context, chatProvider, child) {
              return ChatInputField(
                onSendMessage: (text) async {
                  final error = await chatProvider.sendMessageToBackend(text);
                  if (error != null && mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(error),
                        duration: const Duration(seconds: 3),
                      ),
                    );
                  }
                },
                onVoiceInput: () {
                  // TODO: Implement voice input functionality
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Voice input coming soon!'),
                      duration: Duration(seconds: 2),
                    ),
                  );
                },
                isLoading: chatProvider.isTyping,
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildAppBar() {
    return Container(
      decoration: const BoxDecoration(
        gradient: AppTheme.appBarGradient,
        borderRadius: BorderRadius.only(
          bottomLeft: Radius.circular(30),
          bottomRight: Radius.circular(30),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 10,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // Menu button (for future use)
                  Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Icon(
                      Icons.menu,
                      color: Colors.white,
                      size: 20,
                    ),
                  ),
                  
                  // Title and tagline
                  Expanded(
                    child: Column(
                      children: [
                        Text(
                          'Text Toner',
                          style: GoogleFonts.poppins(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          'Tone your text, instantly',
                          style: GoogleFonts.poppins(
                            fontSize: 14,
                            fontWeight: FontWeight.w400,
                            color: Colors.white.withOpacity(0.9),
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  // Settings button (for future use)
                  Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Icon(
                      Icons.settings,
                      color: Colors.white,
                      size: 20,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 16),
              
              // Quick action chips
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    _buildQuickActionChip('Make it formal', Icons.business),
                    const SizedBox(width: 8),
                    _buildQuickActionChip('Add clarity', Icons.text_snippet),
                    const SizedBox(width: 8),
                    _buildQuickActionChip('Improve tone', Icons.tune),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuickActionChip(String label, IconData icon) {
    return GestureDetector(
      onTap: () async {
        final chatProvider = Provider.of<ChatProvider>(context, listen: false);
        final error = await chatProvider.sendMessageToBackend(label);
        if (error != null && mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(error),
              duration: const Duration(seconds: 3),
            ),
          );
        }
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.2),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: Colors.white.withOpacity(0.3),
            width: 1,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              color: Colors.white,
              size: 14,
            ),
            const SizedBox(width: 4),
            Text(
              label,
              style: GoogleFonts.poppins(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  bool _shouldShowAvatar(List<Message> messages, int index) {
    if (index == 0) return true;
    
    final currentMessage = messages[index];
    final previousMessage = messages[index - 1];
    
    // Show avatar if message type changed or if more than 2 minutes passed
    if (currentMessage.type != previousMessage.type) return true;
    
    final timeDifference = currentMessage.timestamp.difference(previousMessage.timestamp);
    if (timeDifference.inMinutes > 2) return true;
    
    return false;
  }
}
