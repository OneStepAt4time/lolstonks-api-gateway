# Documentation Verification Tests

Automated Playwright tests to verify documentation rendering quality on GitHub Pages.

## Overview

This test suite verifies that the **lolstonks-api-gateway** documentation is correctly rendered, including:

- ✅ **27 pages** across 6 sections (Getting Started, API Reference, Architecture, Operations, Development)
- ✅ **19 Mermaid diagrams** with proper SVG rendering
- ✅ **Text formatting** (code blocks, tables, admonitions, links, lists)
- ✅ **Both environments**: Production (main) and Development (dev)

## Quick Start

### Prerequisites

```bash
# Install dependencies
uv sync --extra test-docs

# Install Playwright browsers
uv run playwright install chromium
```

### Run Tests

```bash
# Test production documentation
uv run pytest tests/docs_verification/ --env=prod -v

# Test development documentation
uv run pytest tests/docs_verification/ --env=dev -v

# Test local build
uv run mkdocs serve &  # Start server
uv run pytest tests/docs_verification/ --env=prod --base-url=http://127.0.0.1:8000 -v
```

## Test Organization

### test_navigation.py
**Purpose**: Verify page accessibility and navigation

**Tests**:
- `test_all_pages_accessible` - All 27 pages return HTTP 200
- `test_navigation_menu_exists` - Navigation menu is present and functional
- `test_table_of_contents_present` - TOC sidebar exists on content pages
- `test_no_404_errors_in_links` - Internal links are valid

**Output**:
- `docs_verification_output/screenshots/{env}/pages/` - Full-page screenshots
- `docs_verification_output/reports/{env}/navigation-report.json` - JSON report
- `docs_verification_output/reports/{env}/navigation-summary.md` - Markdown summary

### test_diagrams.py
**Purpose**: Verify Mermaid diagram rendering

**Tests**:
- `test_all_diagrams_render` - All 19 diagrams render as SVG
- `test_diagram_interactivity` - Interactive features are loaded
- `test_diagrams_by_type` - Group diagrams by type (flowchart, graph, sequence)
- `test_diagram_text_readability` - Text is readable (font size >= 10px)
- `test_diagram_styling_applied` - Custom colors/classes applied

**Verification Criteria**:
- SVG element exists and is visible
- Dimensions >= 200x200px (not collapsed)
- Expected nodes are present
- No Mermaid error messages
- Text is readable

**Output**:
- `docs_verification_output/screenshots/{env}/diagrams/` - High-res diagram screenshots
- `docs_verification_output/reports/{env}/diagrams-report.json` - JSON report
- `docs_verification_output/reports/{env}/diagrams-summary.md` - Markdown summary

### test_formatting.py
**Purpose**: Verify text formatting elements

**Tests**:
- `test_code_blocks_syntax_highlighting` - Syntax highlighting applied, copy button present
- `test_code_block_formatting` - Monospace font, proper width
- `test_tables_rendering` - Headers present, borders visible
- `test_admonitions_styling` - Icons visible, colors applied
- `test_links_formatting` - Distinct color, hover effects
- `test_lists_formatting` - Bullets/numbers, proper indentation
- `test_headings_hierarchy` - H1 exists, hierarchy logical

**Output**:
- `docs_verification_output/reports/{env}/formatting-summary.md` - Markdown summary

## Test Configuration

### Command-Line Options

```bash
# Environment selection
--env=prod          # Test production (default)
--env=dev           # Test development
# No --env=both support yet - run tests twice

# Override base URL (for local testing)
--base-url=http://127.0.0.1:8000

# Pytest standard options
-v                  # Verbose output
-s                  # Show print statements
-k test_diagrams    # Run specific test
--tb=short          # Short traceback format
```

### constants.py Configuration

**Timeouts**:
- `NAVIGATION_TIMEOUT = 30000` (30 seconds) - For page navigation
- `MERMAID_RENDER_TIMEOUT = 10000` (10 seconds) - For Mermaid rendering
- `ELEMENT_WAIT_TIMEOUT = 5000` (5 seconds) - For element appearance

**Thresholds**:
- `MIN_DIAGRAM_WIDTH = 200` pixels
- `MIN_DIAGRAM_HEIGHT = 200` pixels
- `MIN_PAGE_CONTENT_LENGTH = 100` characters

**Modify these in `constants.py` if needed.**

## GitHub Actions Integration

### Workflow Triggers

The `.github/workflows/docs-verification.yml` workflow runs on:

1. **Push to main/develop** - Verifies production/dev environments
2. **Pull Requests** - Verifies local build + production
3. **Manual dispatch** - Choose environment (prod/dev/both)
4. **Weekly schedule** - Sunday 00:00 UTC

### Artifacts

Each workflow run uploads:
- `production-screenshots` - All prod screenshots (30 days retention)
- `production-reports` - All prod reports (30 days retention)
- `development-screenshots` - All dev screenshots (30 days retention, if applicable)
- `development-reports` - All dev reports (30 days retention, if applicable)
- `local-build-screenshots` - Local build screenshots (7 days retention, PR only)
- `local-build-reports` - Local build reports (7 days retention, PR only)
- `comparison-report` - Prod vs dev comparison (30 days, if both tested)

### PR Comments

On pull requests, the workflow automatically comments with:
- Navigation summary (pages passed/failed)
- Links to artifacts
- Quick status overview

## Local Development

### Running Locally with Screenshots

```bash
# 1. Start local docs server
cd lolstonks-api-gateway
uv run mkdocs serve

# 2. In another terminal, run tests
uv run pytest tests/docs_verification/ \
    --env=prod \
    --base-url=http://127.0.0.1:8000 \
    -v

# 3. View results
open docs_verification_output/reports/prod/diagrams-summary.md
open docs_verification_output/screenshots/prod/diagrams/
```

### Debugging Failed Tests

1. **Check screenshot** in `docs_verification_output/screenshots/{env}/`
2. **Read error** in pytest output or JSON report
3. **Navigate manually** to the failing page/diagram
4. **Inspect SVG** in browser DevTools

Common issues:
- **Timeout**: Increase timeouts in `constants.py`
- **Element not found**: Check selector in `constants.py`
- **Size too small**: Diagram might be collapsing - check CSS

### Adding New Diagrams

When adding a new Mermaid diagram to the docs:

1. **Update constants.py**:
```python
{
    "name": "new-page_01_my-diagram",
    "file": "path/to/page.md",
    "url": f"{base_url}/path/to/page/",
    "selector": "div.mermaid:nth-of-type(1)",  # Adjust index
    "diagram_type": "flowchart TD",
    "expected_nodes": ["Node1", "Node2"],
    "description": "My new diagram description",
    "approx_line": 42,
}
```

2. **Run tests** to verify it's detected and rendered

3. **Commit the update** to keep inventory synchronized

## Output Structure

```
docs_verification_output/
├── screenshots/
│   ├── prod/
│   │   ├── pages/              # Full-page screenshots (27 files)
│   │   ├── diagrams/           # Diagram screenshots (19 files)
│   │   └── issues/             # Error screenshots (if any)
│   └── dev/
│       ├── pages/
│       ├── diagrams/
│       └── issues/
├── reports/
│   ├── prod/
│   │   ├── navigation-report.json
│   │   ├── navigation-summary.md
│   │   ├── diagrams-report.json
│   │   ├── diagrams-summary.md
│   │   ├── diagrams-by-type.json
│   │   ├── formatting-summary.md
│   │   └── pytest-report.html
│   ├── dev/
│   │   └── (same as prod/)
│   └── comparison/
│       └── diff-report.md      # Prod vs dev comparison
└── metadata/
    └── test_run_metadata.json
```

## Continuous Improvement

### Extending Tests

To add new verification checks:

1. **Add test function** in appropriate file
2. **Use fixtures** from `conftest.py` (page, base_url, env_name)
3. **Follow naming** convention `test_*`
4. **Save results** using `save_json_report()` helper
5. **Run locally** to verify

Example:
```python
@pytest.mark.asyncio
async def test_new_feature(page: Page, base_url: str):
    await page.goto(base_url)
    # Your verification logic
    assert some_condition, "Feature not working"
```

### Maintaining Diagram Inventory

The diagram inventory in `constants.py` should be kept synchronized with the actual documentation. When diagrams are:

- **Added**: Add entry to `DIAGRAMS` list
- **Removed**: Remove entry from `DIAGRAMS` list
- **Moved**: Update `url` and `selector` fields
- **Modified**: Update `expected_nodes` if structure changes

## Troubleshooting

### Tests Timing Out

**Cause**: Network slow, Mermaid rendering slow
**Fix**: Increase timeouts in `constants.py`

### SVG Not Found

**Cause**: Selector changed, diagram moved
**Fix**: Inspect page HTML, update selector in `constants.py`

### Screenshot Empty/Black

**Cause**: Element not visible, timing issue
**Fix**: Add wait before screenshot, check element visibility

### Playwright Installation Issues

**Cause**: Missing browser binaries or system dependencies
**Fix**:
```bash
uv run playwright install chromium
uv run playwright install-deps  # Linux only
```

## Performance

**Typical run times**:
- Navigation tests: ~2-3 minutes (27 pages)
- Diagram tests: ~3-4 minutes (19 diagrams + rendering wait)
- Formatting tests: ~1-2 minutes
- **Total**: ~6-9 minutes for full suite

**Optimization tips**:
- Run in parallel: `pytest -n auto` (requires pytest-xdist)
- Reduce screenshot quality: Lower `device_scale_factor` in conftest.py
- Test subset: Use `-k` flag to filter tests

## Resources

- **Playwright Python**: https://playwright.dev/python/
- **Pytest**: https://docs.pytest.org/
- **MkDocs Material**: https://squidfunk.github.io/mkdocs-material/
- **Mermaid**: https://mermaid.js.org/

---

**Last Updated**: 2025-01-26
**Maintainer**: Gateway Team
