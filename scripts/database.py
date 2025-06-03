"""
Database connection and operations for Google Search API application
"""
import mysql.connector
from mysql.connector import Error
import logging
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from config import config

# Configure logging
logging.basicConfig(
 level=getattr(logging, config.LOG_LEVEL),
 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
 handlers=[
     logging.FileHandler(config.LOG_FILE),
     logging.StreamHandler()
 ]
)
logger = logging.getLogger(__name__)

class DatabaseManager:
 """Manages database connections and operations"""
 
 def __init__(self):
     self.connection_config = {
         'host': config.DB_HOST,
         'port': config.DB_PORT,
         'user': config.DB_USER,
         'password': config.DB_PASSWORD,
         'database': config.DB_NAME,
         'autocommit': True
     }
 
 @contextmanager
 def get_connection(self):
     """Context manager for database connections"""
     connection = None
     try:
         connection = mysql.connector.connect(**self.connection_config)
         logger.debug("Database connection established")
         yield connection
     except Error as e:
         logger.error(f"Database connection error: {e}")
         raise
     finally:
         if connection and connection.is_connected():
             connection.close()
             logger.debug("Database connection closed")
 
 def test_connection(self) -> bool:
     """Test database connection"""
     try:
         with self.get_connection() as conn:
             cursor = conn.cursor()
             cursor.execute("SELECT 1")
             result = cursor.fetchone()
             logger.info("Database connection test successful")
             return True
     except Error as e:
         logger.error(f"Database connection test failed: {e}")
         return False
 
 def get_daily_request_count(self, target_date: date = None) -> int:
     """Get the number of API requests made today"""
     if target_date is None:
         target_date = date.today()
     
     try:
         with self.get_connection() as conn:
             cursor = conn.cursor()
             cursor.execute(
                 "SELECT request_count FROM daily_usage WHERE usage_date = %s",
                 (target_date,)
             )
             result = cursor.fetchone()
             count = result[0] if result else 0
             logger.debug(f"Daily request count for {target_date}: {count}")
             return count
     except Error as e:
         logger.error(f"Error getting daily request count: {e}")
         return 0
 
 def increment_daily_usage(self, target_date: date = None) -> bool:
     """Increment daily usage counter"""
     if target_date is None:
         target_date = date.today()
     
     try:
         with self.get_connection() as conn:
             cursor = conn.cursor()
             cursor.execute("""
                 INSERT INTO daily_usage (usage_date, request_count) 
                 VALUES (%s, 1)
                 ON DUPLICATE KEY UPDATE 
                 request_count = request_count + 1,
                 updated_at = CURRENT_TIMESTAMP
             """, (target_date,))
             logger.debug(f"Daily usage incremented for {target_date}")
             return True
     except Error as e:
         logger.error(f"Error incrementing daily usage: {e}")
         return False
 
 def log_api_request(self, query: str, num_results: int, start_index: int, 
                    status: str, response_time_ms: int = None, 
                    error_message: str = None) -> Optional[int]:
     """Log an API request to the database"""
     try:
         with self.get_connection() as conn:
             cursor = conn.cursor()
             cursor.execute("""
                 INSERT INTO api_requests 
                 (query_text, num_results, start_index, status, response_time_ms, error_message)
                 VALUES (%s, %s, %s, %s, %s, %s)
             """, (query, num_results, start_index, status, response_time_ms, error_message))
             
             request_id = cursor.lastrowid
             logger.info(f"API request logged with ID: {request_id}")
             return request_id
     except Error as e:
         logger.error(f"Error logging API request: {e}")
         return None
 
 def save_search_results(self, request_id: int, results: List[Dict[str, Any]]) -> bool:
     """Save search results to the database"""
     try:
         with self.get_connection() as conn:
             cursor = conn.cursor()
             
             for position, result in enumerate(results, 1):
                 cursor.execute("""
                     INSERT INTO search_results 
                     (request_id, title, link, snippet, display_link, formatted_url,
                      html_title, html_snippet, cache_id, page_map, position_in_results)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                 """, (
                     request_id,
                     result.get('title', ''),
                     result.get('link', ''),
                     result.get('snippet', ''),
                     result.get('displayLink', ''),
                     result.get('formattedUrl', ''),
                     result.get('htmlTitle', ''),
                     result.get('htmlSnippet', ''),
                     result.get('cacheId', ''),
                     str(result.get('pagemap', {})),
                     position
                 ))
             
             logger.info(f"Saved {len(results)} search results for request ID: {request_id}")
             return True
     except Error as e:
         logger.error(f"Error saving search results: {e}")
         return False
 
 def get_recent_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
     """Get recent API requests"""
     try:
         with self.get_connection() as conn:
             cursor = conn.cursor(dictionary=True)
             cursor.execute("""
                 SELECT * FROM api_requests 
                 ORDER BY created_at DESC 
                 LIMIT %s
             """, (limit,))
             results = cursor.fetchall()
             logger.debug(f"Retrieved {len(results)} recent requests")
             return results
     except Error as e:
         logger.error(f"Error getting recent requests: {e}")
         return []
 
 def get_search_results_by_request_id(self, request_id: int) -> List[Dict[str, Any]]:
     """Get search results for a specific request"""
     try:
         with self.get_connection() as conn:
             cursor = conn.cursor(dictionary=True)
             cursor.execute("""
                 SELECT * FROM search_results 
                 WHERE request_id = %s 
                 ORDER BY position_in_results
             """, (request_id,))
             results = cursor.fetchall()
             logger.debug(f"Retrieved {len(results)} search results for request ID: {request_id}")
             return results
     except Error as e:
         logger.error(f"Error getting search results: {e}")
         return []

# Global database manager instance
db_manager = DatabaseManager()
