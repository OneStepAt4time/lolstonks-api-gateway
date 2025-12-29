"""
Constants for documentation verification tests.

Contains:
- Base URLs for production and development environments
- Complete list of all 27 documentation pages
- Metadata for all 19 Mermaid diagrams with selectors
- Test configuration and thresholds
"""

from typing import TypedDict


# ============================================================================
# Environment URLs
# ============================================================================

ENVIRONMENTS = {
    "production": "https://onestepat4time.github.io/lolstonks-api-gateway",
    "development": "https://onestepat4time.github.io/lolstonks-api-gateway/dev",
}


def get_base_url(env: str, override: str | None = None) -> str:
    """
    Get base URL for environment with optional override for local testing.

    Args:
        env: Environment name ("prod" or "dev")
        override: Optional URL override (e.g., "http://127.0.0.1:8000")

    Returns:
        Base URL string
    """
    if override:
        return override.rstrip("/")

    env_key = "production" if env == "prod" else "development"
    return ENVIRONMENTS[env_key]


# ============================================================================
# Documentation Pages (27 total)
# ============================================================================


def get_pages(base_url: str) -> dict[str, str]:
    """
    Generate complete list of documentation pages for an environment.

    Args:
        base_url: Base URL of the documentation site

    Returns:
        Dictionary mapping page name to full URL
    """
    return {
        # Home (1 page)
        "home": f"{base_url}/",
        # Getting Started (4 pages)
        "getting-started_installation": f"{base_url}/getting-started/installation/",
        "getting-started_quick-start": f"{base_url}/getting-started/quick-start/",
        "getting-started_configuration": f"{base_url}/getting-started/configuration/",
        "getting-started_deployment": f"{base_url}/getting-started/deployment/",
        # API Reference (8 pages)
        "api_openapi-spec": f"{base_url}/api/openapi-spec/",
        "api_overview": f"{base_url}/api/overview/",
        "api_providers": f"{base_url}/api/providers/",
        "api_riot-client": f"{base_url}/api/riot-client/",
        "api_models": f"{base_url}/api/models/",
        "api_routers": f"{base_url}/api/routers/",
        "api_cache": f"{base_url}/api/cache/",
        "api_security": f"{base_url}/api/security/",
        # Architecture (5 pages in navigation)
        "architecture_overview": f"{base_url}/architecture/overview/",
        "architecture_system-overview": f"{base_url}/architecture/system-overview/",
        "architecture_data-flow": f"{base_url}/architecture/data-flow/",
        "architecture_implementation-details": f"{base_url}/architecture/implementation-details/",
        "architecture_models": f"{base_url}/architecture/models/",
        # Operations (3 pages)
        "operations_monitoring": f"{base_url}/operations/monitoring/",
        "operations_troubleshooting": f"{base_url}/operations/troubleshooting/",
        "operations_security": f"{base_url}/operations/security/",
        # Development (6 pages)
        "development_contributing": f"{base_url}/development/contributing/",
        "development_changelog-guide": f"{base_url}/development/changelog-guide/",
        "development_versioning": f"{base_url}/development/versioning/",
        "development_releases": f"{base_url}/development/releases/",
        "development_testing": f"{base_url}/development/testing/",
        "development_documentation": f"{base_url}/development/documentation/",
    }


# Pages NOT in navigation but exist (for comprehensive testing)
def get_extra_pages(base_url: str) -> dict[str, str]:
    """
    Pages that exist but are not in the navigation menu.

    These may contain important diagrams and should be verified.
    """
    return {
        "architecture_routing": f"{base_url}/architecture/routing/",
        "architecture_rate-limiting": f"{base_url}/architecture/rate-limiting/",
        "architecture_caching": f"{base_url}/architecture/caching/",
        "architecture_providers": f"{base_url}/architecture/providers/",
        "architecture_production-deployment": f"{base_url}/architecture/production-deployment/",
    }


# ============================================================================
# Mermaid Diagrams Inventory (19 total)
# ============================================================================


class DiagramMetadata(TypedDict):
    """Metadata for a Mermaid diagram."""

    name: str
    file: str
    url: str
    selector: str
    diagram_type: str
    expected_nodes: list[str]
    description: str
    approx_line: int


def get_diagrams(base_url: str) -> list[DiagramMetadata]:
    """
    Complete inventory of all 19 Mermaid diagrams with metadata.

    Args:
        base_url: Base URL of the documentation site

    Returns:
        List of diagram metadata dictionaries
    """
    return [
        # architecture/overview.md - 5 diagrams
        {
            "name": "overview_01_client-gateway-layer",
            "file": "architecture/overview.md",
            "url": f"{base_url}/architecture/overview/",
            "selector": "div.mermaid:nth-of-type(1)",
            "diagram_type": "graph TB",
            "expected_nodes": ["Clients", "Gateway", "Rate Limiter", "Cache", "Routes", "Health"],
            "description": "Client and Gateway Layer architecture",
            "approx_line": 86,
        },
        {
            "name": "overview_02_gateway-provider-layer",
            "file": "architecture/overview.md",
            "url": f"{base_url}/architecture/overview/",
            "selector": "div.mermaid:nth-of-type(2)",
            "diagram_type": "graph TB",
            "expected_nodes": [
                "Gateway",
                "Registry",
                "Riot API",
                "Data Dragon",
                "Community Dragon",
            ],
            "description": "Gateway and Provider Layer architecture",
            "approx_line": 100,
        },
        {
            "name": "overview_03_provider-external",
            "file": "architecture/overview.md",
            "url": f"{base_url}/architecture/overview/",
            "selector": "div.mermaid:nth-of-type(3)",
            "diagram_type": "graph TB",
            "expected_nodes": ["Providers", "Riot API", "CDN"],
            "description": "Provider and External Data Sources",
            "approx_line": 115,
        },
        {
            "name": "overview_04_simplified-request-flow",
            "file": "architecture/overview.md",
            "url": f"{base_url}/architecture/overview/",
            "selector": "div.mermaid:nth-of-type(4)",
            "diagram_type": "flowchart TD",
            "expected_nodes": ["Request", "Rate Limiting", "Caching", "Response"],
            "description": "Simplified Request Flow with 8+ subgraphs",
            "approx_line": 131,
        },
        {
            "name": "overview_05_api-router-architecture",
            "file": "architecture/overview.md",
            "url": f"{base_url}/architecture/overview/",
            "selector": "div.mermaid:nth-of-type(5)",
            "diagram_type": "flowchart TD",
            "expected_nodes": [
                "Gateway",
                "Game Routes",
                "Account Routes",
                "Data Routes",
                "System Routes",
            ],
            "description": "API Router Architecture",
            "approx_line": 370,
        },
        # architecture/system-overview.md - 1 diagram
        {
            "name": "system-overview_01_architecture",
            "file": "architecture/system-overview.md",
            "url": f"{base_url}/architecture/system-overview/",
            "selector": "div.mermaid:nth-of-type(1)",
            "diagram_type": "flowchart TD",
            "expected_nodes": [
                "Client Layer",
                "Gateway Layer",
                "Infrastructure",
                "Providers",
                "External APIs",
            ],
            "description": "Complete System Architecture (80+ lines)",
            "approx_line": 15,
        },
        # architecture/data-flow.md - 5 diagrams
        {
            "name": "data-flow_01_request-processing",
            "file": "architecture/data-flow.md",
            "url": f"{base_url}/architecture/data-flow/",
            "selector": "div.mermaid:nth-of-type(1)",
            "diagram_type": "flowchart TD",
            "expected_nodes": ["HTTP Request", "ASGI", "Middleware", "Router", "Provider"],
            "description": "End-to-End Request Processing",
            "approx_line": 17,
        },
        {
            "name": "data-flow_02_cache-hit",
            "file": "architecture/data-flow.md",
            "url": f"{base_url}/architecture/data-flow/",
            "selector": "div.mermaid:nth-of-type(2)",
            "diagram_type": "sequenceDiagram",
            "expected_nodes": ["Client", "Gateway", "Redis"],
            "description": "Cache Hit Path (Fast Path)",
            "approx_line": 110,
        },
        {
            "name": "data-flow_03_cache-miss",
            "file": "architecture/data-flow.md",
            "url": f"{base_url}/architecture/data-flow/",
            "selector": "div.mermaid:nth-of-type(3)",
            "diagram_type": "sequenceDiagram",
            "expected_nodes": ["Client", "Gateway", "Redis", "Provider", "External API"],
            "description": "Cache Miss Path (Slow Path)",
            "approx_line": 156,
        },
        {
            "name": "data-flow_04_force-refresh",
            "file": "architecture/data-flow.md",
            "url": f"{base_url}/architecture/data-flow/",
            "selector": "div.mermaid:nth-of-type(4)",
            "diagram_type": "flowchart LR",
            "expected_nodes": ["Request", "force=true", "Skip Cache"],
            "description": "Force Refresh Path",
            "approx_line": 227,
        },
        {
            "name": "data-flow_05_error-handling",
            "file": "architecture/data-flow.md",
            "url": f"{base_url}/architecture/data-flow/",
            "selector": "div.mermaid:nth-of-type(5)",
            "diagram_type": "flowchart TD",
            "expected_nodes": ["Error", "Classification", "Recovery", "Retry"],
            "description": "Error Handling Flow",
            "approx_line": 313,
        },
        # architecture/routing.md - 5 diagrams (NOT in nav)
        {
            "name": "routing_01_router-structure",
            "file": "architecture/routing.md",
            "url": f"{base_url}/architecture/routing/",
            "selector": "div.mermaid:nth-of-type(1)",
            "diagram_type": "flowchart TD",
            "expected_nodes": ["FastAPI", "Registry", "Game", "Account", "Data", "System"],
            "description": "Complete Router Structure",
            "approx_line": 17,
        },
        {
            "name": "routing_02_request-pipeline",
            "file": "architecture/routing.md",
            "url": f"{base_url}/architecture/routing/",
            "selector": "div.mermaid:nth-of-type(2)",
            "diagram_type": "flowchart TD",
            "expected_nodes": ["HTTP", "Validation", "Rate Limit", "Cache", "Provider"],
            "description": "Complete Request Processing Pipeline (60+ lines)",
            "approx_line": 375,
        },
        {
            "name": "routing_03_dynamic-loading",
            "file": "architecture/routing.md",
            "url": f"{base_url}/architecture/routing/",
            "selector": "div.mermaid:nth-of-type(3)",
            "diagram_type": "flowchart TD",
            "expected_nodes": ["Startup", "Discovery", "Registration"],
            "description": "Dynamic Router Loading",
            "approx_line": 544,
        },
        {
            "name": "routing_04_version-strategy",
            "file": "architecture/routing.md",
            "url": f"{base_url}/architecture/routing/",
            "selector": "div.mermaid:nth-of-type(4)",
            "diagram_type": "flowchart LR",
            "expected_nodes": ["v1", "v2", "Deprecation"],
            "description": "Version Strategy",
            "approx_line": 627,
        },
        {
            "name": "routing_05_error-codes",
            "file": "architecture/routing.md",
            "url": f"{base_url}/architecture/routing/",
            "selector": "div.mermaid:nth-of-type(5)",
            "diagram_type": "flowchart TD",
            "expected_nodes": ["Error", "Router Type", "Error Code"],
            "description": "Router-Specific Error Codes",
            "approx_line": 685,
        },
        # architecture/rate-limiting.md - 1 diagram (NOT in nav)
        {
            "name": "rate-limiting_01_token-bucket",
            "file": "architecture/rate-limiting.md",
            "url": f"{base_url}/architecture/rate-limiting/",
            "selector": "div.mermaid:nth-of-type(1)",
            "diagram_type": "graph TD",
            "expected_nodes": ["Bucket", "Refill Rate", "Capacity", "Tokens"],
            "description": "Token Bucket Algorithm",
            "approx_line": 23,
        },
        # architecture/providers.md - 1 diagram (NOT in nav)
        {
            "name": "providers_01_architecture",
            "file": "architecture/providers.md",
            "url": f"{base_url}/architecture/providers/",
            "selector": "div.mermaid:nth-of-type(1)",
            "diagram_type": "flowchart TB",
            "expected_nodes": ["Gateway", "Riot", "Data Dragon", "Community Dragon", "Management"],
            "description": "External Provider Architecture (large with styling)",
            "approx_line": 7,
        },
        # architecture/production-deployment.md - 1 diagram (NOT in nav)
        {
            "name": "production-deployment_01_overview",
            "file": "architecture/production-deployment.md",
            "url": f"{base_url}/architecture/production-deployment/",
            "selector": "div.mermaid:nth-of-type(1)",
            "diagram_type": "flowchart TB",
            "expected_nodes": [
                "Internet",
                "Load Balancer",
                "Application Cluster",
                "Redis",
                "Monitoring",
            ],
            "description": "Production Deployment Overview (100+ lines with styling)",
            "approx_line": 7,
        },
        # architecture/caching.md - 1 diagram (NOT in nav)
        {
            "name": "caching_01_architecture",
            "file": "architecture/caching.md",
            "url": f"{base_url}/architecture/caching/",
            "selector": "div.mermaid:nth-of-type(1)",
            "diagram_type": "graph TB",
            "expected_nodes": ["Request", "Cache Check", "TTL Cache", "Persistent Storage"],
            "description": "Caching Architecture",
            "approx_line": 13,
        },
    ]


# ============================================================================
# Test Configuration & Thresholds
# ============================================================================

# Timeouts
NAVIGATION_TIMEOUT = 30000  # 30 seconds
MERMAID_RENDER_TIMEOUT = 10000  # 10 seconds
ELEMENT_WAIT_TIMEOUT = 5000  # 5 seconds

# Diagram size thresholds
MIN_DIAGRAM_WIDTH = 200  # pixels
MIN_DIAGRAM_HEIGHT = 200  # pixels

# Screenshot quality
SCREENSHOT_DEVICE_SCALE = 2  # Retina quality

# Content validation
MIN_PAGE_CONTENT_LENGTH = 100  # characters

# Expected status codes
SUCCESS_STATUS_CODES = [200]

# MkDocs Material selectors
SELECTORS = {
    "main_content": "article.md-content",
    "navigation": "nav.md-nav--primary",
    "toc": "nav.md-nav--secondary",
    "code_block": "pre > code",
    "copy_button": "button.md-clipboard",
    "table": "table",
    "table_header": "thead",
    "admonition": "div.admonition",
    "mermaid": "div.mermaid",
    "mermaid_svg": "svg[id^='mermaid-']",
}
