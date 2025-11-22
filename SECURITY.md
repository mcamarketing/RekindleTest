# Security & Compliance Documentation

## Overview

RekindlePro Rex system implements production-grade security following OWASP Top 10, GDPR, and SOC 2 best practices.

## Security Architecture

### 1. Authentication & Authorization

#### Supabase Row-Level Security (RLS)
- **Multi-tenant isolation**: All tables include `user_id` column with RLS policies
- **Role-based access control (RBAC)**: Users can only access their own data
- **JWT-based authentication**: Secure token-based auth with automatic expiration

```sql
-- Example RLS policy
CREATE POLICY "Users can only access own missions"
ON rex_missions FOR SELECT
USING (auth.uid() = user_id);
```

#### API Security
- **API key rotation**: Automated rotation every 90 days
- **Rate limiting**: 100 requests/minute per user
- **Request signing**: HMAC-SHA256 signing for webhook callbacks

### 2. Data Protection

#### Encryption
- **At rest**: AES-256 encryption for database (Supabase default)
- **In transit**: TLS 1.3 for all API communications
- **Secrets management**: Environment variables, never committed to git
  - All secrets stored in `.env` file (gitignored)
  - `.env.rex.example` template provided for setup
  - Docker Compose requires passwords to be set (no weak defaults)
  - Password generation: `openssl rand -base64 32`
- **PII redaction**: Automatic redaction before LLM calls

#### Data Retention
- **Mission logs**: 90 days rolling retention
- **Analytics data**: 12 months aggregated, then archived
- **PII data**: Deleted within 30 days of user account deletion

### 3. Input Validation & Sanitization

#### Backend Validation
- **Pydantic models**: All API inputs validated with Pydantic
- **SQL injection prevention**: Parameterized queries only (Supabase SDK)
- **XSS prevention**: HTML sanitization for user-generated content

```python
# Example validation
class CreateMissionRequest(BaseModel):
    user_id: str = Field(..., regex=r'^[a-zA-Z0-9-]{36}$')
    type: MissionTypeEnum = Field(...)
    priority: int = Field(..., ge=0, le=100)
```

#### Frontend Validation
- **Input sanitization**: DOMPurify for HTML content
- **CSRF protection**: SameSite cookies + CSRF tokens
- **Content Security Policy (CSP)**: Strict CSP headers

### 4. Error Handling

#### Secure Error Messages
- **Production**: Generic error messages, no stack traces
- **Development**: Detailed errors for debugging
- **Logging**: Structured logging without PII

```python
# Secure error handling
try:
    result = await agent.execute()
except Exception as e:
    logger.error(f"Agent execution failed: {type(e).__name__}")
    return {"error": "An error occurred processing your request"}
```

### 5. Third-Party Integrations

#### API Key Management
- **Environment variables**: All keys stored in env vars
- **Key rotation**: Automated quarterly rotation
- **Least privilege**: Scoped API keys with minimum permissions

#### Webhook Security
- **Signature verification**: HMAC validation for all webhooks
- **Replay protection**: Timestamp validation (5-minute window)
- **IP whitelisting**: Restrict webhook sources

```python
def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)
```

### 6. LLM Security

#### Prompt Injection Prevention
- **Input validation**: Strict validation before LLM calls
- **Context isolation**: Separate system prompts from user input
- **Output validation**: Validate LLM responses before execution

#### PII Redaction
```python
def redact_pii(context: Dict[str, Any]) -> Dict[str, Any]:
    sensitive_keys = {'email', 'phone', 'ssn', 'credit_card'}
    for key in sensitive_keys:
        if key in context:
            context[key] = '[REDACTED]'
    return context
```

### 7. Infrastructure Security

#### Docker Security
- **Non-root user**: All containers run as non-root
- **Minimal base images**: Alpine/slim images only
- **Vulnerability scanning**: Trivy scanning in CI/CD
- **Read-only filesystems**: Where possible

```dockerfile
# Security best practices
RUN useradd -m -u 1000 rexuser
USER rexuser
HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:8000/health
```

#### Network Security
- **Private networks**: Database and Redis on private network
- **Firewall rules**: Restrict inbound traffic to necessary ports
- **DDoS protection**: Cloudflare/CloudArmor for DDoS mitigation

## Compliance

### GDPR Compliance

#### Right to Access
- **Data export**: Users can export all their data via API
- **Data portability**: JSON format export

#### Right to Deletion
- **Account deletion**: Cascade delete all user data
- **Data retention**: 30-day retention after deletion request

#### Right to Rectification
- **Data correction**: Users can update all personal data
- **Audit trail**: Track all data modifications

### SOC 2 Type II Controls

#### Access Control (CC6.1)
- **MFA required**: For all admin accounts
- **Session management**: 30-minute timeout for inactivity
- **Access logs**: All access logged and monitored

#### Change Management (CC8.1)
- **Code review**: All changes require PR review
- **Automated testing**: CI/CD with 80%+ coverage
- **Deployment approval**: Production deploys require approval

#### Monitoring (CC7.2)
- **Application monitoring**: Real-time error tracking (Sentry)
- **Performance monitoring**: APM with New Relic/Datadog
- **Security monitoring**: Intrusion detection with Wazuh

## Incident Response

### Security Incident Process

1. **Detection**: Automated alerts via monitoring
2. **Assessment**: Severity classification (P0-P4)
3. **Containment**: Isolate affected systems
4. **Eradication**: Remove threat, patch vulnerabilities
5. **Recovery**: Restore normal operations
6. **Post-mortem**: Document lessons learned

### Breach Notification
- **Timeline**: Notification within 72 hours (GDPR requirement)
- **Communication**: Email to affected users + status page
- **Remediation**: Free credit monitoring if PII exposed

## Security Checklist

### Pre-Production
- [ ] All secrets in environment variables
- [ ] RLS policies enabled on all tables
- [ ] HTTPS enforced (HSTS enabled)
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] Error messages sanitized
- [ ] Logging configured (no PII)
- [ ] Security headers configured (CSP, X-Frame-Options, etc.)
- [ ] Dependency vulnerability scan passed
- [ ] Penetration test completed

### Ongoing
- [ ] Weekly dependency updates
- [ ] Monthly security scans
- [ ] Quarterly penetration testing
- [ ] Annual security audit
- [ ] Continuous monitoring alerts

## Security Contacts

- **Security Team**: security@rekindlepro.ai
- **Bug Bounty**: https://hackerone.com/rekindlepro
- **Responsible Disclosure**: 90-day disclosure policy

## Version History

- **v1.0.0** (2025-01-22): Initial security documentation
- Last updated: 2025-01-22
