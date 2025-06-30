#!/usr/bin/env python3
"""
Deployment script for Amazon Title Generator Streamlit App
"""

import os
import sys
import subprocess
import platform

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'streamlit',
        'openai',
        'pandas',
        'jinja2',
        'openpyxl',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages)
    else:
        print("\n✅ All dependencies are installed!")

def check_environment():
    """Check environment setup"""
    print("\n🔍 Checking environment...")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found")
        print("Creating .env file...")
        with open('.env', 'w') as f:
            f.write("# OpenAI API Configuration\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
        print("✅ .env file created. Please add your OpenAI API key.")
    
    # Check API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and api_key != 'your_openai_api_key_here':
        print("✅ OpenAI API key found")
    else:
        print("❌ OpenAI API key not configured")
        print("💡 Please add your OpenAI API key to the .env file")

def test_connection():
    """Test OpenAI connection"""
    print("\n🔍 Testing OpenAI connection...")
    
    try:
        from test_connection import main as test_main
        test_main()
    except Exception as e:
        print(f"❌ Connection test failed: {e}")

def run_app():
    """Run the Streamlit app"""
    print("\n🚀 Starting Streamlit app...")
    
    try:
        # Get the current directory
        current_dir = os.getcwd()
        app_path = os.path.join(current_dir, 'app.py')
        
        if not os.path.exists(app_path):
            print("❌ app.py not found!")
            return
        
        print("✅ app.py found")
        print("🌐 Starting server at http://localhost:8501")
        print("📝 Press Ctrl+C to stop the server")
        
        # Run streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port', '8501',
            '--server.address', 'localhost'
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting app: {e}")

def deploy_streamlit_cloud():
    """Instructions for Streamlit Cloud deployment"""
    print("\n☁️  Streamlit Cloud Deployment")
    print("=" * 50)
    print("1. Push your code to GitHub:")
    print("   git add .")
    print("   git commit -m 'Add Streamlit app'")
    print("   git push origin main")
    print("\n2. Go to https://share.streamlit.io")
    print("3. Sign in with GitHub")
    print("4. Click 'New app'")
    print("5. Select your repository")
    print("6. Set main file path to: app.py")
    print("7. Add environment variables:")
    print("   - OPENAI_API_KEY: your_api_key")
    print("8. Click 'Deploy'")

def main():
    """Main deployment function"""
    print("🛒 Amazon Title Generator - Deployment Script")
    print("=" * 50)
    
    # Check dependencies
    check_dependencies()
    
    # Check environment
    check_environment()
    
    # Test connection
    test_connection()
    
    # Menu
    while True:
        print("\n" + "=" * 50)
        print("Choose an option:")
        print("1. Run app locally")
        print("2. Deploy to Streamlit Cloud")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            run_app()
        elif choice == '2':
            deploy_streamlit_cloud()
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 