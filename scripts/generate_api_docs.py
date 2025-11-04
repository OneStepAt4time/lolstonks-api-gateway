#!/usr/bin/env python3
"""Generate API documentation from a running OpenAPI JSON file.

Writes a detailed `docs/api.md` including path, methods, path/query params,
links to component schemas, and simple example extraction when available.
"""

import json
from pathlib import Path
from typing import Dict, Any, List


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

            rows.append(
                {
                    "tag": tag,
                    "method": method.upper(),
                    "path": path,
                    "summary": summary,
                    "path_params": ", ".join(path_params),
                    "query_params": ", ".join(query_params),
                    "request_schema": req_schema,
                    "response_schema": resp_schema,
                    "example": example,
                }
            )

    # render markdown table lines
    out = []
    out.append(
        "| Tag | Method | Path | Summary | Path params | Query params | Request | Response | Example |"
    )
    out.append("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        out.append(
            f"| {r['tag']} | {r['method']} | `{r['path']}` | {r['summary']} | {r['path_params']} | {r['query_params']} | {r['request_schema']} | {r['response_schema']} | {r['example']} |"
        )
    return out


def generate(openapi_path: Path, out_path: Path):
    doc = load_openapi(openapi_path)
    info = doc.get("info", {})
    title = info.get("title", "API")
    desc = info.get("description", "")
    paths = doc.get("paths", {})
    components = doc.get("components", {})

    md = []
    md.append(f"# {title} (generated)")
    md.append("")
    if desc:
        md.append(desc)
        md.append("")

    md.append("**Auto-generated from the running service's `/openapi.json`.**")
    md.append("")
    md.extend(["## Endpoints", ""])
    md.extend(render_table(paths, components))
    md.append("")
    md.append(
        "For interactive docs visit <http://127.0.0.1:8080/docs> when the gateway is running."
    )

    out_path.write_text("\n".join(md), encoding="utf-8")


if __name__ == "__main__":
    base = Path(__file__).resolve().parents[1]
    openapi = base / "openapi.json"
    out = base / "docs" / "api.md"
    if not openapi.exists():
        print(
            "openapi.json not found. Run the gateway and fetch /openapi.json to this repo root as openapi.json."
        )
        raise SystemExit(1)
    generate(openapi, out)
    print(f"Wrote {out}")
