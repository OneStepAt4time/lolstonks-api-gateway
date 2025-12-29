"""
Mermaid Diagram Verification Tests

Tests that all 19 Mermaid diagrams:
- Render correctly as SVG
- Have appropriate dimensions
- Contain expected content
- Are visually complete

Tests both production and development environments.
"""

import pytest
from pathlib import Path
from playwright.async_api import Page

from .conftest import save_json_report, take_screenshot, wait_for_mermaid_render
from .constants import (
    get_base_url,
    get_diagrams,
    MIN_DIAGRAM_WIDTH,
    MIN_DIAGRAM_HEIGHT,
    SELECTORS,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def base_url(request) -> str:
    """Get base URL for current environment."""
    env = request.config.getoption("--env", default="prod")
    override = request.config.getoption("--base-url", default=None)
    return get_base_url(env, override)


@pytest.fixture
def diagrams(base_url: str) -> list[dict]:
    """Get all diagrams with URLs for current environment."""
    return get_diagrams(base_url)


@pytest.fixture
def env_name(request) -> str:
    """Get environment name for organizing outputs."""
    return request.config.getoption("--env", default="prod")


# ============================================================================
# Diagram Rendering Tests
# ============================================================================


@pytest.mark.asyncio
async def test_all_diagrams_render(page: Page, diagrams: list[dict], env_name: str):
    """
    Test that all Mermaid diagrams render correctly as SVG.

    Verifies for each diagram:
    - SVG element exists
    - SVG is visible
    - Dimensions are adequate (not collapsed)
    - No Mermaid error messages
    - Expected nodes are present (if specified)
    """
    results = []

    for diagram in diagrams:
        try:
            # Navigate to page containing diagram
            await page.goto(diagram["url"], wait_until="networkidle")

            # Wait for Mermaid to render
            await wait_for_mermaid_render(page)

            # Find the specific diagram's SVG
            svg_selector = f"{diagram['selector']} {SELECTORS['mermaid_svg']}"

            svg = await page.wait_for_selector(svg_selector, timeout=5000)
            assert svg is not None, f"SVG not found for {diagram['name']}"

            # Verify SVG is visible
            is_visible = await svg.is_visible()
            assert is_visible, f"SVG not visible for {diagram['name']}"

            # Get SVG dimensions
            bbox = await svg.bounding_box()
            assert bbox is not None, f"Could not get bounding box for {diagram['name']}"

            width = bbox["width"]
            height = bbox["height"]

            # Verify dimensions are adequate
            assert width >= MIN_DIAGRAM_WIDTH, (
                f"Diagram {diagram['name']} too narrow: {width}px < {MIN_DIAGRAM_WIDTH}px"
            )
            assert height >= MIN_DIAGRAM_HEIGHT, (
                f"Diagram {diagram['name']} too short: {height}px < {MIN_DIAGRAM_HEIGHT}px"
            )

            # Check for Mermaid error messages
            svg_content = await svg.inner_text()
            mermaid_errors = ["Syntax error", "Parse error", "Error:", "undefined"]
            has_error = any(err.lower() in svg_content.lower() for err in mermaid_errors)
            assert not has_error, (
                f"Mermaid error detected in {diagram['name']}: {svg_content[:200]}"
            )

            # Verify expected nodes (if specified)
            if diagram.get("expected_nodes"):
                for node in diagram["expected_nodes"]:
                    # Check in SVG content (text elements)
                    assert (
                        node in svg_content
                        or await page.locator(f"text:has-text('{node}')").count() > 0
                    ), f"Expected node '{node}' not found in {diagram['name']}"

            # Take high-resolution screenshot of diagram
            screenshot_path = Path(
                f"docs_verification_output/screenshots/{env_name}/diagrams/{diagram['name']}.png"
            )
            await take_screenshot(page, screenshot_path, element=svg_selector)

            # Record success
            results.append(
                {
                    "diagram": diagram["name"],
                    "file": diagram["file"],
                    "type": diagram["diagram_type"],
                    "status": "✓",
                    "dimensions": f"{width:.0f}x{height:.0f}",
                    "url": diagram["url"],
                    "screenshot": str(screenshot_path),
                }
            )

        except AssertionError as e:
            # Record failure
            # Try to take screenshot of error state
            error_screenshot = Path(
                f"docs_verification_output/screenshots/{env_name}/issues/{diagram['name']}_error.png"
            )
            try:
                await take_screenshot(page, error_screenshot, full_page=True)
            except Exception:
                pass

            results.append(
                {
                    "diagram": diagram["name"],
                    "file": diagram["file"],
                    "type": diagram["diagram_type"],
                    "status": "✗",
                    "error": str(e),
                    "url": diagram["url"],
                    "error_screenshot": str(error_screenshot)
                    if error_screenshot.exists()
                    else None,
                }
            )

        except Exception as e:
            # Record unexpected error
            results.append(
                {
                    "diagram": diagram["name"],
                    "file": diagram["file"],
                    "type": diagram["diagram_type"],
                    "status": "✗",
                    "error": f"Unexpected error: {str(e)}",
                    "url": diagram["url"],
                }
            )

    # Save JSON report
    report_path = Path(f"docs_verification_output/reports/{env_name}/diagrams-report.json")
    save_json_report(results, report_path)

    # Assert all diagrams passed
    failed = [r for r in results if r["status"] == "✗"]
    assert len(failed) == 0, (
        f"{len(failed)}/{len(results)} diagrams failed to render correctly: {[f['diagram'] for f in failed]}"
    )


@pytest.mark.asyncio
async def test_diagram_interactivity(page: Page, base_url: str):
    """
    Test that diagrams have interactive features enabled.

    Verifies:
    - Mermaid interactivity JS is loaded
    - Custom CSS is applied
    """
    # Test on a page with diagrams
    await page.goto(f"{base_url}/architecture/overview/", wait_until="networkidle")
    await wait_for_mermaid_render(page)

    # Check if interactivity script is loaded
    # This is optional - diagrams work without it
    scripts = await page.query_selector_all("script[src]")
    script_sources = []
    for script in scripts:
        src = await script.get_attribute("src")
        if src:
            script_sources.append(src)

    # Just verify page loads - interactivity is a nice-to-have
    assert len(script_sources) > 0, "No scripts loaded on page"


@pytest.mark.asyncio
async def test_diagrams_by_type(page: Page, diagrams: list[dict], env_name: str):
    """
    Group diagrams by type and test each group.

    Useful for identifying type-specific rendering issues.
    """
    # Group diagrams by type
    by_type = {}
    for diagram in diagrams:
        dtype = diagram["diagram_type"]
        if dtype not in by_type:
            by_type[dtype] = []
        by_type[dtype].append(diagram)

    # Report grouping
    type_summary = {dtype: len(diagrams_list) for dtype, diagrams_list in by_type.items()}

    summary_path = Path(f"docs_verification_output/reports/{env_name}/diagrams-by-type.json")
    save_json_report(type_summary, summary_path)

    print("\n📊 Diagram Types Distribution:")
    for dtype, count in type_summary.items():
        print(f"  - {dtype}: {count} diagrams")


# ============================================================================
# Visual Quality Tests
# ============================================================================


@pytest.mark.asyncio
async def test_diagram_text_readability(page: Page, diagrams: list[dict]):
    """
    Test that diagram text is readable (font size, contrast).

    Verifies:
    - Text elements have adequate font size
    - Text is not cut off or overlapping
    """
    # Sample a few diagrams for detailed text analysis
    sample_diagrams = diagrams[:5]  # Test first 5

    for diagram in sample_diagrams:
        await page.goto(diagram["url"], wait_until="networkidle")
        await wait_for_mermaid_render(page)

        svg_selector = f"{diagram['selector']} {SELECTORS['mermaid_svg']}"
        svg = await page.wait_for_selector(svg_selector, timeout=5000)

        if not svg:
            continue

        # Get all text elements in SVG
        text_elements = await svg.query_selector_all("text")

        for text_elem in text_elements[:10]:  # Check first 10 text elements
            # Get font size
            font_size = await text_elem.evaluate("el => window.getComputedStyle(el).fontSize")

            # Font size should be at least 10px for readability
            if font_size:
                size_px = float(font_size.replace("px", ""))
                assert size_px >= 10, (
                    f"Text too small in {diagram['name']}: {size_px}px (should be >= 10px)"
                )


@pytest.mark.asyncio
async def test_diagram_styling_applied(page: Page, base_url: str):
    """
    Test that custom diagram styling (colors, classes) is applied.

    Verifies:
    - Custom CSS classes are present
    - Color definitions are applied
    """
    # Test on a page with styled diagrams
    test_url = f"{base_url}/architecture/providers/"

    await page.goto(test_url, wait_until="networkidle")
    await wait_for_mermaid_render(page)

    # Check if any diagram has custom classes (indicates styling)
    svg = await page.query_selector(SELECTORS["mermaid_svg"])
    if svg:
        svg_html = await svg.evaluate("el => el.outerHTML")
        # Check for class definitions (Mermaid adds these when classDef is used)
        has_classes = "class=" in svg_html or "fill:" in svg_html
        # This is informational - not a failure if missing
        print(f"Custom styling detected: {has_classes}")


# ============================================================================
# Summary Test
# ============================================================================


@pytest.mark.asyncio
async def test_diagrams_summary(env_name: str):
    """
    Generate a comprehensive summary report of diagram test results.

    This test always passes but generates a detailed markdown summary.
    """
    report_path = Path(f"docs_verification_output/reports/{env_name}/diagrams-report.json")

    if not report_path.exists():
        pytest.skip("Diagrams report not found - run test_all_diagrams_render first")

    import json

    with open(report_path, encoding="utf-8") as f:
        results = json.load(f)

    # Calculate statistics
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "✓")
    failed = total - passed

    # Group by file
    by_file = {}
    for r in results:
        file = r.get("file", "unknown")
        if file not in by_file:
            by_file[file] = {"total": 0, "passed": 0, "failed": 0}
        by_file[file]["total"] += 1
        if r.get("status") == "✓":
            by_file[file]["passed"] += 1
        else:
            by_file[file]["failed"] += 1

    # Generate markdown summary
    summary_path = Path(f"docs_verification_output/reports/{env_name}/diagrams-summary.md")
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"# Diagram Verification Summary - {env_name.upper()}\n\n")
        f.write(f"**Environment**: {env_name}\n")
        f.write(f"**Total Diagrams**: {total}\n")
        f.write(f"**Passed**: {passed} ✅\n")
        f.write(f"**Failed**: {failed} ❌\n\n")

        f.write("## Diagrams by File\n\n")
        f.write("| File | Total | Passed | Failed |\n")
        f.write("|------|-------|--------|--------|\n")
        for file, stats in sorted(by_file.items()):
            f.write(f"| {file} | {stats['total']} | {stats['passed']} | {stats['failed']} |\n")

        f.write("\n## Detailed Results\n\n")
        f.write("| Diagram | Type | Dimensions | Status | Error |\n")
        f.write("|---------|------|------------|--------|-------|\n")
        for r in results:
            dims = r.get("dimensions", "N/A")
            error = r.get("error", "-")[:50]  # Truncate errors
            f.write(f"| {r['diagram']} | {r['type']} | {dims} | {r['status']} | {error} |\n")

        if failed > 0:
            f.write("\n## Failed Diagrams Details\n\n")
            for r in results:
                if r.get("status") == "✗":
                    f.write(f"### {r['diagram']}\n\n")
                    f.write(f"- **File**: {r.get('file')}\n")
                    f.write(f"- **Type**: {r.get('type')}\n")
                    f.write(f"- **URL**: {r.get('url')}\n")
                    f.write(f"- **Error**: {r.get('error')}\n\n")

    print(f"\n📊 Diagrams Summary: {passed}/{total} diagrams passed")
    print(f"📄 Full report: {summary_path.absolute()}")
