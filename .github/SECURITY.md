# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

**Note**: We recommend always using the latest stable release.

## Reporting a Vulnerability

We take the security of LOLStonks API Gateway seriously. If you discover a security vulnerability, please follow these steps:

### 1. **DO NOT** Open a Public Issue

Please do **not** report security vulnerabilities through public GitHub issues, discussions, or pull requests.

### 2. Report Privately

Instead, please report security vulnerabilities by:

**Option A: GitHub Security Advisories (Preferred)**
- Go to the [Security tab](https://github.com/OneStepAt4time/lolstonks-api-gateway/security/advisories)
- Click "Report a vulnerability"
- Fill out the form with details

**Option B: Email**
- Contact the repository maintainers directly
- Use the contact information from the repository owner's profile

### 3. Include the Following Information

Please include as much of the following information as possible:

- **Type of vulnerability** (e.g., SQL injection, XSS, authentication bypass)
- **Affected component(s)** (e.g., specific file, endpoint, or feature)
- **Step-by-step instructions** to reproduce the issue
- **Proof of concept** or exploit code (if applicable)
- **Impact assessment** - how an attacker might exploit this
- **Suggested fix** (if you have one)
- **Your contact information** for follow-up questions

### Example Report Template

```
**Summary**: Brief description of the vulnerability

**Severity**: Critical / High / Medium / Low

**Affected Component**:
- File: app/routers/example.py
- Function: vulnerable_function()
- Endpoint: /api/vulnerable

**Steps to Reproduce**:
1. Step one
2. Step two
3. Step three

**Expected Behavior**: What should happen

**Actual Behavior**: What actually happens (the vulnerability)

**Impact**:
- What data could be exposed
- What actions could an attacker perform
- Who is affected

**Proof of Concept**:
[Code or steps demonstrating the vulnerability]

**Suggested Fix**:
[Your recommendation, if any]

**Environment**:
- Version: 1.0.0
- OS: Ubuntu 22.04
- Python: 3.12
```

## Response Timeline

We aim to respond to security reports according to the following timeline:

| Stage | Timeline |
|-------|----------|
| **Initial Response** | Within 48 hours |
| **Vulnerability Confirmation** | Within 5 business days |
| **Fix Development** | Depends on severity |
| **Patch Release** | As soon as safely possible |
| **Public Disclosure** | After patch is available |

### Severity Levels

- **Critical**: Immediate action required (e.g., remote code execution, authentication bypass)
- **High**: Fix within 7 days (e.g., SQL injection, sensitive data exposure)
- **Medium**: Fix within 30 days (e.g., XSS, CSRF)
- **Low**: Fix in next release (e.g., information disclosure, minor security issues)

## Disclosure Policy

- **Coordinated Disclosure**: We prefer coordinated disclosure where we work together to fix the issue before public disclosure
- **Public Disclosure**: After a fix is released, we will publish a security advisory on GitHub
- **CVE Assignment**: For significant vulnerabilities, we will request a CVE identifier
- **Credit**: With your permission, we will credit you in the security advisory

## What to Expect

After you submit a vulnerability report:

1. **Acknowledgment**: We'll confirm receipt within 48 hours
2. **Assessment**: We'll assess the vulnerability and its severity
3. **Communication**: We'll keep you informed of our progress
4. **Fix Development**: We'll work on a patch
5. **Testing**: We'll test the fix thoroughly
6. **Release**: We'll release a patched version
7. **Advisory**: We'll publish a security advisory
8. **Credit**: We'll credit you (if you wish) in the advisory

## Security Best Practices for Users

While we work to keep the codebase secure, users should also follow security best practices:

### API Key Security
- Never commit API keys to version control
- Use environment variables for sensitive data
- Rotate API keys regularly (every 20-25 days for Riot API)
- Use separate keys for development and production

### Deployment Security
- Use HTTPS in production (configure Nginx/reverse proxy)
- Keep dependencies up to date (`uv pip install -U -e .`)
- Use strong passwords for Redis
- Configure firewall rules appropriately
- Run as non-root user in production

### Monitoring
- Enable logging and monitor for suspicious activity
- Set up alerts for unusual patterns
- Regularly review access logs

For detailed security configuration, see the [Security Best Practices](https://onestepat4time.github.io/lolstonks-api-gateway/operations/security/) documentation.

## Scope

### In Scope

The following are in scope for vulnerability reports:

- Authentication and authorization issues
- SQL injection, XSS, CSRF vulnerabilities
- Remote code execution
- Sensitive data exposure
- Rate limiting bypass
- Cache poisoning
- Server-side request forgery (SSRF)
- Insecure dependencies with known vulnerabilities

### Out of Scope

The following are generally out of scope:

- Issues in third-party dependencies (report to the dependency maintainers)
- Riot Games API vulnerabilities (report to Riot Games)
- Social engineering attacks
- Physical attacks
- Issues requiring unusual user interaction
- Theoretical vulnerabilities without proof of concept
- Vulnerabilities in end-of-life versions

## Bug Bounty Program

**Current Status**: We do not currently offer a bug bounty program.

However, we greatly appreciate responsible disclosure and will:
- Acknowledge your contribution publicly (with your permission)
- Credit you in our security advisories
- Provide recognition in our contributors list

## Security Updates

To stay informed about security updates:

- **Watch** this repository for security advisories
- Enable **notifications** for security alerts on GitHub
- Check the [Releases](https://github.com/OneStepAt4time/lolstonks-api-gateway/releases) page regularly
- Follow security advisories on the [Security tab](https://github.com/OneStepAt4time/lolstonks-api-gateway/security)

## Contact

For security-related questions that are not vulnerabilities:
- Open a [Discussion](https://github.com/OneStepAt4time/lolstonks-api-gateway/discussions)
- Review the [Security Documentation](https://onestepat4time.github.io/lolstonks-api-gateway/operations/security/)

---

**Thank you for helping keep LOLStonks API Gateway and its users safe!**

*Last Updated: 2025-10-29*
