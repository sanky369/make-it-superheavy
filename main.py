import argparse
from agent import OpenRouterAgent
from model_factory import ModelAwareAgent, ModelFactory
from config_utils import check_required_env_vars

def main():
    """Main entry point for the OpenRouter agent"""
    parser = argparse.ArgumentParser(description='Single Agent CLI')
    parser.add_argument('--model', 
                       choices=['grok-4', 'kimi-k2', 'o3', 'claude-sonnet-4'],
                       default='kimi-k2',
                       help='Model to use for the agent')
    parser.add_argument('--list-models', action='store_true',
                       help='List available models and exit')
    
    args = parser.parse_args()
    
    # Check required environment variables
    if not check_required_env_vars():
        return 1
    
    if args.list_models:
        factory = ModelFactory()
        print("Available models:")
        for model_key, config in factory.get_available_models().items():
            print(f"  {model_key}: {config['display_name']}")
            print(f"    Context: {config['context_window']} tokens")
            print(f"    Recommended for: {', '.join(config['recommended_for'])}")
            print()
        return
    
    print(f"Single Agent with {args.model}")
    print("Type 'quit', 'exit', or 'bye' to exit")
    print("Type 'switch <model>' to change model")
    print("Type 'models' to see available models")
    print("-" * 50)
    
    try:
        agent = ModelAwareAgent(args.model)
        model_info = agent.get_model_info()
        print("Agent initialized successfully!")
        print(f"Using model: {model_info['display_name']}")
        print("Note: Make sure to set your OpenRouter API key in config.yaml")
        print("-" * 50)
    except Exception as e:
        print(f"Error initializing agent: {e}")
        print("Make sure you have:")
        print("1. Set your OpenRouter API key in config.yaml")
        print("2. Installed all dependencies with: pip install -r requirements.txt")
        return
    
    while True:
        try:
            user_input = input("\nUser: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'models':
                factory = ModelFactory()
                print("\nAvailable Models:")
                for model_key, config in factory.get_available_models().items():
                    current = " (current)" if model_key == agent.model_key else ""
                    print(f"  - {model_key}: {config['display_name']}{current}")
                continue
            
            if user_input.lower().startswith('switch '):
                model_name = user_input[7:].strip()
                try:
                    agent = ModelAwareAgent(model_name)
                    model_info = agent.get_model_info()
                    print(f"Model switched to: {model_info['display_name']}")
                except ValueError as e:
                    print(f"Error: {e}")
                continue
            
            if not user_input:
                print("Please enter a question or command.")
                continue
            
            print("Agent: Thinking...")
            response = agent.run(user_input)
            print(f"Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    main()