# Subconscious AI MCP Server

Run AI-powered conjoint experiments from Claude, Cursor, or any MCP-compatible client.

## 🚀 Quick Start

### Option 1: Use Hosted Server (Recommended)

Add to your MCP client configuration:

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "subconscious-ai": {
      "url": "https://ghostshell-runi.vercel.app/api/sse?token=YOUR_TOKEN"
    }
  }
}
```

**Cursor** (`~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "subconscious-ai": {
      "url": "https://ghostshell-runi.vercel.app/api/sse?token=YOUR_TOKEN"
    }
  }
}
```

Get your token at [app.subconscious.ai](https://app.subconscious.ai) → Settings → Access Token

### Option 2: Run Locally

```bash
git clone https://github.com/Subconscious-ai/subconscious-ai-mcp.git
cd subconscious-ai-mcp
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Add to your MCP config:
```json
{
  "mcpServers": {
    "subconscious-ai": {
      "command": "/path/to/venv/bin/python3",
      "args": ["/path/to/server/main.py"],
      "env": {
        "AUTH0_JWT_TOKEN": "your_token",
        "API_BASE_URL": "https://api.subconscious.ai"
      }
    }
  }
}
```

## 📋 Available Tools

| Tool | Description |
|------|-------------|
| `check_causality` | Validate research question is causal |
| `generate_attributes_levels` | Generate experiment attributes/levels |
| `create_experiment` | Create and run a conjoint experiment |
| `get_experiment_status` | Check experiment progress |
| `list_experiments` | List all your experiments |
| `get_experiment_results` | Get detailed results |
| `get_amce_data` | Get AMCE analytics data |
| `get_causal_insights` | Get AI-generated insights |

## 🔬 Experiment Workflow

```
1. "Check if this is causal: What factors influence EV purchases?"
2. "Generate attributes for an EV preference study"
3. "Create an experiment about EV purchasing decisions"
4. "Check the status of experiment <run_id>"
5. "Get causal insights from experiment <run_id>"
```

## 🌐 REST API

You can also call tools directly via HTTP:

```bash
# List experiments
curl -X POST https://ghostshell-runi.vercel.app/api/call/list_experiments \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"limit": 5}'

# Check causality
curl -X POST https://ghostshell-runi.vercel.app/api/call/check_causality \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"why_prompt": "What factors influence EV purchases?"}'

# Create experiment
curl -X POST https://ghostshell-runi.vercel.app/api/call/create_experiment \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"why_prompt": "What factors influence EV purchases?"}'
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Server info |
| `/api/health` | GET | Health check |
| `/api/tools` | GET | List all tools |
| `/api/sse` | GET | MCP SSE connection |
| `/api/call/{tool}` | POST | Call a tool (REST) |

## 🏗️ Self-Hosting

Deploy your own instance:

```bash
npm i -g vercel
cd subconscious-ai-mcp-toolkit
vercel --prod
```

## 📁 Project Structure

```
subconscious-ai-mcp-toolkit/
├── api/
│   └── index.py          # Vercel serverless (SSE + REST)
├── server/
│   ├── main.py           # Local MCP server (stdio)
│   ├── config.py         # Configuration
│   └── tools/            # Tool implementations
├── examples/
│   └── claude/config.json
├── vercel.json
└── requirements.txt
```

## 📄 License

MIT License
