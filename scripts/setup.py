"""
Comprehensive setup script for Google Search API application
Handles installation, configuration, validation, and testing
"""
import os
import sys
import subprocess
import importlib
import unittest
import mysql.connector
from unittest.mock import patch, MagicMock
from datetime import date
from dotenv import load_dotenv

class GoogleSearchAppSetup:
    """Main setup class for the Google Search API application"""
    
    def __init__(self):
        self.required_packages = [
            'mysql-connector-python',
            'requests',
            'python-dotenv',
            'schedule'
        ]
        
        self.required_env_vars = [
            'GOOGLE_API_KEY',
            'GOOGLE_SEARCH_ENGINE_ID',
            'DB_PASSWORD'
        ]
    
    def install_packages(self):
        """Install required Python packages"""
        print("📦 Installing required packages...")
        print("-" * 50)
        
        missing_packages = []
        
        for package in self.required_packages:
            try:
                if package == 'mysql-connector-python':
                    import mysql.connector
                elif package == 'python-dotenv':
                    import dotenv
                else:
                    importlib.import_module(package)
                print(f"  ✅ {package} - Already installed")
            except ImportError:
                print(f"  📥 {package} - Installing...")
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                    print(f"  ✅ {package} - Installed successfully")
                except subprocess.CalledProcessError as e:
                    print(f"  ❌ {package} - Failed to install: {e}")
                    missing_packages.append(package)
        
        if missing_packages:
            print(f"\n❌ Failed to install: {', '.join(missing_packages)}")
            print("Please install manually with:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
        
        print("\n✅ All packages installed successfully!")
        return True
    
    def create_env_file(self):
        """Create a .env file with template and instructions"""
        
        env_content = """# Google Search API Configuration
# Get these from Google Cloud Console: https://console.cloud.google.com/
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here

# MySQL Database Configuration
# Update these with your MySQL server details
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=google_search_app

# API Rate Limiting Configuration
MAX_DAILY_REQUESTS=50
DEFAULT_RESULTS_PER_QUERY=10

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=google_search_app.log
"""
        
        instructions = """
# 📋 SETUP INSTRUCTIONS

## 1. Google API Setup:
a) Go to https://console.cloud.google.com/
b) Create a new project or select existing one
c) Enable "Custom Search API"
d) Go to "Credentials" and create an API key
e) Copy the API key and paste it as GOOGLE_API_KEY above

## 2. Google Custom Search Engine Setup:
a) Go to https://cse.google.com/
b) Click "Add" to create a new search engine
c) Enter "*" as the site to search (for web-wide search)
d) Create the search engine
e) Copy the Search Engine ID and paste it as GOOGLE_SEARCH_ENGINE_ID above

## 3. MySQL Database Setup:
a) Make sure MySQL/XAMPP is running
b) Update DB_PASSWORD with your MySQL root password
c) Run the database creation script: mysql -u root -p < scripts/01_create_database.sql

## 4. After updating this file:
- Save the file
- Run: python scripts/main.py
"""
        
        # Check if .env already exists
        if os.path.exists('.env'):
            print("⚠️  .env file already exists!")
            response = input("Do you want to overwrite it? (y/N): ").lower().strip()
            if response != 'y':
                print("❌ Keeping existing .env file.")
                return False
        
        # Write .env file
        with open('.env', 'w') as f:
            f.write(env_content)
            f.write(instructions)
        
        print("✅ Created .env file template")
        print("\n📝 IMPORTANT: Please edit the .env file and add your actual credentials!")
        print("📍 Location: " + os.path.abspath('.env'))
        
        return True
    
    def check_env_file(self):
        """Check if .env file exists and has required variables"""
        print("\n📄 Checking .env file...")
        
        if not os.path.exists('.env'):
            print("  ❌ .env file not found")
            return False
        
        print("  ✅ .env file exists")
        
        # Load environment variables
        load_dotenv()
        
        missing_vars = []
        for var in self.required_env_vars:
            value = os.getenv(var, '')
            if not value or value.startswith('your_'):
                print(f"  ❌ {var} - Not configured")
                missing_vars.append(var)
            else:
                print(f"  ✅ {var} - Configured")
        
        return len(missing_vars) == 0
    
    def check_database_connection(self):
        """Check MySQL database connection"""
        print("\n🗄️  Checking database connection...")
        
        load_dotenv()
        
        try:
            connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', '3306')),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'google_search_app')
            )
            
            if connection.is_connected():
                print("  ✅ Database connection successful")
                
                # Check if tables exist
                cursor = connection.cursor()
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                expected_tables = ['api_requests', 'search_results', 'daily_usage']
                existing_tables = [table[0] for table in tables]
                
                print("  📋 Checking database tables:")
                all_tables_exist = True
                for table in expected_tables:
                    if table in existing_tables:
                        print(f"    ✅ {table}")
                    else:
                        print(f"    ❌ {table} - Missing")
                        all_tables_exist = False
                
                connection.close()
                return all_tables_exist
            
        except mysql.connector.Error as e:
            print(f"  ❌ Database connection failed: {e}")
            return False
        
        return False
    
    def run_tests(self):
        """Run basic application tests"""
        print("\n🧪 Running Application Tests...")
        print("-" * 50)
        
        # Import test modules (simplified inline tests)
        test_results = {
            'config_test': self._test_config(),
            'database_test': self._test_database(),
            'api_test': self._test_api()
        }
        
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        
        print(f"\n📊 Test Results: {passed}/{total} passed")
        
        for test_name, result in test_results.items():
            status = "✅" if result else "❌"
            print(f"  {status} {test_name}")
        
        return passed == total
    
    def _test_config(self):
        """Test configuration loading"""
        try:
            sys.path.insert(0, os.path.dirname(__file__))
            from config import Config
            config = Config.from_env()
            return hasattr(config, 'GOOGLE_API_KEY')
        except Exception as e:
            print(f"    Config test error: {e}")
            return False
    
    def _test_database(self):
        """Test database manager"""
        try:
            sys.path.insert(0, os.path.dirname(__file__))
            from database import DatabaseManager
            db_manager = DatabaseManager()
            # Just test that we can create the object
            return hasattr(db_manager, 'get_connection')
        except Exception as e:
            print(f"    Database test error: {e}")
            return False
    
    def _test_api(self):
        """Test API client"""
        try:
            sys.path.insert(0, os.path.dirname(__file__))
            from google_search_api import GoogleSearchAPI
            api = GoogleSearchAPI()
            return hasattr(api, 'search')
        except Exception as e:
            print(f"    API test error: {e}")
            return False
    
    def validate_setup(self):
        """Validate the complete setup"""
        print("\n🔍 Validating Setup...")
        print("=" * 50)
        
        # Check components
        packages_ok = self._check_packages()
        env_ok = self.check_env_file()
        db_ok = self.check_database_connection()
        
        print(f"\n📊 Setup Status:")
        print(f"   Packages: {'✅' if packages_ok else '❌'}")
        print(f"   Environment: {'✅' if env_ok else '❌'}")
        print(f"   Database: {'✅' if db_ok else '❌'}")
        
        if packages_ok and env_ok and db_ok:
            print(f"\n🎉 Setup complete! You can now run:")
            print(f"   python scripts/main.py        # Interactive search")
            print(f"   python scripts/scheduler.py   # Automated scheduler")
            return True
        else:
            print(f"\n⚠️  Please complete the missing setup steps.")
            return False
    
    def _check_packages(self):
        """Check if packages are installed"""
        for package in self.required_packages:
            try:
                if package == 'mysql-connector-python':
                    import mysql.connector
                elif package == 'python-dotenv':
                    import dotenv
                else:
                    importlib.import_module(package)
            except ImportError:
                return False
        return True
    
    def provide_instructions(self):
        """Provide setup instructions based on what's missing"""
        print("\n🔧 Setup Instructions:")
        print("-" * 30)
        
        packages_ok = self._check_packages()
        env_ok = self.check_env_file()
        db_ok = self.check_database_connection()
        
        if not packages_ok:
            print(f"\n1️⃣  Install missing Python packages:")
            print(f"   Run: python scripts/setup.py --install")
        
        if not env_ok:
            print(f"\n2️⃣  Configure environment variables:")
            print(f"   Run: python scripts/setup.py --create-env")
            print(f"   Then edit the .env file with your actual credentials")
        
        if not db_ok:
            print(f"\n3️⃣  Set up MySQL database:")
            print(f"   - Make sure MySQL/XAMPP is running")
            print(f"   - Run: mysql -u root -p < scripts/01_create_database.sql")
            print(f"   - Update DB_PASSWORD in .env file")
    
    def full_setup(self):
        """Run complete setup process"""
        print("🚀 Google Search API Application - Complete Setup")
        print("=" * 60)
        
        # Step 1: Install packages
        if not self.install_packages():
            return False
        
        # Step 2: Create environment file
        print(f"\n📝 Creating environment configuration...")
        if not self.create_env_file():
            print("Using existing .env file")
        
        # Step 3: Provide next steps
        print(f"\n🎯 Next Steps:")
        print("1. Open the .env file in a text editor")
        print("2. Replace 'your_google_api_key_here' with your actual Google API key")
        print("3. Replace 'your_search_engine_id_here' with your Custom Search Engine ID")
        print("4. Replace 'your_mysql_password_here' with your MySQL password")
        print("5. Set up your MySQL database:")
        print("   mysql -u root -p < scripts/01_create_database.sql")
        print("6. Validate setup: python scripts/setup.py --validate")
        print("7. Run the application: python scripts/main.py")
        
        print(f"\n📚 Need help getting Google API credentials?")
        print("Check the instructions in the .env file!")
        
        return True

def main():
    """Main setup function"""
    setup = GoogleSearchAppSetup()
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == '--install':
            setup.install_packages()
        elif arg == '--create-env':
            setup.create_env_file()
        elif arg == '--validate':
            setup.validate_setup()
        elif arg == '--test':
            setup.run_tests()
        elif arg == '--check':
            setup.provide_instructions()
        elif arg == '--help':
            print("🔧 Google Search API Setup Tool")
            print("Usage: python scripts/setup.py [option]")
            print("\nOptions:")
            print("  --install     Install required packages")
            print("  --create-env  Create .env configuration file")
            print("  --validate    Validate complete setup")
            print("  --test        Run application tests")
            print("  --check       Check setup status and provide instructions")
            print("  --help        Show this help message")
            print("  (no option)   Run complete setup process")
        else:
            print(f"❌ Unknown option: {arg}")
            print("Use --help for available options")
    else:
        # Run full setup
        setup.full_setup()

if __name__ == "__main__":
    main()
