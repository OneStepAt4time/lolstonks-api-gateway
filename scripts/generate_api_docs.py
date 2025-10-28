#!/usr/bin/env python3
"""Enhanced API documentation generator for LOLStonks API Gateway.

This script generates comprehensive API documentation from a running OpenAPI JSON file
and integrates it with the MkDocs documentation system.

Features:
- Generates detailed API endpoint documentation
- Creates comprehensive schema documentation
- Integrates with MkDocs navigation
- Supports multiple output formats
- Enhanced table formatting and examples
"""

import asyncio
import httpx
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


def load_openapi(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_ref_name(schema: Dict[str, Any]) -> str:
    if not schema:
        return ""
    ref = schema.get("$ref")
    if ref:
        return ref.split("/")[-1]
    # handle inline schema types
    t = schema.get("type")
    if t:
        return t
    return ""


def params_list(parameters: List[Dict[str, Any]], where: str) -> List[str]:
    out = []
    for p in parameters:
        if p.get("in") == where:
            name = p.get("name")
            schema = p.get("schema", {})
            t = schema.get("type", "")
            out.append(f"{name}{':' + t if t else ''}")
    return out


def render_table(paths: Dict[str, Any], components: Dict[str, Any]) -> List[str]:
    rows = []
    for path in sorted(paths.keys()):
        for method in sorted(paths[path].keys()):
            op = paths[path][method]
            tag = (op.get("tags") or [""])[0]
            summary = op.get("summary", "").replace("\n", " ")
            parameters = op.get("parameters", [])
            path_params = params_list(parameters, "path")
            query_params = params_list(parameters, "query")

            # response schema (200)
            responses = op.get("responses", {})
            resp200 = responses.get("200", {})
            resp_schema = ""
            if isinstance(resp200.get("content", {}), dict):
                app_json = resp200.get("content", {}).get("application/json", {})
                resp_schema = schema_ref_name(app_json.get("schema", {}))

            # request body schema (if any)
            req_schema = ""
            request_body = op.get("requestBody", {})
            if isinstance(request_body.get("content", {}), dict):
                app_json = request_body.get("content", {}).get("application/json", {})
                req_schema = schema_ref_name(app_json.get("schema", {}))

            # example short
            example = ""
            if isinstance(resp200.get("content", {}), dict):
                app_json = resp200.get("content", {}).get("application/json", {})
                ex = app_json.get("example")
                if ex is not None:
                    # stringify small examples
                    try:
                        s = json.dumps(ex)
                        example = s if len(s) < 240 else s[:237] + "..."
                    except Exception:
                        example = str(ex)

            rows.append({
                "tag": tag,
                "method": method.upper(),
                "path": path,
                "summary": summary,
                "path_params": ", ".join(path_params),
                "query_params": ", ".join(query_params),
                "request_schema": req_schema,
                "response_schema": resp_schema,
                "example": example,
            })

    # render markdown table lines
    out = []
    out.append("| Tag | Method | Path | Summary | Path params | Query params | Request | Response | Example |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        out.append(
            f"| {r['tag']} | {r['method']} | `{r['path']}` | {r['summary']} | {r['path_params']} | {r['query_params']} | {r['request_schema']} | {r['response_schema']} | {r['example']} |"
        )
    return out


async def fetch_openapi_from_server(base_url: str = "http://localhost:8080") -> Dict[str, Any]:
    """Fetch OpenAPI schema from running server."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/openapi.json", timeout=10.0)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Failed to fetch OpenAPI from {base_url}: {e}")
        return None


def generate_api_overview(openapi_doc: Dict[str, Any]) -> List[str]:
    """Generate API overview documentation."""
    info = openapi_doc.get("info", {})
    title = info.get("title", "LOLStonks API Gateway")
    description = info.get("description", "")
    version = info.get("version", "1.0.0")

    md = []
    md.append(f"# {title}")
    md.append("")

    if description:
        md.append(description)
        md.append("")

    md.append(f"**Version**: {version}")
    md.append("")
    md.append(f"**Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    md.append("")

    # API statistics
    paths = openapi_doc.get("paths", {})
    components = openapi_doc.get("components", {})

    endpoint_count = sum(len(methods) for methods in paths.values())
    schema_count = len(components.get("schemas", {}))

    md.append("## API Statistics")
    md.append("")
    md.append(f"- **Total Endpoints**: {endpoint_count}")
    md.append(f"- **Total Schemas**: {schema_count}")
    md.append(f"- **API Base URL**: `http://localhost:8080`")
    md.append("")

    # Interactive documentation links
    md.append("## Interactive Documentation")
    md.append("")
    md.append("When the server is running, you can access:")
    md.append("")
    md.append("- **Swagger UI**: [http://localhost:8080/docs](http://localhost:8080/docs)")
    md.append("- **ReDoc**: [http://localhost:8080/redoc](http://localhost:8080/redoc)")
    md.append("- **OpenAPI JSON**: [http://localhost:8080/openapi.json](http://localhost:8080/openapi.json)")
    md.append("")

    return md


def generate_endpoints_table(paths: Dict[str, Any], components: Dict[str, Any]) -> List[str]:
    """Generate enhanced endpoints table with better formatting."""

    # Group by tags for better organization
    tag_groups = {}
    for path in sorted(paths.keys()):
        for method in sorted(paths[path].keys()):
            op = paths[path][method]
            tag = (op.get("tags") or ["General"])[0]

            if tag not in tag_groups:
                tag_groups[tag] = []

            tag_groups[tag].append({
                "method": method.upper(),
                "path": path,
                "operation": op
            })

    md = []
    md.append("## API Endpoints")
    md.append("")

    for tag, operations in tag_groups.items():
        md.append(f"### {tag}")
        md.append("")

        # Table header
        md.append("| Method | Path | Summary | Parameters | Response |")
        md.append("|--------|------|---------|------------|----------|")

        for op_data in operations:
            method = op_data["method"]
            path = op_data["path"]
            operation = op_data["operation"]

            summary = operation.get("summary", "").replace("\n", " ")
            parameters = operation.get("parameters", [])

            # Format parameters
            path_params = [p["name"] for p in parameters if p.get("in") == "path"]
            query_params = [p["name"] for p in parameters if p.get("in") == "query"]

            params_str = ""
            if path_params:
                params_str += f"Path: {', '.join(path_params)}"
            if query_params:
                if params_str:
                    params_str += "<br>"
                params_str += f"Query: {', '.join(query_params)}"

            # Get response schema
            responses = operation.get("responses", {})
            resp200 = responses.get("200", {})
            resp_schema = "Unknown"

            if isinstance(resp200.get("content", {}), dict):
                app_json = resp200.get("content", {}).get("application/json", {})
                schema = app_json.get("schema", {})
                if "$ref" in schema:
                    resp_schema = schema["$ref"].split("/")[-1]
                elif "type" in schema:
                    resp_schema = schema["type"]

            # Format method with color
            method_badges = {
                "GET": "🟢",
                "POST": "🔵",
                "PUT": "🟡",
                "DELETE": "🔴",
                "PATCH": "🟠"
            }
            method_display = f"{method_badges.get(method, '⚪')} {method}"

            md.append(f"| {method_display} | `{path}` | {summary} | {params_str or 'None'} | {resp_schema} |")

        md.append("")

    return md


def generate_schema_documentation(components: Dict[str, Any]) -> List[str]:
    """Generate comprehensive schema documentation."""
    schemas = components.get("schemas", {})

    if not schemas:
        return []

    md = []
    md.append("## Data Schemas")
    md.append("")

    # Group schemas by type/prefix
    schema_groups = {}
    for name, schema in schemas.items():
        # Simple grouping by prefix
        if name.startswith("Summoner"):
            group = "Summoner Models"
        elif name.startswith("Match"):
            group = "Match Models"
        elif name.startswith("League"):
            group = "League Models"
        elif name.startswith("Champion"):
            group = "Champion Models"
        elif name.endswith("Params"):
            group = "Parameter Models"
        elif name.endswith("Dto"):
            group = "Response Models"
        else:
            group = "Other Models"

        if group not in schema_groups:
            schema_groups[group] = []

        schema_groups[group].append((name, schema))

    for group_name, schemas_list in schema_groups.items():
        md.append(f"### {group_name}")
        md.append("")

        for name, schema in sorted(schemas_list):
            md.append(f"#### {name}")
            md.append("")

            # Schema description
            description = schema.get("description", "")
            if description:
                md.append(f"{description}")
                md.append("")

            # Schema properties
            properties = schema.get("properties", {})
            if properties:
                md.append("| Property | Type | Description | Required |")
                md.append("|----------|------|-------------|----------|")

                required_fields = set(schema.get("required", []))

                for prop_name, prop_schema in properties.items():
                    prop_type = prop_schema.get("type", "unknown")
                    prop_desc = prop_schema.get("description", "")
                    is_required = "✅" if prop_name in required_fields else "❌"

                    # Handle enum values
                    if "enum" in prop_schema:
                        enum_values = prop_schema["enum"]
                        prop_type += f"<br>Enum: {', '.join(map(str, enum_values))}"

                    md.append(f"| `{prop_name}` | {prop_type} | {prop_desc} | {is_required} |")

                md.append("")

        md.append("")

    return md


def generate_error_documentation(paths: Dict[str, Any]) -> List[str]:
    """Generate error response documentation."""
    md = []
    md.append("## Error Handling")
    md.append("")
    md.append("The API uses standard HTTP status codes and returns error information in the following format:")
    md.append("")
    md.append("```json")
    md.append("{")
    md.append('  "detail": "Error description",')
    md.append('  "status_code": 400')
    md.append("}")
    md.append("```")
    md.append("")
    md.append("### Common Error Codes")
    md.append("")
    md.append("| Status Code | Description | Cause |")
    md.append("|-------------|-------------|-------|")
    md.append("| 400 | Bad Request | Invalid parameters or malformed request |")
    md.append("| 404 | Not Found | Resource does not exist |")
    md.append("| 429 | Too Many Requests | Rate limit exceeded (handled automatically) |")
    md.append("| 500 | Internal Server Error | Server error or external API failure |")
    md.append("| 503 | Service Unavailable | External API (Riot) is down |")
    md.append("")
    md.append("### Rate Limiting")
    md.append("")
    md.append("The gateway includes automatic rate limiting with the following features:")
    md.append("")
    md.append("- **Automatic Retry**: 429 responses are automatically retried with exponential backoff")
    md.append("- **Rate Limit Headers**: All responses include rate limit information")
    md.append("- **Graceful Degradation**: The service continues to operate during rate limit events")
    md.append("")

    return md


def generate_usage_examples(paths: Dict[str, Any]) -> List[str]:
    """Generate usage examples for common operations."""
    md = []
    md.append("## Usage Examples")
    md.append("")

    # Find common operations and generate examples
    examples = [
        {
            "title": "Get Summoner by Name",
            "description": "Retrieve summoner information using their summoner name.",
            "method": "GET",
            "path": "/summoner/by-name/{summonerName}",
            "example": "curl \"http://localhost:8080/summoner/by-name/Faker?region=kr\""
        },
        {
            "title": "Get Match History",
            "description": "Retrieve recent match IDs for a player using their PUUID.",
            "method": "GET",
            "path": "/match/ids/by-puuid/{puuid}",
            "example": "curl \"http://localhost:8080/match/ids/by-puuid/puuid-here?region=kr&count=5\""
        },
        {
            "title": "Get Challenger League",
            "description": "Retrieve the challenger league for a specific queue.",
            "method": "GET",
            "path": "/league/challenger/{queue}",
            "example": "curl \"http://localhost:8080/league/challenger/RANKED_SOLO_5x5?region=kr\""
        }
    ]

    for example in examples:
        md.append(f"### {example['title']}")
        md.append("")
        md.append(example['description'])
        md.append("")
        md.append(f"**Endpoint**: `{example['method']} {example['path']}`")
        md.append("")
        md.append("```bash")
        md.append(example['example'])
        md.append("```")
        md.append("")

    md.append("### Python Client Example")
    md.append("")
    md.append("```python")
    md.append("import httpx")
    md.append("import asyncio")
    md.append("")
    md.append("async def get_summoner_data():")
    md.append('    """Get summoner information example."""')
    md.append("    async with httpx.AsyncClient() as client:")
    md.append('        response = await client.get(')
    md.append('            "http://localhost:8080/summoner/by-name/Faker",')
    md.append('            params={"region": "kr"}')
    md.append("        )")
    md.append("        if response.status_code == 200:")
    md.append("            return response.json()")
    md.append("        return None")
    md.append("")
    md.append("# Usage")
    md.append("summoner = asyncio.run(get_summoner_data())")
    md.append('if summoner:')
    md.append('    print(f"Summoner: {summoner[\\\'name\\\']} (Level {summoner[\\\'summonerLevel\\\']})")')
    md.append("```")
    md.append("")

    return md


def generate(openapi_doc: Dict[str, Any], output_dir: Path) -> None:
    """Generate comprehensive API documentation."""

    print("Generating API documentation...")

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate different documentation sections
    sections = []

    # API overview
    sections.extend(generate_api_overview(openapi_doc))

    # Endpoints table
    paths = openapi_doc.get("paths", {})
    components = openapi_doc.get("components", {})
    sections.extend(generate_endpoints_table(paths, components))

    # Schema documentation
    sections.extend(generate_schema_documentation(components))

    # Error documentation
    sections.extend(generate_error_documentation(paths))

    # Usage examples
    sections.extend(generate_usage_examples(paths))

    # Footer
    sections.extend([
        "---",
        "",
        f"*Documentation generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*",
        "",
        "For the most up-to-date interactive documentation, visit [Swagger UI](http://localhost:8000/docs) when the server is running."
    ])

    # Write main API documentation
    api_file = output_dir / "api" / "overview.md"
    api_file.parent.mkdir(parents=True, exist_ok=True)
    api_file.write_text("\n".join(sections), encoding="utf-8")
    print(f"Generated API overview: {api_file}")

    # Save OpenAPI JSON for reference
    openapi_file = output_dir / "data" / "openapi.json"
    openapi_file.parent.mkdir(parents=True, exist_ok=True)
    with open(openapi_file, "w") as f:
        json.dump(openapi_doc, f, indent=2)
    print(f"Saved OpenAPI schema: {openapi_file}")


async def main():
    """Main documentation generation function."""
    base_dir = Path(__file__).resolve().parents[1]
    docs_dir = base_dir / "docs"

    # Try to fetch from running server first
    print("Attempting to fetch OpenAPI from running server...")
    openapi_doc = await fetch_openapi_from_server()

    if openapi_doc:
        print("Successfully fetched OpenAPI from server")
    else:
        # Fallback to local file
        openapi_file = base_dir / "openapi.json"
        if openapi_file.exists():
            print(f"Using local OpenAPI file: {openapi_file}")
            openapi_doc = json.loads(openapi_file.read_text(encoding="utf-8"))
        else:
            print("ERROR: No OpenAPI schema found!")
            print("Please either:")
            print("1. Start the API server (uvicorn app.main:app)")
            print("2. Place openapi.json in the project root")
            sys.exit(1)

    # Generate documentation
    generate(openapi_doc, docs_dir)
    print("Documentation generation completed!")


if __name__ == "__main__":
    asyncio.run(main())


