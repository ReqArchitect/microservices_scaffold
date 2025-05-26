# This file has been moved to docs/README.md
# For full documentation, see docs/README.md

[//]: # (Symlink for GitHub visibility) 

## Badges

![Coverage](https://github.com/ReqArchitect/microservices_scaffold/actions/workflows/ci.yml/badge.svg)
![Security](https://github.com/ReqArchitect/microservices_scaffold/actions/workflows/security.yml/badge.svg)
![Contract Tests](https://github.com/ReqArchitect/microservices_scaffold/actions/workflows/contract.yml/badge.svg)

## Test Strategy

- **Unit, integration, and contract tests** for all services
- **RBAC and multi-tenant matrix** for all endpoints
- **Audit log and metrics assertions**
- **Security, rate limiting, and chaos/fault injection**
- **Test data isolation and cleanup**

### Running Tests

```bash
make test  # runs all tests
make contract-test  # runs contract tests
make security-scan  # runs Bandit/Trivy
```

See `docs/DEVELOPER_GUIDE.md` for advanced scenarios and troubleshooting. 