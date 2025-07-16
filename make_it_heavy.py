import time
import threading
import sys
import argparse
from orchestrator import TaskOrchestrator
from config_utils import check_required_env_vars

class OrchestratorCLI:
    def __init__(self, agent_model=None, no_save=False, output_dir='outputs'):
        self.orchestrator = TaskOrchestrator(agent_model=agent_model)
        self.start_time = None
        self.running = False
        
        # Configure output settings
        if no_save:
            self.orchestrator.config['output']['auto_save'] = False
        else:
            self.orchestrator.config['output']['auto_save'] = True
            self.orchestrator.config['output']['directory'] = output_dir
        
        # Get current model configuration
        config = self.orchestrator.get_current_config()
        orchestrator_model = config['orchestrator_model']
        agent_model = config['agent_model']
        
        # Extract display name from orchestrator model
        self.model_display = f"KIMI-K2 HEAVY (Agents: {agent_model.upper().replace('-', ' ')})"
        
    def clear_screen(self):
        """Properly clear the entire screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def format_time(self, seconds):
        """Format seconds into readable time string"""
        if seconds < 60:
            return f"{int(seconds)}S"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}M{secs}S"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}H{minutes}M"
    
    def create_progress_bar(self, status):
        """Create progress visualization based on status"""
        # ANSI color codes
        ORANGE = '\033[38;5;208m'  # Orange color
        RED = '\033[91m'           # Red color
        RESET = '\033[0m'          # Reset color
        
        if status == "QUEUED":
            return "○ " + "·" * 70
        elif status == "INITIALIZING...":
            return f"{ORANGE}◐{RESET} " + "·" * 70
        elif status == "PROCESSING...":
            # Animated processing bar in orange
            dots = f"{ORANGE}:" * 10 + f"{RESET}" + "·" * 60
            return f"{ORANGE}●{RESET} " + dots
        elif status == "COMPLETED":
            return f"{ORANGE}●{RESET} " + f"{ORANGE}:" * 70 + f"{RESET}"
        elif status.startswith("FAILED"):
            return f"{RED}✗{RESET} " + f"{RED}×" * 70 + f"{RESET}"
        else:
            return f"{ORANGE}◐{RESET} " + "·" * 70
    
    def update_display(self):
        """Update the console display with current status"""
        if not self.running:
            return
            
        # Calculate elapsed time
        elapsed = time.time() - self.start_time if self.start_time else 0
        time_str = self.format_time(elapsed)
        
        # Get current progress
        progress = self.orchestrator.get_progress_status()
        
        # Clear screen properly
        self.clear_screen()
        
        # Header with dynamic model name
        print(self.model_display)
        if self.running:
            print(f"● RUNNING • {time_str}")
        else:
            print(f"● COMPLETED • {time_str}")
        print()
        
        # Agent status lines
        for i in range(self.orchestrator.num_agents):
            status = progress.get(i, "QUEUED")
            progress_bar = self.create_progress_bar(status)
            print(f"AGENT {i+1:02d}  {progress_bar}")
        
        print()
        sys.stdout.flush()
    
    def progress_monitor(self):
        """Monitor and update progress display in separate thread"""
        while self.running:
            self.update_display()
            time.sleep(1.0)  # Update every 1 second (reduced flicker)
    
    def run_task(self, user_input):
        """Run orchestrator task with live progress display"""
        self.start_time = time.time()
        self.running = True
        
        # Start progress monitoring in background thread
        progress_thread = threading.Thread(target=self.progress_monitor, daemon=True)
        progress_thread.start()
        
        try:
            # Run the orchestrator
            result = self.orchestrator.orchestrate(user_input)
            
            # Stop progress monitoring
            self.running = False
            
            # Final display update
            self.update_display()
            
            # Show results
            print("=" * 80)
            print("FINAL RESULTS")
            print("=" * 80)
            print()
            print(result)
            print()
            print("=" * 80)
            
            return result
            
        except Exception as e:
            self.running = False
            self.update_display()
            print(f"\nError during orchestration: {str(e)}")
            return None
    
    def interactive_mode(self):
        """Run interactive CLI session"""
        print("Multi-Agent Orchestrator")
        print(f"Configured for {self.orchestrator.num_agents} parallel agents")
        
        config = self.orchestrator.get_current_config()
        print(f"Orchestrator Model: {config['orchestrator_model']}")
        print(f"Agent Model: {config['agent_model']}")
        print(f"Available Agent Models: {', '.join(self.orchestrator.get_available_models())}")
        
        print("Type 'quit', 'exit', or 'bye' to exit")
        print("Type 'switch <model>' to change agent model")
        print("Type 'models' to see available models")
        
        # Show output settings
        auto_save = self.orchestrator.config.get('output', {}).get('auto_save', False)
        output_dir = self.orchestrator.config.get('output', {}).get('directory', 'outputs')
        if auto_save:
            print(f"Auto-save enabled: outputs → {output_dir}/")
        else:
            print("Auto-save disabled")
        print("-" * 50)
        
        try:
            orchestrator_config = self.orchestrator.config['openrouter']
            print(f"Using OpenRouter with API key configured")
            print("Orchestrator initialized successfully!")
            print("Note: Make sure to set your OpenRouter API key in config.yaml")
            print("-" * 50)
        except Exception as e:
            print(f"Error initializing orchestrator: {e}")
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
                    print("\nAvailable Agent Models:")
                    for model in self.orchestrator.get_available_models():
                        current = " (current)" if model == self.orchestrator.agent_model else ""
                        print(f"  - {model}{current}")
                    continue
                
                if user_input.lower().startswith('switch '):
                    model_name = user_input[7:].strip()
                    try:
                        self.orchestrator.set_agent_model(model_name)
                        print(f"Agent model switched to: {model_name}")
                        # Update display name
                        self.model_display = f"KIMI-K2 HEAVY (Agents: {model_name.upper()})"
                    except ValueError as e:
                        print(f"Error: {e}")
                    continue
                
                if not user_input:
                    print("Please enter a question or command.")
                    continue
                
                print("\nOrchestrator: Starting multi-agent analysis...")
                print()
                
                # Run task with live progress
                result = self.run_task(user_input)
                
                if result is None:
                    print("Task failed. Please try again.")
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
                print("Please try again or type 'quit' to exit.")

def main():
    """Main entry point for the orchestrator CLI"""
    parser = argparse.ArgumentParser(description='Multi-Agent Orchestrator CLI')
    parser.add_argument('--agent-model', 
                       choices=['grok-4', 'kimi-k2', 'o3', 'claude-sonnet-4'],
                       help='Model to use for agents (orchestrator always uses kimi-k2)')
    parser.add_argument('--list-models', action='store_true',
                       help='List available models and exit')
    parser.add_argument('--no-save', action='store_true',
                       help='Disable auto-save to markdown file')
    parser.add_argument('--output-dir', default='outputs',
                       help='Directory to save output files (default: outputs)')
    
    args = parser.parse_args()
    
    # Check required environment variables
    if not check_required_env_vars():
        return 1
    
    if args.list_models:
        from model_factory import ModelFactory
        factory = ModelFactory()
        print("Available models:")
        for model_key, config in factory.get_available_models().items():
            print(f"  {model_key}: {config['display_name']}")
            print(f"    Context: {config['context_window']} tokens")
            print(f"    Recommended for: {', '.join(config['recommended_for'])}")
            print()
        return
    
    cli = OrchestratorCLI(agent_model=args.agent_model, no_save=args.no_save, output_dir=args.output_dir)
    cli.interactive_mode()

if __name__ == "__main__":
    main()