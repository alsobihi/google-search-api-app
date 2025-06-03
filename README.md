# Google Search API Application

A streamlined Python application for automated Google search data collection with MySQL database integration and intelligent scheduling capabilities.

## 🚀 Features

- **Automated Scheduling**: Schedule searches to run at specified intervals
- **Interactive Search**: Perform individual searches with detailed results
- **Database Integration**: Store search results in MySQL with detailed metadata
- **Rate Limiting**: Built-in protection for Google API free tier limits
- **Keyword Management**: Flexible keyword management with file import/export
- **Real-time Monitoring**: Track API usage, costs, and search statistics
- **Free Tier Protection**: Automatic safeguards to prevent exceeding free API limits
- **Comprehensive Logging**: Detailed logs for monitoring and debugging

## 📋 Prerequisites

- Python 3.7+
- MySQL Server (or XAMPP/WAMP)
- Google Custom Search API Key
- Google Custom Search Engine ID

## 🛠️ Quick Installation

### 1. Clone the Repository
\`\`\`bash
git clone https://github.com/yourusername/google-search-api-app.git
cd google-search-api-app
\`\`\`

### 2. Run Complete Setup
\`\`\`bash
# This will install packages and create configuration files
python scripts/setup.py
\`\`\`

### 3. Configure Your Credentials
Edit the `.env` file created by setup:
\`\`\`env
GOOGLE_API_KEY=your_actual_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_actual_search_engine_id
DB_PASSWORD=your_mysql_password
\`\`\`

### 4. Set Up Database
\`\`\`bash
# Start MySQL server (XAMPP/WAMP or standalone)
mysql -u root -p < scripts/01_create_database.sql
\`\`\`

### 5. Validate Setup
\`\`\`bash
python scripts/setup.py --validate
\`\`\`

## 🔧 Setup Options

The setup script provides several options:

\`\`\`bash
python scripts/setup.py --install     # Install required packages only
python scripts/setup.py --create-env  # Create .env file only
python scripts/setup.py --validate    # Check if everything is configured
python scripts/setup.py --test        # Run application tests
python scripts/setup.py --check       # Check status and get instructions
python scripts/setup.py --help        # Show all options
\`\`\`

## 🔑 Getting Google API Credentials

### 1. Google API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable "Custom Search API"
4. Go to "Credentials" and create an API key
5. Copy the API key to your `.env` file

### 2. Custom Search Engine ID
1. Go to [Google Custom Search](https://cse.google.com/)
2. Click "Add" to create a new search engine
3. Enter "*" as the site to search (for web-wide search)
4. Create the search engine
5. Copy the Search Engine ID to your `.env` file

## 🚀 Usage

### Quick Start
\`\`\`bash
# Run the application
python scripts/scheduler.py
\`\`\`

## 📊 Application Features

The application provides a comprehensive menu-driven interface:

### Main Menu Options:
1. **Start hourly schedule** - Set up automated searches
2. **Check scheduler status** - Monitor running schedules
3. **Stop scheduler** - Stop active schedules
4. **View current API usage** - Check quota and costs
5. **Manage keywords** - Configure search terms
6. **API settings** - Adjust rate limits and defaults
7. **Interactive search** - Perform individual searches
8. **View recent searches** - Browse search history
9. **Run one-time bulk search** - Execute immediate bulk search
0. **Exit** - Close the application

### Setting Up a Schedule:
1. Run `python scripts/scheduler.py`
2. Select "Start hourly schedule"
3. Configure:
- **Frequency**: Every X hours (default: 25)
- **Results per keyword**: 1-100 (default: 10)
- **Duration**: Days to run (default: unlimited)

### Example Schedule Configuration:
\`\`\`
Run every X hours (default 25): 24
Results per keyword (default 10): 50
Maximum days to run (default: unlimited): 7

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
\`\`\`

## 🔧 Keyword Management

### Default Keywords
The application comes with data science-focused keywords:
- Data Analysis, Data Analytics, Data Analyst
- Data Mining, Data Modeling, Data Visualization
- Business Intelligence, Machine Learning, Deep Learning

### Managing Keywords:
1. **View current keywords**: See active keyword list
2. **Change default keywords**: Replace with custom terms
3. **Load from file**: Import keywords from text file
4. **Save to file**: Export keywords for backup

### Custom Keywords Example:
\`\`\`
# In main menu: Manage keywords > Change default keywords
Enter new keywords (one per line, empty line to finish):
artificial intelligence
machine learning
deep learning
neural networks
computer vision

✅ Updated default keywords! Now using 5 keywords
\`\`\`

## 🔍 Interactive Search

The application includes an interactive search mode for individual queries:

1. Select "Interactive search" from the main menu
2. Enter your search query
3. Specify number of results (1-100)
4. View results immediately in the terminal

### Example Interactive Search:
\`\`\`
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
\`\`\`

## 💰 API Cost Management

### Free Tier Limits:
- **100 searches per day** (Google's free tier)
- **No cost** for first 100 daily searches
- **Automatic protection** against exceeding limits

### Paid Tier:
- **$5.00 per 1,000 queries** ($0.005 per search)
- **No daily limits**
- **Cost estimates** shown in application

### Cost Examples:
- 200 searches/day: $0.50/day, $15/month
- 500 searches/day: $2.00/day, $60/month
- 1000 searches/day: $4.50/day, $135/month

## 📈 Monitoring and Analytics

### Real-time Statistics:
- API usage tracking (daily/remaining)
- Success/failure rates
- Cost projections
- Free tier status

### Database Schema:
- **api_requests**: Search request logs
- **search_results**: Detailed search results
- **daily_usage**: Daily API usage tracking

### Accessing Data:
\`\`\`sql
-- View recent searches
SELECT * FROM api_requests ORDER BY created_at DESC LIMIT 10;

-- Get search results for a specific query
SELECT * FROM search_results WHERE request_id = 1;

-- Check daily usage
SELECT * FROM daily_usage ORDER BY usage_date DESC;
\`\`\`

## 🐛 Troubleshooting

### Quick Diagnosis
\`\`\`bash
# Check setup status
python scripts/setup.py --check

# Validate configuration
python scripts/setup.py --validate

# Run tests
python scripts/setup.py --test
\`\`\`

### Common Issues:

#### 1. Missing Dependencies
\`\`\`
ModuleNotFoundError: No module named 'schedule'
\`\`\`
**Solution**: Run `python scripts/setup.py --install`

#### 2. API Key Errors
\`\`\`
ValueError: Google API key and Search Engine ID must be provided
\`\`\`
**Solution**: Check your `.env` file has correct API credentials

#### 3. Database Connection Errors
\`\`\`
Database connection failed
\`\`\`
**Solution**: Verify MySQL is running and credentials are correct

#### 4. Rate Limit Exceeded
\`\`\`
Daily API request limit exceeded
\`\`\`
**Solution**: Wait for daily reset or increase `MAX_DAILY_REQUESTS` in `.env`

### Debug Commands:
\`\`\`bash
# View detailed logs
tail -f google_search_app.log
tail -f scheduler.log

# Check MySQL connection
mysql -u root -p google_search_app
\`\`\`

## 📁 Project Structure

\`\`\`
google-search-api-app/
├── scripts/
│   ├── 01_create_database.sql      # Database schema
│   ├── config.py                   # Configuration management
│   ├── database.py                 # Database operations
│   ├── google_search_api.py        # API client
│   ├── scheduler.py                # Main application (all-in-one)
│   └── setup.py                    # Complete setup and validation tool
├── .env                            # Environment variables (created by setup)
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
├── google_search_app.log           # Application logs
└── scheduler.log                   # Scheduler logs
\`\`\`

## ⚙️ Configuration Options

### Environment Variables (.env):
- `GOOGLE_API_KEY`: Your Google Custom Search API key
- `GOOGLE_SEARCH_ENGINE_ID`: Your Custom Search Engine ID
- `DB_HOST`: MySQL host (default: localhost)
- `DB_PORT`: MySQL port (default: 3306)
- `DB_USER`: MySQL username (default: root)
- `DB_PASSWORD`: MySQL password
- `DB_NAME`: Database name (default: google_search_app)
- `MAX_DAILY_REQUESTS`: Daily API limit (default: 50)
- `DEFAULT_RESULTS_PER_QUERY`: Default results per search (default: 10)
- `LOG_LEVEL`: Logging level (default: INFO)
- `LOG_FILE`: Log file name (default: google_search_app.log)

### Runtime Configuration:
- **API Settings**: Modify daily limits and defaults through the application menu
- **Keywords**: Change default keywords or load from files
- **Schedule**: Configure frequency, duration, and results per keyword

## 🔒 Security Best Practices

### Environment Variables:
- Never commit `.env` files to version control
- Use strong MySQL passwords
- Restrict API key permissions in Google Cloud

### Database Security:
- Use dedicated database user with limited permissions
- Enable MySQL SSL if accessing remotely
- Regular database backups

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Run `python scripts/setup.py --check` for diagnosis
3. Review the logs (`google_search_app.log`, `scheduler.log`)
4. Open an issue on GitHub with detailed error information

## 🔗 Useful Links

- [Google Custom Search API Documentation](https://developers.google.com/custom-search/v1/overview)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Google Custom Search Engine Setup](https://cse.google.com/)
- [MySQL Documentation](https://dev.mysql.com/doc/)

---

**Happy Searching!** 🔍✨
