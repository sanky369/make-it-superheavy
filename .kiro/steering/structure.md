# Project Structure & Organization

## Root Directory Layout

```
make-it-superheavy/
├── main.py                    # Single agent CLI entry point
├── make_it_heavy.py          # Multi-agent orchestrator CLI
├── agent.py                  # Legacy agent implementation
├── orchestrator.py           # Multi-agent orchestration logic
├── model_factory.py          # Multi-model abstraction layer
├── config_utils.py           # Configuration utilities
├── setup.py                  # Setup and validation script
├── test_models.py            # Model testing suite
├── example_output.py         # Output functionality examples
├── config.yaml               # Main configuration file
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── .env                     # Environment variables (gitignored)
├── outputs/                 # Auto-saved output files
└── tools/                   # Plugin-based tool system
```

## Core Module Responsibilities

### Entry Points

- **main.py**: Single agent mode with model selection
- **make_it_heavy.py**: Multi-agent orchestration with progress visualization
- **setup.py**: Environment setup and validation

### Core Logic

- **agent.py**: Legacy OpenRouterAgent class (single model)
- **orchestrator.py**: TaskOrchestrator for parallel agent coordination
- **model_factory.py**: ModelFactory and ModelAwareAgent for multi-model support
- **config_utils.py**: YAML loading with environment variable substitution

## Tools Directory Structure

```
tools/
├── __init__.py              # Auto-discovery system
├── base_tool.py            # Abstract base class for all tools
├── search_tool.py          # Web search with DuckDuckGo
├── calculator_tool.py      # Safe mathematical calculations
├── read_file_tool.py       # File reading operations
├── write_file_tool.py      # File writing operations
├── write_output_tool.py    # Markdown output generation
└── task_done_tool.py       # Task completion signaling
```

## Tool System Conventions

- All tools inherit from `BaseTool` abstract base class
- Tools are auto-discovered by scanning the `tools/` directory
- Each tool implements: `name`, `description`, `parameters`, `execute()`
- Tools use OpenRouter function calling schema format
- New tools are added by dropping Python files in `tools/` directory

## Configuration Structure

### config.yaml Organization

```yaml
openrouter: # API configuration
models: # Multi-model settings
  orchestrator: # Fixed as kimi-k2
  default_agent: # Default agent model
  available_agents: # List of available models
agent: # Agent behavior settings
orchestrator: # Multi-agent coordination settings
search: # Search tool configuration
output: # Auto-save settings
```

### Environment Variables

- **OPENROUTER_API_KEY**: Required API key for OpenRouter
- Loaded via python-dotenv from `.env` file
- Substituted in config.yaml using `${VAR_NAME}` syntax

## Output Management

- **outputs/**: Directory for auto-saved markdown files
- **Naming convention**: `YYYYMMDD_HHMMSS_query_summary.md`
- **Configurable**: Directory and auto-save behavior via config.yaml
- **Tool-driven**: Uses `write_output_tool.py` for consistent formatting

## Code Organization Patterns

- **Single responsibility**: Each module has a clear, focused purpose
- **Plugin architecture**: Tools are dynamically discovered and loaded
- **Configuration-driven**: Behavior controlled via YAML configuration
- **Error handling**: Graceful fallbacks and user-friendly error messages
- **CLI-first**: Both single and multi-agent modes have interactive CLIs
