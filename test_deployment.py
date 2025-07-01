#!/usr/bin/env python3
"""
Test script to verify deployment readiness for Streamlit Cloud
"""

import os
import sys
import importlib

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    required_packages = [
        'streamlit',
        'openai', 
        'pandas',
        'jinja2',
        'openpyxl',
        'python-dotenv',
        'numpy',
        'altair',
        'pydeck'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n⚠️  Failed imports: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ All packages imported successfully!")
        return True

def test_environment():
    """Test environment variable setup"""
    print("\n🔍 Testing environment setup...")
    
    # Test .env file
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found (this is OK for Streamlit Cloud)")
    
    # Test API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and api_key != 'your_openai_api_key_here':
        print("✅ OpenAI API key found in environment")
        return True
    else:
        print("⚠️  OpenAI API key not found in environment")
        print("💡 This is expected for Streamlit Cloud deployment")
        return True

def test_app_structure():
    """Test if app.py can be imported"""
    print("\n🔍 Testing app structure...")
    
    if not os.path.exists('app.py'):
        print("❌ app.py not found!")
        return False
    
    try:
        # Try to import the main app functions
        import app
        print("✅ app.py can be imported")
        
        # Check if main functions exist
        if hasattr(app, 'initialize_openai'):
            print("✅ initialize_openai function found")
        else:
            print("⚠️  initialize_openai function not found")
        
        if hasattr(app, 'generate_title'):
            print("✅ generate_title function found")
        else:
            print("⚠️  generate_title function not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing app.py: {e}")
        return False

def test_requirements():
    """Test if requirements.txt exists and is valid"""
    print("\n🔍 Testing requirements.txt...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found!")
        return False
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip()
        
        if requirements:
            print("✅ requirements.txt found and not empty")
            print(f"📦 Contains {len(requirements.split())} lines")
            return True
        else:
            print("❌ requirements.txt is empty")
            return False
            
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def test_gitignore():
    """Test if .gitignore exists"""
    print("\n🔍 Testing .gitignore...")
    
    if os.path.exists('.gitignore'):
        print("✅ .gitignore found")
        
        # Check if it contains important entries
        with open('.gitignore', 'r') as f:
            content = f.read()
        
        important_patterns = ['.env', '__pycache__', '.venv']
        found_patterns = []
        
        for pattern in important_patterns:
            if pattern in content:
                found_patterns.append(pattern)
        
        if found_patterns:
            print(f"✅ Contains important patterns: {', '.join(found_patterns)}")
        else:
            print("⚠️  Missing important patterns in .gitignore")
        
        return True
    else:
        print("⚠️  .gitignore not found")
        return False

def main():
    """Run all tests"""
    print("🚀 Streamlit Cloud Deployment Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_environment,
        test_app_structure,
        test_requirements,
        test_gitignore
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 All tests passed! Your app is ready for Streamlit Cloud deployment.")
        print("\n📋 Next steps:")
        print("1. Push your code to GitHub")
        print("2. Go to share.streamlit.io")
        print("3. Connect your repository")
        print("4. Set OPENAI_API_KEY in environment variables")
        print("5. Deploy!")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("\n🔧 Please fix the failed tests before deploying.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 