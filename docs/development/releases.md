# Release Management

Complete guide to creating and managing releases for LOLStonks API Gateway.

## Table of Contents

- [Release Types](#release-types)
- [Release Process](#release-process)
- [Automated Workflows](#automated-workflows)
- [Version Tagging](#version-tagging)
- [Git Hooks](#git-hooks)
- [Docker Images](#docker-images)

## Release Types

The project supports two types of releases:

### 1. Production Releases

Production releases are stable, tested versions intended for production use.

**Tag Format:** `v{MAJOR}.{MINOR}.{PATCH}`
- Examples: `v2.0.0`, `v2.1.0`, `v2.0.1`

**Requirements:**
- ✅ All tests must pass
- ✅ VERSION file must match tag
- ✅ pyproject.toml version must match tag
- ✅ app/__init__.py version must match tag
- ✅ CHANGELOG.md must have entry for version
- ✅ Code must be linted and formatted

**Docker Tags:**
- `latest`
- `v{VERSION}`
- `{VERSION}`

### 2. Development/Pre-Release Versions

Development releases are for testing and preview purposes.

**Tag Formats:**
- **Development:** `v{MAJOR}.{MINOR}.{PATCH}-dev.{BUILD}`
  - Example: `v2.1.0-dev.1`, `v2.1.0-dev.2`
  - Purpose: Internal testing, continuous integration

- **Alpha:** `v{MAJOR}.{MINOR}.{PATCH}-alpha.{BUILD}`
  - Example: `v2.1.0-alpha.1`
  - Purpose: Early testing, incomplete features

- **Beta:** `v{MAJOR}.{MINOR}.{PATCH}-beta.{BUILD}`
  - Example: `v2.1.0-beta.1`
  - Purpose: Feature complete, bug fixing

- **Release Candidate:** `v{MAJOR}.{MINOR}.{PATCH}-rc.{BUILD}`
  - Example: `v2.1.0-rc.1`
  - Purpose: Final testing before production

**Requirements:**
- ✅ Tests should pass (warnings allowed)
- ⚠️ Version file match not strictly enforced
- ⚠️ CHANGELOG.md entry optional
- ✅ Marked as pre-release in GitHub

**Docker Tags:**
- `dev` / `alpha` / `beta` / `rc`
- `{FULL_VERSION}` (e.g., `2.1.0-dev.1`)

## Release Process

### Production Release

#### Step 1: Prepare Code

```bash
# Create feature branch
git checkout -b feature/my-feature develop

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/my-feature
```

#### Step 2: Update CHANGELOG

Add entries to `CHANGELOG.md`:

```markdown
## [Unreleased]

### Added
- New feature X
- New endpoint Y

### Fixed
- Bug in Z
```

#### Step 3: Bump Version

```bash
# Bump version (updates all files)
python scripts/bump_version.py minor  # 2.0.0 -> 2.1.0

# This updates:
# - VERSION
# - pyproject.toml
# - app/__init__.py
# - CHANGELOG.md (moves [Unreleased] to version section)
```

#### Step 4: Review and Commit

```bash
# Review changes
git diff

# Commit version bump
git add VERSION pyproject.toml app/__init__.py CHANGELOG.md
git commit -m "chore: bump version to 2.1.0"
```

#### Step 5: Merge to Main

```bash
# Merge to main branch
git checkout main
git merge develop
git push origin main
```

#### Step 6: Create Tag

```bash
# Create annotated tag
git tag -a v2.1.0 -m "Release v2.1.0

## Highlights
- New multi-provider architecture
- 76+ API endpoints
- Enhanced security monitoring

## Changes
See CHANGELOG.md for full details
"

# Push tag (triggers GitHub Actions)
git push origin v2.1.0
```

#### Step 7: Verify Release

GitHub Actions will automatically:
1. ✅ Validate version consistency
2. ✅ Run tests
3. ✅ Run linting
4. ✅ Create GitHub release
5. ✅ Build and push Docker images

Check: https://github.com/OneStepAt4time/lolstonks-api-gateway/releases

### Development Release

#### Quick Development Release

```bash
# Ensure you're on develop branch
git checkout develop

# Make and commit changes
git add .
git commit -m "feat: experimental feature"

# Push changes
git push origin develop

# Create development tag (no version bump needed)
git tag v2.1.0-dev.1
git push origin v2.1.0-dev.1
```

#### Structured Pre-Release Process

**Alpha Release:**
```bash
# Feature is started but incomplete
git tag -a v2.1.0-alpha.1 -m "Alpha release: Testing new provider system"
git push origin v2.1.0-alpha.1
```

**Beta Release:**
```bash
# Feature is complete, needs testing
git tag -a v2.1.0-beta.1 -m "Beta release: Provider system ready for testing"
git push origin v2.1.0-beta.1
```

**Release Candidate:**
```bash
# Final testing before production
git tag -a v2.1.0-rc.1 -m "Release candidate: Final testing"
git push origin v2.1.0-rc.1
```

**Production Release:**
```bash
# RC is approved, create production release
python scripts/bump_version.py 2.1.0
git commit -am "chore: bump version to 2.1.0"
git tag -a v2.1.0 -m "Release v2.1.0"
git push origin main --tags
```

## Automated Workflows

### Production Release Workflow

**Trigger:** Push tag matching `v[0-9]+.[0-9]+.[0-9]+`

**Workflow:** `.github/workflows/release-production.yml`

**Steps:**
1. **Validate Release**
   - Verify VERSION file matches tag
   - Verify pyproject.toml matches tag
   - Verify CHANGELOG.md has entry

2. **Build and Test**
   - Install dependencies
   - Run full test suite with coverage
   - Run linting (ruff, mypy)
   - Run security checks (bandit)

3. **Create GitHub Release**
   - Extract changelog entry
   - Create release with notes
   - Mark as latest release

4. **Build Docker Image**
   - Build multi-platform image
   - Push to GitHub Container Registry
   - Tag as `latest` and version

### Development Release Workflow

**Trigger:** Push tag matching `v*-dev.*`, `v*-alpha.*`, `v*-beta.*`, `v*-rc.*`

**Workflow:** `.github/workflows/release-develop.yml`

**Steps:**
1. **Validate Development Release**
   - Version mismatch allowed (warning only)
   - Detect release type

2. **Build and Test**
   - Run tests
   - Linting failures allowed

3. **Create Pre-release**
   - Generate changelog from commits
   - Create GitHub pre-release
   - Add warning about non-production use

4. **Build Docker Image**
   - Build and push with appropriate tags
   - Tag as `dev`/`alpha`/`beta`/`rc`

## Version Tagging

### Tag Naming Convention

```
v{MAJOR}.{MINOR}.{PATCH}[-{PRERELEASE}]

Examples:
v2.0.0          # Production
v2.1.0-dev.1    # Development
v2.1.0-alpha.1  # Alpha
v2.1.0-beta.1   # Beta
v2.1.0-rc.1     # Release Candidate
```

### Creating Tags

**Lightweight tag (not recommended):**
```bash
git tag v2.1.0
```

**Annotated tag (recommended):**
```bash
git tag -a v2.1.0 -m "Release message"
```

**Delete tag:**
```bash
# Local
git tag -d v2.1.0

# Remote
git push origin :refs/tags/v2.1.0
```

### Signing Tags

For production releases, use GPG-signed tags:

```bash
# Configure GPG
git config user.signingkey YOUR_GPG_KEY
git config tag.gpgSign true

# Create signed tag
git tag -s v2.1.0 -m "Release v2.1.0"

# Verify signature
git tag -v v2.1.0
```

## Git Hooks

### Pre-Push Hook

The project includes a pre-push hook that validates releases.

**Install:**
```bash
# Run setup script
bash scripts/setup-hooks.sh

# Or manually
git config core.hooksPath .githooks
chmod +x .githooks/pre-push
```

**What it checks:**

For production tags (`v{X}.{Y}.{Z}`):
- ✅ VERSION file matches tag
- ✅ pyproject.toml version matches tag
- ✅ app/__init__.py version matches tag
- ✅ CHANGELOG.md has entry

For development tags (`v{X}.{Y}.{Z}-{type}.{N}`):
- ℹ️ Shows warnings but allows push
- ⚠️ Reminds you it's a pre-release

**Bypass hook (if needed):**
```bash
git push --no-verify
```

### Hook Output Examples

**Success:**
```
Running pre-push hook...
Validating tag: v2.1.0
  Tag version: 2.1.0
  Production release tag detected
Validating production release requirements...
  ✓ VERSION file matches tag
  ✓ pyproject.toml version matches tag
  ✓ app/__init__.py version matches tag
  ✓ CHANGELOG.md has entry for 2.1.0
✅ All production release validations passed!
```

**Failure:**
```
Running pre-push hook...
Validating tag: v2.1.0
❌ Version mismatch!
  VERSION file: 2.0.0
  Git tag: 2.1.0

  Fix: python scripts/bump_version.py 2.1.0
```

## Docker Images

### Image Tags

**Production Release (`v2.1.0`):**
```
ghcr.io/onestepat4time/lolstonks-api-gateway:latest
ghcr.io/onestepat4time/lolstonks-api-gateway:2.1.0
ghcr.io/onestepat4time/lolstonks-api-gateway:v2.1.0
```

**Development Release (`v2.1.0-dev.1`):**
```
ghcr.io/onestepat4time/lolstonks-api-gateway:dev
ghcr.io/onestepat4time/lolstonks-api-gateway:2.1.0-dev.1
```

**Alpha Release (`v2.1.0-alpha.1`):**
```
ghcr.io/onestepat4time/lolstonks-api-gateway:alpha
ghcr.io/onestepat4time/lolstonks-api-gateway:2.1.0-alpha.1
```

### Using Docker Images

```bash
# Latest production
docker pull ghcr.io/onestepat4time/lolstonks-api-gateway:latest
docker run -p 8080:8080 ghcr.io/onestepat4time/lolstonks-api-gateway:latest

# Specific version
docker pull ghcr.io/onestepat4time/lolstonks-api-gateway:2.1.0
docker run -p 8080:8080 ghcr.io/onestepat4time/lolstonks-api-gateway:2.1.0

# Development version
docker pull ghcr.io/onestepat4time/lolstonks-api-gateway:dev
docker run -p 8080:8080 ghcr.io/onestepat4time/lolstonks-api-gateway:dev
```

## Rollback Procedure

If a release has critical issues:

### 1. Immediately Deploy Previous Version

```bash
# Docker
docker pull ghcr.io/onestepat4time/lolstonks-api-gateway:2.0.1
docker-compose down
docker-compose up -d

# Kubernetes
kubectl set image deployment/lolstonks-api lolstonks-api=ghcr.io/onestepat4time/lolstonks-api-gateway:2.0.1
```

### 2. Delete Bad Release

```bash
# Delete local tag
git tag -d v2.1.0

# Delete remote tag
git push origin :refs/tags/v2.1.0

# Delete GitHub release manually via web UI
```

### 3. Fix Issues and Re-release

```bash
# Fix the issue
git checkout -b hotfix/critical-bug

# Fix and commit
git commit -am "fix: critical bug"

# Merge to main
git checkout main
git merge hotfix/critical-bug

# Create new release
python scripts/bump_version.py 2.1.1
git commit -am "chore: bump version to 2.1.1"
git tag -a v2.1.1 -m "Hotfix: Fixed critical bug"
git push origin main --tags
```

## Best Practices

### Do's ✅

- **Always bump version before tagging**
- **Write meaningful changelog entries**
- **Test thoroughly before production releases**
- **Use pre-releases for testing new features**
- **Sign production tags with GPG**
- **Automate as much as possible**
- **Keep release notes clear and user-focused**

### Don'ts ❌

- **Don't skip version numbers** (2.0.0 → 2.2.0)
- **Don't reuse or move tags**
- **Don't release without tests passing**
- **Don't release without CHANGELOG entry**
- **Don't force-push tags**
- **Don't bypass hooks without good reason**

## Troubleshooting

### Hook Prevents Push

**Problem:** Pre-push hook blocks your tag push

**Solution:**
```bash
# Check what's wrong
python scripts/bump_version.py  # Shows current version

# Fix version files
python scripts/bump_version.py 2.1.0

# Or bypass if intentional
git push --no-verify
```

### Version Mismatch

**Problem:** Different versions in different files

**Solution:**
```bash
# Use bump script to sync all files
python scripts/bump_version.py 2.1.0

# Commit the changes
git add VERSION pyproject.toml app/__init__.py CHANGELOG.md
git commit -m "chore: sync versions to 2.1.0"
```

### GitHub Action Fails

**Problem:** Release workflow fails

**Solution:**
1. Check workflow logs in GitHub Actions
2. Verify all version files match
3. Ensure tests pass locally: `pytest`
4. Ensure linting passes: `ruff check app/`
5. Re-run failed jobs if it was a temporary issue

## Further Reading

- [Versioning Guide](./versioning.md)
- [Changelog Guide](./changelog-guide.md)
- [Contributing Guide](./contributing.md)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
