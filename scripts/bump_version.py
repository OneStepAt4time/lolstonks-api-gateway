#!/usr/bin/env python3
"""
Version bumping script for LOLStonks API Gateway.

This script updates the version number across all relevant files in the project:
- VERSION file
- pyproject.toml
- app/__init__.py
- CHANGELOG.md (adds new version section)

Usage:
    python scripts/bump_version.py patch    # 2.0.0 -> 2.0.1
    python scripts/bump_version.py minor    # 2.0.0 -> 2.1.0
    python scripts/bump_version.py major    # 2.0.0 -> 3.0.0
    python scripts/bump_version.py 2.5.0    # Set specific version
"""

import re
import sys
from datetime import date
from pathlib import Path
from typing import Tuple


class VersionBumper:
    """Handles version bumping across project files."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.version_file = project_root / "VERSION"
        self.pyproject_file = project_root / "pyproject.toml"
        self.init_file = project_root / "app" / "__init__.py"
        self.changelog_file = project_root / "CHANGELOG.md"

    def read_current_version(self) -> str:
        """Read current version from VERSION file."""
        if not self.version_file.exists():
            raise FileNotFoundError(f"VERSION file not found at {self.version_file}")

        version = self.version_file.read_text().strip()
        if not self._is_valid_version(version):
            raise ValueError(f"Invalid version format in VERSION file: {version}")

        return version

    def _is_valid_version(self, version: str) -> bool:
        """Validate semantic version format."""
        pattern = r"^\d+\.\d+\.\d+$"
        return bool(re.match(pattern, version))

    def parse_version(self, version: str) -> Tuple[int, int, int]:
        """Parse version string into (major, minor, patch) tuple."""
        parts = version.split(".")
        return int(parts[0]), int(parts[1]), int(parts[2])

    def bump_version(self, current: str, bump_type: str) -> str:
        """
        Bump version based on type.

        Args:
            current: Current version string (e.g., "2.0.0")
            bump_type: One of "major", "minor", "patch", or a specific version

        Returns:
            New version string
        """
        # If bump_type is a version string, validate and return it
        if self._is_valid_version(bump_type):
            return bump_type

        major, minor, patch = self.parse_version(current)

        if bump_type == "major":
            return f"{major + 1}.0.0"
        elif bump_type == "minor":
            return f"{major}.{minor + 1}.0"
        elif bump_type == "patch":
            return f"{major}.{minor}.{patch + 1}"
        else:
            raise ValueError(
                f"Invalid bump type: {bump_type}. Use 'major', 'minor', 'patch', or a specific version."
            )

    def update_version_file(self, new_version: str) -> None:
        """Update VERSION file."""
        self.version_file.write_text(f"{new_version}\n")
        print(f"✓ Updated VERSION: {new_version}")

    def update_pyproject(self, new_version: str) -> None:
        """Update version in pyproject.toml."""
        content = self.pyproject_file.read_text()

        # Update version field
        updated = re.sub(r'version = "[^"]*"', f'version = "{new_version}"', content, count=1)

        if updated == content:
            raise ValueError("Could not find version field in pyproject.toml")

        self.pyproject_file.write_text(updated)
        print(f"✓ Updated pyproject.toml: {new_version}")

    def update_init_file(self, new_version: str) -> None:
        """Update version in app/__init__.py."""
        if not self.init_file.exists():
            # Create __init__.py with version
            content = f'"""LOLStonks API Gateway."""\n\n__version__ = "{new_version}"\n'
            self.init_file.write_text(content)
            print(f"✓ Created app/__init__.py with version: {new_version}")
            return

        content = self.init_file.read_text()

        # Check if __version__ exists
        if "__version__" in content:
            updated = re.sub(r'__version__ = "[^"]*"', f'__version__ = "{new_version}"', content)
        else:
            # Add __version__ to the file
            updated = content + f'\n__version__ = "{new_version}"\n'

        self.init_file.write_text(updated)
        print(f"✓ Updated app/__init__.py: {new_version}")

    def update_changelog(self, new_version: str, old_version: str) -> None:
        """Update CHANGELOG.md with new version section."""
        if not self.changelog_file.exists():
            print("⚠ CHANGELOG.md not found, skipping")
            return

        content = self.changelog_file.read_text()

        # Find the [Unreleased] section
        unreleased_pattern = r"## \[Unreleased\](.*?)(?=\n## \[|\Z)"
        match = re.search(unreleased_pattern, content, re.DOTALL)

        if not match:
            print("⚠ Could not find [Unreleased] section in CHANGELOG.md")
            return

        unreleased_content = match.group(1).strip()

        # Check if there are actually changes in unreleased
        if not unreleased_content or unreleased_content.startswith("###"):
            print("⚠ No changes in [Unreleased] section")
            return

        # Get today's date
        today = date.today().strftime("%Y-%m-%d")

        # Create new version section
        new_section = f"## [{new_version}] - {today}\n\n{unreleased_content}\n\n"

        # Replace [Unreleased] section with empty one and add new version
        updated = content.replace(
            match.group(0), f"## [Unreleased]\n\n{new_section}## [{old_version}]"
        )

        # Update comparison links at the bottom
        # Add new unreleased link
        unreleased_link_pattern = r"\[Unreleased\]: .*"
        new_unreleased_link = f"[Unreleased]: https://github.com/OneStepAt4time/lolstonks-api-gateway/compare/v{new_version}...HEAD"

        if re.search(unreleased_link_pattern, updated):
            updated = re.sub(unreleased_link_pattern, new_unreleased_link, updated)
        else:
            # Add links section if it doesn't exist
            updated += f"\n{new_unreleased_link}\n"

        # Add new version link
        version_link = f"[{new_version}]: https://github.com/OneStepAt4time/lolstonks-api-gateway/compare/v{old_version}...v{new_version}\n"

        # Insert after [Unreleased] link
        updated = updated.replace(new_unreleased_link, f"{new_unreleased_link}\n{version_link}")

        self.changelog_file.write_text(updated)
        print(f"✓ Updated CHANGELOG.md: Added v{new_version} section")

    def run(self, bump_type: str, update_changelog: bool = True) -> None:
        """
        Run the version bump process.

        Args:
            bump_type: Type of version bump or specific version
            update_changelog: Whether to update CHANGELOG.md
        """
        current_version = self.read_current_version()
        new_version = self.bump_version(current_version, bump_type)

        print(f"\nBumping version: {current_version} → {new_version}\n")

        # Confirm with user
        response = input(f"Update version to {new_version}? [y/N]: ")
        if response.lower() not in ("y", "yes"):
            print("Aborted.")
            return

        # Update all files
        self.update_version_file(new_version)
        self.update_pyproject(new_version)
        self.update_init_file(new_version)

        if update_changelog:
            self.update_changelog(new_version, current_version)

        print(f"\n✅ Successfully bumped version to {new_version}")
        print("\nNext steps:")
        print("1. Review the changes with: git diff")
        print(f"2. Commit the changes: git commit -am 'chore: bump version to {new_version}'")
        print(f"3. Create a git tag: git tag -a v{new_version} -m 'Release v{new_version}'")
        print("4. Push changes: git push && git push --tags")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    bump_type = sys.argv[1]
    project_root = Path(__file__).parent.parent

    bumper = VersionBumper(project_root)

    try:
        bumper.run(bump_type)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
