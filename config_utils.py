"""
Configuration utilities for environment variable substitution
"""

import os
import re
import yaml
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


def load_config(config_path: str = "config.yaml") -> dict:
    """
    Load configuration file with environment variable substitution
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing the configuration
        
    Raises:
        ValueError: If required environment variable is not found
    """
    with open(config_path, 'r') as f:
        config_content = f.read()
    
    # Replace environment variables in config
    config_content = substitute_env_vars(config_content)
    
    return yaml.safe_load(config_content)


def substitute_env_vars(content: str) -> str:
    """
    Substitute environment variables in config content
    
    Args:
        content: Configuration file content as string
        
    Returns:
        Content with environment variables substituted
        
    Raises:
        ValueError: If required environment variable is not found
    """
    def replace_env_var(match):
        var_name = match.group(1)
        env_value = os.getenv(var_name)
        if env_value is None:
            raise ValueError(f"Environment variable '{var_name}' not found. Please set it before running the application.")
        return env_value
    
    # Replace ${VAR_NAME} patterns with environment variables
    return re.sub(r'\$\{([^}]+)\}', replace_env_var, content)


def check_required_env_vars():
    """
    Check if all required environment variables are set
    
    Returns:
        bool: True if all required vars are set, False otherwise
    """
    required_vars = ['OPENROUTER_API_KEY']
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables before running the application.")
        print("\nExample:")
        print("export OPENROUTER_API_KEY=your_openrouter_api_key_here")
        print("# or on Windows:")
        print("set OPENROUTER_API_KEY=your_openrouter_api_key_here")
        return False
    
    return True