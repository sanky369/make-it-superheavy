"""
Model Factory for Multi-Provider AI Support

This module provides a unified interface for different AI model providers,
allowing the orchestrator to use kimi-k2 while agents can use different models.
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from openai import OpenAI
from config_utils import load_config


class BaseModelProvider(ABC):
    """Abstract base class for AI model providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the API client for this provider"""
        pass
    
    @abstractmethod
    def call_llm(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict]] = None, max_tokens: Optional[int] = None) -> Any:
        """Make API call to the model"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name for API calls"""
        pass


class OpenRouterProvider(BaseModelProvider):
    """OpenRouter provider for kimi-k2, grok-4, o3, and claude-sonnet-4"""
    
    def __init__(self, config: Dict[str, Any], model_name: str):
        self.model_name = model_name
        super().__init__(config)
    
    def _initialize_client(self):
        """Initialize OpenRouter client"""
        self.client = OpenAI(
            base_url=self.config['openrouter']['base_url'],
            api_key=self.config['openrouter']['api_key']
        )
    
    def call_llm(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict]] = None, max_tokens: Optional[int] = None) -> Any:
        """Make OpenRouter API call"""
        try:
            call_params = {
                "model": self.model_name,
                "messages": messages
            }
            
            if tools:
                call_params["tools"] = tools
                
            if max_tokens:
                call_params["max_tokens"] = max_tokens
            
            response = self.client.chat.completions.create(**call_params)
            return response
        except Exception as e:
            raise Exception(f"OpenRouter API call failed for {self.model_name}: {str(e)}")
    
    def get_model_name(self) -> str:
        return self.model_name


class ModelFactory:
    """Factory class to create appropriate model providers"""
    
    # Model configurations with provider mappings
    MODEL_CONFIGS = {
        "kimi-k2": {
            "provider": "openrouter",
            "model_name": "moonshotai/kimi-k2",
            "display_name": "Kimi K2",
            "context_window": 128000,
            "supports_tools": True,
            "recommended_for": ["orchestration", "research", "analysis"]
        },
        "grok-4": {
            "provider": "openrouter", 
            "model_name": "x-ai/grok-4",
            "display_name": "Grok 4",
            "context_window": 256000,
            "supports_tools": True,
            "recommended_for": ["reasoning", "coding", "analysis"]
        },
        "o3": {
            "provider": "openrouter",
            "model_name": "openai/o3",
            "display_name": "OpenAI o3",
            "context_window": 200000,
            "supports_tools": True,
            "recommended_for": ["reasoning", "math", "coding"]
        },
        "claude-sonnet-4": {
            "provider": "openrouter",
            "model_name": "anthropic/claude-sonnet-4",
            "display_name": "Claude Sonnet 4",
            "context_window": 200000,
            "supports_tools": True,
            "recommended_for": ["coding", "reasoning", "analysis"]
        },
        "gemini-2.5-pro": {
            "provider": "openrouter",
            "model_name": "google/gemini-2.5-pro",
            "display_name": "Gemini 2.5 Pro",
            "context_window": 1048576,
            "max_output": 65536,
            "supports_tools": False,
            "recommended_for": ["synthesis", "large_context", "analysis"]
        },
        "gpt-4.1": {
            "provider": "openrouter",
            "model_name": "openai/gpt-4.1",
            "display_name": "GPT-4.1",
            "context_window": 1047576,
            "max_output": 32768,
            "supports_tools": True,
            "recommended_for": ["orchestration", "reasoning", "instruction_following"]
        }
    }
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_config(config_path)
    
    def create_provider(self, model_key: str) -> BaseModelProvider:
        """Create a provider instance for the specified model"""
        if model_key not in self.MODEL_CONFIGS:
            raise ValueError(f"Unsupported model: {model_key}. Available models: {list(self.MODEL_CONFIGS.keys())}")
        
        model_config = self.MODEL_CONFIGS[model_key]
        provider_type = model_config["provider"]
        
        if provider_type == "openrouter":
            return OpenRouterProvider(self.config, model_config["model_name"])
        else:
            raise ValueError(f"Unsupported provider: {provider_type}")
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get all available models and their configurations"""
        return self.MODEL_CONFIGS
    
    def get_model_info(self, model_key: str) -> Dict[str, Any]:
        """Get detailed information about a specific model"""
        if model_key not in self.MODEL_CONFIGS:
            raise ValueError(f"Unknown model: {model_key}")
        return self.MODEL_CONFIGS[model_key]
    
    def get_orchestrator_model(self) -> str:
        """Get the recommended model for orchestration (kimi-k2 as per requirements)"""
        return "kimi-k2"
    
    def get_agent_models(self) -> List[str]:
        """Get available models for agents"""
        return ["grok-4", "kimi-k2", "o3", "claude-sonnet-4"]


class ModelAwareAgent:
    """Enhanced agent class that can use different models"""
    
    def __init__(self, model_key: str, config_path: str = "config.yaml", silent: bool = False):
        self.model_key = model_key
        self.silent = silent
        
        # Load configuration
        self.config = load_config(config_path)
        
        # Create model provider
        self.factory = ModelFactory(config_path)
        self.provider = self.factory.create_provider(model_key)
        
        # Import and initialize tools
        from tools import discover_tools
        self.discovered_tools = discover_tools(self.config, silent=self.silent)
        self.tools = [tool.to_openrouter_schema() for tool in self.discovered_tools.values()]
        self.tool_mapping = {name: tool.execute for name, tool in self.discovered_tools.items()}
    
    def call_llm(self, messages: List[Dict[str, Any]], max_tokens: Optional[int] = None) -> Any:
        """Make API call using the configured model provider"""
        return self.provider.call_llm(messages, self.tools, max_tokens)
    
    def handle_tool_call(self, tool_call):
        """Handle a tool call and return the result message"""
        try:
            # Extract tool name and arguments
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            # Call appropriate tool from tool_mapping
            if tool_name in self.tool_mapping:
                tool_result = self.tool_mapping[tool_name](**tool_args)
            else:
                tool_result = {"error": f"Unknown tool: {tool_name}"}
            
            # Return tool result message
            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": json.dumps(tool_result)
            }
        
        except Exception as e:
            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": json.dumps({"error": f"Tool execution failed: {str(e)}"})
            }
    
    def run(self, user_input: str) -> str:
        """Run the agent with user input and return FULL conversation content"""
        # Initialize messages with system prompt and user input
        messages = [
            {
                "role": "system",
                "content": self.config['system_prompt']
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
        
        # Track all assistant responses for full content capture
        full_response_content = []
        
        # Implement agentic loop
        max_iterations = self.config.get('agent', {}).get('max_iterations', 10)
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            if not self.silent:
                model_info = self.factory.get_model_info(self.model_key)
                print(f"🔄 Agent iteration {iteration}/{max_iterations} using {model_info['display_name']}")
            
            # Call LLM
            response = self.call_llm(messages)
            
            # Add the response to messages
            assistant_message = response.choices[0].message
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": assistant_message.tool_calls
            })
            
            # Capture assistant content for full response
            if assistant_message.content:
                full_response_content.append(assistant_message.content)
            
            # Check if there are tool calls
            if assistant_message.tool_calls:
                if not self.silent:
                    print(f"🔧 Agent making {len(assistant_message.tool_calls)} tool call(s)")
                # Handle each tool call
                task_completed = False
                for tool_call in assistant_message.tool_calls:
                    if not self.silent:
                        print(f"   📞 Calling tool: {tool_call.function.name}")
                    tool_result = self.handle_tool_call(tool_call)
                    messages.append(tool_result)
                    
                    # Check if this was the task completion tool
                    if tool_call.function.name == "mark_task_complete":
                        task_completed = True
                        if not self.silent:
                            print("✅ Task completion tool called - exiting loop")
                        # Return FULL conversation content, not just completion message
                        return "\n\n".join(full_response_content)
                
                # If task was completed, we already returned above
                if task_completed:
                    return "\n\n".join(full_response_content)
            else:
                if not self.silent:
                    print("💭 Agent responded without tool calls - continuing loop")
            
            # Continue the loop regardless of whether there were tool calls or not
        
        # If max iterations reached, return whatever content we gathered
        return "\n\n".join(full_response_content) if full_response_content else "Maximum iterations reached. The agent may be stuck in a loop."
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return self.factory.get_model_info(self.model_key)