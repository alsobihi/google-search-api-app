<div align="center">

# 🔍 Google Search API Application

**A powerful Python application for automated Google search data collection with MySQL database integration and intelligent scheduling capabilities.**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/alsobihi/google-search-api-app.svg)](https://github.com/alsobihi/google-search-api-app/issues)
[![GitHub Stars](https://img.shields.io/github/stars/alsobihi/google-search-api-app.svg)](https://github.com/alsobihi/google-search-api-app/stargazers)

[Features](#-features) • [Installation](#️-installation) • [Usage](#-usage) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 🚀 Features

<table>
<tr>
<td width="50%">

### 🤖 **Automation**
- **Scheduled Searches**: Run searches at specified intervals
- **Bulk Processing**: Handle multiple keywords efficiently
- **Free Tier Protection**: Automatic cost safeguards
- **Smart Rate Limiting**: Respect API quotas

</td>
<td width="50%">

### 🔍 **Search Capabilities**
- **Interactive Search**: Real-time individual queries
- **Keyword Management**: Import/export keyword lists
- **Result Storage**: MySQL database integration
- **Search History**: Browse and analyze past searches

</td>
</tr>
<tr>
<td width="50%">

### 📊 **Monitoring**
- **Real-time Statistics**: API usage tracking
- **Cost Projections**: Estimate expenses
- **Success Metrics**: Monitor search performance
- **Comprehensive Logging**: Detailed operation logs

</td>
<td width="50%">

### ⚙️ **Configuration**
- **Easy Setup**: One-command installation
- **Flexible Settings**: Customizable parameters
- **Environment Management**: Secure credential storage
- **Database Schema**: Automated table creation

</td>
</tr>
</table>

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.7+** - [Download Python](https://www.python.org/downloads/)
- **MySQL Server** - [Download MySQL](https://www.mysql.com/downloads/) or use [XAMPP](https://www.apachefriends.org/)
- **Google Custom Search API Key** - [Get API Key](https://console.cloud.google.com/)
- **Google Custom Search Engine ID** - [Create Search Engine](https://cse.google.com/)

---

## 🛠️ Installation

### Quick Start (Recommended)


# 1. Clone the repository
```
git clone https://github.com/alsobihi//google-search-api-app.git
```

```
cd google-search-api-app
```
# 2. Run automated setup
```
python scripts/setup.py
```

# 3. Configure credentials (edit the generated .env file)
# Add your Google API key and Search Engine ID

# 4. Set up database

```
mysql -u root -p < scripts/01_create_database.sql
```

# 5. Validate setup
```
python scripts/setup.py --validate
```

# 6. Start the application
```
python scripts/scheduler.py
```



<details>
<summary><b>📖 Detailed Installation Steps</b></summary>

### Step 1: Clone Repository
```
git clone https://github.com/alsobih/google-search-api-app.git
```

```
cd google-search-api-app
```

### Step 2: Install Dependencies

# Option A: Automatic installation

```
python scripts/setup.py --install
```

# Option B: Manual installation

```
pip install mysql-connector-python requests python-dotenv schedule
```



### Step 3: Configure Environment

# Create configuration file

```
python scripts/setup.py --create-env
```

# Edit .env file with your credentials
nano .env  # or use your preferred editor


### Step 4: Database Setup

# Start MySQL server
# For XAMPP: Start Apache and MySQL from control panel
# For standalone MySQL: service mysql start

# Create database and tables

```
mysql -u root -p < scripts/01_create_database.sql
```



### Step 5: Validation

# Check setup status
```
python scripts/setup.py --check
```

# Validate configuration

```
python scripts/setup.py --validate
```

# Run tests

```
python scripts/setup.py --test
```



</details>



## 🔑 Getting API Credentials

### Google Custom Search API Setup

<details>
<summary><b>🔧 Step-by-Step API Configuration</b></summary>

#### 1. Google Cloud Console Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services** → **Library**
4. Search for "Custom Search API" and enable it
5. Go to **APIs & Services** → **Credentials**
6. Click **Create Credentials** → **API Key**
7. Copy the generated API key

#### 2. Custom Search Engine Setup
1. Visit [Google Custom Search](https://cse.google.com/)
2. Click **Add** to create a new search engine
3. In "Sites to search", enter `*` (for web-wide search)
4. Click **Create**
5. Copy the **Search Engine ID** from the control panel

#### 3. Configure Application
Add your credentials to the `.env` file:
`env`

```
GOOGLE_API_KEY=your_actual_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```



</details>



## 🚀 Usage

### Quick Start Commands


# Start the main application

```
python scripts/scheduler.py
```

# Check setup status

```
python scripts/setup.py --check
```

# View help

```
python scripts/setup.py --help
```



### Application Interface

The application provides a comprehensive menu-driven interface:

```
📋 Main Menu:
1. Start hourly schedule        # Automated scheduling
2. Check scheduler status       # Monitor schedules  
3. Stop scheduler              # Stop automation
4. View current API usage      # Check quotas
5. Manage keywords             # Configure search terms
6. API settings               # Adjust limits
7. Interactive search         # Individual searches
8. View recent searches       # Browse history
9. Run one-time bulk search   # Immediate bulk search
0. Exit                       # Close application
```

### Example Workflows

<details>
<summary><b>🔄 Setting Up Automated Searches</b></summary>

1. **Start the application:**
   
```
   python scripts/scheduler.py
```

 

3. **Configure schedule:**
   - Select option `1` (Start hourly schedule)
   - Set frequency: `24` hours
   - Results per keyword: `50`
   - Duration: `7` days

4. **Review configuration:**
   ```
   📊 DETAILED SCHEDULE SUMMARY
   ============================================================
   📅 Schedule Configuration:
   Frequency: Every 24 hour(s)
   Results per keyword: 50
   Keywords to search: 9
   Duration: 7 days

   🔢 API Call Calculations:
   API calls per keyword: 5 (Google returns max 10 results per call)
   Total API calls per run: 45
   Runs per day: 1.0
   Total API calls per day: 45

   💰 Free Tier Status: ✅ Stays within free tier
   ```

5. **Confirm and start:**
   - Review the summary
   - Confirm to start the scheduler
   - Monitor progress in real-time

</details>

<details>
<summary><b>🔍 Interactive Search Example</b></summary>

1. **Access interactive search:**
   - Select option `7` from main menu

2. **Perform search:**
   ```
   🔍 Interactive Search
   Enter a search query: machine learning algorithms
   Number of results (default 10): 20

   🔍 Searching for: 'machine learning algorithms'
   Requesting 20 results...
   This will use approximately 2 API calls

   ✅ Got 10 results
   ✅ Got 10 results

   📊 Search Results for: 'machine learning algorithms'
   Total results found: 20

   1. Introduction to Machine Learning Algorithms
      🔗 https://example.com/ml-intro
      📝 A comprehensive guide to machine learning algorithms...
   ```

3. **View updated statistics:**
   ```
   📈 Updated API Usage:
   Used Today: 12/50
   Remaining: 38
   ```

</details>



## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

`env`
# Google API Configuration

```
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here

# MySQL Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=google_search_app

# API Rate Limiting
MAX_DAILY_REQUESTS=50
DEFAULT_RESULTS_PER_QUERY=10

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=google_search_app.log
```



### Keyword Management

<details>
<summary><b>📝 Managing Search Keywords</b></summary>

#### Default Keywords
The application comes with data science-focused keywords:
- Data Analysis, Data Analytics, Data Analyst
- Data Mining, Data Modeling, Data Visualization
- Business Intelligence, Machine Learning, Deep Learning

#### Custom Keywords
1. **Via Application Menu:**
   - Select option `5` (Manage keywords)
   - Choose "Change default keywords"
   - Enter new keywords (one per line)

2. **Via File Import:**
   
   # Create keywords file
   echo -e "artificial intelligence\nmachine learning\ndeep learning" > keywords.txt
   
   # Import via application menu
   # Select option 5 → Load keywords from file
   ```

3. **Programmatic Management:**
   ```
   # Save current keywords
   save_keywords_to_file(DEFAULT_KEYWORDS, "backup_keywords.txt")
   
   # Load keywords from file
   new_keywords = load_keywords_from_file("custom_keywords.txt")
   ```

</details>



## 💰 Cost Management

### Free Tier Limits

| Tier | Daily Limit | Cost | Features |
|------|-------------|------|----------|
| **Free** | 100 searches | $0.00 | Basic usage, automatic protection |
| **Paid** | Unlimited | $5.00/1000 searches | No daily limits, advanced features |

### Cost Examples

```
📊 Cost Projections:
• 200 searches/day: $0.50/day, $15.00/month
• 500 searches/day: $2.00/day, $60.00/month  
• 1000 searches/day: $4.50/day, $135.00/month
```

### Free Tier Protection

The application includes automatic safeguards:
- ✅ **Pre-search validation** - Check quotas before execution
- ✅ **Real-time monitoring** - Track usage during operations
- ✅ **Cost warnings** - Alert before exceeding free tier
- ✅ **Emergency stops** - Halt operations if limits approached

---

## 📊 Database Schema

### Tables Overview

```
-- API request tracking
CREATE TABLE api_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query_text VARCHAR(500) NOT NULL,
    num_results INT DEFAULT 10,
    status ENUM('success', 'error', 'rate_limited'),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Search results storage  
CREATE TABLE search_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT,
    title TEXT,
    link VARCHAR(1000),
    snippet TEXT,
    position_in_results INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Daily usage tracking
CREATE TABLE daily_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usage_date DATE NOT NULL UNIQUE,
    request_count INT DEFAULT 0
);
```

### Data Analysis Examples

<details>
<summary><b>📈 SQL Query Examples</b></summary>

```sql
-- View recent searches
SELECT query_text, status, created_at 
FROM api_requests 
ORDER BY created_at DESC 
LIMIT 10;

-- Get search results for a specific query
SELECT sr.title, sr.link, sr.snippet
FROM search_results sr
JOIN api_requests ar ON sr.request_id = ar.id
WHERE ar.query_text = 'machine learning'
ORDER BY sr.position_in_results;

-- Daily usage statistics
SELECT usage_date, request_count
FROM daily_usage 
ORDER BY usage_date DESC 
LIMIT 30;

-- Success rate analysis
SELECT 
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM api_requests), 2) as percentage
FROM api_requests 
GROUP BY status;

-- Top searched keywords
SELECT 
    query_text,
    COUNT(*) as search_count,
    MAX(created_at) as last_searched
FROM api_requests 
WHERE status = 'success'
GROUP BY query_text 
ORDER BY search_count DESC 
LIMIT 10;
```

</details>



## 🐛 Troubleshooting

### Quick Diagnosis


# Check setup status
python scripts/setup.py --check

# Validate configuration  
python scripts/setup.py --validate

# Run application tests
```
python scripts/setup.py --test
```

### Common Issues

<details>
<summary><b>❌ Missing Dependencies</b></summary>

**Error:**
```
ModuleNotFoundError: No module named 'schedule'
```

**Solution:**
```
python scripts/setup.py --install
```

</details>

<details>
<summary><b>❌ API Configuration Issues</b></summary>

**Error:**
```
Google API key and Search Engine ID must be provided
```

**Solutions:**
1. Check `.env` file exists and contains credentials
2. Verify API key is valid in Google Cloud Console
3. Ensure Custom Search Engine is properly configured
4. Run: `python scripts/setup.py --create-env`

</details>

<details>
<summary><b>❌ Database Connection Issues</b></summary>

**Error:**
```
Database connection failed
```

**Solutions:**
1. Ensure MySQL server is running
2. Check credentials in `.env` file
3. Verify database exists: `mysql -u root -p -e "SHOW DATABASES;"`
4. Recreate database: `mysql -u root -p < scripts/01_create_database.sql`

</details>

<details>
<summary><b>❌ Rate Limit Issues</b></summary>

**Error:**
```
Daily API request limit exceeded
```

**Solutions:**
1. Wait for daily reset (midnight UTC)
2. Increase `MAX_DAILY_REQUESTS` in `.env` file
3. Use API settings menu in application
4. Consider upgrading to paid tier

</details>

### Debug Commands


# View application logs

```
tail -f google_search_app.log
```

# View scheduler logs  

```
tail -f scheduler.log
```

# Check MySQL connection

```
mysql -u root -p google_search_app
```

# Test API connectivity

```
curl "https://www.googleapis.com/customsearch/v1?key=YOUR_API_KEY&cx=YOUR_ENGINE_ID&q=test"
```


---

## 📁 Project Structure

```
google-search-api-app/
├── 📁 scripts/
│   ├── 📄 01_create_database.sql      # Database schema
│   ├── 📄 config.py                   # Configuration management
│   ├── 📄 database.py                 # Database operations
│   ├── 📄 google_search_api.py        # API client
│   ├── 📄 scheduler.py                # Main application
│   └── 📄 setup.py                    # Setup and validation
├── 📄 .env                            # Environment variables
├── 📄 .gitignore                      # Git ignore rules
├── 📄 README.md                       # This documentation
├── 📄 LICENSE                         # MIT License
├── 📄 google_search_app.log           # Application logs
└── 📄 scheduler.log                   # Scheduler logs
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Getting Started

1. **Fork the repository**
   ```
   git fork https://github.com/alsobihi/google-search-api-app.git
   ```

2. **Create a feature branch**
   ```
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**
   ```
   python scripts/setup.py --test
   ```

5. **Commit and push**
   
   git commit -m 'Add amazing feature'
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**

### Development Guidelines

<details>
<summary><b>📋 Code Standards</b></summary>

- **Python Style**: Follow PEP 8 guidelines
- **Documentation**: Add docstrings for all functions
- **Testing**: Include unit tests for new features
- **Logging**: Use appropriate log levels
- **Error Handling**: Implement comprehensive error handling

</details>

### Areas for Contribution

- 🐛 **Bug Fixes** - Help identify and fix issues
- ✨ **New Features** - Add functionality and improvements
- 📚 **Documentation** - Improve guides and examples
- 🧪 **Testing** - Expand test coverage
- 🎨 **UI/UX** - Enhance user interface and experience

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Google Search API Application

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🆘 Support

### Getting Help

- 📖 **Documentation**: Check this README and inline code comments
- 🐛 **Issues**: [Open an issue](https://github.com/alsobihi/google-search-api-app/issues) for bugs or feature requests
- 💬 **Discussions**: [Join discussions](https://github.com/alsobihi/google-search-api-app/discussions) for questions and ideas
- 📧 **Email**: Contact the maintainers directly

### Diagnostic Tools


# Quick health check
python scripts/setup.py --check

# Comprehensive validation
python scripts/setup.py --validate

# Run all tests
```
python scripts/setup.py --test
```

---

## 🔗 Useful Links

| Resource | Description | Link |
|----------|-------------|------|
| **Google Custom Search API** | Official API documentation | [📖 Docs](https://developers.google.com/custom-search/v1/overview) |
| **Google Cloud Console** | Manage API keys and projects | [🔧 Console](https://console.cloud.google.com/) |
| **Custom Search Engine** | Create and manage search engines | [⚙️ Setup](https://cse.google.com/) |
| **MySQL Documentation** | Database setup and management | [📚 MySQL Docs](https://dev.mysql.com/doc/) |
| **Python.org** | Python installation and guides | [🐍 Python](https://www.python.org/) |

---

<div align="center">

### ⭐ Star this repository if you find it helpful!

**Made with ❤️ by the community**

[⬆️ Back to Top](#-google-search-api-application)

</div>
