import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from typing import Dict, List, Tuple, Optional
import logging
import re
from ..config import settings

logger = logging.getLogger(__name__)

class ToneAnalyzer:
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.is_loaded = False
        
        # Updated tone detection prompt for sad/angry/friendly classification
        self.tone_detection_prompt = "Classify the emotional tone of this text as either 'sad', 'angry', or 'friendly'. Consider the overall emotional sentiment and word choice. Text: {text}"
        
        # Text improvement prompts - simplified to just improve while maintaining tone
        self.improvement_prompts = {
            "sad": "Improve the grammar, clarity, and flow of this text while keeping its sad emotional tone: {text}",
            "angry": "Improve the grammar, clarity, and flow of this text while keeping its angry emotional tone: {text}",
            "friendly": "Improve the grammar, clarity, and flow of this text while keeping its friendly emotional tone: {text}"
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
        """Detect the emotional tone (sad, angry, friendly) of the text"""
        if not self.is_loaded:
            raise Exception("Model not loaded")
        
        try:
            # Use updated prompt for sad/angry/friendly detection
            prompt = self.tone_detection_prompt.format(text=text)
            
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
            
            # Extract tone from result - look for sad, angry, or friendly
            result_lower = result.lower()
            if "sad" in result_lower:
                return "sad"
            elif "angry" in result_lower:
                return "angry"
            elif "friendly" in result_lower:
                return "friendly"
            else:
                # Fallback logic based on common patterns
                if any(word in text.lower() for word in ['sorry', 'disappointed', 'upset', 'hurt', 'cry', 'tears']):
                    return "sad"
                elif any(word in text.lower() for word in ['angry', 'mad', 'furious', 'hate', 'stupid', 'damn']):
                    return "angry"
                else:
                    return "friendly"
                
        except Exception as e:
            logger.error(f"Error in tone detection: {e}")
            # Fallback to friendly if detection fails
            return "friendly"
    
    def _improve_text(self, text: str, detected_tone: str) -> str:
        """Improve text while maintaining the detected tone"""
        if not self.is_loaded:
            raise Exception("Model not loaded")
        
        try:
            # Use the detected tone for improvement
            if detected_tone not in self.improvement_prompts:
                detected_tone = "friendly"  # Default fallback
            
            prompt = self.improvement_prompts[detected_tone].format(text=text)
            
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
    
    async def analyze_tone(self, text: str) -> Dict[str, str]:
        """Main method to analyze text tone and improve it"""
        if not self.is_loaded:
            await self.load_model()
        
        # Preprocess text
        processed_text = self._preprocess_text(text)
        
        try:
            # Detect tone
            detected_tone = self._detect_tone(processed_text)
            
            # Improve text while maintaining the detected tone
            improved_text = self._improve_text(processed_text, detected_tone)
            
            return {
                "tone": detected_tone,
                "improved_text": improved_text
            }
            
        except Exception as e:
            logger.error(f"Error in tone analysis: {e}")
            # Return fallback response
            return {
                "tone": "friendly",
                "improved_text": text
            }

# Global tone analyzer instance
tone_analyzer = ToneAnalyzer()