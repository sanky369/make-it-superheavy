# Multi-Model Support Guide

This guide explains how to use the expanded multi-model support in the Make It Heavy project.

## Overview

The project now supports multiple AI models with the following architecture:

- **Orchestrator**: Always uses **Kimi K2** (as per requirements)
- **Agents**: Can use **Grok-4**, **Kimi K2**, **OpenAI o3**, or **Claude Sonnet 4**

## Available Models

| Model               | Provider   | Context Window | Recommended For                   |
| ------------------- | ---------- | -------------- | --------------------------------- |
| **kimi-k2**         | OpenRouter | 128,000 tokens | Orchestration, Research, Analysis |
| **grok-4**          | OpenRouter | 256,000 tokens | Reasoning, Coding, Analysis       |
| **o3**              | OpenRouter | 200,000 tokens | Reasoning, Math, Coding           |
| **claude-sonnet-4** | OpenRouter | 200,000 tokens | Coding, Reasoning, Analysis       |

## Quick Start

### 1. Single Agent Mode

```bash
# Use default model (kimi-k2)
python main.py

# Use specific model
python main.py --model grok-4
python main.py --model o3
python main.py --model claude-sonnet-4

# List available models
python main.py --list-models
```

### 2. Multi-Agent Mode (Orchestrator)

```bash
# Use default agent model (kimi-k2) with kimi-k2 orchestrator
python make_it_heavy.py

# Use specific agent model
python make_it_heavy.py --agent-model o3
python make_it_heavy.py --agent-model grok-4
python make_it_heavy.py --agent-model claude-sonnet-4

# Control output saving
python make_it_heavy.py --no-save                    # Disable auto-save
python make_it_heavy.py --output-dir my_reports      # Custom output directory

# List available models
python make_it_heavy.py --list-models
```

## Interactive Commands

### Single Agent Mode

- `models` - List available models
- `switch <model>` - Switch to a different model
- `quit`, `exit`, `bye` - Exit the program

### Multi-Agent Mode

- `models` - List available agent models
- `switch <model>` - Switch agent model (orchestrator stays kimi-k2)
- `quit`, `exit`, `bye` - Exit the program

## Configuration

### Config File (config.yaml)

```yaml
# Model configurations for multi-model support
models:
  # Orchestrator model (fixed as kimi-k2 per requirements)
  orchestrator:
    model_key: "kimi-k2"

  # Default model for agents (can be overridden)
  default_agent:
    model_key: "kimi-k2"

  # Available models for agent selection
  available_agents:
    - "grok-4"
    - "kimi-k2"
    - "o3"
    - "claude-sonnet-4"

# Output settings
output:
  directory: "outputs"
  auto_save: true
```

### Programmatic Usage

```python
from model_factory import ModelFactory, ModelAwareAgent
from orchestrator import TaskOrchestrator

# Create model factory
factory = ModelFactory()

# List available models
models = factory.get_available_models()
print(models)

# Create agent with specific model
agent = ModelAwareAgent("grok-4")
response = agent.run("What is AI?")

# Create orchestrator with specific agent model
orchestrator = TaskOrchestrator(agent_model="grok-4")
result = orchestrator.orchestrate("Explain quantum computing")
```

## Model Factory API

### ModelFactory Class

```python
class ModelFactory:
    def create_provider(self, model_key: str) -> BaseModelProvider
    def get_available_models(self) -> Dict[str, Dict[str, Any]]
    def get_model_info(self, model_key: str) -> Dict[str, Any]
    def get_orchestrator_model(self) -> str
    def get_agent_models(self) -> List[str]
```

### ModelAwareAgent Class

```python
class ModelAwareAgent:
    def __init__(self, model_key: str, config_path: str = "config.yaml", silent: bool = False)
    def run(self, user_input: str) -> str
    def get_model_info(self) -> Dict[str, Any]
```

### TaskOrchestrator Class

```python
class TaskOrchestrator:
    def __init__(self, config_path="config.yaml", silent=False, agent_model=None)
    def orchestrate(self, user_input: str) -> str
    def get_available_models(self) -> List[str]
    def get_current_config(self) -> Dict[str, str]
    def set_agent_model(self, model_key: str)
```

## Output Management

### Auto-Save Feature

The orchestrator automatically saves results to markdown files in the `outputs/` directory:

- **Filename format**: `YYYYMMDD_HHMMSS_query_snippet.md`
- **Content includes**: Query, result, timestamp, and metadata
- **Directory**: Configurable via `--output-dir` or config file

### Output Commands

```bash
# Enable auto-save (default)
python make_it_heavy.py

# Disable auto-save
python make_it_heavy.py --no-save

# Custom output directory
python make_it_heavy.py --output-dir my_reports

# Combine options
python make_it_heavy.py --agent-model grok-4 --output-dir analysis_reports
```

### Manual Output Saving

```python
from tools.write_output_tool import WriteOutputTool

# Create write tool
write_tool = WriteOutputTool(config)

# Save output
result = write_tool.execute(
    query="Your query here",
    result="The orchestrator result",
    filename="custom_name"  # Optional
)

print(f"Saved to: {result['filepath']}")
```

### Output File Structure

```markdown
# Orchestrator Output

**Generated:** 2024-01-15 14:30:25  
**Query:** Complete Passive-Income Playbook

---

## Result

### Complete Passive-Income Playbook: 3 Core Systems to Earn $300/Month on Autopilot

Everything below is beginner-friendly, zero-to-low cost...

---

*Generated by Make It Heavy Multi-Agent Orchestrator*
```

## Testing

Run the comprehensive test suite:

```bash
python test_models.py
```

This will test:

- Model factory initialization
- Each model provider connection
- ModelAwareAgent with each model
- Orchestrator functionality

## Architecture Details

### Model Abstraction

The system uses a factory pattern with the following components:

1. **BaseModelProvider**: Abstract base class for all model providers
2. **OpenRouterProvider**: Concrete implementation for OpenRouter API
3. **ModelFactory**: Factory class to create appropriate providers
4. **ModelAwareAgent**: Enhanced agent class that uses model factory

### Request Flow

1. User makes request
2. ModelFactory creates appropriate provider
3. Provider handles API specifics
4. Agent uses provider to process request
5. Response is returned to user

### Error Handling

- Invalid model selection shows available options
- API failures are caught and reported
- Fallback mechanisms for orchestrator synthesis

## Best Practices

1. **Model Selection**:

   - Use **kimi-k2** for tasks requiring large context windows
   - Use **grok-4** for reasoning and analysis tasks
   - Use **o3** for mathematical and coding problems
   - Use **claude-sonnet-4** for complex coding tasks

2. **Performance**:

   - Orchestrator always uses kimi-k2 for consistency
   - Agent models can be switched based on task requirements
   - Context windows vary by model - choose appropriately

3. **API Keys**:
   - Ensure OpenRouter API key is set in config.yaml
   - All models use the same OpenRouter endpoint
   - Monitor usage for cost management

## Troubleshooting

### Common Issues

1. **Model not available**: Check if model is in available_agents list
2. **API key errors**: Verify OpenRouter API key in config.yaml
3. **Context window exceeded**: Switch to model with larger context window
4. **Rate limiting**: Implement delays between requests

### Debug Mode

Enable debug output by setting `silent=False`:

```python
agent = ModelAwareAgent("grok-4", silent=False)
orchestrator = TaskOrchestrator(silent=False)
```

## Migration Guide

### From Single Model to Multi-Model

1. Update imports:

```python
# Old
from agent import OpenRouterAgent

# New
from model_factory import ModelAwareAgent
```

2. Update agent creation:

```python
# Old
agent = OpenRouterAgent()

# New
agent = ModelAwareAgent("kimi-k2")
```

3. Update orchestrator:

```python
# Old
orchestrator = TaskOrchestrator()

# New
orchestrator = TaskOrchestrator(agent_model="kimi-k2")
```

## Future Enhancements

Planned features:

- Support for additional model providers
- Model performance benchmarking
- Automatic model selection based on task type
- Cost optimization features
- Model usage analytics
