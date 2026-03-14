# Security Policy

## Reporting a Vulnerability

**Please do NOT publicly disclose security vulnerabilities.** We take security seriously and will address reported vulnerabilities promptly.

### How to Report

If you discover a security vulnerability in Dual-RAG-Evaluator, please send an email to:
- **Email**: security@example.com (Replace with actual contact)
- **GitHub Security Advisory**: Use GitHub's [Private Vulnerability Reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities)

### What to Include

Please provide the following information:

1. **Type of vulnerability** (e.g., SQL injection, XSS, authentication bypass, etc.)
2. **Location** (file, line number, or module)
3. **Description** of the vulnerability
4. **Steps to reproduce** the issue
5. **Potential impact** of the vulnerability
6. **Suggested remediation** (if you have one)

### Response Timeline

We aim to:
- **Acknowledge** your report within 48 hours
- **Provide initial assessment** within 1 week
- **Release a fix** or mitigation plan within 30 days for critical vulnerabilities
- **Credit you** for the discovery (if desired)

## Supported Versions

Security updates are available for:

| Version | Supported | Support Until |
|---------|-----------|---------------|
| 1.0.x   | ✅ Yes    | 2025-12-31   |
| < 1.0   | ❌ No     | N/A          |

## Security Best Practices

When using Dual-RAG-Evaluator:

### 1. Environment Variables
- Never commit `.env` files to version control
- Use `.env.template` for configuration templates
- Store sensitive data (API keys, credentials) in environment variables, not in code

### 2. Document Handling
- Only upload trusted documents (PDFs, DOCX, TXT, Markdown)
- Be aware of file size limits (10MB by default)
- Documents are processed locally; no external transmission

### 3. Virtual Environments
- Always use virtual environments (Python venv, conda, etc.)
- Keep Python packages updated: `pip install --upgrade pip`

### 4. Dependencies
- Review `requirements.txt` and `requirements-dev.txt`
- Keep dependencies updated for security patches
- Run `safety check` periodically: `pip install safety && safety check`

### 5. Access Control
- Protect access to your computer and files
- Restrict who can launch the GUI application
- Consider containerization (Docker) for isolated environments

### 6. Data Protection
- ChromaDB stores embeddings locally in `data/embeddings/`
- Ensure proper file system permissions on sensitive directories
- Regular backups of cached results

## Known Vulnerabilities

None currently reported. For latest updates, check:
- [GitHub Security Advisories](https://github.com/Srini235/Dual-RAG-Evaluator/security)
- [CVE Database](https://cve.mitre.org/)

## Dependency Security

We use:
- **Automated checks** via GitHub's Dependabot
- **Pre-commit hooks** for code quality
- **Regular security audits** of dependencies

## Security Features

- **No external data transmission** (processing is local)
- **No authentication required** (desktop application)
- **No network services** exposed by default
- **File access restrictions** via system permissions
- **Configuration validation** via `.env` schema

## Responsible Disclosure

We follow the principle of:
1. **Confidentiality**: Keep vulnerability details confidential until patch is released
2. **Integrity**: Coordinate with the project to ensure responsible fix
3. **Availability**: Minimize service disruption through coordinated release

## Security Checklist for Deployment

- [ ] Review and update `.env` configuration
- [ ] Verify file system permissions (especially `data/` directories)
- [ ] Keep Python and dependencies up to date
- [ ] Run security checks: `safety check`, `bandit -r src`
- [ ] Enable logging and monitor for suspicious activity
- [ ] Restrict physical access to the machine running the application
- [ ] Regular backups of important results and configurations
- [ ] Test disaster recovery procedures

## Questions?

For security-related questions, contact security@example.com (Replace with actual contact)

For general questions, refer to [README.md](README.md) or open an issue on GitHub.

---

Thank you for taking security seriously and helping keep Dual-RAG-Evaluator safe!
