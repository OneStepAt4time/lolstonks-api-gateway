# Pull Request

## Type of Change
- [ ] Feature (non-breaking change)
- [ ] Bug fix (non-breaking change)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] Test improvement
- [ ] Hotfix (urgent production fix)

## Summary
Brief description of the changes and the problem being solved.

## Related Issues
- Fixes # (issue)
- Related to # (issue)
- Closes # (issue)

## Changes Made
Describe the changes in detail:
- What changed and why
- Technical approach
- Key implementation details

## Breaking Changes
If this PR introduces breaking changes, describe them:
- API changes
- Configuration changes
- Migration steps required

## Verification
Describe how you verified the changes:
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing steps
- [ ] Screenshots/logs (if applicable)

## Testing
```bash
# Commands to verify the changes
make test-quick
make lint
# Add specific test commands if applicable
```

## Documentation
- [ ] Code is self-documenting with clear comments
- [ ] API documentation updated (if API changes)
- [ ] CHANGELOG.md updated (for user-facing changes)
- [ ] Architecture docs updated (if architectural changes)

## Checklist
- [ ] My code follows the project's style guidelines (run `make format && make lint`)
- [ ] I have performed a self-review of my code
- [ ] I have commented my code where necessary
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing tests pass locally with `make test-quick`
- [ ] Any dependent changes have been merged and published
- [ ] I have checked my code for correct error handling
- [ ] I have considered edge cases and input validation

## Additional Notes
Any additional context, screenshots, or information that reviewers should know.

## Deployment Notes
Special considerations for deployment:
- Database migrations required?
- Configuration changes required?
- Feature flags?
- Rollback plan?
