# Release Approval Setup

This guide explains how to configure production release approval gates in GitHub to ensure that production releases require manual approval before deployment.

## Overview

The production release workflow includes an approval gate that requires manual review before creating a GitHub release and deploying to production. This prevents accidental releases and ensures proper oversight for production deployments.

## Setting Up the Production Environment

To enable release approval gates, you need to configure a protected environment in your GitHub repository.

### Step 1: Navigate to Environment Settings

1. Go to your GitHub repository
2. Click on **Settings** (top navigation bar)
3. In the left sidebar, click on **Environments**
4. Click **New environment**

### Step 2: Create Production Environment

1. Enter the environment name: `production`
2. Click **Configure environment**

### Step 3: Configure Protection Rules

Configure the following protection rules for the production environment:

#### Required Reviewers

1. Check **Required reviewers**
2. Add team members or teams who should approve production releases
3. Recommended: Add at least 1-2 senior team members
4. You can add up to 6 reviewers

**Best Practice**: Choose reviewers who:
- Understand the release process
- Can verify changelog and release notes
- Have authority to approve production deployments
- Are available during your release windows

#### Wait Timer (Optional)

1. Check **Wait timer** if you want a mandatory delay
2. Set the number of minutes to wait before deployment
3. Recommended: 5-30 minutes for critical releases
4. This gives time for last-minute checks or cancellations

**Use Case**: Useful for scheduled releases or when you want a "cooling off" period.

#### Deployment Branches (Recommended)

1. Under **Deployment branches**, select **Selected branches**
2. Add branch pattern: `refs/tags/v*`
3. This ensures only version tags can trigger production releases

### Step 4: Environment Secrets (Optional)

If you need production-specific secrets (e.g., notification webhooks):

1. Scroll to **Environment secrets**
2. Click **Add secret**
3. Add secrets like:
   - `SLACK_WEBHOOK_URL`
   - `DISCORD_WEBHOOK_URL`
   - `TEAMS_WEBHOOK_URL`

These will only be available during production deployments.

## Complete Configuration Example

Here's a recommended production environment configuration:

```yaml
Environment Name: production

Protection Rules:
  ✓ Required reviewers: 2 reviewers
    - @tech-lead
    - @senior-engineer-1
    - @senior-engineer-2

  ✓ Wait timer: 10 minutes

  ✓ Deployment branches: Selected branches
    - refs/tags/v*

Environment Secrets:
  - SLACK_WEBHOOK_URL
  - NOTIFICATION_EMAIL
```

## How Approval Works

### Release Process with Approval

1. **Developer creates a release tag** (e.g., `v2.1.0`)
   ```bash
   git tag -a v2.1.0 -m "Release v2.1.0"
   git push --tags
   ```

2. **Automated validation runs**
   - Version consistency checks
   - Changelog validation
   - Tests, linting, security scans

3. **Approval gate triggers**
   - Workflow pauses at the `create-release` job
   - Configured reviewers receive notification
   - GitHub shows "Waiting for approval" status

4. **Reviewer approves or rejects**
   - Reviewer goes to Actions tab
   - Reviews the workflow run
   - Checks release notes and test results
   - Clicks "Review deployments"
   - Approves or rejects the deployment

5. **Deployment proceeds (if approved)**
   - GitHub Release is created
   - Docker image is built and pushed
   - Image security scan runs
   - Deployment health checks run
   - Release notifications sent (if configured)

### Approval Notification

Reviewers will receive notifications via:
- GitHub web notifications (bell icon)
- Email (if enabled in GitHub settings)
- GitHub mobile app (if installed)

## Reviewer Responsibilities

When reviewing a production release, check:

### 1. Version and Tag
- ✅ Version number follows semantic versioning
- ✅ Version matches CHANGELOG.md entry
- ✅ Tag format is correct (v1.2.3)

### 2. Changelog
- ✅ CHANGELOG.md has detailed entry for this version
- ✅ All changes are documented
- ✅ Breaking changes are clearly marked
- ✅ Migration instructions included (if needed)

### 3. Test Results
- ✅ All tests passed
- ✅ Code coverage is acceptable
- ✅ Linting checks passed
- ✅ Security scans passed

### 4. Build Validation
- ✅ Build completed successfully
- ✅ No dependency issues
- ✅ Type checking passed

### 5. Timing and Context
- ✅ Release timing is appropriate
- ✅ No ongoing incidents
- ✅ Team is available for monitoring
- ✅ Rollback plan is understood

## Viewing Pending Approvals

### For Reviewers

1. Go to the **Actions** tab in GitHub
2. Click on the running workflow
3. You'll see "Review pending deployments"
4. Click **Review deployments**
5. Select the environment to approve
6. Add an optional comment
7. Click **Approve and deploy** or **Reject**

### For Release Creators

1. Go to the **Actions** tab
2. Find your workflow run
3. You'll see "Waiting for approval from required reviewers"
4. Monitor status and wait for approval
5. You can cancel the workflow if needed

## Approval Best Practices

### For Teams

1. **Define Release Windows**: Schedule releases during specific times
2. **Rotation Policy**: Rotate reviewer responsibilities
3. **On-call Alignment**: Align releases with on-call schedules
4. **Communication**: Use Slack/Teams to coordinate approvals
5. **Documentation**: Keep release runbooks updated

### For Reviewers

1. **Timely Reviews**: Review within 15-30 minutes during release windows
2. **Ask Questions**: Don't approve if unsure
3. **Check Dependencies**: Verify external service compatibility
4. **Verify Rollback**: Ensure rollback procedures are ready
5. **Document Decisions**: Add comments explaining approval/rejection

### For Release Managers

1. **Pre-announce**: Notify team before pushing release tag
2. **Staging First**: Always deploy to staging before production
3. **Monitor Ready**: Be ready to monitor after approval
4. **Rollback Ready**: Have rollback plan ready
5. **Communication**: Update team on release status

## Bypassing Approval (Emergency Only)

In true emergencies, repository admins can bypass approval gates:

1. Go to repository **Settings** → **Environments** → **production**
2. Temporarily uncheck **Required reviewers**
3. Allow the workflow to proceed
4. **IMPORTANT**: Re-enable protection immediately after emergency
5. Document the bypass in a post-mortem

**Warning**: Only use bypass for critical security patches or severe production issues.

## Automating Development Releases

Development releases (dev, alpha, beta, rc) do NOT require approval and run automatically. This allows for rapid iteration and testing.

```bash
# Development release - no approval required
git tag -a v2.1.0-dev.1 -m "Development release"
git push --tags
```

## Troubleshooting

### Approval Not Triggering

**Problem**: Workflow runs but doesn't wait for approval

**Solutions**:
1. Verify environment name is exactly `production` (case-sensitive)
2. Check that environment exists in Settings → Environments
3. Ensure required reviewers are configured
4. Verify deployment branch patterns include `refs/tags/v*`

### Wrong Reviewers Notified

**Problem**: Unexpected people receiving approval requests

**Solutions**:
1. Check reviewers list in environment settings
2. Remove team members who shouldn't review
3. Consider using GitHub teams instead of individuals

### Approval Timeout

**Problem**: Workflow times out waiting for approval

**Solutions**:
1. GitHub workflows timeout after 6 hours by default
2. Ensure reviewers are notified and available
3. Consider adding slack/email notifications
4. Set up backup reviewers

### Can't Approve Own Release

**Problem**: You pushed the tag and want to approve your own release

**Solutions**:
1. This is intentional - prevents self-approval
2. Add other team members as reviewers
3. For solo projects, you can configure environment to allow self-approval (not recommended)

## Monitoring and Metrics

Track these metrics to improve your release process:

- **Approval Time**: Time from tag push to approval
- **Rejection Rate**: % of releases rejected
- **Rollback Rate**: % of releases requiring rollback
- **Release Frequency**: Number of releases per week/month

Use GitHub Actions logs and releases page to gather this data.

## Summary

Production approval gates provide:
- ✅ Manual oversight for production releases
- ✅ Time for final verification
- ✅ Team awareness of deployments
- ✅ Audit trail of who approved what
- ✅ Emergency stop mechanism

This is a critical safety mechanism for production deployments and should be configured for all production environments.
