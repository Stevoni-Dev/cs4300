<!--
Sync Impact Report
Version change: 1.0.0 -> 1.1.0
Modified principles: IV. Verified API Behavior -> IV. Test-Driven Development and Test Classification.
Added sections: None.
Removed sections: None.
Follow-up TODO: Confirm the original ratification date.
-->

# Homework 2 Constitution

## Core Principles

### I. RESTful API Contracts
The application MUST expose a resource-oriented REST API using appropriate HTTP methods,
status codes, and media types. Endpoints MUST validate inputs and return consistent,
documented response and error shapes. API contract changes MUST be reflected in source
documentation and the README.

### II. Source Code Documentation
Source code MUST document modules and externally used functions, types, and API handlers
with their purpose, inputs, outputs, and observable behavior. Comments MUST explain
non-obvious decisions or constraints and MUST be updated when the behavior changes.

### III. README as Maintained Documentation
The README MUST describe the application's purpose, setup, configuration, execution, and
available API behavior. Any change that affects those instructions or the API contract
MUST update the README in the same change.

### IV. Test-Driven Development and Test Classification
Test-driven development is NON-NEGOTIABLE for new behavior: contributors MUST write a
test first, confirm that it fails for the expected reason, implement the behavior, and
then refactor while keeping the test passing. Every new behavior MUST have a unit test.
Integration tests MUST also cover behavior that crosses component boundaries, including
API routing, persistence, authentication, or serialization, when those boundaries are
affected. Every test MUST be explicitly marked as exactly one of `unit` or `integration`.

### V. Secure Handling of Requests
The application MUST treat request data as untrusted, validate it at the API boundary,
and enforce authorization before exposing or changing protected resources. Secrets MUST
not be stored in source code or returned in API responses.

## API and Security Constraints
API behavior MUST remain consistent across endpoints, especially for validation failures
and not-found responses. Breaking contract changes MUST be identified in documentation
and accompanied by a compatibility or migration note. Configuration and secrets MUST be
provided outside source code.

## Development Workflow and Quality Gates
Before completing a change, contributors MUST run the relevant unit and integration
tests and update source documentation and the README wherever behavior or setup has
changed. Reviewers MUST check the API contract, security boundaries, test coverage, test
classification, and documentation impact. New dependencies and abstractions MUST be
limited to what the requirement needs.

## Governance
This constitution governs project decisions and MUST be checked during planning and code
review. Amendments MUST be reviewed, recorded in this file, and follow semantic versioning:
MAJOR for incompatible governance changes, MINOR for new or materially expanded rules, and
PATCH for clarifications that do not change requirements. Every amendment MUST update the
last-amended date. The original ratification date remains unchanged.

**Version**: 1.1.0 | **Ratified**: TODO(RATIFICATION_DATE): confirm original adoption date | **Last Amended**: 2026-10-06
