# Subconscious AI MCP Server

[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

Run AI-powered conjoint experiments from Claude, Cursor, or any MCP-compatible client. Understand **why** people make decisions using causal inference and synthetic populations.

## ✨ Features

- **🧠 Causal Research** - Validate research questions and generate statistically valid experiments
- **👥 Synthetic Populations** - AI personas based on US Census microdata (IPUMS) for representative sampling
- **📊 Conjoint Analysis** - AMCE (Average Marginal Component Effects) for measuring attribute importance
- **🤖 MCP Protocol** - Works with Claude Desktop, Cursor, and any MCP-compatible AI assistant
- **🌐 REST API** - Direct HTTP access for integrations (n8n, Zapier, custom apps)
- **⚡ Real-time Updates** - Server-Sent Events (SSE) for live experiment progress

## 🚀 Quick Start

### Option 1: Use Hosted Server (Recommended)

No setup required! Add to your MCP client configuration:

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

> 🔑 Get your token at [app.subconscious.ai](https://app.subconscious.ai) → Settings → Access Token

### Option 2: Run Locally

**Prerequisites:**
- Python 3.11+
- A Subconscious AI account and Access token

```bash
# Clone the repository
git clone https://github.com/Subconscious-ai/subconscious-ai-mcp.git
cd subconscious-ai-mcp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export AUTH0_JWT_TOKEN="your_token_here"
export API_BASE_URL="https://api.subconscious.ai"
```

Add to your MCP config:
```json
{
  "mcpServers": {
    "subconscious-ai": {
      "command": "/absolute/path/to/venv/bin/python3",
      "args": ["/absolute/path/to/server/main.py"],
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
| `check_causality` | Validate that a research question is causal |
| `generate_attributes_levels` | Generate experiment attributes and levels using AI |
| `validate_population` | Validate target population demographics |
| `get_population_stats` | Get population statistics for a country |
| `create_experiment` | Create and run a conjoint experiment |
| `get_experiment_status` | Check experiment progress |
| `list_experiments` | List all your experiments |
| `get_experiment_results` | Get detailed experiment results |
| `get_run_details` | Get detailed run information |
| `get_run_artifacts` | Get run artifacts and files |
| `update_run_config` | Update run configuration |
| `generate_personas` | Generate AI personas for an experiment |
| `get_experiment_personas` | Get personas for an experiment |
| `get_amce_data` | Get AMCE analytics data |
| `get_causal_insights` | Get AI-generated causal insights |

## 🔬 Example Workflow

```
You: "Check if this is a causal question: What factors influence people's decision to buy electric vehicles?"

AI: ✅ This is a causal question. Let me generate attributes for this study.

You: "Generate attributes for an EV preference study"

AI: Generated 5 attributes with 4 levels each:
    - Price: $25,000 / $35,000 / $45,000 / $55,000
    - Range: 200 miles / 300 miles / 400 miles / 500 miles
    ...

You: "Create an experiment about EV purchasing decisions"

AI: 🚀 Experiment created! Run ID: abc-123-xyz
    Status: Processing (surveying 500 synthetic respondents)

You: "Check the status of experiment abc-123-xyz"

AI: ✅ Experiment completed!
    - 500 respondents surveyed
    - Ready for analysis

You: "Get causal insights from this experiment"

AI: 📊 Key Findings:
    - Price has the strongest effect (-0.32 AMCE)
    - 400+ mile range increases preference by 28%
    - Brand reputation matters more than charging speed
```

## 🌐 REST API

Call tools directly via HTTP for integrations:

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
  -d '{"why_prompt": "What factors influence EV purchases?", "confidence_level": "Reasonable"}'

# Get experiment results
curl -X POST https://ghostshell-runi.vercel.app/api/call/get_experiment_results \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"run_id": "your-run-id"}'
```

## 📡 API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | No | Server info and available tools |
| `/api/health` | GET | No | Health check |
| `/api/tools` | GET | No | List all tools with schemas |
| `/api/sse` | GET | Yes | MCP SSE connection (token in query param) |
| `/api/call/{tool}` | POST | Yes | Call a tool directly |

## 🏗️ Self-Hosting on Vercel

Deploy your own instance for your organization:

```bash
# Install Vercel CLI
npm i -g vercel

# Clone and deploy
git clone https://github.com/Subconscious-ai/subconscious-ai-mcp.git
cd subconscious-ai-mcp
vercel --prod
```

Configure environment variables in Vercel dashboard:
- `API_BASE_URL`: `https://api.subconscious.ai` (or your backend URL)

> ⚠️ Users must provide their own tokens - the server proxies requests to the Subconscious AI backend.

## 💡 Feature Requests & Support

Have a feature request or need help? Email us at **nihar@subconscious.ai**

## 📚 Resources

- [Subconscious AI Platform](https://app.subconscious.ai) - Create experiments via UI
- [API Documentation](https://subconscious.docs.buildwithfern.com/wiki/get-started/welcome-to-subconscious-ai) — Full API reference
- [MCP Protocol](https://modelcontextprotocol.io) - Model Context Protocol specification
- [Conjoint Analysis](https://en.wikipedia.org/wiki/Conjoint_analysis) - Learn about the methodology
- [![Glama MCP Server](https://glama.ai/mcp/servers/@NehharShah/mcp-subconscios/badge)](https://glama.ai/mcp/servers/@NehharShah/mcp-subconscios)

## 📄 License

This software requires an active [Subconscious AI subscription](https://app.subconscious.ai/). See the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ by <a href="https://subconscious.ai">Subconscious AI</a>
</p>
