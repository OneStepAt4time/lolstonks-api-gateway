# Git Flow Branching Strategy

This document outlines the Git Flow branching strategy used for the LOLStonks API Gateway project.

## Branch Structure

We follow a modified Git Flow workflow optimized for continuous delivery and GitHub Flow best practices.

```
main (production)
  |
  └── develop (integration)
        |
        ├── feature/tournament-api
        ├── fix/cache-timeout
        ├── hotfix/security-patch
        └── refactor/user-model
```

## Primary Branches

### `main` Branch
- **Purpose**: Production-ready code
- **Protection**: Branch protection rules enabled
- **Deployment**: Automatic deployment to production on merge
- **Status**: Always deployable, passing all tests
- **Tags**: Semantic versioning tags (e.g., `v1.0.0`, `v1.1.0`)

### `develop` Branch
- **Purpose**: Integration branch for features
- **Base branch**: For all feature and fix branches
- **Status**: Should always be stable and passing tests
- **Deployment**: Automatic deployment to staging environment
- **Merge target**: Features merge into `develop`, not `main`

## Supporting Branches

### `feature/*` Branches
- **Purpose**: Develop new features
- **Naming**: `feature/<feature-name>` or `feature/<ticket-id>-<short-desc>`
- **Source**: Branch from `develop`
- **Merge target**: Merge back into `develop`
- **Examples**:
  ```
  feature/tournament-api
  feature/123-spectator-mode
  feature/rate-limiting
  ```

### `fix/*` Branches
- **Purpose**: Bug fixes for non-urgent issues
- **Naming**: `fix/<bug-description>` or `fix/<ticket-id>-<short-desc>`
- **Source**: Branch from `develop`
- **Merge target**: Merge back into `develop`
- **Examples**:
  ```
  fix/cache-timeout
  fix/456-redis-connection
  fix/invalid-response-handling
  ```

### `hotfix/*` Branches
- **Purpose**: Urgent production fixes
- **Naming**: `hotfix/<issue-description>`
- **Source**: Branch from `main`
- **Merge target**: Merge into BOTH `main` AND `develop`
- **Examples**:
  ```
  hotfix/security-vulnerability
  hotfix/critical-api-failure
  hotfix/data-corruption
  ```

### `refactor/*` Branches
- **Purpose**: Code refactoring without behavior changes
- **Naming**: `refactor/<description>`
- **Source**: Branch from `develop`
- **Merge target**: Merge back into `develop`
- **Examples**:
  ```
  refactor/extract-cache-layer
  refactor/standardize-error-handling
  ```

### `docs/*` Branches
- **Purpose**: Documentation-only changes
- **Naming**: `docs/<description>`
- **Source**: Branch from `develop`
- **Merge target**: Merge back into `develop`
- **Examples**:
  ```
  docs/update-api-guide
  docs/add-troubleshooting-section
  ```

### `test/*` Branches
- **Purpose**: Adding or improving tests
- **Naming**: `test/<description>`
- **Source**: Branch from `develop`
- **Merge target**: Merge back into `develop`
- **Examples**:
  ```
  test/add-integration-tests
  test/improve-coverage
  ```

## Workflow Rules

### Starting New Work

1. **Always branch from the appropriate base**:
   - Features and fixes → from `develop`
   - Hotfixes → from `main`

2. **Create descriptive branch names**:
   ```bash
   # Good
   git checkout -b feature/tournament-api

   # Bad
   git checkout -b my-branch
   ```

3. **Keep branches focused**:
   - One branch should address one issue/feature
   - Small, focused pull requests are easier to review

### During Development

1. **Commit frequently** with meaningful messages:
   ```bash
   # Follow Conventional Commits
   feat: add Tournament API router
   fix: resolve Redis connection timeout
   docs: update API documentation
   test: add integration tests for caching
   ```

2. **Keep branches updated**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout feature/tournament-api
   git merge develop
   ```

3. **Run tests before pushing**:
   ```bash
   make test-quick
   make lint
   make format
   ```

### Creating Pull Requests

1. **Target the correct branch**:
   - `feature/*` → merge into `develop`
   - `fix/*` → merge into `develop`
   - `hotfix/*` → merge into `main` AND `develop`

2. **Fill out the PR template**:
   - Summary of changes
   - Related issues
   - Verification steps
   - Checklist completed

3. **Ensure CI passes**:
   - All tests must pass
   - Code coverage maintained
   - No linting errors

4. **Get review approval**:
   - At least one maintainer approval required
   - Address all review feedback

### After Merge

1. **Delete your branch** after merge:
   ```bash
   git branch -d feature/tournament-api
   git push origin --delete feature/tournament-api
   ```

2. **Update local `develop`**:
   ```bash
   git checkout develop
   git pull origin develop
   ```

## Release Process

### Pre-release Checklist

1. All tests passing
2. Documentation updated
3. CHANGELOG.md updated
4. Version number incremented
5. Tag created

### Creating a Release

1. **From `develop` to `main`**:
   ```bash
   git checkout main
   git merge develop
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin main --tags
   ```

2. **GitHub Actions will**:
   - Run full test suite
   - Build Docker image
   - Deploy to production
   - Create GitHub Release

### Post-release

1. **Update `develop` with release changes**:
   ```bash
   git checkout develop
   git merge main
   ```

2. **Start next development cycle**

## Branch Protection Rules

### `main` Branch
- Require pull request reviews (1 approval)
- Require status checks to pass:
  - `ci`
  - `test-quick`
  - `lint`
- Require branches to be up to date
- Restrict who can push (maintainers only)

### `develop` Branch
- Require pull request reviews (1 approval)
- Require status checks to pass
- Require branches to be up to date

## Emergency Procedures

### Hotfix Workflow

When a critical bug is found in production:

1. **Create hotfix from `main`**:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/critical-security-fix
   ```

2. **Implement fix** (minimal changes only)

3. **Test thoroughly**

4. **Merge to `main`**:
   - Create PR to `main`
   - Expedited review
   - Merge immediately

5. **Merge to `develop`**:
   ```bash
   git checkout develop
   git merge hotfix/critical-security-fix
   git push origin develop
   ```

6. **Tag and deploy**:
   ```bash
   git checkout main
   git tag -a v1.0.1 -m "Hotfix: critical security fix"
   git push origin main --tags
   ```

## Best Practices

### DO's
- Write clear, descriptive commit messages
- Keep branches focused on a single issue
- Update branches frequently with `develop`
- Run tests before pushing
- Fill out PR templates completely
- Delete merged branches
- Tag releases properly

### DON'Ts
- Don't commit directly to `main` or `develop`
- Don't let branches diverge too far from `develop`
- Don't create huge pull requests
- Don't merge without review
- Don't skip tests
- Don't leave stale branches
- Don't use unclear branch names

## CI/CD Integration

The GitHub Actions workflows enforce this branching strategy:

- `ci.yml` - Runs on all branches
- `release-production.yml` - Only runs on `main`
- `release-develop.yml` - Only runs on `develop`
- Branch protection ensures rules are followed

## Quick Reference

| Task | Branch | Command |
|------|--------|---------|
| Start feature | `develop` | `git checkout -b feature/name` |
| Start fix | `develop` | `git checkout -b fix/name` |
| Start hotfix | `main` | `git checkout -b hotfix/name` |
| Update branch | - | `git merge develop` |
| Create PR | - | GitHub UI / `gh pr create` |
| Delete branch | - | `git branch -d branch-name` |

## Additional Resources

- [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

---

**Last Updated**: 2025-01-29
