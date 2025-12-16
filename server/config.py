"""Configuration management for MCP server."""

import logging
import os
from typing import List

from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("subconscious-ai")


class MCPConfig:
    """MCP server configuration."""

    access_token: str | None

    def __init__(self):
        # Auth0 Configuration
        self.auth0_domain: str = os.getenv("AUTH0_DOMAIN", "")
        self.auth0_audience: str = os.getenv("AUTH0_AUDIENCE", "")
        # Try M2M client credentials first, then fall back to regular
        self.auth0_client_id: str = (
            os.getenv("SUBCONSCIOUSAI_M2M_CLIENT_ID") or os.getenv("AUTH0_CLIENT_ID", "")
        )
        self.auth0_client_secret: str = (
            os.getenv("SUBCONSCIOUSAI_M2M_CLIENT_SECRET")
            or os.getenv("AUTH0_CLIENT_SECRET", "")
        )
        # Access token (try new name first, fall back to old for backward compat)
        self.access_token = os.getenv("SUBCONSCIOUS_ACCESS_TOKEN") or os.getenv(
            "AUTH0_JWT_TOKEN"
        )

        # API Configuration
        self.api_base_url = os.getenv("API_BASE_URL", "https://api.subconscious.ai")

        # Server Configuration
        self.server_name = "subconscious-ai"
        self.server_version = "1.0.0"

        # Timeout Configuration
        self.request_timeout = 300
        self.max_retries = 3
        self.retry_delay = 1.0

        # CORS Configuration
        # Note: Starlette CORSMiddleware doesn't support wildcards in origins list.
        # Use cors_origin_regex for pattern matching.
        cors_origins_env = os.getenv("CORS_ALLOWED_ORIGINS", "")
        cors_allow_all = os.getenv("CORS_ALLOW_ALL", "").lower() in ("true", "1", "yes")

        if cors_origins_env:
            self.cors_allowed_origins: List[str] = [
                origin.strip() for origin in cors_origins_env.split(",") if origin.strip()
            ]
            self.cors_origin_regex: str | None = None
        elif cors_allow_all:
            self.cors_allowed_origins = ["*"]
            self.cors_origin_regex = None
        else:
            # Default: explicit production origins + regex for dev/preview
            self.cors_allowed_origins = [
                "https://app.subconscious.ai",
                "https://holodeck.subconscious.ai",
                "https://ghostshell-runi.vercel.app",
            ]
            # Regex to match Vercel preview deployments and localhost
            self.cors_origin_regex = r"https://.*\.vercel\.app|http://localhost:\d+|http://127\.0\.0\.1:\d+"

        # Note: allow_credentials=True cannot be used with allow_origins=["*"] per CORS spec
        self.cors_allow_credentials = "*" not in self.cors_allowed_origins


# Global configuration instance
config = MCPConfig()


def get_auth_token() -> str:
    """Get access token from environment."""
    token: str | None = config.access_token
    if token is None:
        raise ValueError(
            "SUBCONSCIOUS_ACCESS_TOKEN required. Get your token from app.subconscious.ai → Settings → Access Token"
        )
    return token
