# Subconscious AI MCP Toolkit

MCP (Model Context Protocol) server for the Subconscious AI API. Enables AI assistants like Claude and Cursor to run conjoint experiments programmatically.

## Features

- **Ideation Tools**: Validate research questions, generate experiment attributes
- **Experiment Management**: Create, monitor, and retrieve experiment results
- **Population Validation**: Validate target populations before running experiments
- **Analytics**: Access AMCE data and causal insights from completed experiments

## Installation

```bash
git clone https://github.com/Subconscious-ai/subconscious-ai-mcp.git
cd subconscious-ai-mcp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Get your JWT token:
   - Login to [Subconscious AI](https://app.subconscious.ai)
   - Open Settings -> Click Access token (After you subscribed to the plan)
   - Copy the `Authorization: Bearer <token>` value

3. Add your token to `.env`:
```
AUTH0_JWT_TOKEN=your_token_here
API_BASE_URL=https://api.dev.subconscious.ai
```

## Usage

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "subconscious-ai": {
      "command": "/path/to/venv/bin/python3",
      "args": ["/path/to/server/main.py"],
      "env": {
        "AUTH0_JWT_TOKEN": "your_token",
        "API_BASE_URL": "https://api.dev.subconscious.ai"
      }
    }
  }
}
```

### Cursor IDE

Add to `~/.cursor/mcp.json` (same format as Claude).

### Test Locally

```bash
source venv/bin/activate
python3 server/main.py
```

## Available Tools

| Tool | Description |
|------|-------------|
| `check_causality` | Validate research question is causal |
| `generate_attributes_levels` | Generate experiment attributes/levels |
| `create_experiment` | Create and run an experiment |
| `get_experiment_status` | Check experiment progress |
| `get_experiment_results` | Get experiment results |
| `list_experiments` | List all experiments |
| `validate_population` | Validate target population |
| `get_amce_data` | Get AMCE analytics data |
| `get_causal_insights` | Get causal insights |

## Experiment Workflow

```
1. check_causality("What factors influence EV purchases?")
2. generate_attributes_levels("What factors influence EV purchases?")
3. create_experiment("What factors influence EV purchases?")
4. get_experiment_status(run_id)
5. get_experiment_results(run_id)
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint
ruff check server/

# Type check
mypy server/
```

## Project Structure

```
subconscious-ai-mcp-toolkit/
├── server/
│   ├── main.py              # MCP server entry point
│   ├── config.py            # Configuration
│   ├── tools/               # MCP tool definitions
│   │   ├── ideation.py      # Causality, attributes
│   │   ├── experiments.py   # Experiment management
│   │   ├── population.py    # Population validation
│   │   └── analytics.py     # AMCE and insights
│   └── utils/
│       └── api_client.py    # HTTP client
├── tests/                   # Unit tests
├── examples/                # Config examples
├── .github/workflows/       # CI/CD
├── pyproject.toml           # Project config
└── requirements.txt         # Dependencies
```

## License

MIT License - see LICENSE file for details.
