-- Create database and tables for Google Search API application
CREATE DATABASE IF NOT EXISTS google_search_app;
USE google_search_app;

-- Table to track API requests and enforce limits
CREATE TABLE IF NOT EXISTS api_requests (
 id INT AUTO_INCREMENT PRIMARY KEY,
 request_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
 query_text VARCHAR(500) NOT NULL,
 num_results INT DEFAULT 10,
 start_index INT DEFAULT 1,
 status ENUM('success', 'error', 'rate_limited') NOT NULL,
 response_time_ms INT,
 error_message TEXT,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table to store search results data
CREATE TABLE IF NOT EXISTS search_results (
 id INT AUTO_INCREMENT PRIMARY KEY,
 request_id INT,
 title TEXT,
 link VARCHAR(1000),
 snippet TEXT,
 display_link VARCHAR(500),
 formatted_url VARCHAR(1000),
 html_title TEXT,
 html_snippet TEXT,
 cache_id VARCHAR(100),
 page_map TEXT,
 position_in_results INT,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (request_id) REFERENCES api_requests(id) ON DELETE CASCADE,
 INDEX idx_request_id (request_id),
 INDEX idx_created_at (created_at)
);

-- Table to track daily API usage for rate limiting
CREATE TABLE IF NOT EXISTS daily_usage (
 id INT AUTO_INCREMENT PRIMARY KEY,
 usage_date DATE NOT NULL UNIQUE,
 request_count INT DEFAULT 0,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
