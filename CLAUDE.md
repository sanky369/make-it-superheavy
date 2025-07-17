# CLAUDE.md

## Project Overview
**Make It SuperHeavy** is a Python multi-agent AI framework that emulates "Grok heavy" functionality using OpenRouter's API. It orchestrates multiple AI agents to provide comprehensive, multi-perspective analysis on user queries.

## Key Components

### Core Files
- `main.py` - Single agent CLI with multi-model support
- `make_it_heavy.py` - Multi-agent orchestrator CLI 
- `orchestrator.py` - Core orchestration logic for managing parallel agents
- `agent.py` - Individual agent implementation
- `model_factory.py` - Multi-model abstraction layer
- `config.yaml` - Configuration file with API keys and model settings

### Tools System (`tools/`)
Auto-discovered tools that agents can use:
- `search_tool.py` - Web search via DuckDuckGo
- `calculator_tool.py` - Mathematical calculations
- `read_file_tool.py` - File reading operations
- `write_file_tool.py` - File writing operations
- `write_output_tool.py` - Auto-save results to markdown
- `task_done_tool.py` - Task completion signaling

## Available Models
- **kimi-k2** (default orchestrator) - 128k context, research/analysis
- **grok-4** - 256k context, reasoning/coding
- **o3** - 200k context, math/reasoning
- **claude-sonnet-4** - 200k context, coding/analysis

## How It Works

### Single Agent Mode (`main.py`)
1. User provides query
2. Single agent processes with full tool access
3. Agent works iteratively until task complete
4. Returns comprehensive response

### Multi-Agent Mode (`make_it_heavy.py`)
1. **Question Generation** - Kimi K2 creates 4 specialized research questions
2. **Parallel Processing** - 4 agents run simultaneously using chosen model
3. **Live Progress** - Visual progress bars show agent status
4. **Synthesis** - Kimi K2 combines all perspectives into final answer
5. **Auto-save** - Results saved to `outputs/` as markdown files

## Configuration
- OpenRouter API key required (set in `config.yaml` or `.env`)
- Orchestrator always uses `kimi-k2` model
- Agent model can be configured via CLI or config
- Auto-save enabled by default to `outputs/` directory

## Usage Patterns
```bash
# Single agent with specific model
uv run main.py --model grok-4

# Multi-agent with specific agent model
uv run make_it_heavy.py --agent-model claude-sonnet-4

# List available models
uv run main.py --list-models
```

## Development Notes
- Uses `uv` for Python package management
- All tools auto-discovered from `tools/` directory
- Thread-safe progress tracking for parallel execution
- Graceful error handling and fallback mechanisms
- Comprehensive logging and visual feedback

## Testing & Validation
- Check `test_models.py` for model validation
- Verify API key setup before running
- Monitor output files in `outputs/` directory
- Use `--no-save` flag to disable auto-save during testing