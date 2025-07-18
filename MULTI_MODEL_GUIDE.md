# Multi-Model Support Guide

This guide explains how to use the expanded multi-model support in the Make It Heavy project.

## Overview

The project now supports multiple AI models with the following architecture:

- **Orchestrator**: Choose from **Kimi K2** (128k context) or **GPT-4.1** (1M context) for question generation
- **Synthesis**: Always uses **Gemini 2.5 Pro** (1M context, 65k output for large-scale synthesis)
- **Agents**: Can use **Grok-4**, **Kimi K2**, **OpenAI o3**, **Claude Sonnet 4**, **Gemini 2.5 Pro**, or **GPT-4.1**

## Available Models

| Model               | Provider   | Context Window | Max Output | Recommended For                   |
| ------------------- | ---------- | -------------- | ---------- | --------------------------------- |
| **kimi-k2**         | OpenRouter | 128,000 tokens | ~8k tokens | Orchestration, Research, Analysis |
| **grok-4**          | OpenRouter | 256,000 tokens | ~8k tokens | Reasoning, Coding, Analysis       |
| **o3**              | OpenRouter | 200,000 tokens | ~8k tokens | Reasoning, Math, Coding           |
| **claude-sonnet-4** | OpenRouter | 200,000 tokens | ~8k tokens | Coding, Reasoning, Analysis       |
| **gemini-2.5-pro**  | OpenRouter | 1,048,576 tokens | 65k tokens | **Synthesis, Large Context Analysis** |
| **gpt-4.1**         | OpenRouter | 1,047,576 tokens | 32k tokens | **Orchestration, Reasoning, Instruction Following** |

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

- `models` - List available agent and orchestrator models
- `switch <model>` - Switch agent model
- `switch-orchestrator <model>` - Switch orchestrator model (choose between kimi-k2 and gpt-4.1)
- `quit`, `exit`, `bye` - Exit the program

### Orchestrator Model Selection

**Kimi K2** (Default)
- 128k context window
- Cost-effective for standard research
- Good for straightforward question generation

**GPT-4.1** (Advanced)
- 1M context window (8x larger)
- Superior instruction following (87.4% IFEval)
- Excellent for complex, multi-layered questions
- Better for nuanced research orchestration

**Example Usage:**
```bash
# Step 1: Start the program
uv run make_it_heavy.py

# Step 2: Use interactive commands inside the running program
> models
Available Agent Models:
  - grok-4
  - kimi-k2 (current)
  - o3
  - claude-sonnet-4
  - gemini-2.5-pro
  - gpt-4.1

Available Orchestrator Models:
  - kimi-k2 (current)
  - gpt-4.1

> switch-orchestrator gpt-4.1
Orchestrator model switched to: gpt-4.1

> switch grok-4
Agent model switched to: grok-4

> Your research question here...
```

## Configuration

### Config File (config.yaml)

```yaml
# Model configurations for multi-model support
models:
  # Orchestrator model (switchable between kimi-k2 and gpt-4.1)
  orchestrator:
    model_key: "kimi-k2"  # Options: "kimi-k2", "gpt-4.1"
    
  # Synthesis model (for combining agent results - large context window)
  synthesis:
    model_key: "gemini-2.5-pro"
    max_tokens: 65000  # Maximum output tokens for comprehensive synthesis

  # Default model for agents (can be overridden)
  default_agent:
    model_key: "kimi-k2"

  # Available models for agent selection
  available_agents:
    - "grok-4"
    - "kimi-k2"
    - "o3"
    - "claude-sonnet-4"
    - "gemini-2.5-pro"
    - "gpt-4.1"
    
  # Available orchestrator models
  available_orchestrators:
    - "kimi-k2"
    - "gpt-4.1"

# Output settings
output:
  directory: "outputs"
  auto_save: true
```

### Orchestrator Model Selection Guide

**When to Use Kimi K2:**
- Standard research questions
- Cost-conscious applications
- Straightforward question generation
- Quick iterations and testing
- Budget-friendly research projects

**When to Use GPT-4.1:**
- Complex, multi-layered research topics
- Questions requiring nuanced understanding
- Advanced reasoning and logic
- High-stakes research projects
- Superior instruction following needed
- Long-context question generation

**Performance Comparison:**

| Feature | Kimi K2 | GPT-4.1 |
|---------|---------|---------|
| Context Window | 128k | 1M (8x larger) |
| Instruction Following | Good | Superior (87.4% IFEval) |
| Question Quality | Standard | Advanced |
| Cost | Lower | Higher |
| Speed | Faster | Moderate |
| Reasoning | Good | Excellent |

**Example Scenarios:**

```bash
# First start the program: uv run make_it_heavy.py

# For standard research
> switch-orchestrator kimi-k2
Use for: "Best programming languages 2024", "Healthy meal plans", "Travel guides"

# For complex analysis
> switch-orchestrator gpt-4.1
Use for: "Multi-modal AI architecture analysis", "Quantum computing applications", "Complex business strategies"
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

## Advanced Synthesis Architecture

### Large Context Synthesis

The system now uses **Gemini 2.5 Pro** specifically for synthesis, providing:

- **1,048,576 token context window** - Can process massive agent outputs
- **65,536 token maximum output** - Generate comprehensive reports up to ~50 pages
- **Advanced reasoning** - Superior synthesis of complex multi-agent results
- **Cost optimization** - Only synthesis uses the large context model

### Synthesis Flow

1. **Question Generation**: Kimi K2 creates specialized questions
2. **Agent Processing**: Your chosen model processes individual questions
3. **Result Collection**: All agent outputs collected (up to 1M tokens total)
4. **Advanced Synthesis**: Gemini 2.5 Pro combines results into comprehensive report (up to 65k tokens)

### Configuration

```yaml
# config.yaml
models:
  synthesis:
    model_key: "gemini-2.5-pro"
    max_tokens: 65000  # Maximum output for synthesis
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

_Generated by Make It Heavy Multi-Agent Orchestrator_
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
