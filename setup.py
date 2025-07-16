#!/usr/bin/env python3
"""
Setup script for Make It SuperHeavy
"""

import os
import shutil
import sys
from pathlib import Path

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("ℹ️  python-dotenv not installed, skipping .env file loading")
    print("   Install with: uv pip install python-dotenv")


def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from .env.example")
        print("⚠️  Please edit .env and add your OpenRouter API key")
        return True
    elif env_file.exists():
        print("ℹ️  .env file already exists")
        return True
    else:
        print("❌ .env.example not found")
        return False


def check_api_key():
    """Check if API key is set"""
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("⚠️  OPENROUTER_API_KEY environment variable not set")
        print("Please set it in your .env file or as an environment variable")
        return False
    elif api_key == "your_openrouter_api_key_here":
        print("⚠️  Please replace the placeholder API key in .env with your actual OpenRouter API key")
        return False
    else:
        print("✅ OpenRouter API key is set")
        return True


def create_outputs_directory():
    """Create outputs directory if it doesn't exist"""
    outputs_dir = Path("outputs")
    if not outputs_dir.exists():
        outputs_dir.mkdir()
        print("✅ Created outputs directory")
    else:
        print("ℹ️  outputs directory already exists")


def test_imports():
    """Test that all required modules can be imported"""
    try:
        from model_factory import ModelFactory
        from config_utils import check_required_env_vars
        from orchestrator import TaskOrchestrator
        print("✅ All required modules can be imported")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install requirements: uv pip install -r requirements.txt")
        return False


def main():
    """Main setup function"""
    print("🚀 Make It SuperHeavy Setup")
    print("=" * 40)
    
    success = True
    
    # Create .env file
    if not create_env_file():
        success = False
    
    # Create outputs directory
    create_outputs_directory()
    
    # Test imports
    if not test_imports():
        success = False
    
    # Check API key
    if not check_api_key():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Make sure your OpenRouter API key is set in .env")
        print("2. Run: uv run main.py --list-models")
        print("3. Run: uv run make_it_heavy.py")
    else:
        print("❌ Setup completed with issues")
        print("Please resolve the issues above before using the application")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())