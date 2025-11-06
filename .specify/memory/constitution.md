<!--
Sync Impact Report:
- Version change: [template] → 1.0.0
- New constitution for Django + Tailwind CSS e-commerce platform
- Added principles: Security-First, API-First, Component-Driven UI, Test-Driven Development, Performance & Scalability
- Added sections: Security Requirements, Development Workflow
- Templates requiring updates: ✅ updated
- Follow-up TODOs: None
-->

# EShop Constitution

## Core Principles

### I. Security-First (NON-NEGOTIABLE)
Security MUST be implemented from day one, not retrofitted. All user data, payments, and personal information MUST be protected using industry-standard practices. Authentication and authorization MUST be implemented before any user-facing features. All inputs MUST be validated and sanitized. PCI DSS compliance considerations MUST guide payment handling design.

**Rationale**: E-commerce platforms handle sensitive customer data, payment information, and financial transactions. Security breaches can result in regulatory violations, financial losses, and complete loss of customer trust.

### II. API-First Architecture
All business logic MUST be exposed through well-documented REST APIs before any UI implementation. APIs MUST follow consistent patterns, use proper HTTP status codes, and include comprehensive error handling. API contracts MUST be defined and tested independently of frontend implementations.

**Rationale**: API-first approach enables multiple frontends (web, mobile, admin), third-party integrations, and easier testing. It enforces separation of concerns and enables scalable architecture.

### III. Component-Driven UI Development
Frontend MUST be built using reusable, composable components with Tailwind CSS utility classes. Components MUST be documented with usage examples and prop interfaces. Design system consistency MUST be maintained through shared component library. No custom CSS outside of Tailwind utilities without explicit justification.

**Rationale**: Component-driven development ensures UI consistency, reduces code duplication, improves maintainability, and enables rapid feature development through reusable building blocks.

### IV. Test-Driven Development (NON-NEGOTIABLE)
TDD mandatory: Tests written → User approved → Tests fail → Then implement. Red-Green-Refactor cycle strictly enforced. All critical user journeys (registration, login, checkout, payment) MUST have comprehensive integration tests. API endpoints MUST have contract tests before implementation.

**Rationale**: E-commerce applications require high reliability. Bugs in checkout, payment, or inventory management directly impact revenue. TDD ensures robust, reliable code from the start.

### V. Performance & Scalability
Page load times MUST be under 3 seconds on 3G connections. Database queries MUST be optimized with proper indexing and query analysis. Image optimization and CDN usage MUST be implemented for product images. Caching strategies MUST be implemented at multiple layers (database, application, CDN).

**Rationale**: Performance directly impacts conversion rates in e-commerce. Slow sites lose customers and revenue. Scalability planning prevents costly refactoring as the business grows.

## Security Requirements

All authentication MUST use Django's built-in authentication with proper session management. Password policies MUST enforce strong passwords with complexity requirements. All forms MUST include CSRF protection. SQL injection protection MUST be ensured through Django ORM usage (no raw SQL without review). All file uploads MUST be validated and stored securely. Environment variables MUST be used for all secrets and configuration.

## Development Workflow

All features MUST follow the specification → clarification → planning → tasks → implementation workflow. Code reviews MUST verify security practices, test coverage, and performance considerations. Database migrations MUST be reviewed for data integrity and rollback safety. Production deployments MUST include health checks and rollback procedures.

## Governance

This constitution supersedes all other development practices and guidelines. All feature specifications, technical plans, and code reviews MUST verify compliance with these principles. Any violations MUST be justified with explicit documentation of risks and mitigation strategies. Amendments to this constitution require explicit approval and migration plan for existing code.

**Version**: 1.0.0 | **Ratified**: 2025-01-27 | **Last Amended**: 2025-01-27