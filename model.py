import requests
import re
import random

# HuggingFace Inference API Details
API_URL = "https://api-inference.huggingface.co/models/mrm8488/bert-tiny-finetuned-fake-news-detection"

def query_api(payload):
    try:
        response = requests.post(API_URL, json=payload, timeout=3)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def analyze_patterns(text):
    """
    Analyzes text for stylistic patterns (heuristics).
    Returns a score contribution and reasons.
    """
    reasons = []
    score_bump = 0
    text_lower = text.lower()
    
    # Emotional/Sensational words
    emotional_triggers = ['shocking', 'unbelievable', 'exposed', 'secret', 'panic', 'terror', 'miracle', 'mind-blowing', 'shame', 'betrayal', 'hoax', 'banned', 'conspiracy']
    found_triggers = [word for word in emotional_triggers if word in text_lower]
    if found_triggers:
        reasons.append(f"Contains sensational language: '{', '.join(found_triggers[:3])}...'")
        score_bump += 20 * len(found_triggers)
        
    # Caps lock usage
    if len(text) > 10 and sum(1 for c in text if c.isupper()) / len(text) > 0.3:
        reasons.append("Excessive use of capitalization.")
        score_bump += 30
        
    # Punctuation
    if "!!" in text or "?!?" in text:
        reasons.append("Non-standard punctuation used to evoke emotion.")
        score_bump += 20

    # Length check
    if len(text.split()) < 5:
        reasons.append("Headline is critically short.")
        score_bump += 10
        
    return score_bump, reasons

def predict_news(text):
    # 1. Get AI Prediction
    api_result = query_api({"inputs": text})
    
    # 2. Heuristics
    impulse_score, pattern_reasons = analyze_patterns(text)
    
    # Defaults
    score = 50
    label = "Uncertain"
    classification = "UNCERTAIN"
    reasons = []
    
    classification_done = False

    # 3. Process API
    if api_result and isinstance(api_result, list) and len(api_result) > 0 and isinstance(api_result[0], list):
        try:
            predictions = api_result[0]
            top_pred = max(predictions, key=lambda x: x.get('score', 0))
            confidence = top_pred.get('score', 0)
            pred_label = top_pred.get('label')
            
            if confidence >= 0.65:
                if pred_label == 'LABEL_0': # FAKE
                    label = "Likely Fake"
                    classification = "FAKE"
                    score = int((1 - confidence) * 100)
                    reasons.append(f"AI Model high confidence ({int(confidence*100)}%) of misinformation.")
                else: # REAL
                    label = "Likely Real"
                    classification = "REAL"
                    score = int(confidence * 100)
                    reasons.append(f"AI Model high confidence ({int(confidence*100)}%) this is legitimate.")
                classification_done = True
        except:
            pass
            
    # 4. Fallback Logic (Strong Heuristics can override Uncertainty if API fails)
    if not classification_done:
        if api_result is None:
            reasons.append("External AI service unreachable; using local analysis.")
        
        # If strong signals of fake news exist
        if impulse_score >= 40:
            classification = "FAKE"
            label = "Likely Fake"
            score = max(5, 50 - impulse_score) # Lower score = more fake. 50-40=10 (very fake)
            reasons.append("Language patterns strongly suggest clickbait or misinformation.")
        elif impulse_score == 0 and len(text.split()) > 6:
            # Clean text, long enough
            # We can't say Likely Real confidently without source check, but for demo we can lean that way if neutral
            classification = "REAL"
            label = "Likely Real"
            score = 85
            reasons.append("No sensational patterns detected.")
            reasons.append("Tone appears neutral and objective.")
        else:
            # Truly Uncertain
            score = 50
            label = "Uncertain"
            classification = "UNCERTAIN"
            reasons.append("Insufficient data to classify.")

    if pattern_reasons:
        reasons.extend(pattern_reasons)
        
    return {
        "credibility_score": score,
        "label": label,
        "classification": classification,
        "reasons": reasons[:4]
    }
