import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_staggered_animations/flutter_staggered_animations.dart';
import '../models/message.dart';
import '../theme/app_theme.dart';

class MessageBubble extends StatelessWidget {
  final Message message;
  final bool showAvatar;

  const MessageBubble({
    super.key,
    required this.message,
    this.showAvatar = true,
  });

  @override
  Widget build(BuildContext context) {
    return AnimationConfiguration.staggeredList(
      position: 0,
      duration: const Duration(milliseconds: 600),
      child: SlideAnimation(
        verticalOffset: 50.0,
        child: FadeInAnimation(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: Row(
              mainAxisAlignment: message.type == MessageType.user
                  ? MainAxisAlignment.end
                  : MainAxisAlignment.start,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (message.type == MessageType.bot && showAvatar) ...[
                  _buildAvatar(),
                  const SizedBox(width: 8),
                ],
                Flexible(
                  child: Container(
                    constraints: BoxConstraints(
                      maxWidth: MediaQuery.of(context).size.width * 0.75,
                    ),
                    decoration: BoxDecoration(
                      color: message.type == MessageType.user
                          ? AppTheme.userMessageBg
                          : AppTheme.botMessageBg,
                      borderRadius: BorderRadius.only(
                        topLeft: const Radius.circular(20),
                        topRight: const Radius.circular(20),
                        bottomLeft: Radius.circular(
                          message.type == MessageType.user ? 20 : 4,
                        ),
                        bottomRight: Radius.circular(
                          message.type == MessageType.user ? 4 : 20,
                        ),
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 8,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 12,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        if (message.isTyping) ...[
                          _buildTypingIndicator(),
                        ] else ...[
                          Text(
                            message.text,
                            style: GoogleFonts.poppins(
                              fontSize: 15,
                              fontWeight: FontWeight.w400,
                              color: message.type == MessageType.user
                                  ? AppTheme.userMessageText
                                  : AppTheme.botMessageText,
                              height: 1.4,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            _formatTime(message.timestamp),
                            style: GoogleFonts.poppins(
                              fontSize: 11,
                              fontWeight: FontWeight.w300,
                              color: message.type == MessageType.user
                                  ? AppTheme.userMessageText.withOpacity(0.7)
                                  : AppTheme.textGrey,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
                if (message.type == MessageType.user && showAvatar) ...[
                  const SizedBox(width: 8),
                  _buildUserAvatar(),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildAvatar() {
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        gradient: AppTheme.appBarGradient,
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: const Icon(
        Icons.smart_toy,
        color: Colors.white,
        size: 18,
      ),
    );
  }

  Widget _buildUserAvatar() {
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        gradient: AppTheme.sendButtonGradient,
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: const Icon(
        Icons.person,
        color: Colors.white,
        size: 18,
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _buildTypingDot(0),
        const SizedBox(width: 4),
        _buildTypingDot(1),
        const SizedBox(width: 4),
        _buildTypingDot(2),
      ],
    );
  }

  Widget _buildTypingDot(int index) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0.0, end: 1.0),
      duration: const Duration(milliseconds: 600),
      builder: (context, value, child) {
        final delay = index * 0.2;
        final animationValue = (value - delay).clamp(0.0, 1.0);
        final opacity = (animationValue * 2).clamp(0.0, 1.0) > 1.0
            ? 2.0 - (animationValue * 2).clamp(0.0, 1.0)
            : (animationValue * 2).clamp(0.0, 1.0);
        
        return Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: AppTheme.primaryBlue.withOpacity(opacity),
            shape: BoxShape.circle,
          ),
        );
      },
    );
  }

  String _formatTime(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);
    
    if (difference.inMinutes < 1) {
      return 'now';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}m';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}h';
    } else {
      return '${difference.inDays}d';
    }
  }
}
