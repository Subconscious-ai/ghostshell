# Contributing to Subconscious AI MCP Server

Thank you for your interest in contributing to the Subconscious AI MCP Server! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- A Subconscious AI account (for testing)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/subconscious-ai-mcp.git
   cd subconscious-ai-mcp
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   export AUTH0_JWT_TOKEN="your_test_token"
   export API_BASE_URL="https://api.subconscious.ai"
   ```

## 📋 Development Workflow

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_handlers.py -v

# Run with coverage
pytest tests/ -v --cov=server --cov-report=html
```

### Code Quality

We use `ruff` for linting and `mypy` for type checking:

```bash
# Run linting
ruff check server/ api/

# Auto-fix linting issues
ruff check server/ api/ --fix

# Run type checking
mypy server/ api/
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Write docstrings for public functions and classes
- Keep functions focused and single-purpose

## 🔧 Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-new-tool` - New features
- `fix/handle-timeout-error` - Bug fixes
- `docs/update-readme` - Documentation changes
- `refactor/simplify-handlers` - Code refactoring

### Commit Messages

Write clear, concise commit messages:

```
Add retry logic for transient API errors

- Implement exponential backoff with jitter
- Add configurable max retries
- Handle network timeouts gracefully
```

### Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** with tests
3. **Ensure all tests pass** (`pytest tests/ -v`)
4. **Ensure code quality** (`ruff check server/ api/`)
5. **Update documentation** if needed
6. **Submit a pull request** with a clear description

## 🏗️ Project Architecture

### Directory Structure

```
server/
├── main.py           # Entry point for stdio transport
├── config.py         # Configuration management
├── utils/
│   └── api_client.py # HTTP client wrapper
└── tools/
    ├── __init__.py   # Tool exports
    ├── ideation.py   # Causality & attribute tools
    ├── experiments.py # Experiment tools
    ├── runs.py       # Run management tools
    ├── analytics.py  # Analytics tools
    └── _core/
        ├── base.py       # Base types
        ├── exceptions.py # Exception hierarchy
        ├── handlers.py   # Tool handlers
        └── retry.py      # Retry logic
```

### Adding a New Tool

1. **Define the tool schema** in the appropriate file (`ideation.py`, `experiments.py`, etc.):

   ```python
   MY_NEW_TOOL = Tool(
       name="my_new_tool",
       description="Description of what the tool does",
       inputSchema={
           "type": "object",
           "properties": {
               "param1": {
                   "type": "string",
                   "description": "Description of param1",
               },
           },
           "required": ["param1"],
       },
   )
   ```

2. **Implement the handler** in `_core/handlers.py`:

   ```python
   async def my_new_tool(
       args: Dict[str, Any], token_provider: TokenProvider
   ) -> ToolResult:
       """Handle my_new_tool requests."""
       try:
           response = await _api_request(
               "POST",
               "/api/v1/endpoint",
               token_provider,
               {"param1": args["param1"]},
           )
           return ToolResult(
               success=True,
               data=response,
               message="Success message",
           )
       except AuthenticationError:
           return ToolResult(success=False, error="Authentication failed")
       except Exception as e:
           return ToolResult(success=False, error=str(e))
   ```

3. **Export the tool** in `tools/__init__.py`

4. **Register in main.py** and **api/index.py**

5. **Add tests** in `tests/test_handlers.py`

### Error Handling

Use the custom exception hierarchy:

```python
from server.tools._core.exceptions import (
    AuthenticationError,  # 401 errors
    ValidationError,      # 400/422 errors
    NotFoundError,        # 404 errors
    RateLimitError,       # 429 errors
    ServerError,          # 500+ errors
    NetworkError,         # Connection/timeout errors
)
```

## 🧪 Testing Guidelines

### Test Structure

```python
class TestMyNewTool:
    """Tests for my_new_tool handler."""

    @pytest.mark.asyncio
    async def test_successful_call(self, mock_httpx):
        """Test successful tool execution."""
        mock_httpx.post.return_value = MockResponse(200, {"result": "success"})
        
        result = await my_new_tool(
            {"param1": "value"},
            lambda: "test_token"
        )
        
        assert result.success is True
        assert result.data["result"] == "success"

    @pytest.mark.asyncio
    async def test_handles_auth_error(self, mock_httpx):
        """Test authentication error handling."""
        mock_httpx.post.return_value = MockResponse(401, {"error": "Unauthorized"})
        
        result = await my_new_tool(
            {"param1": "value"},
            lambda: "invalid_token"
        )
        
        assert result.success is False
        assert "Authentication" in result.error
```

### Test Coverage

Aim for high test coverage on:
- Happy path scenarios
- Error handling (auth, validation, network)
- Edge cases (empty inputs, missing fields)

## 📚 Documentation

When adding new features:
- Update the README.md with new tools or endpoints
- Add inline documentation (docstrings)
- Update examples if applicable

## 🤝 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## ❓ Questions?

- Open an issue for bugs or feature requests
- Join our [Discord](https://discord.gg/3bgj4ZhABz) for discussions
- Email: nihar@subconscious.ai

---

Thank you for contributing! 🎉

