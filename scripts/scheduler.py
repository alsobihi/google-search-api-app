"""
Scheduler for automated bulk searches at specified intervals
Includes interactive search capabilities
"""
import time
import schedule
import threading
from datetime import datetime, timedelta
import logging
import os
import sys
import requests
import json
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    # Google API Configuration
    GOOGLE_API_KEY: str = ""
    GOOGLE_SEARCH_ENGINE_ID: str = ""
    
    # MySQL Database Configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "google_search_app"
    
    # API Rate Limiting
    MAX_DAILY_REQUESTS: int = 50
    DEFAULT_RESULTS_PER_QUERY: int = 10
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "google_search_app.log"
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables"""
        return cls(
            GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY', ''),
            GOOGLE_SEARCH_ENGINE_ID=os.getenv('GOOGLE_SEARCH_ENGINE_ID', ''),
            DB_HOST=os.getenv('DB_HOST', 'localhost'),
            DB_PORT=int(os.getenv('DB_PORT', '3306')),
            DB_USER=os.getenv('DB_USER', 'root'),
            DB_PASSWORD=os.getenv('DB_PASSWORD', ''),
            DB_NAME=os.getenv('DB_NAME', 'google_search_app'),
            MAX_DAILY_REQUESTS=int(os.getenv('MAX_DAILY_REQUESTS', '50')),
            DEFAULT_RESULTS_PER_QUERY=int(os.getenv('DEFAULT_RESULTS_PER_QUERY', '10')),
            LOG_LEVEL=os.getenv('LOG_LEVEL', 'INFO'),
            LOG_FILE=os.getenv('LOG_FILE', 'google_search_app.log')
        )

# Global configuration instance
config = Config.from_env()

# Configure logging for scheduler with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log', encoding='utf-8'),
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
    
    def get_daily_request_count(self, target_date=None) -> int:
        """Get the number of API requests made today"""
        if target_date is None:
            from datetime import date
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
    
    def increment_daily_usage(self, target_date=None) -> bool:
        """Increment daily usage counter"""
        if target_date is None:
            from datetime import date
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

class GoogleSearchAPI:
    """Google Custom Search API client with rate limiting"""
    
    def __init__(self):
        self.api_key = config.GOOGLE_API_KEY
        self.search_engine_id = config.GOOGLE_SEARCH_ENGINE_ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.db_manager = DatabaseManager()
    
    def is_configured(self) -> bool:
        """Check if API is properly configured"""
        return bool(self.api_key and self.search_engine_id)
    
    def _check_rate_limit(self) -> bool:
        """Check if we can make another API request today"""
        current_count = self.db_manager.get_daily_request_count()
        if current_count >= config.MAX_DAILY_REQUESTS:
            logger.warning(f"Daily rate limit reached: {current_count}/{config.MAX_DAILY_REQUESTS}")
            return False
        return True
    
    def search(self, query: str, num_results: int = None, start_index: int = 1) -> Dict[str, Any]:
        """Perform a Google search with rate limiting and database logging"""
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
            request_id = self.db_manager.log_api_request(
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
                request_id = self.db_manager.log_api_request(
                    query, num_results, start_index, 'success', response_time_ms
                )
                
                # Increment daily usage
                self.db_manager.increment_daily_usage()
                
                # Extract and save results
                results = data.get('items', [])
                if request_id and results:
                    self.db_manager.save_search_results(request_id, results)
                
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
                
                request_id = self.db_manager.log_api_request(
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
            
            request_id = self.db_manager.log_api_request(
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
            
            request_id = self.db_manager.log_api_request(
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
        today_count = self.db_manager.get_daily_request_count()
        remaining = max(0, config.MAX_DAILY_REQUESTS - today_count)
        
        return {
            'daily_limit': config.MAX_DAILY_REQUESTS,
            'used_today': today_count,
            'remaining_today': remaining,
            'percentage_used': (today_count / config.MAX_DAILY_REQUESTS) * 100
        }

# Global instances
db_manager = DatabaseManager()
search_api = GoogleSearchAPI()

# Default keyword list for data science topics
DEFAULT_KEYWORDS = [
    "Data Analysis",
    "Data Analytics", 
    "Data Analyst",
    "Data Mining",
    "Data Modeling",
    "Data Visualization",
    "Business Intelligence",
    "Machine Learning",
    "Deep Learning"
]

# Free tier safety limits
FREE_TIER_DAILY_LIMIT = 100  # Google's free tier limit
MAX_RESULTS_PER_KEYWORD = 10  # Maximum results per API call

def calculate_api_calls(keywords, results_per_keyword):
    """Calculate how many API calls will be needed"""
    calls_per_keyword = (results_per_keyword + MAX_RESULTS_PER_KEYWORD - 1) // MAX_RESULTS_PER_KEYWORD
    return len(keywords) * calls_per_keyword

def bulk_search_keywords(keywords=None, results_per_keyword=10, delay_between_searches=2, enforce_free_tier=True):
    """Perform bulk searches for a list of keywords"""
    
    if keywords is None:
        keywords = DEFAULT_KEYWORDS
    
    # Calculate API calls needed
    api_calls_needed = calculate_api_calls(keywords, results_per_keyword)
    
    print("🚀 Starting Bulk Search Operation")
    print("=" * 60)
    print(f"📋 Keywords to search: {len(keywords)}")
    print(f"📊 Results per keyword: {results_per_keyword}")
    print(f"⏱️  Delay between searches: {delay_between_searches} seconds")
    print(f"🔢 Total API calls needed: {api_calls_needed}")
    
    # Free tier safety check
    if enforce_free_tier and api_calls_needed > FREE_TIER_DAILY_LIMIT:
        print(f"\n⚠️ WARNING: This operation would exceed the free tier limit!")
        print(f"   API calls needed: {api_calls_needed}")
        print(f"   Free tier limit: {FREE_TIER_DAILY_LIMIT}")
        print(f"   Excess calls: {api_calls_needed - FREE_TIER_DAILY_LIMIT} (would incur charges)")
        
        # Calculate safe number of keywords
        calls_per_keyword = (results_per_keyword + MAX_RESULTS_PER_KEYWORD - 1) // MAX_RESULTS_PER_KEYWORD
        safe_keyword_count = FREE_TIER_DAILY_LIMIT // calls_per_keyword
        
        print(f"\n💡 Recommendations to stay within free tier:")
        print(f"   1. Reduce to {safe_keyword_count} keywords (currently {len(keywords)})")
        print(f"   2. Reduce results per keyword to {MAX_RESULTS_PER_KEYWORD} (currently {results_per_keyword})")
        print(f"   3. Run multiple smaller batches on different days")
        print(f"   4. Disable free tier protection with --no-free-tier-protection")
        
        response = input(f"\nContinue anyway? This may incur charges! (yes/NO): ").lower().strip()
        if response != 'yes':
            print("❌ Bulk search cancelled to protect free tier limits")
            return None
        
        print("\n⚠️ Free tier protection overridden. Proceeding with search...")
    
    # Check if we have enough quota in our app
    stats = search_api.get_usage_stats()
    if stats['remaining_today'] < api_calls_needed:
        print(f"\n❌ Insufficient API quota in your application!")
        print(f"   API calls needed: {api_calls_needed}")
        print(f"   Remaining quota: {stats['remaining_today']}")
        print(f"   Increase MAX_DAILY_REQUESTS in .env file or reduce search scope")
        return None
    
    print(f"\n✅ API Quota Check: {stats['remaining_today']} calls available")
    
    # Start bulk search
    results_summary = {
        'start_time': datetime.now(),
        'keywords_searched': [],
        'successful_searches': 0,
        'failed_searches': 0,
        'total_results_collected': 0,
        'api_calls_made': 0
    }
    
    print(f"\n🔍 Starting searches...")
    print("-" * 60)
    
    # Track API calls to ensure we don't exceed free tier
    api_calls_made = 0
    
    for i, keyword in enumerate(keywords, 1):
        print(f"\n[{i}/{len(keywords)}] Searching: '{keyword}'")
        
        # Calculate how many API calls this keyword will use
        calls_for_keyword = (results_per_keyword + MAX_RESULTS_PER_KEYWORD - 1) // MAX_RESULTS_PER_KEYWORD
        
        # Check if this would exceed free tier
        if enforce_free_tier and api_calls_made + calls_for_keyword > FREE_TIER_DAILY_LIMIT:
            print(f"⚠️ Stopping: Next search would exceed free tier limit of {FREE_TIER_DAILY_LIMIT} calls")
            print(f"   Current API calls: {api_calls_made}")
            print(f"   Calls needed for '{keyword}': {calls_for_keyword}")
            break
        
        # For multiple API calls per keyword (pagination)
        collected_results = []
        keyword_success = True
        
        for page in range(1, calls_for_keyword + 1):
            start_index = ((page - 1) * MAX_RESULTS_PER_KEYWORD) + 1
            
            # Perform search for this page
            result = search_api.search(keyword, MAX_RESULTS_PER_KEYWORD, start_index)
            api_calls_made += 1
            results_summary['api_calls_made'] += 1
            
            if result['success']:
                collected_results.extend(result['results'])
                print(f"   ✅ Page {page}/{calls_for_keyword}: Got {len(result['results'])} results")
            else:
                keyword_success = False
                print(f"   ❌ Page {page}/{calls_for_keyword} failed: {result['error']}")
                break
            
            # Add small delay between pagination requests
            if page < calls_for_keyword:
                time.sleep(1)
        
        # Record results for this keyword
        if keyword_success:
            results_summary['successful_searches'] += 1
            results_summary['total_results_collected'] += len(collected_results)
            
            print(f"   ✅ Success: {len(collected_results)} total results for '{keyword}'")
            
            results_summary['keywords_searched'].append({
                'keyword': keyword,
                'status': 'success',
                'results_count': len(collected_results),
                'api_calls': calls_for_keyword
            })
            
        else:
            results_summary['failed_searches'] += 1
            
            results_summary['keywords_searched'].append({
                'keyword': keyword,
                'status': 'failed',
                'error': "One or more API calls failed",
                'partial_results': len(collected_results)
            })
        
        # Add delay between keywords (except for the last one)
        if i < len(keywords):
            print(f"   ⏳ Waiting {delay_between_searches} seconds...")
            time.sleep(delay_between_searches)
        
        # Free tier safety check during execution
        if enforce_free_tier and api_calls_made >= FREE_TIER_DAILY_LIMIT:
            print(f"\n⚠️ Reached free tier limit of {FREE_TIER_DAILY_LIMIT} API calls. Stopping to avoid charges.")
            break
    
    # Calculate final statistics
    results_summary['end_time'] = datetime.now()
    results_summary['total_duration'] = (results_summary['end_time'] - results_summary['start_time']).total_seconds()
    results_summary['free_tier_limit'] = FREE_TIER_DAILY_LIMIT
    results_summary['within_free_tier'] = api_calls_made <= FREE_TIER_DAILY_LIMIT
    
    # Print final summary
    print_bulk_search_summary(results_summary)
    
    return results_summary

def print_bulk_search_summary(summary):
    """Print a detailed summary of the bulk search operation"""
    
    print("\n" + "="*60)
    print("📊 BULK SEARCH SUMMARY")
    print("="*60)
    
    print(f"⏰ Start Time: {summary['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ End Time: {summary['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  Total Duration: {summary['total_duration']:.1f} seconds")
    
    print(f"\n📈 Search Statistics:")
    print(f"   Total Keywords: {len(summary['keywords_searched'])}")
    print(f"   Successful: {summary['successful_searches']} ✅")
    print(f"   Failed: {summary['failed_searches']} ❌")
    if summary['successful_searches'] > 0:
        print(f"   Success Rate: {(summary['successful_searches']/len(summary['keywords_searched'])*100):.1f}%")
    
    print(f"\n📊 Results Statistics:")
    print(f"   Total Results Collected: {summary['total_results_collected']}")
    if summary['successful_searches'] > 0:
        print(f"   Average per Keyword: {summary['total_results_collected']/summary['successful_searches']:.1f}")
    print(f"   API Calls Made: {summary['api_calls_made']}")
    
    # Free tier status
    free_tier_status = "✅ Within free tier" if summary.get('within_free_tier', True) else "❌ Exceeded free tier"
    print(f"\n💰 Free Tier Status: {free_tier_status}")
    print(f"   Free Tier Limit: {summary.get('free_tier_limit', FREE_TIER_DAILY_LIMIT)} API calls")
    print(f"   Used: {summary['api_calls_made']} API calls")
    
    # Show updated usage stats
    updated_stats = search_api.get_usage_stats()
    print(f"\n🔢 Updated API Usage:")
    print(f"   Used Today: {updated_stats['used_today']}/{updated_stats['daily_limit']}")
    print(f"   Remaining: {updated_stats['remaining_today']}")
    print(f"   Usage: {updated_stats['percentage_used']:.1f}%")
    
    # Show successful searches
    print(f"\n✅ Successful Searches:")
    for item in summary['keywords_searched']:
        if item['status'] == 'success':
            print(f"   • {item['keyword']}: {item['results_count']} results")
    
    # Show failed searches if any
    failed_searches = [item for item in summary['keywords_searched'] if item['status'] == 'failed']
    if failed_searches:
        print(f"\n❌ Failed Searches:")
        for item in failed_searches:
            print(f"   • {item['keyword']}: {item['error']}")

def save_keywords_to_file(keywords, filename="search_keywords.txt"):
    """Save keywords list to a file"""
    with open(filename, 'w') as f:
        for keyword in keywords:
            f.write(f"{keyword}\n")
    print(f"💾 Keywords saved to: {filename}")

def load_keywords_from_file(filename="search_keywords.txt"):
    """Load keywords from a file"""
    try:
        with open(filename, 'r') as f:
            keywords = [line.strip() for line in f if line.strip()]
        print(f"📂 Loaded {len(keywords)} keywords from: {filename}")
        return keywords
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return None

class BulkSearchScheduler:
    """Automated bulk search scheduler"""
    
    def __init__(self):
        self.is_running = False
        self.scheduler_thread = None
        self.total_runs = 0
        self.successful_runs = 0
        self.failed_runs = 0
        self.start_time = None
        
    def scheduled_bulk_search(self, keywords=None, results_per_keyword=10):
        """Execute a scheduled bulk search"""
        if keywords is None:
            keywords = DEFAULT_KEYWORDS
            
        logger.info(f"Starting scheduled bulk search #{self.total_runs + 1}")
        logger.info(f"Keywords: {len(keywords)}, Results per keyword: {results_per_keyword}")
        
        try:
            # Check API quota before starting
            stats = search_api.get_usage_stats()
            # Calculate actual API calls needed (Google returns max 10 results per call)
            calls_per_keyword = (results_per_keyword + 9) // 10  # Ceiling division
            api_calls_needed = len(keywords) * calls_per_keyword
            
            if stats['remaining_today'] < api_calls_needed:
                logger.warning(f"Insufficient API quota. Need: {api_calls_needed}, Available: {stats['remaining_today']}")
                self.failed_runs += 1
                return False
            
            # Execute bulk search
            result = bulk_search_keywords(
                keywords=keywords,
                results_per_keyword=results_per_keyword,
                delay_between_searches=1,  # Shorter delay for automated runs
                enforce_free_tier=True
            )
            
            if result:
                self.successful_runs += 1
                logger.info(f"Scheduled search completed successfully")
                logger.info(f"Results: {result['total_results_collected']} total, {result['api_calls_made']} API calls")
                return True
            else:
                self.failed_runs += 1
                logger.error(f"Scheduled search failed")
                return False
                
        except Exception as e:
            self.failed_runs += 1
            logger.error(f"Scheduled search error: {e}")
            return False
        finally:
            self.total_runs += 1
    
    def start_hourly_schedule(self, hours_interval=1, keywords=None, results_per_keyword=10, max_days=None):
        """
        Start hourly scheduled searches
        
        Args:
            hours_interval: Run every X hours
            keywords: List of keywords to search
            results_per_keyword: Results per keyword
            max_days: Maximum days to run (None = run indefinitely)
        """
        if self.is_running:
            logger.warning("Scheduler is already running")
            return False
        
        self.is_running = True
        self.start_time = datetime.now()
        
        # Calculate end time if max_days is specified
        end_time = None
        if max_days:
            end_time = self.start_time + timedelta(days=max_days)
        
        logger.info(f"Starting hourly scheduler")
        logger.info(f"Interval: Every {hours_interval} hour(s)")
        logger.info(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        if end_time:
            logger.info(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Keywords: {len(keywords or DEFAULT_KEYWORDS)}")
        logger.info(f"Results per keyword: {results_per_keyword}")
        
        # Schedule the job
        if hours_interval == 1:
            schedule.every().hour.do(self.scheduled_bulk_search, keywords, results_per_keyword)
        else:
            schedule.every(hours_interval).hours.do(self.scheduled_bulk_search, keywords, results_per_keyword)
        
        # Run first search immediately
        logger.info("Running initial search...")
        self.scheduled_bulk_search(keywords, results_per_keyword)
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, args=(end_time,))
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        return True
    
    def _run_scheduler(self, end_time=None):
        """Internal method to run the scheduler"""
        try:
            while self.is_running:
                # Check if we've reached the end time
                if end_time and datetime.now() >= end_time:
                    logger.info(f"Reached end time. Stopping scheduler.")
                    self.stop()
                    break
                
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            self.is_running = False
    
    def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return False
        
        self.is_running = False
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        logger.info("Scheduler stopped")
        self.print_summary()
        return True
    
    def get_status(self):
        """Get current scheduler status"""
        runtime = datetime.now() - self.start_time if self.start_time else timedelta(0)
        next_run = schedule.next_run() if schedule.jobs else None
        success_rate = (self.successful_runs / max(self.total_runs, 1)) * 100 if self.total_runs > 0 else 0
        
        return {
            'running': self.is_running,
            'start_time': self.start_time,
            'runtime': runtime,
            'total_runs': self.total_runs,
            'successful_runs': self.successful_runs,
            'failed_runs': self.failed_runs,
            'success_rate': success_rate,
            'next_run': next_run,
            'scheduled_jobs': len(schedule.jobs)
        }
    
    def print_summary(self):
        """Print scheduler summary"""
        status = self.get_status()
        
        print("\n" + "="*50)
        print("📊 SCHEDULER SUMMARY")
        print("="*50)
        
        if status['running']:
            print(f"🟢 Status: Running")
            if status['start_time']:
                print(f"⏰ Start Time: {status['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"⏱️  Runtime: {str(status['runtime']).split('.')[0]}")
            if status['next_run']:
                print(f"⏭️  Next Run: {status['next_run'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📋 Scheduled Jobs: {status['scheduled_jobs']}")
        else:
            print(f"🔴 Status: Stopped")
            if status['start_time']:
                print(f"⏰ Last Start Time: {status['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n📈 Statistics:")
        print(f"   Total Runs: {status['total_runs']}")
        print(f"   Successful: {status['successful_runs']} ✅")
        print(f"   Failed: {status['failed_runs']} ❌")
        print(f"   Success Rate: {status['success_rate']:.1f}%")

def print_detailed_schedule_summary(hours, results_per_keyword, max_days, keywords):
    """Print detailed schedule summary with API usage information"""
    
    # Calculate API calls
    calls_per_keyword = (results_per_keyword + 9) // 10  # Ceiling division
    calls_per_run = len(keywords) * calls_per_keyword
    runs_per_day = 24 / hours
    calls_per_day = calls_per_run * runs_per_day
    
    # Get current API usage
    try:
        stats = search_api.get_usage_stats()
        current_usage = {
            'daily_limit': stats['daily_limit'],
            'used_today': stats['used_today'],
            'remaining_today': stats['remaining_today'],
            'percentage_used': stats['percentage_used']
        }
    except Exception as e:
        current_usage = {
            'daily_limit': 'Unknown',
            'used_today': 'Unknown',
            'remaining_today': 'Unknown',
            'percentage_used': 0
        }
    
    # Free tier calculations
    FREE_TIER_LIMIT = 100
    free_tier_used = min(current_usage['used_today'] if isinstance(current_usage['used_today'], int) else 0, FREE_TIER_LIMIT)
    free_tier_remaining = max(0, FREE_TIER_LIMIT - free_tier_used)
    free_tier_percentage = (free_tier_used / FREE_TIER_LIMIT) * 100
    
    # Calculate projections
    days_until_limit = None
    if calls_per_day > 0 and isinstance(current_usage['remaining_today'], int):
        days_until_limit = current_usage['remaining_today'] / calls_per_day
    
    free_tier_days_until_limit = None
    if calls_per_day > 0:
        free_tier_days_until_limit = free_tier_remaining / calls_per_day
    
    print(f"\n" + "="*60)
    print("📊 DETAILED SCHEDULE SUMMARY")
    print("="*60)
    
    # Schedule Information
    print(f"📅 Schedule Configuration:")
    print(f"   Frequency: Every {hours} hour(s)")
    print(f"   Results per keyword: {results_per_keyword}")
    print(f"   Keywords to search: {len(keywords)}")
    if max_days:
        print(f"   Maximum duration: {max_days} days")
    else:
        print(f"   Duration: Unlimited")
    
    # API Call Calculations with detailed breakdown
    print(f"\n🔢 API Call Calculations:")
    print(f"   Results per keyword: {results_per_keyword}")
    print(f"   API calls per keyword: {calls_per_keyword} (Google returns max 10 results per call)")
    print(f"   Total API calls per run: {calls_per_run}")
    print(f"   Runs per day: {runs_per_day:.1f}")
    print(f"   Total API calls per day: {calls_per_day:.0f}")
    
    # Current API Usage
    print(f"\n📈 Current API Usage:")
    print(f"   Daily Limit: {current_usage['daily_limit']}")
    print(f"   Used Today: {current_usage['used_today']}")
    print(f"   Remaining: {current_usage['remaining_today']}")
    print(f"   Usage: {current_usage['percentage_used']:.1f}%")
    
    # Free Tier Status
    print(f"\n💰 Free Tier Status:")
    print(f"   Free Tier Limit: {FREE_TIER_LIMIT} calls/day")
    print(f"   Used: {free_tier_used}/{FREE_TIER_LIMIT}")
    print(f"   Remaining: {free_tier_remaining}")
    print(f"   Usage: {free_tier_percentage:.1f}%")
    
    # Projections and Warnings
    print(f"\n🔮 Projections:")
    if calls_per_day > FREE_TIER_LIMIT:
        excess_calls = calls_per_day - FREE_TIER_LIMIT
        print(f"   ⚠️ EXCEEDS FREE TIER by {excess_calls:.0f} calls/day")
        print(f"   💸 Estimated daily cost: ${(excess_calls * 0.005):.2f}")
        print(f"   💸 Estimated monthly cost: ${(excess_calls * 0.005 * 30):.2f}")
    else:
        print(f"   ✅ Stays within free tier")
        if free_tier_days_until_limit and free_tier_days_until_limit > 0:
            print(f"   📅 Free tier will last: {free_tier_days_until_limit:.1f} days at this rate")
    
    if days_until_limit and days_until_limit > 0:
        print(f"   📅 Current quota will last: {days_until_limit:.1f} days at this rate")
    elif isinstance(current_usage['remaining_today'], int) and current_usage['remaining_today'] <= 0:
        print(f"   ⚠️ Current quota exhausted!")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if calls_per_day > FREE_TIER_LIMIT:
        safe_hours = (calls_per_run * 24) / FREE_TIER_LIMIT
        safe_results = int(FREE_TIER_LIMIT / (len(keywords) * runs_per_day))
        print(f"   • To stay in free tier, run every {safe_hours:.0f}+ hours")
        print(f"   • Or reduce results to {safe_results} per keyword")
    
    if calls_per_day > 50:
        print(f"   • Consider running less frequently to conserve quota")
    
    if calls_per_day < 10:
        print(f"   • You could run more frequently if needed")
    
    # Safety Warnings
    if calls_per_day > FREE_TIER_LIMIT:
        print(f"\n⚠️  WARNING: This schedule will incur charges!")
        print(f"   Free tier protection will prompt before exceeding limits")
    
    return calls_per_day

def manage_keywords():
    """Keyword management interface"""
    
    print("\n🔍 Keyword Management")
    print("=" * 40)
    
    while True:
        print(f"\n📋 Keyword Options:")
        print(f"1. View current default keywords ({len(DEFAULT_KEYWORDS)} keywords)")
        print(f"2. Change the default keywords")
        print(f"3. Load keywords from file")
        print(f"4. Save current keywords to file")
        print(f"5. Return to main menu")
        
        choice = input(f"\nSelect option (1-5): ").strip()
        
        if choice == '1':
            # View current default keywords
            print(f"\n📋 Current Default Keywords ({len(DEFAULT_KEYWORDS)} total):")
            for i, keyword in enumerate(DEFAULT_KEYWORDS, 1):
                print(f"   {i:2d}. {keyword}")
        
        elif choice == '2':
            # Change the default keywords
            print(f"\n✏️ Change Default Keywords")
            print(f"Current keywords: {len(DEFAULT_KEYWORDS)} total")
            print(f"Choose how to set new keywords:")
            print(f"1. Enter new keywords manually")
            print(f"2. Load from file")
            print(f"3. Cancel")
            
            sub_choice = input(f"\nSelect option (1-3): ").strip()
            
            if sub_choice == '1':
                # Enter new keywords manually
                print(f"\nEnter new keywords (one per line, empty line to finish):")
                print(f"Current keywords will be replaced.")
                new_keywords = []
                while True:
                    keyword = input().strip()
                    if not keyword:
                        break
                    new_keywords.append(keyword)
                
                if new_keywords:
                    # Update the global DEFAULT_KEYWORDS
                    DEFAULT_KEYWORDS.clear()
                    DEFAULT_KEYWORDS.extend(new_keywords)
                    print(f"✅ Updated default keywords! Now using {len(DEFAULT_KEYWORDS)} keywords")
                    
                    # Show the new keywords
                    print(f"\n📋 New Default Keywords:")
                    for i, keyword in enumerate(DEFAULT_KEYWORDS, 1):
                        print(f"   {i:2d}. {keyword}")
                else:
                    print("❌ No keywords entered. Default keywords unchanged.")
            
            elif sub_choice == '2':
                # Load from file
                filename = input(f"Enter filename (default: search_keywords.txt): ").strip() or "search_keywords.txt"
                keywords = load_keywords_from_file(filename)
                if keywords:
                    # Update the global DEFAULT_KEYWORDS
                    DEFAULT_KEYWORDS.clear()
                    DEFAULT_KEYWORDS.extend(keywords)
                    print(f"✅ Updated default keywords from file! Now using {len(DEFAULT_KEYWORDS)} keywords")
                    
                    # Show the new keywords
                    print(f"\n📋 New Default Keywords:")
                    for i, keyword in enumerate(DEFAULT_KEYWORDS, 1):
                        print(f"   {i:2d}. {keyword}")
            
            elif sub_choice == '3':
                print("❌ Cancelled. Default keywords unchanged.")
        
        elif choice == '3':
            # Load keywords from file (for viewing, not changing defaults)
            filename = input(f"Enter filename (default: search_keywords.txt): ").strip() or "search_keywords.txt"
            keywords = load_keywords_from_file(filename)
            if keywords:
                print(f"\n📋 Keywords from {filename} ({len(keywords)} total):")
                for i, keyword in enumerate(keywords, 1):
                    print(f"   {i:2d}. {keyword}")
        
        elif choice == '4':
            # Save current keywords to file
            filename = input(f"Enter filename (default: search_keywords.txt): ").strip() or "search_keywords.txt"
            save_keywords_to_file(DEFAULT_KEYWORDS, filename)
        
        elif choice == '5':
            # Return to main menu
            print("⬅️ Returning to main menu")
            return
        
        else:
            print("❌ Invalid option. Please choose 1-5.")

def update_env_file(key, value):
    """Update a value in the .env file"""
    env_file_path = '.env'
    
    # Read current .env file
    lines = []
    key_found = False
    
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as f:
            lines = f.readlines()
    
    # Update or add the key
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            key_found = True
            break
    
    # If key not found, add it
    if not key_found:
        lines.append(f"{key}={value}\n")
    
    # Write back to file
    with open(env_file_path, 'w') as f:
        f.writelines(lines)

def manage_api_settings():
    """API settings management interface"""
    
    print("\n⚙️ API Settings Management")
    print("=" * 40)
    
    while True:
        print(f"\n📋 Current API Settings:")
        print(f"   Daily Limit (MAX_DAILY_REQUESTS): {config.MAX_DAILY_REQUESTS}")
        print(f"   Default Results per Query: {config.DEFAULT_RESULTS_PER_QUERY}")
        
        # Show current usage
        try:
            stats = search_api.get_usage_stats()
            print(f"\n📈 Current Usage:")
            print(f"   Used Today: {stats['used_today']}/{stats['daily_limit']}")
            print(f"   Remaining: {stats['remaining_today']}")
            print(f"   Usage: {stats['percentage_used']:.1f}%")
        except Exception as e:
            print(f"\n❌ Error getting current usage: {e}")
        
        print(f"\n🔧 Settings Options:")
        print(f"1. Change daily API limit (MAX_DAILY_REQUESTS)")
        print(f"2. Change default results per query")
        print(f"3. View Google API pricing info")
        print(f"4. Return to main menu")
        
        choice = input(f"\nSelect option (1-4): ").strip()
        
        if choice == '1':
            # Change daily API limit
            print(f"\n📊 Change Daily API Limit")
            print(f"Current limit: {config.MAX_DAILY_REQUESTS}")
            print(f"\n💡 Recommendations:")
            print(f"   • Free tier: 100 calls/day (no cost)")
            print(f"   • Paid tier: $5 per 1000 calls")
            print(f"   • Conservative: 50-100 calls/day")
            print(f"   • Moderate: 200-500 calls/day")
            print(f"   • Heavy: 1000+ calls/day")
            
            try:
                new_limit = input(f"\nEnter new daily limit (current: {config.MAX_DAILY_REQUESTS}): ").strip()
                if new_limit:
                    new_limit = int(new_limit)
                    if new_limit > 0:
                        # Update .env file
                        update_env_file('MAX_DAILY_REQUESTS', str(new_limit))
                        
                        # Update config object
                        config.MAX_DAILY_REQUESTS = new_limit
                        
                        print(f"✅ Updated daily API limit to {new_limit}")
                        
                        if new_limit > 100:
                            cost_per_day = ((new_limit - 100) * 0.005) if new_limit > 100 else 0
                            print(f"💸 Estimated daily cost: ${cost_per_day:.2f} (after free 100 calls)")
                            print(f"💸 Estimated monthly cost: ${cost_per_day * 30:.2f}")
                        else:
                            print(f"💰 Stays within free tier!")
                        
                        print(f"🔄 Restart the application to apply changes")
                    else:
                        print("❌ Limit must be greater than 0")
                else:
                    print("❌ No changes made")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
        
        elif choice == '2':
            # Change default results per query
            print(f"\n📊 Change Default Results per Query")
            print(f"Current default: {config.DEFAULT_RESULTS_PER_QUERY}")
            print(f"\n💡 Note:")
            print(f"   • Google returns max 10 results per API call")
            print(f"   • 100 results = 10 API calls per keyword")
            print(f"   • More results = more API calls = higher cost")
            
            try:
                new_default = input(f"\nEnter new default (1-100, current: {config.DEFAULT_RESULTS_PER_QUERY}): ").strip()
                if new_default:
                    new_default = int(new_default)
                    if 1 <= new_default <= 100:
                        # Update .env file
                        update_env_file('DEFAULT_RESULTS_PER_QUERY', str(new_default))
                        
                        # Update config object
                        config.DEFAULT_RESULTS_PER_QUERY = new_default
                        
                        print(f"✅ Updated default results per query to {new_default}")
                        print(f"🔄 Restart the application to apply changes")
                    else:
                        print("❌ Default must be between 1 and 100")
                else:
                    print("❌ No changes made")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
        
        elif choice == '3':
            # View pricing info
            print(f"\n💰 Google Custom Search API Pricing")
            print(f"=" * 40)
            print(f"🆓 Free Tier:")
            print(f"   • 100 search queries per day")
            print(f"   • No cost")
            print(f"   • Resets daily")
            
            print(f"\n💳 Paid Tier:")
            print(f"   • $5.00 per 1,000 queries")
            print(f"   • $0.005 per query")
            print(f"   • No daily limit")
            
            print(f"\n📊 Cost Examples:")
            print(f"   • 200 queries/day: ${((200-100) * 0.005):.2f}/day, ${((200-100) * 0.005 * 30):.2f}/month")
            print(f"   • 500 queries/day: ${((500-100) * 0.005):.2f}/day, ${((500-100) * 0.005 * 30):.2f}/month")
            print(f"   • 1000 queries/day: ${((1000-100) * 0.005):.2f}/day, ${((1000-100) * 0.005 * 30):.2f}/month")
            
            print(f"\n🔗 More info: https://developers.google.com/custom-search/v1/overview")
        
        elif choice == '4':
            # Return to main menu
            print("⬅️ Returning to main menu")
            return
        
        else:
            print("❌ Invalid option. Please choose 1-4.")

def interactive_search():
    """Interactive search mode"""
    print("\n🔍 Interactive Search")
    print("=" * 40)
    
    while True:
        print("\nEnter a search query (or 'back' to return to main menu):")
        query = input("> ").strip()
        
        if query.lower() == 'back':
            return
        
        if not query:
            print("❌ Query cannot be empty")
            continue
        
        # Get number of results
        try:
            results_input = input("Number of results (default 10): ").strip()
            num_results = int(results_input) if results_input else 10
            num_results = min(max(num_results, 1), 100)  # Clamp between 1-100
        except ValueError:
            print("❌ Invalid number, using default (10)")
            num_results = 10
        
        # Perform search
        print(f"\n🔍 Searching for: '{query}'")
        print(f"Requesting {num_results} results...")
        
        # Calculate API calls needed
        api_calls = (num_results + 9) // 10  # Ceiling division
        print(f"This will use approximately {api_calls} API calls")
        
        # Check API quota
        stats = search_api.get_usage_stats()
        if stats['remaining_today'] < api_calls:
            print(f"⚠️ Warning: This search may exceed your remaining API quota")
            print(f"Required: {api_calls}, Available: {stats['remaining_today']}")
            confirm = input("Continue anyway? (y/N): ").lower().strip()
            if confirm != 'y':
                print("❌ Search cancelled")
                continue
        
        # Perform search with pagination if needed
        all_results = []
        success = True
        
        for page in range(1, api_calls + 1):
            start_index = ((page - 1) * 10) + 1
            max_results = min(10, num_results - len(all_results))
            
            print(f"Fetching page {page}/{api_calls}...")
            result = search_api.search(query, max_results, start_index)
            
            if result['success']:
                all_results.extend(result['results'])
                print(f"✅ Got {len(result['results'])} results")
            else:
                print(f"❌ Error: {result['error']}")
                success = False
                break
            
            # Add small delay between pagination requests
            if page < api_calls:
                time.sleep(1)
        
        # Print results
        if success:
            print(f"\n📊 Search Results for: '{query}'")
            print(f"Total results found: {len(all_results)}")
            
            for i, item in enumerate(all_results, 1):
                print(f"\n{i}. {item.get('title', 'No Title')}")
                print(f"   🔗 {item.get('link', 'No Link')}")
                print(f"   📝 {item.get('snippet', 'No Description')}")
            
            # Show updated API usage
            updated_stats = search_api.get_usage_stats()
            print(f"\n📈 Updated API Usage:")
            print(f"   Used Today: {updated_stats['used_today']}/{updated_stats['daily_limit']}")
            print(f"   Remaining: {updated_stats['remaining_today']}")
        
        # Ask if user wants to continue
        input("\nPress Enter to continue...")

def show_recent_searches():
    """Show recent search requests"""
    print("\n📋 Recent Searches")
    print("=" * 40)
    
    try:
        requests = db_manager.get_recent_requests(20)
        
        if not requests:
            print("📭 No recent searches found")
            return
        
        print(f"Found {len(requests)} recent searches:")
        
        for req in requests:
            status_emoji = "✅" if req['status'] == 'success' else "❌" if req['status'] == 'error' else "⚠️"
            print(f"{status_emoji} [{req['id']}] {req['query_text']}")
            print(f"    📅 {req['created_at']} | Results: {req['num_results']}")
            
            # Ask if user wants to see results for this search
            view_results = input("View results for this search? (y/N): ").lower().strip()
            if view_results == 'y':
                results = db_manager.get_search_results_by_request_id(req['id'])
                
                if results:
                    print(f"\n📊 Results for search: '{req['query_text']}'")
                    print(f"Total results: {len(results)}")
                    
                    for i, item in enumerate(results, 1):
                        print(f"\n{i}. {item.get('title', 'No Title')}")
                        print(f"   🔗 {item.get('link', 'No Link')}")
                        print(f"   📝 {item.get('snippet', 'No Description')}")
                else:
                    print("📭 No results found for this search")
            
            # Ask if user wants to continue viewing searches
            continue_viewing = input("Continue viewing recent searches? (Y/n): ").lower().strip()
            if continue_viewing == 'n':
                break
    
    except Exception as e:
        print(f"❌ Error retrieving recent searches: {e}")

def interactive_scheduler():
    """Interactive scheduler setup"""
    scheduler = BulkSearchScheduler()
    
    print("⏰ Google Search API Application")
    print("=" * 40)
    print("💰 FREE TIER PROTECTION ENABLED")
    
    while True:
        print(f"\n📋 Main Menu:")
        print(f"1. Start hourly schedule")
        print(f"2. Check scheduler status")
        print(f"3. Stop scheduler")
        print(f"4. View current API usage")
        print(f"5. Manage keywords")
        print(f"6. API settings")
        print(f"7. Interactive search")
        print(f"8. View recent searches")
        print(f"9. Run one-time bulk search")
        print(f"0. Exit")
        
        choice = input(f"\nSelect option (0-9): ").strip()
        
        if choice == '1':
            # Hourly schedule - use current default keywords
            try:
                print(f"\n⏰ Setting up schedule with current default keywords ({len(DEFAULT_KEYWORDS)} keywords)")
                
                # Get hours interval with proper default handling
                hours_input = input("Run every X hours (default 25): ").strip()
                if hours_input == "":
                    hours = 25
                else:
                    hours = int(hours_input)
                hours = max(1, hours)  # Minimum 1 hour
                
                # Get results per keyword with proper default handling (allow up to 100)
                results_input = input("Results per keyword (default 10): ").strip()
                if results_input == "":
                    results_per_keyword = 10
                else:
                    results_per_keyword = int(results_input)
                results_per_keyword = min(max(results_per_keyword, 1), 100)  # Clamp 1-100
                
                # Get max days with proper default handling
                max_days_input = input("Maximum days to run (default: unlimited): ").strip()
                if max_days_input == "":
                    max_days = None
                else:
                    max_days = int(max_days_input)
                
                # Print detailed summary using current default keywords
                calls_per_day = print_detailed_schedule_summary(hours, results_per_keyword, max_days, DEFAULT_KEYWORDS)
                
                # Check for warnings
                if calls_per_day > 100:
                    print(f"\n⚠️ WARNING: This schedule would use {calls_per_day:.0f} API calls per day")
                    print(f"   This exceeds the free tier limit of 100 calls/day")
                    response = input("Continue anyway? (yes/NO): ").lower().strip()
                    if response != 'yes':
                        continue
                
                confirm = input(f"\nStart hourly scheduler? (y/N): ").lower().strip()
                if confirm == 'y':
                    if scheduler.start_hourly_schedule(hours, DEFAULT_KEYWORDS, results_per_keyword, max_days):
                        print("✅ Hourly scheduler started!")
                    else:
                        print("❌ Failed to start scheduler")
                
            except ValueError:
                print("❌ Invalid input. Please enter numbers only.")
        
        elif choice == '2':
            # Check status
            scheduler.print_summary()
        
        elif choice == '3':
            # Stop scheduler
            if scheduler.stop():
                print("✅ Scheduler stopped successfully")
            else:
                print("⚠️ Scheduler was not running")
        
        elif choice == '4':
            # Check API usage
            try:
                stats = search_api.get_usage_stats()
                print(f"\n📈 Current API Usage:")
                print(f"   Daily Limit: {stats['daily_limit']}")
                print(f"   Used Today: {stats['used_today']}")
                print(f"   Remaining: {stats['remaining_today']}")
                print(f"   Usage: {stats['percentage_used']:.1f}%")
                
                # Free tier status
                FREE_TIER_LIMIT = 100
                free_tier_used = min(stats['used_today'], FREE_TIER_LIMIT)
                free_tier_remaining = max(0, FREE_TIER_LIMIT - free_tier_used)
                free_tier_percentage = (free_tier_used / FREE_TIER_LIMIT) * 100
                
                print(f"\n💰 Free Tier Status:")
                print(f"   Free Tier Limit: {FREE_TIER_LIMIT} calls/day")
                print(f"   Used: {free_tier_used}/{FREE_TIER_LIMIT}")
                print(f"   Remaining: {free_tier_remaining}")
                print(f"   Usage: {free_tier_percentage:.1f}%")
                
                if stats['used_today'] > FREE_TIER_LIMIT:
                    excess = stats['used_today'] - FREE_TIER_LIMIT
                    print(f"   ⚠️ Exceeded free tier by {excess} calls")
                    print(f"   💸 Estimated cost today: ${(excess * 0.005):.2f}")
                
            except Exception as e:
                print(f"❌ Error getting API usage: {e}")
        
        elif choice == '5':
            # Manage keywords
            manage_keywords()
        
        elif choice == '6':
            # API settings
            manage_api_settings()
        
        elif choice == '7':
            # Interactive search
            interactive_search()
        
        elif choice == '8':
            # View recent searches
            show_recent_searches()
        
        elif choice == '9':
            # Run one-time bulk search
            print(f"\n🚀 One-time Bulk Search")
            print(f"Using current default keywords ({len(DEFAULT_KEYWORDS)} keywords)")
            
            try:
                results_input = input("Results per keyword (default 10): ").strip()
                results_per_keyword = int(results_input) if results_input else 10
                results_per_keyword = min(max(results_per_keyword, 1), 100)
                
                delay_input = input("Delay between searches in seconds (default 2): ").strip()
                delay = int(delay_input) if delay_input else 2
                delay = max(1, delay)
                
                # Run bulk search
                result = bulk_search_keywords(
                    keywords=DEFAULT_KEYWORDS,
                    results_per_keyword=results_per_keyword,
                    delay_between_searches=delay,
                    enforce_free_tier=True
                )
                
                if result:
                    print("✅ Bulk search completed successfully!")
                else:
                    print("❌ Bulk search failed or was cancelled")
                    
            except ValueError:
                print("❌ Invalid input. Please enter numbers only.")
        
        elif choice == '0':
            # Exit
            if scheduler.is_running:
                response = input("Scheduler is running. Stop it before exiting? (y/N): ").lower().strip()
                if response == 'y':
                    scheduler.stop()
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please choose 0-9.")

def main():
    """Main function"""
    try:
        # Check if API is configured
        if not search_api.is_configured():
            print("❌ Google Search API is not properly configured!")
            print("Please check your .env file and ensure you have:")
            print("  - GOOGLE_API_KEY")
            print("  - GOOGLE_SEARCH_ENGINE_ID")
            print("\nRun 'python scripts/setup.py' to configure the application.")
            sys.exit(1)
        
        # Check database connection
        try:
            db_manager.get_daily_request_count()
        except Exception as e:
            print("❌ Database connection failed!")
            print(f"Error: {e}")
            print("\nPlease check your MySQL configuration and ensure:")
            print("  - MySQL server is running")
            print("  - Database credentials are correct in .env file")
            print("  - Database and tables have been created")
            print("\nRun 'python scripts/setup.py --validate' to check your setup.")
            sys.exit(1)
        
        interactive_scheduler()
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted. Goodbye!")

if __name__ == "__main__":
    main()
