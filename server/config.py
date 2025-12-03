"""Configuration management for MCP server."""

import os

from dotenv import load_dotenv

# Load .env file
load_dotenv()


class MCPConfig:
    """MCP server configuration."""

    def __init__(self):
        # Auth0 Configuration
        self.auth0_domain = os.getenv("AUTH0_DOMAIN", "")
        self.auth0_audience = os.getenv("AUTH0_AUDIENCE", "")
        # Try M2M client credentials first, then fall back to regular
        self.auth0_client_id = os.getenv("SUBCONSCIOUSAI_M2M_CLIENT_ID") or os.getenv("AUTH0_CLIENT_ID", "")
        self.auth0_client_secret = os.getenv("SUBCONSCIOUSAI_M2M_CLIENT_SECRET") or os.getenv("AUTH0_CLIENT_SECRET", "")
        # Direct JWT token (optional)
        self.auth0_jwt_token = os.getenv("AUTH0_JWT_TOKEN")

        # API Configuration
        self.api_base_url = os.getenv("API_BASE_URL", "https://api.subconscious.ai")

        # Server Configuration
        self.server_name = "subconscious-ai"
        self.server_version = "1.0.0"

        # Timeout Configuration
        self.request_timeout = 300
        self.max_retries = 3
        self.retry_delay = 1.0


# Global configuration instance
config = MCPConfig()


def get_auth_token() -> str:
    """Get Auth0 JWT token from environment."""
    if not config.auth0_jwt_token:
        raise ValueError(
            "AUTH0_JWT_TOKEN required. Get your token from the browser after logging into holodeck."
        )
    return config.auth0_jwt_token
