#!/usr/bin/env python3
"""
Test script to verify all model integrations work correctly
"""

import sys
import time
from model_factory import ModelFactory, ModelAwareAgent
from orchestrator import TaskOrchestrator
from config_utils import check_required_env_vars

def test_model_factory():
    """Test the model factory and available models"""
    print("=== Testing Model Factory ===")
    
    try:
        factory = ModelFactory()
        models = factory.get_available_models()
        
        print(f"Available models: {list(models.keys())}")
        
        for model_key, config in models.items():
            print(f"\n{model_key}:")
            print(f"  Display Name: {config['display_name']}")
            print(f"  Provider: {config['provider']}")
            print(f"  Model Name: {config['model_name']}")
            print(f"  Context Window: {config['context_window']:,} tokens")
            print(f"  Supports Tools: {config['supports_tools']}")
            print(f"  Recommended For: {', '.join(config['recommended_for'])}")
        
        print("\n✅ Model Factory test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Model Factory test failed: {e}")
        return False

def test_model_provider(model_key):
    """Test a specific model provider"""
    print(f"\n=== Testing {model_key} Provider ===")
    
    try:
        factory = ModelFactory()
        provider = factory.create_provider(model_key)
        
        print(f"Provider created for {model_key}")
        print(f"Model name: {provider.get_model_name()}")
        
        # Test a simple API call
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello from " + model_key + "!' and nothing else."}
        ]
        
        print("Making test API call...")
        response = provider.call_llm(messages)
        
        if response and response.choices:
            content = response.choices[0].message.content
            print(f"Response: {content}")
            print(f"✅ {model_key} provider test passed!")
            return True
        else:
            print(f"❌ {model_key} provider test failed: No response")
            return False
            
    except Exception as e:
        print(f"❌ {model_key} provider test failed: {e}")
        return False

def test_model_aware_agent(model_key):
    """Test ModelAwareAgent with a specific model"""
    print(f"\n=== Testing ModelAwareAgent with {model_key} ===")
    
    try:
        agent = ModelAwareAgent(model_key, silent=True)
        
        print(f"Agent created with model: {model_key}")
        
        # Test agent run
        test_input = "What is 2+2? Just answer with the number."
        print(f"Testing with input: {test_input}")
        
        start_time = time.time()
        response = agent.run(test_input)
        end_time = time.time()
        
        print(f"Response: {response}")
        print(f"Time taken: {end_time - start_time:.2f}s")
        print(f"✅ ModelAwareAgent with {model_key} test passed!")
        return True
        
    except Exception as e:
        print(f"❌ ModelAwareAgent with {model_key} test failed: {e}")
        return False

def test_orchestrator():
    """Test orchestrator with different agent models"""
    print(f"\n=== Testing Orchestrator ===")
    
    try:
        # Test with grok-4 agents
        orchestrator = TaskOrchestrator(silent=True, agent_model="grok-4")
        
        config = orchestrator.get_current_config()
        print(f"Orchestrator model: {config['orchestrator_model']}")
        print(f"Agent model: {config['agent_model']}")
        
        print("Testing task decomposition...")
        subtasks = orchestrator.decompose_task("What is artificial intelligence?", 2)
        print(f"Generated subtasks: {subtasks}")
        
        if len(subtasks) == 2:
            print("✅ Orchestrator test passed!")
            return True
        else:
            print("❌ Orchestrator test failed: Wrong number of subtasks")
            return False
            
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting Model Integration Tests...")
    print("=" * 60)
    
    # Check required environment variables
    if not check_required_env_vars():
        return 1
    
    results = []
    
    # Test model factory
    results.append(test_model_factory())
    
    # Test each model provider
    models_to_test = ["kimi-k2", "grok-4", "o3", "claude-sonnet-4"]
    
    for model in models_to_test:
        results.append(test_model_provider(model))
    
    # Test ModelAwareAgent with each model
    for model in models_to_test:
        results.append(test_model_aware_agent(model))
    
    # Test orchestrator
    results.append(test_orchestrator())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())