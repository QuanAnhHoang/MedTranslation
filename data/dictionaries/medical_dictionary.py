import json
import csv
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging
from datetime import datetime
import difflib

class MedicalDictionary:
    def __init__(self, dictionary_path: str = "medical_dictionary.json"):
        self.dictionary_path = Path(dictionary_path)
        self.terms: Dict[str, Dict] = {}
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Load dictionary if exists
        self._load_dictionary()
    
    def _load_dictionary(self):
        """Load the medical dictionary from file"""
        try:
            if self.dictionary_path.exists():
                with self.dictionary_path.open('r', encoding='utf-8') as f:
                    self.terms = json.load(f)
                self.logger.info(f"Loaded {len(self.terms)} terms from dictionary")
            else:
                self.logger.info("No existing dictionary found. Starting with empty dictionary")
        except Exception as e:
            self.logger.error(f"Error loading dictionary: {str(e)}")
            self.terms = {}
    
    def _save_dictionary(self):
        """Save the medical dictionary to file"""
        try:
            with self.dictionary_path.open('w', encoding='utf-8') as f:
                json.dump(self.terms, f, ensure_ascii=False, indent=2)
            self.logger.info("Dictionary saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving dictionary: {str(e)}")
    
    def add_term(self, 
                 english: str, 
                 vietnamese: str, 
                 category: str = "general",
                 source: str = "manual",
                 confidence: float = 1.0) -> bool:
        """
        Add a new term to the dictionary
        
        Args:
            english: English term
            vietnamese: Vietnamese translation
            category: Medical category
            source: Source of the translation
            confidence: Confidence score of the translation
            
        Returns:
            bool: Success status
        """
        try:
            english = english.lower().strip()
            vietnamese = vietnamese.strip()
            
            term_data = {
                "vietnamese": vietnamese,
                "category": category,
                "source": source,
                "confidence": confidence,
                "added_date": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "versions": [{
                    "vietnamese": vietnamese,
                    "confidence": confidence,
                    "date": datetime.now().isoformat(),
                    "source": source
                }]
            }
            
            self.terms[english] = term_data
            self._save_dictionary()
            self.logger.info(f"Added term: {english} - {vietnamese}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding term: {str(e)}")
            return False
    
    def update_term(self,
                    english: str,
                    vietnamese: str,
                    source: str = "manual",
                    confidence: float = 1.0) -> bool:
        """
        Update an existing term's translation
        
        Args:
            english: English term
            vietnamese: New Vietnamese translation
            source: Source of the update
            confidence: Confidence score of the new translation
            
        Returns:
            bool: Success status
        """
        try:
            english = english.lower().strip()
            vietnamese = vietnamese.strip()
            
            if english not in self.terms:
                self.logger.warning(f"Term not found: {english}")
                return False
            
            term = self.terms[english]
            
            # Add new version to version history
            term["versions"].append({
                "vietnamese": vietnamese,
                "confidence": confidence,
                "date": datetime.now().isoformat(),
                "source": source
            })
            
            # Update current translation
            term["vietnamese"] = vietnamese
            term["confidence"] = confidence
            term["last_updated"] = datetime.now().isoformat()
            term["source"] = source
            
            self._save_dictionary()
            self.logger.info(f"Updated term: {english} - {vietnamese}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating term: {str(e)}")
            return False
    
    def get_translation(self, english: str) -> Optional[Dict]:
        """
        Get translation for an English term
        
        Args:
            english: English term to look up
            
        Returns:
            Dictionary containing translation data or None if not found
        """
        english = english.lower().strip()
        return self.terms.get(english)
    
    def get_similar_terms(self, term: str, n: int = 5) -> List[Tuple[str, float]]:
        """
        Find similar terms using fuzzy matching
        
        Args:
            term: Term to find matches for
            n: Number of matches to return
            
        Returns:
            List of tuples containing (term, similarity_score)
        """
        term = term.lower().strip()
        matches = []
        
        for existing_term in self.terms.keys():
            ratio = difflib.SequenceMatcher(None, term, existing_term).ratio()
            if ratio > 0.6:  # Minimum similarity threshold
                matches.append((existing_term, ratio))
        
        # Sort by similarity score and return top n
        return sorted(matches, key=lambda x: x[1], reverse=True)[:n]
    
    def export_csv(self, filepath: str):
        """
        Export dictionary to CSV file
        
        Args:
            filepath: Path to save CSV file
        """
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['English', 'Vietnamese', 'Category', 'Confidence', 'Last Updated'])
                
                for english, data in self.terms.items():
                    writer.writerow([
                        english,
                        data['vietnamese'],
                        data['category'],
                        data['confidence'],
                        data['last_updated']
                    ])
            
            self.logger.info(f"Dictionary exported to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {str(e)}")
    
    def import_csv(self, filepath: str, source: str = "import"):
        """
        Import terms from CSV file
        
        Args:
            filepath: Path to CSV file
            source: Source identifier for imported terms
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.add_term(
                        english=row['English'],
                        vietnamese=row['Vietnamese'],
                        category=row.get('Category', 'general'),
                        source=source,
                        confidence=float(row.get('Confidence', 1.0))
                    )
            
            self.logger.info(f"Successfully imported terms from {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error importing from CSV: {str(e)}")