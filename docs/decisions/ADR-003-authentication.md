# ADR-003: Opaque Server-Side Sessions

## Status

Accepted.

## Context

The investigator application requires revocable sessions, CSRF protection, password reset, verification, rate limiting, and clear server-side authorization.

## Decision

Use opaque random session tokens stored only as hashes in PostgreSQL. Deliver the raw session token in an HttpOnly cookie and a separate CSRF token for mutation requests.

Passwords use Argon2id. Verification and reset tokens are single-use, hashed at rest, and expiring.

## Consequences

Session revocation and account recovery are straightforward and do not depend on long-lived self-contained browser tokens. The API performs authorization on every protected resource.
