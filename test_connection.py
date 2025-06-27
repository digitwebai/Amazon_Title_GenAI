#!/usr/bin/env python3
"""
Test script to check OpenAI connection and identify Streamlit issues
"""

import os
import openai
from dotenv import load_dotenv

def test_openai_connection():
    """Test OpenAI connection without Streamlit"""
    print("Testing OpenAI connection...")
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("💡 Please set your OpenAI API key in a .env file or environment variable")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    # Set API key
    openai.api_key = api_key
    
    try:
        print("🔄 Testing API connection...")
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, can you respond?"}
            ],
            timeout=10
        )
        print("✅ OpenAI connection successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection failed: {str(e)}")
        return False

def test_streamlit_imports():
    """Test Streamlit imports"""
    print("\nTesting Streamlit imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        import pandas as pd
        print("✅ Pandas imported successfully")
        
        from jinja2 import Template
        print("✅ Jinja2 imported successfully")
        
        import openpyxl
        print("✅ OpenPyXL imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False

def test_app_functions():
    """Test app functions without Streamlit context"""
    print("\nTesting app functions...")
    
    try:
        from app import create_prompt, generate_title
        
        # Test create_prompt
        prompt = create_prompt("Test Title", "Test description")
        print("✅ create_prompt function works")
        
        # Test generate_title (this will fail without API key, but we can test the function exists)
        print("✅ generate_title function imported")
        
        return True
        
    except Exception as e:
        print(f"❌ App function error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🔍 Amazon Title Generator - Connection Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_streamlit_imports()
    
    # Test app functions
    functions_ok = test_app_functions()
    
    # Test OpenAI connection
    openai_ok = test_openai_connection()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Imports: {'✅' if imports_ok else '❌'}")
    print(f"Functions: {'✅' if functions_ok else '❌'}")
    print(f"OpenAI: {'✅' if openai_ok else '❌'}")
    
    if all([imports_ok, functions_ok, openai_ok]):
        print("\n🎉 All tests passed! Your app should work correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        
        if not openai_ok:
            print("\n💡 To fix OpenAI connection:")
            print("1. Create a .env file in your project root")
            print("2. Add: OPENAI_API_KEY=your_actual_api_key_here")
            print("3. Make sure you have sufficient API credits")

if __name__ == "__main__":
    main() 