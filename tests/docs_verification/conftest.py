"""
Pytest configuration and fixtures for documentation verification tests.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator

import pytest
from playwright.async_api import Browser, Page, async_playwright, Playwright


# ============================================================================
# Configuration
# ============================================================================


@pytest.fixture(scope="session")
def output_dir() -> Path:
    """Root output directory for test artifacts."""
    return Path("docs_verification_output")


@pytest.fixture(scope="session")
def screenshots_dir(output_dir: Path) -> Path:
    """Directory for screenshots."""
    return output_dir / "screenshots"


@pytest.fixture(scope="session")
def reports_dir(output_dir: Path) -> Path:
    """Directory for JSON reports."""
    return output_dir / "reports"


@pytest.fixture(scope="session")
def metadata_dir(output_dir: Path) -> Path:
    """Directory for metadata files."""
    return output_dir / "metadata"


# ============================================================================
# Playwright Setup
# ============================================================================


@pytest.fixture(scope="session")
async def playwright_instance() -> AsyncGenerator[Playwright, None]:
    """
    Start Playwright instance for the test session.
    """
    async with async_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
async def browser(playwright_instance: Playwright) -> AsyncGenerator[Browser, None]:
    """
    Launch Chromium browser for the test session.

    Configuration:
    - Headless mode for CI/CD
    - High viewport for desktop testing
    - Device scale factor 2 for high-quality screenshots
    """
    browser = await playwright_instance.chromium.launch(
        headless=True,  # Set to False for debugging
        args=[
            "--disable-web-security",  # For CORS if needed
            "--disable-features=IsolateOrigins,site-per-process",
        ],
    )
    yield browser
    await browser.close()


@pytest.fixture(scope="function")
async def page(browser: Browser) -> AsyncGenerator[Page, None]:
    """
    Create a new page for each test with optimized settings.

    Configuration:
    - 1920x1080 viewport (desktop)
    - Device scale factor 2 (Retina display quality)
    - Extended timeouts for Mermaid rendering
    """
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        device_scale_factor=2,  # High-quality screenshots
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    )

    # Set default navigation timeout (Mermaid can be slow to render)
    context.set_default_navigation_timeout(30000)  # 30 seconds
    context.set_default_timeout(10000)  # 10 seconds for other operations

    page = await context.new_page()

    # Listen to console errors
    page.on(
        "console",
        lambda msg: print(f"[CONSOLE {msg.type}] {msg.text}")
        if msg.type in ["error", "warning"]
        else None,
    )

    yield page

    await page.close()
    await context.close()


# ============================================================================
# Parametrization Helpers
# ============================================================================


@pytest.fixture(scope="session")
def environment(request) -> str:
    """
    Get environment to test (production or development).

    Usage:
        pytest --env=prod
        pytest --env=dev
        pytest (defaults to prod)
    """
    return request.config.getoption("--env", default="prod")


def pytest_addoption(parser):
    """Add custom command-line options."""
    parser.addoption(
        "--env",
        action="store",
        default="prod",
        choices=["prod", "dev", "both"],
        help="Environment to test: prod, dev, or both (default: prod)",
    )
    # Add --base-url option (may already be registered by pytest-playwright)
    # If it exists, pytest-playwright already registered it, so skip
    try:
        # Try to add it - if it already exists, this will raise ValueError
        parser.addoption(
            "--base-url",
            action="store",
            default=None,
            help="Override base URL for local testing (e.g., http://127.0.0.1:8000)",
        )
    except ValueError:
        # Option already registered by pytest-playwright, ignore
        pass


# ============================================================================
# Screenshot Helpers
# ============================================================================


async def take_screenshot(
    page: Page,
    path: Path,
    full_page: bool = False,
    element: str | None = None,
) -> None:
    """
    Take a screenshot with error handling and directory creation.

    Args:
        page: Playwright page instance
        path: Output path for screenshot
        full_page: Whether to capture full page (scrolling)
        element: Optional CSS selector for element screenshot
    """
    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if element:
            # Screenshot specific element
            element_handle = await page.wait_for_selector(element, timeout=5000)
            if element_handle:
                await element_handle.screenshot(path=str(path))
        else:
            # Full page or viewport screenshot
            await page.screenshot(path=str(path), full_page=full_page)
    except Exception as e:
        print(f"Screenshot failed for {path}: {e}")


async def wait_for_mermaid_render(page: Page, timeout: int = 10000) -> None:
    """
    Wait for Mermaid diagrams to finish rendering.

    Mermaid diagrams are initially <pre class="mermaid">, then transformed to SVG.
    This waits for the transformation to complete.

    Args:
        page: Playwright page instance
        timeout: Max time to wait in milliseconds
    """
    try:
        # Wait for at least one SVG to appear (indicates Mermaid initialized)
        await page.wait_for_selector("svg[id^='mermaid-']", timeout=timeout, state="visible")

        # Additional wait for all diagrams to render
        await page.wait_for_timeout(2000)
    except Exception as e:
        print(f"Mermaid rendering wait failed: {e}")


# ============================================================================
# Report Helpers
# ============================================================================


def save_json_report(data: dict | list, path: Path) -> None:
    """
    Save JSON report with error handling and pretty formatting.

    Args:
        data: Dictionary or list to save as JSON
        path: Output path for JSON file
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    # Add timestamp if not present
    if isinstance(data, dict) and "timestamp" not in data:
        data["timestamp"] = datetime.now().isoformat()

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_markdown_report(
    title: str,
    results: list[dict],
    output_path: Path,
) -> None:
    """
    Generate markdown report from test results.

    Args:
        title: Report title
        results: List of result dictionaries
        output_path: Path to save markdown file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        # Summary stats
        total = len(results)
        passed = sum(1 for r in results if r.get("status") == "✓")
        failed = total - passed

        f.write("## Summary\n\n")
        f.write(f"- **Total**: {total}\n")
        f.write(f"- **Passed**: {passed} ✅\n")
        f.write(f"- **Failed**: {failed} ❌\n\n")
        f.write("---\n\n")

        # Detailed results table
        f.write("## Detailed Results\n\n")
        if results:
            # Get table headers from first result keys
            headers = list(results[0].keys())

            # Write header row
            f.write("| " + " | ".join(headers) + " |\n")
            f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")

            # Write data rows
            for result in results:
                row = [str(result.get(h, "")) for h in headers]
                f.write("| " + " | ".join(row) + " |\n")


# ============================================================================
# Pytest Hooks
# ============================================================================


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(output_dir: Path, metadata_dir: Path):
    """
    Setup test environment before any tests run.
    Creates necessary directories and saves test metadata.
    """
    # Create output directories
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    # Save test run metadata
    metadata = {
        "test_run_start": datetime.now().isoformat(),
        "playwright_version": "1.40+",
        "python_version": "3.12+",
    }

    save_json_report(metadata, metadata_dir / "test_run_metadata.json")

    yield

    # Cleanup if needed (can be extended)
    print(f"\n✅ Test artifacts saved to: {output_dir.absolute()}")
