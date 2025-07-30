from typing import List
import requests
from bs4 import BeautifulSoup
from components import BaseComponent
from core import ComponentResultObject
import time
import re
from datetime import datetime


class WebSearchComponent(BaseComponent):
    max_results: int = 5
    timeout: int = 10
    user_agent: str = "yanig/1.0 (https://github.com/user/yanig)"
    
    def invoke(self, input: List[ComponentResultObject]) -> List[ComponentResultObject]:
        results = []
        
        for cro in input:
            search_query = cro["content"]["original_text"]
            max_results = cro["content"]["page_count"] if cro["content"]["page_count"] is not None else self.max_results
            
            if search_query is None or search_query.strip() == "":
                continue
                
            search_results = self._perform_wikipedia_search(search_query, max_results)
            extracted_results = self._extract_content_from_urls(search_results, search_query)
            results.extend(extracted_results)
            
        return results
    
    def _perform_wikipedia_search(self, query: str, max_results: int) -> List[dict]:
        """Perform Wikipedia search and return list of results"""
        try:
            # Clean up query for Wikipedia - remove year/time references and "latest"
            cleaned_query = self._clean_query_for_wikipedia(query)
            
            opensearch_url = "https://en.wikipedia.org/w/api.php"
            
            # Search for page titles
            search_params = {
                'action': 'opensearch',
                'search': cleaned_query,
                'limit': max_results,
                'namespace': 0,
                'format': 'json'
            }
            
            headers = {'User-Agent': self.user_agent}
            response = requests.get(opensearch_url, params=search_params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            search_data = response.json()
            
            if len(search_data) < 4 or len(search_data[1]) == 0:
                # If no results, try with just the core topic
                fallback_query = self._extract_core_topic(query)
                
                search_params['search'] = fallback_query
                response = requests.get(opensearch_url, params=search_params, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                search_data = response.json()
            
            if len(search_data) < 4:
                return []
            
            titles = search_data[1]
            descriptions = search_data[2] if len(search_data) >= 3 and len(search_data[2]) > 0 else [""] * len(titles)
            urls = search_data[3] if len(search_data) >= 4 else []
            
            results = []
            for i, title in enumerate(titles):
                desc = descriptions[i] if i < len(descriptions) else ""
                url = urls[i] if i < len(urls) else f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                
                results.append({
                    'title': title,
                    'href': url,
                    'body': desc,
                    'rank': i + 1
                })
            
            return results
            
        except Exception as e:
            print(f"WebSearchComponent: Wikipedia search failed for query '{query}': {str(e)}")
            return []
    
    def _clean_query_for_wikipedia(self, query: str) -> str:
        """Clean search query to work better with Wikipedia"""
        # Remove temporal words that don't exist in Wikipedia
        temporal_words = ['aktuellste', 'neueste', 'aktuelle', 'neue', 'kommende', '2024', '2025', 'entwicklungen', 'trends']
        
        words = query.lower().split()
        cleaned_words = [word for word in words if word not in temporal_words]
        
        return ' '.join(cleaned_words)
    
    def _extract_core_topic(self, query: str) -> str:
        """Extract the core topic from query for fallback search"""
        # Simple extraction - take the first 1-2 main words
        words = query.lower().split()
        core_words = []
        
        for word in words:
            if word not in ['latest', 'recent', 'current', 'new', 'emerging', 'developments', 'trends', '2024', '2025']:
                core_words.append(word)
                if len(core_words) >= 2:  # Limit to 2 core words
                    break
        
        return ' '.join(core_words) if core_words else 'artificial intelligence'
    
    def _extract_content_from_urls(self, search_results: List[dict], original_query: str) -> List[ComponentResultObject]:
        """Extract content from each URL and create ComponentResultObjects"""
        extracted_results = []
        
        for idx, result in enumerate(search_results):
            try:
                url = result.get('href', '')
                title = result.get('title', '')
                snippet = result.get('body', '')
                
                if not url:
                    continue
                
                # Extract content from URL
                content = self._fetch_and_extract_content(url)
                publish_date = self._extract_publish_date(content, result)
                
                # Create ComponentResultObject
                cro = ComponentResultObject()
                cro["source"] = url
                cro["content"]["original_text"] = content
                cro["content"]["title"] = title
                cro["content"]["publish_date"] = publish_date
                cro["preprocessing"]["keywords"] = original_query
                cro["retrieval"]["rank"] = idx + 1
                
                extracted_results.append(cro)
                
                # Wait before next request to be polite
                if idx < len(search_results) - 1:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"WebSearchComponent: Failed to extract content from {result.get('href', 'unknown URL')}: {str(e)}")
                continue
                
        return extracted_results
    
    def _fetch_and_extract_content(self, url: str) -> str:
        """Fetch webpage and extract main content"""
        try:
            headers = {'User-Agent': self.user_agent}
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            # Try to find main content area
            main_content = None
            for selector in ['main', 'article', '.content', '#content', '.post', '.entry']:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            # If no main content found, use body
            if not main_content:
                main_content = soup.find('body')
            
            # If still nothing, use the whole soup
            if not main_content:
                main_content = soup
            
            # Extract text
            content_text = main_content.get_text()
            
            # Clean up the content (remove excessive whitespace)
            cleaned_content = re.sub(r'\s+', ' ', content_text).strip()
            
            return cleaned_content
            
        except Exception as e:
            print(f"WebSearchComponent: Failed to fetch content from {url}: {str(e)}")
            return ""
    
    def _extract_publish_date(self, content: str, search_result: dict) -> str:
        """Try to extract publish date from content or search result"""
        try:
            # Ensure content is a string
            if not isinstance(content, str):
                return None
                
            # Try to find date patterns in the content (basic approach)
            # This is a simple implementation - could be enhanced with more sophisticated date parsing
            date_patterns = [
                r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
                r'\d{2}\.\d{2}\.\d{4}' # DD.MM.YYYY
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, content[:1000])  # Check first 1000 chars
                if matches:
                    return matches[0]
            
            # If no date found, return None
            return None
            
        except Exception:
            return None
