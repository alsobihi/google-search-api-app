"""
Google Search API client with rate limiting and database integration
"""
import requests
import time
import json
import logging
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from database import db_manager
from config import config

logger = logging.getLogger(__name__)

class GoogleSearchAPI:
 """Google Custom Search API client with rate limiting"""
 
 def __init__(self):
     self.api_key = config.GOOGLE_API_KEY
     self.search_engine_id = config.GOOGLE_SEARCH_ENGINE_ID
     self.base_url = "https://www.googleapis.com/customsearch/v1"
 
 def is_configured(self) -> bool:
     """Check if API is properly configured"""
     return bool(self.api_key and self.search_engine_id)
 
 def _check_rate_limit(self) -> bool:
     """Check if we can make another API request today"""
     current_count = db_manager.get_daily_request_count()
     if current_count >= config.MAX_DAILY_REQUESTS:
         logger.warning(f"Daily rate limit reached: {current_count}/{config.MAX_DAILY_REQUESTS}")
         return False
     return True
 
 def search(self, query: str, num_results: int = None, start_index: int = 1) -> Dict[str, Any]:
     """
     Perform a Google search with rate limiting and database logging
     
     Args:
         query: Search query string
         num_results: Number of results to return (default from config)
         start_index: Starting index for results (1-based)
     
     Returns:
         Dictionary containing search results and metadata
     """
     if not self.is_configured():
         error_msg = "Google API key and Search Engine ID must be provided"
         logger.error(error_msg)
         return {
             'success': False,
             'error': error_msg,
             'request_id': None,
             'results': []
         }
         
     if num_results is None:
         num_results = config.DEFAULT_RESULTS_PER_QUERY
     
     # Check rate limit
     if not self._check_rate_limit():
         error_msg = f"Daily API request limit of {config.MAX_DAILY_REQUESTS} exceeded"
         request_id = db_manager.log_api_request(
             query, num_results, start_index, 'rate_limited', error_message=error_msg
         )
         return {
             'success': False,
             'error': error_msg,
             'request_id': request_id,
             'results': []
         }
     
     # Prepare API request
     params = {
         'key': self.api_key,
         'cx': self.search_engine_id,
         'q': query,
         'num': min(num_results, 10),  # Google API max is 10 per request
         'start': start_index
     }
     
     start_time = time.time()
     request_id = None
     
     try:
         logger.info(f"Making Google Search API request for query: '{query}'")
         response = requests.get(self.base_url, params=params, timeout=30)
         response_time_ms = int((time.time() - start_time) * 1000)
         
         if response.status_code == 200:
             data = response.json()
             
             # Log successful request
             request_id = db_manager.log_api_request(
                 query, num_results, start_index, 'success', response_time_ms
             )
             
             # Increment daily usage
             db_manager.increment_daily_usage()
             
             # Extract and save results
             results = data.get('items', [])
             if request_id and results:
                 db_manager.save_search_results(request_id, results)
             
             logger.info(f"Search successful: {len(results)} results returned")
             
             return {
                 'success': True,
                 'request_id': request_id,
                 'query': query,
                 'total_results': data.get('searchInformation', {}).get('totalResults', '0'),
                 'search_time': data.get('searchInformation', {}).get('searchTime', '0'),
                 'results': results,
                 'response_time_ms': response_time_ms
             }
         
         else:
             error_msg = f"API request failed with status {response.status_code}: {response.text}"
             logger.error(error_msg)
             
             request_id = db_manager.log_api_request(
                 query, num_results, start_index, 'error', response_time_ms, error_msg
             )
             
             return {
                 'success': False,
                 'error': error_msg,
                 'request_id': request_id,
                 'results': []
             }
     
     except requests.exceptions.RequestException as e:
         response_time_ms = int((time.time() - start_time) * 1000)
         error_msg = f"Network error: {str(e)}"
         logger.error(error_msg)
         
         request_id = db_manager.log_api_request(
             query, num_results, start_index, 'error', response_time_ms, error_msg
         )
         
         return {
             'success': False,
             'error': error_msg,
             'request_id': request_id,
             'results': []
         }
     
     except Exception as e:
         response_time_ms = int((time.time() - start_time) * 1000)
         error_msg = f"Unexpected error: {str(e)}"
         logger.error(error_msg)
         
         request_id = db_manager.log_api_request(
             query, num_results, start_index, 'error', response_time_ms, error_msg
         )
         
         return {
             'success': False,
             'error': error_msg,
             'request_id': request_id,
             'results': []
         }
 
 def get_usage_stats(self) -> Dict[str, Any]:
     """Get current usage statistics"""
     today_count = db_manager.get_daily_request_count()
     remaining = max(0, config.MAX_DAILY_REQUESTS - today_count)
     
     return {
         'daily_limit': config.MAX_DAILY_REQUESTS,
         'used_today': today_count,
         'remaining_today': remaining,
         'percentage_used': (today_count / config.MAX_DAILY_REQUESTS) * 100
     }

# Global API client instance
search_api = GoogleSearchAPI()
