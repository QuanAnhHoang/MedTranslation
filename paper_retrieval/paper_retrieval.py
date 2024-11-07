from typing import Dict, List, Optional, Any
import json
from datetime import datetime
from pathlib import Path
import logging
from crossref_client import CrossRefClient

class PaperRetrievalSystem:
    def __init__(self, email: str, cache_dir: str = "cache"):
        self.client = CrossRefClient(email)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _get_cache_path(self, doi: str) -> Path:
        """Get the cache file path for a DOI"""
        return self.cache_dir / f"{doi.replace('/', '_')}.json"

    def _cache_paper(self, doi: str, data: Dict[str, Any]):
        """Cache paper data to file"""
        try:
            cache_path = self._get_cache_path(doi)
            with cache_path.open('w', encoding='utf-8') as f:
                json.dump({
                    'data': data,
                    'cached_at': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to cache paper {doi}: {str(e)}")

    def _get_cached_paper(self, doi: str) -> Optional[Dict[str, Any]]:
        """Retrieve paper data from cache if available"""
        cache_path = self._get_cache_path(doi)
        if cache_path.exists():
            try:
                with cache_path.open('r', encoding='utf-8') as f:
                    cached = json.load(f)
                    return cached['data']
            except Exception as e:
                self.logger.error(f"Failed to read cache for {doi}: {str(e)}")
                return None
        return None

    def get_paper(self, doi: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Retrieve paper metadata by DOI
        
        Args:
            doi: The DOI to retrieve
            use_cache: Whether to use cached data if available
            
        Returns:
            Dictionary containing paper metadata or None if not found
        """
        if use_cache:
            cached = self._get_cached_paper(doi)
            if cached:
                self.logger.info(f"Retrieved paper {doi} from cache")
                return cached

        paper = self.client.get_work_by_doi(doi)
        if paper:
            self._cache_paper(doi, paper)
            return paper
        return None

    def get_paper_with_references(self, doi: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Retrieve paper metadata and its references
        
        Args:
            doi: The DOI to retrieve
            use_cache: Whether to use cached data if available
            
        Returns:
            Dictionary containing paper metadata and references or None if not found
        """
        paper = self.get_paper(doi, use_cache)
        if not paper:
            return None
            
        references = self.client.get_references_by_doi(doi)
        if references:
            paper['references'] = references
            self._cache_paper(doi, paper)
            
        return paper

    def search_papers(self, query: str, 
                     filters: Optional[Dict[str, str]] = None,
                     limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for papers using query string
        
        Args:
            query: Search query
            filters: Optional filters to apply
            limit: Maximum number of results
            
        Returns:
            List of paper metadata dictionaries
        """
        results = self.client.search_works(query, filters, limit)
        if results and 'items' in results:
            return results['items']
        return []

    def extract_paper_info(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant information from paper metadata
        
        Args:
            paper: Paper metadata dictionary
            
        Returns:
            Dictionary containing extracted information
        """
        try:
            return {
                'doi': paper.get('DOI'),
                'title': paper.get('title', [None])[0],
                'authors': [
                    {
                        'given': author.get('given'),
                        'family': author.get('family')
                    }
                    for author in paper.get('author', [])
                ],
                'published': paper.get('published-print', {}).get('date-parts', [[None]])[0][0],
                'journal': paper.get('container-title', [None])[0],
                'type': paper.get('type'),
                'abstract': paper.get('abstract')
            }
        except Exception as e:
            self.logger.error(f"Failed to extract paper info: {str(e)}")
            return {}