"""
Machine Learning Service for Ransomware Detection
"""
import os
import pickle
import re
from typing import Dict, List
from loguru import logger


class MLService:
    """ML service for filename-based ransomware detection"""
    
    def __init__(self):
        """Initialize ML service"""
        self.model = None
        self.vectorizer = None
        self.model_loaded = False
        
    def load_model(self, model_path: str = None):
        """Load the trained model"""
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), '../../data/models/filename_model.pkl')
        
        try:
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data.get('model')
                    self.vectorizer = model_data.get('vectorizer')
                    self.model_loaded = True
                logger.info(f"✅ ML model loaded from {model_path}")
            else:
                logger.warning(f"⚠️ Model file not found at {model_path}. Using rule-based detection.")
                self.model_loaded = False
        except Exception as e:
            logger.error(f"❌ Error loading ML model: {e}")
            self.model_loaded = False
    
    def analyze_filename(self, filename: str) -> Dict:
        """
        Analyze filename for ransomware indicators
        
        Args:
            filename: The filename to analyze
            
        Returns:
            Dict containing score, level, reasons, advice, and confidence
        """
        reasons = []
        score = 0
        
        # Rule-based detection patterns
        ransomware_patterns = {
            r'\.[a-z]{4,10}$': ("Unusual extension", 15),
            r'^[A-Z0-9]{8,}': ("Random uppercase characters", 20),
            r'\d{8,}': ("Long numeric sequence", 10),
            r'\.encrypt(ed)?$': ("Encrypted indicator", 30),
            r'\.locked?$': ("Locked indicator", 30),
            r'\.crypt(o)?$': ("Crypto indicator", 25),
            r'\.locky$': ("Known ransomware extension", 40),
            r'\.cerber$': ("Known ransomware extension", 40),
            r'\.wannacry$': ("Known ransomware extension", 40),
            r'README|DECRYPT|RESTORE': ("Ransom note keywords", 35),
        }
        
        # Check patterns
        for pattern, (reason, points) in ransomware_patterns.items():
            if re.search(pattern, filename, re.IGNORECASE):
                reasons.append(reason)
                score += points
        
        # If ML model is available, use it
        confidence = 0.7  # Default rule-based confidence
        if self.model_loaded and self.model and self.vectorizer:
            try:
                features = self.vectorizer.transform([filename])
                prediction = self.model.predict(features)[0]
                proba = self.model.predict_proba(features)[0]
                confidence = max(proba)
                
                if prediction == 1:  # Malicious
                    score = int(score * 0.3 + 70 * confidence)  # Blend ML and rules
                    reasons.append("ML model detected ransomware patterns")
                else:
                    score = int(score * 0.7 + 30 * (1 - confidence))
            except Exception as e:
                logger.error(f"ML prediction error: {e}")
        
        # Determine risk level
        if score >= 70:
            level = "HIGH RISK"
            advice = "Do not open! Likely ransomware. Quarantine immediately."
        elif score >= 40:
            level = "MEDIUM RISK"
            advice = "Caution advised. Scan with antivirus before opening."
        elif score >= 20:
            level = "LOW RISK"
            advice = "Some suspicious patterns detected. Proceed with caution."
        else:
            level = "SAFE"
            advice = "No obvious ransomware indicators found."
            reasons.append("File appears normal")
        
        return {
            "score": min(score, 100),
            "level": level,
            "reasons": reasons if reasons else ["No suspicious patterns found"],
            "advice": advice,
            "confidence": round(confidence, 2)
        }


# Global ML service instance
ml_service = MLService()
