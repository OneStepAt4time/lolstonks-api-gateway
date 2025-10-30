#!/usr/bin/env python3
"""
Exports the OpenAPI schema from the FastAPI application.

This script generates the OpenAPI schema from the main FastAPI application
and saves it to a JSON file. This is useful for generating documentation,
API clients, or for any other purpose that requires the API definition.
"""

import json
from pathlib import Path
from app.main import app


def export_openapi():
    """
    Exports the OpenAPI schema to a JSON file.

    This function retrieves the OpenAPI schema from the FastAPI application and
    writes it to `docs/data/openapi.json`. It also prints a confirmation
    message to the console with some basic statistics about the exported schema.
    """
    openapi_schema = app.openapi()

    # Save to docs/data/openapi.json
    output_path = Path("docs/data/openapi.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

    print(f"[OK] OpenAPI schema exported to {output_path}")
    print(f"  - {len(openapi_schema.get('paths', {}))} endpoints")
    print(f"  - {len(openapi_schema.get('components', {}).get('schemas', {}))} schemas")


if __name__ == "__main__":
    export_openapi()
