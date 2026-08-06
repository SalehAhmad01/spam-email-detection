import os
import re
import pickle
from pathlib import Path
from django.conf import settings

# Rule-based Detection Engine for Nigerian SMS & Email Threat Filtering

FRAUD_KEYWORDS = [
    'bvn', 'nin', 'otp', 'pin', 'cvv', 'atm card', 'card number', 'account freeze',
    'cbn', 'cbn-verify', 'central bank', 'audit-portal', 'palmpay', 'opay',
    'customs', 'clearance fee', 'inheritance', 'relative abroad', 'tax refund',
    'firs', 'deactivated', 'suspended', 'unusual login', 'security alert', 'deactivation'
]

SPAM_KEYWORDS = [
    'won', 'winner', 'promo', 'claim', 'cash reward', 'car', 'giveaway',
    'cheap loan', 'no collateral', 'herbal', 'miracle tea', 'lose 10kg',
    'free data', 'double your money', '200k', '500k', '500,000', 'followers',
    'discount', 'recharge card'
]

PIDGIN_MARKERS = [
    'abeg', 'dey', 'make', 'don', 'wetin', 'baba', 'sharp sharp', 'wahala',
    'dem', 'oya', 'sef', 'oga', 'gist', 'reach', 'carry', 'check am'
]

_ML_MODEL_CACHE = None


def load_ml_model():
    """
    Loads ML pipeline model safely. If pickle file does not exist, returns fallback rule predictor.
    """
    global _ML_MODEL_CACHE
    if _ML_MODEL_CACHE is not None:
        return _ML_MODEL_CACHE

    model_path = getattr(settings, 'ML_MODEL_PATH', None)
    if not model_path:
        model_path = Path(settings.BASE_DIR) / 'apps' / 'detector' / 'data' / 'model.pkl'

    if os.path.exists(model_path):
        try:
            with open(model_path, 'rb') as f:
                _ML_MODEL_CACHE = pickle.load(f)
                return _ML_MODEL_CACHE
        except Exception:
            _ML_MODEL_CACHE = None

    return None


def predict_ml(raw_text: str) -> dict:
    """
    Runs prediction through ML pipeline model if available, otherwise safe rule-based fallback.
    """
    model = load_ml_model()
    if model and hasattr(model, 'predict'):
        try:
            preds = model.predict([raw_text])
            pred_label = preds[0] if preds else None
            proba = 0.90
            if hasattr(model, 'predict_proba'):
                probas = model.predict_proba([raw_text])
                if probas is not None and len(probas) > 0:
                    proba = float(max(probas[0]))
            return {'label': pred_label, 'confidence': float(proba), 'source': 'ml_pipeline'}
        except Exception:
            pass

    return {'label': None, 'confidence': 0.0, 'source': 'fallback'}


def analyze_message(raw_text: str, channel: str = 'sms', sender: str = None) -> dict:
    """
    Analyzes input message text and returns detection classification metrics:
    - label: 'legit' | 'spam' | 'fraud'
    - confidence_score: float (0.0 to 1.0)
    - flagged_keywords: list of matched keywords/rules
    - language_mix: 'english' | 'pidgin' | 'mixed'
    - model_version: str
    """
    if not raw_text:
        return {
            'label': 'legit',
            'confidence_score': 1.0,
            'flagged_keywords': [],
            'language_mix': 'english',
            'model_version': 'v1.0-rules-engine'
        }

    text_lower = raw_text.lower()

    # 1. Match Fraud & Spam Keywords
    flagged_fraud = [kw for kw in FRAUD_KEYWORDS if kw in text_lower]
    flagged_spam = [kw for kw in SPAM_KEYWORDS if kw in text_lower]

    flagged_keywords = list(set(flagged_fraud + flagged_spam))

    # 2. Language Detection
    pidgin_matches = [m for m in PIDGIN_MARKERS if m in text_lower]
    words = re.findall(r'\w+', text_lower)
    total_words = len(words) or 1

    if len(pidgin_matches) >= 3 or (len(pidgin_matches) / total_words >= 0.25):
        language_mix = 'pidgin'
    elif len(pidgin_matches) >= 1:
        language_mix = 'mixed'
    else:
        language_mix = 'english'

    # 3. ML Prediction Probe
    ml_res = predict_ml(raw_text)

    # 4. Label & Confidence Scoring
    if flagged_fraud:
        label = 'fraud'
        confidence_score = min(0.85 + (len(flagged_fraud) * 0.04), 0.99)
    elif flagged_spam:
        label = 'spam'
        confidence_score = min(0.80 + (len(flagged_spam) * 0.04), 0.96)
    elif ml_res.get('label'):
        label = ml_res['label']
        confidence_score = ml_res['confidence']
    else:
        label = 'legit'
        confidence_score = 0.95

    return {
        'label': label,
        'confidence_score': round(confidence_score, 2),
        'flagged_keywords': flagged_keywords,
        'language_mix': language_mix,
        'model_version': 'v1.0-hybrid-engine'
    }
