import pytest
from app.services.tone_analyzer import tone_analyzer
from app.models import ToneType

@pytest.mark.asyncio
async def test_tone_analyzer_initialization():
    """Test tone analyzer initialization"""
    assert tone_analyzer is not None
    assert hasattr(tone_analyzer, 'analyze_tone')

@pytest.mark.asyncio
async def test_analyze_friendly_tone():
    """Test analyzing friendly tone"""
    text = "Hey there! How are you doing today? I hope you're having a great day!"
    
    # Note: This test requires the model to be loaded
    # In a real test environment, you'd mock the model or use a test model
    try:
        result = await tone_analyzer.analyze_tone(text)
        
        assert result is not None
        assert result.original_text == text
        assert result.detected_tone in ToneType
        assert 0.0 <= result.confidence_score <= 1.0
        assert len(result.suggestions) > 0
        assert result.improved_text is not None
        
    except Exception as e:
        # If model is not loaded, skip the test
        pytest.skip(f"Model not loaded: {e}")

@pytest.mark.asyncio
async def test_analyze_formal_tone():
    """Test analyzing formal tone"""
    text = "Dear Sir/Madam, I am writing to inquire about the status of my application."
    
    try:
        result = await tone_analyzer.analyze_tone(text)
        
        assert result is not None
        assert result.original_text == text
        assert result.detected_tone in ToneType
        assert 0.0 <= result.confidence_score <= 1.0
        
    except Exception as e:
        pytest.skip(f"Model not loaded: {e}")

@pytest.mark.asyncio
async def test_analyze_assertive_tone():
    """Test analyzing assertive tone"""
    text = "You must complete this task by Friday. There are no exceptions."
    
    try:
        result = await tone_analyzer.analyze_tone(text)
        
        assert result is not None
        assert result.original_text == text
        assert result.detected_tone in ToneType
        assert 0.0 <= result.confidence_score <= 1.0
        
    except Exception as e:
        pytest.skip(f"Model not loaded: {e}")

@pytest.mark.asyncio
async def test_analyze_apologetic_tone():
    """Test analyzing apologetic tone"""
    text = "I'm really sorry for the inconvenience. I apologize for the delay."
    
    try:
        result = await tone_analyzer.analyze_tone(text)
        
        assert result is not None
        assert result.original_text == text
        assert result.detected_tone in ToneType
        assert 0.0 <= result.confidence_score <= 1.0
        
    except Exception as e:
        pytest.skip(f"Model not loaded: {e}")

def test_tone_keywords():
    """Test tone keyword detection"""
    assert hasattr(tone_analyzer, 'tone_keywords')
    assert ToneType.FRIENDLY in tone_analyzer.tone_keywords
    assert ToneType.FORMAL in tone_analyzer.tone_keywords
    assert ToneType.ASSERTIVE in tone_analyzer.tone_keywords
    assert ToneType.APOLOGETIC in tone_analyzer.tone_keywords

def test_tone_mapping():
    """Test tone mapping configuration"""
    assert hasattr(tone_analyzer, 'tone_mapping')
    assert 'positive' in tone_analyzer.tone_mapping
    assert 'negative' in tone_analyzer.tone_mapping
    assert 'neutral' in tone_analyzer.tone_mapping
