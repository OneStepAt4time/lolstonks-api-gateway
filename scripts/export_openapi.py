#!/usr/bin/env python3
"""Export OpenAPI schema from FastAPI app."""

import json
from pathlib import Path
from app.main import app


def export_openapi():
    """Export OpenAPI schema to JSON file."""
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
