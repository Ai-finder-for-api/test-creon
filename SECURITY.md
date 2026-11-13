# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

Security issues and vulnerabilities should be reported directly via GitHub Issues or to the Quantum Suite security team.
All reported vulnerabilities will receive an acknowledgment within 24 hours.

### Security Principles
- **Local Isolation**: The mock HTTP server binds strictly to `127.0.0.1` (loopback only) by default, preventing external exposure.
- **Zero Telemetry**: No tracking, analytics, or outbound telemetry is gathered or transmitted.
- **Environment Secret Redaction**: Sensitive headers and tokens stored in Environment variables are held in memory and never logged to disk without explicit user export.