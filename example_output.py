#!/usr/bin/env python3
"""
Example showing how to use the output functionality
"""

from orchestrator import TaskOrchestrator
from tools.write_output_tool import WriteOutputTool

def main():
    print("=== Output Functionality Example ===")
    
    # Example 1: Manual output saving
    print("\n1. Manual Output Saving:")
    
    # Create write tool
    import yaml
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    write_tool = WriteOutputTool(config)
    
    # Save example output
    result = write_tool.execute(
        query="What is artificial intelligence?",
        result="Artificial intelligence (AI) is a branch of computer science that aims to create intelligent machines...",
        filename="ai_explanation"
    )
    
    if result['success']:
        print(f"✅ Saved to: {result['filepath']}")
    else:
        print(f"❌ Error: {result['error']}")
    
    # Example 2: Auto-save with orchestrator
    print("\n2. Auto-save with Orchestrator:")
    
    # Create orchestrator with auto-save enabled
    orchestrator = TaskOrchestrator(silent=True)
    orchestrator.config['output']['auto_save'] = True
    orchestrator.config['output']['directory'] = 'example_outputs'
    
    print("Running orchestrator with auto-save enabled...")
    print("(This would save output automatically)")
    
    # Example 3: Different output directories
    print("\n3. Custom Output Directories:")
    
    # Save to different directories
    directories = ['reports', 'research', 'analysis']
    
    for i, directory in enumerate(directories):
        write_tool.config['output']['directory'] = directory
        result = write_tool.execute(
            query=f"Example query {i+1}",
            result=f"Example result for query {i+1}",
            filename=f"example_{i+1}"
        )
        
        if result['success']:
            print(f"✅ Saved to: {result['filepath']}")
    
    print("\n=== Example Complete ===")

if __name__ == "__main__":
    main()