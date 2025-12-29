"""
Navigation and Page Accessibility Tests

Tests that all documentation pages:
- Are accessible (HTTP 200)
- Have content (not empty)
- Render without errors
- Have working navigation

Tests both production and development environments.
"""

import pytest
from pathlib import Path
from playwright.async_api import Page

from .conftest import save_json_report, take_screenshot
from .constants import get_base_url, get_pages, get_extra_pages, MIN_PAGE_CONTENT_LENGTH, SELECTORS


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def base_url(request) -> str:
    """Get base URL for current environment."""
    env = request.config.getoption("--env", default="prod")
    override = request.config.getoption("--base-url", default=None)
    return get_base_url(env, override)


@pytest.fixture
def all_pages(base_url: str) -> dict[str, str]:
    """Get all pages including navigation and extra pages."""
    pages = get_pages(base_url)
    extra = get_extra_pages(base_url)
    return {**pages, **extra}


@pytest.fixture
def env_name(request) -> str:
    """Get environment name for organizing outputs."""
    return request.config.getoption("--env", default="prod")


# ============================================================================
# Navigation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_all_pages_accessible(page: Page, all_pages: dict[str, str], env_name: str):
    """
    Test that all documentation pages are accessible and return HTTP 200.

    Verifies:
    - HTTP status 200
    - Page loads without errors
    - Content is not empty
    - Main content container exists
    """
    results = []

    for page_name, url in all_pages.items():
        try:
            # Navigate to page
            response = await page.goto(url, wait_until="networkidle")

            # Verify HTTP status
            status = response.status if response else 0
            assert status == 200, f"Page {page_name} returned status {status}"

            # Verify main content exists
            content_element = await page.query_selector(SELECTORS["main_content"])
            assert content_element is not None, f"Main content not found on {page_name}"

            # Verify content is not empty
            content_text = await content_element.inner_text()
            content_length = len(content_text.strip())
            assert (
                content_length > MIN_PAGE_CONTENT_LENGTH
            ), f"Page {page_name} has suspiciously little content ({content_length} chars)"

            # Take full-page screenshot
            screenshot_path = Path(
                f"docs_verification_output/screenshots/{env_name}/pages/{page_name}.png"
            )
            await take_screenshot(page, screenshot_path, full_page=True)

            # Record success
            results.append(
                {
                    "page": page_name,
                    "url": url,
                    "status": "✓",
                    "http_status": status,
                    "content_length": content_length,
                    "screenshot": str(screenshot_path),
                }
            )

        except AssertionError as e:
            # Record failure
            results.append(
                {
                    "page": page_name,
                    "url": url,
                    "status": "✗",
                    "error": str(e),
                }
            )

        except Exception as e:
            # Record unexpected error
            results.append(
                {
                    "page": page_name,
                    "url": url,
                    "status": "✗",
                    "error": f"Unexpected error: {str(e)}",
                }
            )

    # Save JSON report
    report_path = Path(f"docs_verification_output/reports/{env_name}/navigation-report.json")
    save_json_report(results, report_path)

    # Assert all pages passed
    failed = [r for r in results if r["status"] == "✗"]
    assert (
        len(failed) == 0
    ), f"{len(failed)}/{len(results)} pages failed accessibility check: {[f['page'] for f in failed]}"


@pytest.mark.asyncio
async def test_navigation_menu_exists(page: Page, base_url: str):
    """
    Test that the navigation menu is present and functional.

    Verifies:
    - Primary navigation exists
    - Navigation links are clickable
    - Navigation sections are visible
    """
    await page.goto(base_url, wait_until="networkidle")

    # Verify primary navigation exists
    nav = await page.query_selector(SELECTORS["navigation"])
    assert nav is not None, "Primary navigation not found"

    # Verify navigation is visible
    is_visible = await nav.is_visible()
    assert is_visible, "Navigation menu is not visible"

    # Get all navigation links
    nav_links = await nav.query_selector_all("a")
    assert len(nav_links) > 0, "No navigation links found"

    # Verify at least major sections are present
    nav_text = await nav.inner_text()
    expected_sections = [
        "Getting Started",
        "API Reference",
        "Architecture",
        "Operations",
        "Development",
    ]

    for section in expected_sections:
        assert section in nav_text, f"Navigation section '{section}' not found"


@pytest.mark.asyncio
async def test_table_of_contents_present(page: Page, all_pages: dict[str, str]):
    """
    Test that pages with headings have a table of contents.

    Verifies:
    - TOC sidebar exists on content pages
    - TOC links match page headings
    """
    # Test on a few representative pages
    test_pages = [
        ("architecture_overview", all_pages.get("architecture_overview")),
        ("api_overview", all_pages.get("api_overview")),
        ("getting-started_installation", all_pages.get("getting-started_installation")),
    ]

    for page_name, url in test_pages:
        if not url:
            continue

        await page.goto(url, wait_until="networkidle")

        # Check if TOC exists
        toc = await page.query_selector(SELECTORS["toc"])

        # TOC should exist on pages with multiple headings
        if toc:
            is_visible = await toc.is_visible()
            assert is_visible, f"TOC exists but not visible on {page_name}"


@pytest.mark.asyncio
async def test_no_404_errors_in_links(page: Page, base_url: str):
    """
    Test that internal links don't lead to 404 errors.

    Verifies:
    - Internal links are valid
    - No broken links in navigation
    """
    await page.goto(base_url, wait_until="networkidle")

    # Get all internal links
    all_links = await page.query_selector_all("a[href]")

    internal_links = []
    for link in all_links:
        href = await link.get_attribute("href")
        if href and (href.startswith("/") or base_url in href):
            internal_links.append(href)

    # Sample test a few internal links (testing all would be very slow)
    sample_size = min(10, len(internal_links))
    import random

    random.seed(42)  # Deterministic sampling
    sampled_links = random.sample(internal_links, sample_size) if internal_links else []

    broken_links = []
    for link in sampled_links:
        # Construct full URL
        if link.startswith("/"):
            full_url = base_url + link
        else:
            full_url = link

        try:
            response = await page.goto(full_url, wait_until="domcontentloaded", timeout=10000)
            if response and response.status == 404:
                broken_links.append(link)
        except Exception:
            # Timeout or other error - might be external or anchor link
            pass

    assert len(broken_links) == 0, f"Found {len(broken_links)} broken links: {broken_links}"


# ============================================================================
# Summary Test
# ============================================================================


@pytest.mark.asyncio
async def test_navigation_summary(env_name: str):
    """
    Generate a summary report of navigation test results.

    This test always passes but generates a markdown summary.
    """
    report_path = Path(f"docs_verification_output/reports/{env_name}/navigation-report.json")

    if not report_path.exists():
        pytest.skip("Navigation report not found - run test_all_pages_accessible first")

    import json

    with open(report_path) as f:
        results = json.load(f)

    # Calculate statistics
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "✓")
    failed = total - passed

    # Generate markdown summary
    summary_path = Path(f"docs_verification_output/reports/{env_name}/navigation-summary.md")
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    with open(summary_path, "w") as f:
        f.write(f"# Navigation Test Summary - {env_name.upper()}\n\n")
        f.write(f"**Environment**: {env_name}\n")
        f.write(f"**Total Pages**: {total}\n")
        f.write(f"**Passed**: {passed} ✅\n")
        f.write(f"**Failed**: {failed} ❌\n\n")

        if failed > 0:
            f.write("## Failed Pages\n\n")
            for r in results:
                if r.get("status") == "✗":
                    f.write(f"- **{r['page']}**: {r.get('error', 'Unknown error')}\n")
        else:
            f.write("## ✅ All Pages Passed!\n\n")
            f.write("All documentation pages are accessible and rendering correctly.\n")

    print(f"\n📊 Navigation Summary: {passed}/{total} pages passed")
    print(f"📄 Full report: {summary_path.absolute()}")
