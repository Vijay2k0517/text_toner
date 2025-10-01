import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from typing import Dict, List, Tuple, Optional
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class ToneAnalyzer:
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.is_loaded = False
        
        # Tone detection prompts for FLAN-T5
        self.tone_detection_prompts = {
            "positive": "Classify the sentiment of this text as positive, negative, or neutral. Text: {text}",
            "negative": "Classify the sentiment of this text as positive, negative, or neutral. Text: {text}",
            "neutral": "Classify the sentiment of this text as positive, negative, or neutral. Text: {text}"
        }
        
        # Text improvement prompts based on target tone
        self.improvement_prompts = {
            "positive": "Rewrite this text to make it more positive and upbeat while preserving the original meaning: {text}",
            "negative": "Rewrite this text to make it more negative or critical while preserving the original meaning: {text}",
            "neutral": "Rewrite this text to make it more neutral and objective while preserving the original meaning: {text}",
            "professional": "Rewrite this text to make it more professional and formal while preserving the original meaning: {text}",
            "friendly": "Rewrite this text to make it more friendly and warm while preserving the original meaning: {text}",
            "formal": "Rewrite this text to make it more formal and structured while preserving the original meaning: {text}"
        }
    
    async def load_model(self):
        """Load the FLAN-T5 XL model and tokenizer"""
        try:
            logger.info(f"Loading model: {settings.HUGGINGFACE_MODEL}")
            logger.info(f"Using device: {self.device}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.HUGGINGFACE_MODEL,
                use_fast=True
            )
            
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                settings.HUGGINGFACE_MODEL,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
                device_map="auto" if self.device.type == "cuda" else None
            )
            
            if self.device.type == "cpu":
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
    
    def _detect_tone(self, text: str) -> str:
        """Detect the general tone (positive, negative, neutral) of the text"""
        if not self.is_loaded:
            raise Exception("Model not loaded")
        
        try:
            # Use a simple prompt for tone detection
            prompt = f"Classify the sentiment of this text as positive, negative, or neutral. Text: {text}"
            
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=50,
                    num_beams=2,
                    early_stopping=True,
                    do_sample=False
                )
            
            # Decode the output
            result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract tone from result
            result_lower = result.lower()
            if "positive" in result_lower:
                return "positive"
            elif "negative" in result_lower:
                return "negative"
            else:
                return "neutral"
                
        except Exception as e:
            logger.error(f"Error in tone detection: {e}")
            # Fallback to neutral if detection fails
            return "neutral"
    
    def _improve_text(self, text: str, target_tone: Optional[str] = None) -> str:
        """Improve text based on target tone using FLAN-T5"""
        if not self.is_loaded:
            raise Exception("Model not loaded")
        
        try:
            # Use target tone if provided, otherwise use neutral
            tone = target_tone if target_tone and target_tone in self.improvement_prompts else "neutral"
            
            prompt = self.improvement_prompts[tone].format(text=text)
            
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=min(len(text) + 100, 512),
                    num_beams=3,
                    early_stopping=True,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9
                )
            
            # Decode the output
            improved_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Clean up the result
            improved_text = improved_text.strip()
            
            # If the model didn't generate a good response, return original text
            if len(improved_text) < len(text) * 0.5 or improved_text.lower() == text.lower():
                return text
            
            return improved_text
            
        except Exception as e:
            logger.error(f"Error in text improvement: {e}")
            # Return original text if improvement fails
            return text
    
    async def analyze_tone(self, text: str, target_tone: Optional[str] = None) -> Dict[str, str]:
        """Main method to analyze text tone and improve it"""
        if not self.is_loaded:
            await self.load_model()
        
        # Preprocess text
        processed_text = self._preprocess_text(text)
        
        try:
            # Detect tone
            detected_tone = self._detect_tone(processed_text)
            
            # Improve text
            improved_text = self._improve_text(processed_text, target_tone)
            
            return {
                "original_text": text,
                "detected_tone": detected_tone,
                "improvised_text": improved_text
            }
            
        except Exception as e:
            logger.error(f"Error in tone analysis: {e}")
            # Return fallback response
            return {
                "original_text": text,
                "detected_tone": "neutral",
                "improvised_text": text
            }

# Global tone analyzer instance
tone_analyzer = ToneAnalyzer()