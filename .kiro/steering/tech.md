# Technology Stack & Build System

## Core Technologies

- **Python 3.8+**: Primary language
- **OpenRouter API**: Multi-model AI provider (Kimi K2, Grok-4, OpenAI o3, Claude Sonnet 4)
- **uv**: Recommended Python package manager for fast dependency management
- **YAML**: Configuration management with environment variable substitution
- **Threading**: Parallel agent execution using ThreadPoolExecutor

## Key Dependencies

```
openai          # OpenRouter API client
requests        # HTTP requests for web scraping
beautifulsoup4  # HTML parsing for search results
pyyaml          # YAML configuration parsing
ddgs            # DuckDuckGo search integration
python-dotenv   # Environment variable management
```

## Architecture Patterns

- **Factory Pattern**: ModelFactory for multi-provider AI support
- **Plugin Architecture**: Auto-discovery tool system in `tools/` directory
- **Abstract Base Classes**: BaseTool for consistent tool interfaces
- **Configuration-driven**: YAML-based configuration with env var substitution
- **Orchestrator Pattern**: TaskOrchestrator for multi-agent coordination

## Common Commands

### Development Setup

```bash
# Clone and setup environment
git clone <repo>
cd make-it-superheavy
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Setup configuration
cp .env.example .env
# Edit .env with your OpenRouter API key
```

### Running the Application

```bash
# Single agent mode
uv run main.py --model grok-4
uv run main.py --list-models

# Multi-agent orchestration
uv run make_it_heavy.py --agent-model claude-sonnet-4
uv run make_it_heavy.py --no-save
uv run make_it_heavy.py --output-dir reports

# Setup and validation
python setup.py
```

### Testing

```bash
# Test model configurations
python test_models.py

# Validate environment
python -c "from config_utils import check_required_env_vars; check_required_env_vars()"
```

## Configuration Management

- **config.yaml**: Main configuration with model settings and prompts
- **.env**: Environment variables (API keys, sensitive data)
- **Environment variable substitution**: `${OPENROUTER_API_KEY}` pattern in YAML
- **Multi-model configuration**: Separate orchestrator and agent model settings
