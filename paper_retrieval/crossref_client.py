import requests
from typing import Dict, Optional, Any
from urllib.parse import quote
import logging

class CrossRefClient:
    def __init__(self, email: str):
        self.base_url = "https://api.crossref.org"
        self.email = email
        self.headers = {
            "User-Agent": f"PaperRetrieval/1.0 (mailto:{email})"
        }
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def get_work_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve work metadata by DOI from CrossRef API
        
        Args:
            doi: The DOI to look up
            
        Returns:
            Dictionary containing work metadata or None if not found
        """
        try:
            encoded_doi = quote(doi)
            url = f"{self.base_url}/works/{encoded_doi}"
            
            self.logger.info(f"Fetching DOI: {doi}")
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                self.logger.warning(f"DOI not found: {doi}")
                return None
            else:
                self.logger.error(f"Error fetching DOI {doi}: {response.status_code}")
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for DOI {doi}: {str(e)}")
            raise
            
    def search_works(self, query: str, 
                    filters: Optional[Dict[str, str]] = None, 
                    limit: int = 20, 
                    offset: int = 0) -> Dict[str, Any]:
        """
        Search for works using CrossRef API
        
        Args:
            query: Search query string
            filters: Optional dictionary of filters
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            Dictionary containing search results
        """
        try:
            url = f"{self.base_url}/works"
            params = {
                "query": query,
                "rows": limit,
                "offset": offset
            }
            
            if filters:
                for key, value in filters.items():
                    params[key] = value
            
            self.logger.info(f"Searching works with query: {query}")
            response = requests.get(url, params=params, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Search failed with status code: {response.status_code}")
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Search request failed: {str(e)}")
            raise

    def get_references_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve references for a work by DOI
        
        Args:
            doi: The DOI to get references for
            
        Returns:
            Dictionary containing reference data or None if not found
        """
        try:
            encoded_doi = quote(doi)
            url = f"{self.base_url}/works/{encoded_doi}/references"
            
            self.logger.info(f"Fetching references for DOI: {doi}")
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                self.logger.warning(f"References not found for DOI: {doi}")
                return None
            else:
                self.logger.error(f"Error fetching references for DOI {doi}: {response.status_code}")
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for references of DOI {doi}: {str(e)}")
            raise