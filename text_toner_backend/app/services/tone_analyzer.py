import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, List, Tuple, Optional
import numpy as np
from datetime import datetime
import logging
from ..config import settings
from ..models import ToneType, ToneAnalysisResponse

logger = logging.getLogger(__name__)

class ToneAnalyzer:
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.is_loaded = False
        
        # Tone mapping for sentiment analysis
        self.tone_mapping = {
            "positive": [ToneType.FRIENDLY, ToneType.ENTHUSIASTIC, ToneType.PROFESSIONAL],
            "negative": [ToneType.APOLOGETIC, ToneType.EMOTIONAL],
            "neutral": [ToneType.FORMAL, ToneType.CASUAL, ToneType.ASSERTIVE]
        }
        
        # Tone-specific keywords for better classification
        self.tone_keywords = {
            ToneType.FORMAL: ["sincerely", "respectfully", "regards", "yours truly", "please", "would you", "could you"],
            ToneType.FRIENDLY: ["hey", "hi", "hello", "thanks", "thank you", "appreciate", "great", "awesome"],
            ToneType.APOLOGETIC: ["sorry", "apologize", "apology", "regret", "unfortunately", "my bad", "excuse me"],
            ToneType.ASSERTIVE: ["must", "should", "need to", "have to", "will", "shall", "definitely", "certainly"],
            ToneType.EMOTIONAL: ["feel", "feeling", "upset", "happy", "sad", "angry", "excited", "worried"],
            ToneType.PROFESSIONAL: ["business", "professional", "corporate", "industry", "expertise", "experience"],
            ToneType.CASUAL: ["cool", "awesome", "great", "nice", "yeah", "sure", "okay", "no problem"],
            ToneType.ENTHUSIASTIC: ["amazing", "fantastic", "incredible", "wonderful", "excellent", "brilliant", "outstanding"]
        }
    
    async def load_model(self):
        """Load the Hugging Face model and tokenizer"""
        try:
            logger.info(f"Loading model: {settings.HUGGINGFACE_MODEL}")
            logger.info(f"Using device: {self.device}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(settings.HUGGINGFACE_MODEL)
            self.model = AutoModelForSequenceClassification.from_pretrained(settings.HUGGINGFACE_MODEL)
            
            self.model.to(self.device)
            self.model.eval()
            
            self.is_loaded = True
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Truncate if too long
        if len(text) > settings.MAX_TEXT_LENGTH:
            text = text[:settings.MAX_TEXT_LENGTH]
        
        # Basic cleaning
        text = text.strip()
        return text
    
    def _analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """Analyze sentiment using the loaded model"""
        if not self.is_loaded:
            raise Exception("Model not loaded")
        
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=settings.MAX_TEXT_LENGTH,
            padding=True
        )
        
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class].item()
        
        # Map model output to sentiment
        sentiment_labels = ["negative", "neutral", "positive"]
        sentiment = sentiment_labels[predicted_class]
        
        return sentiment, confidence
    
    def _analyze_tone_keywords(self, text: str) -> Dict[ToneType, float]:
        """Analyze text for tone-specific keywords"""
        text_lower = text.lower()
        tone_scores = {}
        
        for tone, keywords in self.tone_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            tone_scores[tone] = score / len(keywords) if keywords else 0
        
        return tone_scores
    
    def _generate_suggestions(self, text: str, detected_tone: ToneType) -> List[str]:
        """Generate tone improvement suggestions"""
        suggestions = []
        
        if detected_tone == ToneType.FORMAL:
            suggestions.extend([
                "Consider using more conversational language for a friendlier tone",
                "Try adding personal pronouns like 'I' and 'you' to make it more engaging",
                "Include a greeting or closing to make it more personable"
            ])
        elif detected_tone == ToneType.ASSERTIVE:
            suggestions.extend([
                "Consider softening your language with phrases like 'I think' or 'perhaps'",
                "Try using questions instead of statements to be more collaborative",
                "Add context or reasoning to make your point more persuasive"
            ])
        elif detected_tone == ToneType.EMOTIONAL:
            suggestions.extend([
                "Consider using more neutral language to maintain professionalism",
                "Try focusing on facts and solutions rather than feelings",
                "Use 'I feel' statements to express emotions constructively"
            ])
        elif detected_tone == ToneType.CASUAL:
            suggestions.extend([
                "Consider using more formal language for professional contexts",
                "Try using complete sentences and proper punctuation",
                "Add specific details to make your message more informative"
            ])
        
        # Add general suggestions
        suggestions.extend([
            "Consider your audience when choosing your tone",
            "Make sure your message is clear and actionable",
            "Proofread for grammar and spelling"
        ])
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _improve_text(self, text: str, detected_tone: ToneType, target_tone: Optional[ToneType] = None) -> str:
        """Generate an improved version of the text"""
        if target_tone is None:
            # Default to professional tone
            target_tone = ToneType.PROFESSIONAL
        
        improved_text = text
        
        # Simple improvements based on tone
        if detected_tone == ToneType.CASUAL and target_tone == ToneType.PROFESSIONAL:
            # Replace casual words with professional ones
            replacements = {
                "hey": "Hello",
                "hi": "Hello",
                "thanks": "Thank you",
                "cool": "excellent",
                "awesome": "outstanding",
                "yeah": "yes",
                "okay": "acceptable"
            }
            
            for casual, professional in replacements.items():
                improved_text = improved_text.replace(casual, professional)
        
        elif detected_tone == ToneType.ASSERTIVE and target_tone == ToneType.FRIENDLY:
            # Soften assertive language
            replacements = {
                "must": "should consider",
                "have to": "might want to",
                "need to": "could benefit from",
                "will": "would like to"
            }
            
            for assertive, friendly in replacements.items():
                improved_text = improved_text.replace(assertive, friendly)
        
        return improved_text
    
    async def analyze_tone(self, text: str) -> ToneAnalysisResponse:
        """Main method to analyze text tone"""
        if not self.is_loaded:
            await self.load_model()
        
        # Preprocess text
        processed_text = self._preprocess_text(text)
        
        # Analyze sentiment
        sentiment, sentiment_confidence = self._analyze_sentiment(processed_text)
        
        # Analyze tone keywords
        tone_scores = self._analyze_tone_keywords(processed_text)
        
        # Combine sentiment and keyword analysis
        sentiment_tone_candidates = self.tone_mapping.get(sentiment, [ToneType.CASUAL])
        
        # Find the best tone match
        best_tone = ToneType.CASUAL
        best_score = 0
        
        for tone in sentiment_tone_candidates:
            score = tone_scores.get(tone, 0) * sentiment_confidence
            if score > best_score:
                best_score = score
                best_tone = tone
        
        # If no strong keyword match, use sentiment-based tone
        if best_score < settings.CONFIDENCE_THRESHOLD:
            best_tone = sentiment_tone_candidates[0]
            best_score = sentiment_confidence
        
        # Generate suggestions and improved text
        suggestions = self._generate_suggestions(processed_text, best_tone)
        improved_text = self._improve_text(processed_text, best_tone)
        
        # Create tone breakdown
        tone_breakdown = {tone.value: score for tone, score in tone_scores.items()}
        tone_breakdown["sentiment"] = sentiment_confidence
        
        return ToneAnalysisResponse(
            original_text=text,
            detected_tone=best_tone,
            confidence_score=best_score,
            tone_breakdown=tone_breakdown,
            suggestions=suggestions,
            improved_text=improved_text,
            analysis_timestamp=datetime.utcnow()
        )

# Global tone analyzer instance
tone_analyzer = ToneAnalyzer()
