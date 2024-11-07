from typing import Dict, List, Optional, Tuple
import re
import logging
from medical_dictionary import MedicalDictionary

class TranslationValidator:
    def __init__(self, dictionary: MedicalDictionary):
        self.dictionary = dictionary
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        
        # Common Vietnamese diacritics patterns
        self.diacritic_patterns = {
            'a': '[aáàảãạăắằẳẵặâấầẩẫậ]',
            'e': '[eéèẻẽẹêếềểễệ]',
            'i': '[iíìỉĩị]',
            'o': '[oóòỏõọôốồổỗộơớờởỡợ]',
            'u': '[uúùủũụưứừửữự]',
            'y': '[yýỳỷỹỵ]',
            'd': '[dđ]'
        }
    
    def validate_translation(self, 
                           english: str, 
                           vietnamese: str) -> Dict[str, any]:
        """
        Validate a Vietnamese translation of an English medical term
        
        Args:
            english: English term
            vietnamese: Vietnamese translation to validate
            
        Returns:
            Dictionary containing validation results
        """
        results = {
            "valid": True,
            "issues": [],
            "confidence": 1.0,
            "suggestions": []
        }
        
        # Check if term exists in dictionary
        existing = self.dictionary.get_translation(english)
        if existing:
            if existing["vietnamese"].lower() != vietnamese.lower():
                results["valid"] = False
                results["issues"].append("Translation differs from dictionary")
                results["suggestions"].append(existing["vietnamese"])
                results["confidence"] *= 0.7
        
        # Check for missing diacritics
        if self._has_missing_diacritics(vietnamese):
            results["valid"] = False
            results["issues"].append("Missing diacritical marks")
            results["confidence"] *= 0.8
        
        # Check for basic formatting
        if not self._check_formatting(vietnamese):
            results["valid"] = False
            results["issues"].append("Incorrect formatting")
            results["confidence"] *= 0.9
        
        # Find similar terms for reference
        similar_terms = self.dictionary.get_similar_terms(english)
        if similar_terms:
            results["similar_terms"] = [
                {
                    "english": term,
                    "vietnamese": self.dictionary.get_translation(term)["vietnamese"],
                    "similarity": score
                }
                for term, score in similar_terms
            ]
        
        return results
    
    def _has_missing_diacritics(self, text: str) -> bool:
        """
        Check if Vietnamese text is missing diacritical marks
        
        Args:
            text: Vietnamese text to check
            
        Returns:
            bool: True if missing diacritics likely
        """
        # Simple heuristic: Check if text contains basic Vietnamese characters
        vietnamese_chars = 'àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ'
        text_lower = text.lower()
        
        # If text contains Vietnamese words but no diacritics, likely missing marks
        has_vietnamese_words = bool(re.search(r'[ăâđêôơư]', text_lower))
        has_diacritics = any(c in text_lower for c in vietnamese_chars)
        
        return has_vietnamese_words and not has_diacritics
    
    def _check_formatting(self, text: str) -> bool:
        """
        Check if text follows basic formatting rules
        
        Args:
            text: Text to check
            
        Returns:
            bool: True if formatting is correct
        """
        # Check basic formatting rules
        if not text:
            return False
            
        # Should not start or end with whitespace
        if text != text.strip():
            return False
            
        # Should not have multiple consecutive spaces
        if '  ' in text:
            return False
            
        # Should not contain unusual characters
        if bool(re.search(r'[^a-zA-Z0-9àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđĐ\s\-.,()]', text)):
            return False
            
        return True
    
    def suggest_improvements(self, 
                           english: str, 
                           vietnamese: str) -> List[str]:
        """
        Suggest improvements for a translation
        
        Args:
            english: English term
            vietnamese: Vietnamese translation
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # Check dictionary for existing translation
        existing = self.dictionary.get_translation(english)
        if existing and existing["vietnamese"] != vietnamese:
            suggestions.append(f"Consider using established translation: {existing['vietnamese']}")
        
        # Check for missing diacritics
        if self._has_missing_diacritics(vietnamese):
            suggestions.append("Add appropriate diacritical marks to Vietnamese text")
        
        # Check formatting
        if not self._check_formatting(vietnamese):
            suggestions.append("Fix formatting issues (whitespace, special characters)")
        
        # Find similar terms
        similar_terms = self.dictionary.get_similar_terms(english)
        if similar_terms:
            suggestions.append("Related terms for reference:")
            for term, score in similar_terms[:3]:
                term_data = self.dictionary.get_translation(term)
                suggestions.append(f"- {term}: {term_data['vietnamese']}")
        
        return suggestions