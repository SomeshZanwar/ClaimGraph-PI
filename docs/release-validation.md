# ClaimGraph PI Release Validation

Release implementation validation is green in [CI run 288](https://github.com/SomeshZanwar/ClaimGraph-PI/actions/runs/37570827101), completed October 6, 2026 in America/Chicago (October 7 UTC). It validates branch commit `34f6502eddfc4a4a9fb49f6f97842cf40161d730` through the merge checkout for [PR 12](https://github.com/SomeshZanwar/ClaimGraph-PI/pull/12). The PR checks also validate the subsequent documentation reconciliation; the numbered run here remains the verified implementation evidence rather than predicting a future result.

| Job | Verified result |
| --- | --- |
| Backend and Analytics | PASS |
| Frontend | PASS |
| Security | PASS |

The complete pipeline includes migrations, backend tests and coverage enforcement, dbt build/tests, deterministic risk checks, dependency readiness, Neo4j projection, graph analytics, anomaly scoring, case composition, frontend lint/unit/build, bundle budget, browser QA, dependency audits, secret scanning, documentation checks, repository QA, and both Compose configurations.

## Accessibility and dependency closure

- Regenerated `frontend/package-lock.json` for `@axe-core/playwright`; clean `npm ci` installs pass and the frontend audit reports zero vulnerabilities.
- Added zero-violation axe assertions for WCAG 2.1 A/AA on public routes, 404, consent and mobile navigation states, and protected queue, case evidence, and provider network flows. The existing desktop/mobile projects run these assertions without rule exclusions.
- Corrected primary-action text contrast by darkening normal and hover backgrounds, and gave the labeled provider graph a valid image role. The design specification reflects the updated action colors.
- Browser QA passed 29 tests, with one intentional skip of the mobile-only navigation test in the desktop project. Frontend unit tests passed 2 tests.
- Run 286 failed because the lockfile did not match the axe manifest addition. Run 287 then exposed contrast and graph-role violations. Run 288 passed after those defects were corrected. Run 289 validated the final PR state, and post-merge run 290 passed on `main`.

Protected browser flows use public-safe mocked API fixtures. Axe checks do not replace keyboard, zoom, assistive-technology, or deployed-environment review. Local Windows browser checks could not complete because loopback connections to the preview listener timed out; successful browser evidence above comes from Linux GitHub Actions.

## Remaining boundary

Public hosting/domain provisioning, production SMTP, live TLS and account validation, search-engine submission, and a live demo URL remain external launch actions in the [launch checklist](launch-checklist.md). They are not claimed as complete.

RiskStream (Project 2) has not started. Explicit user approval is required before moving to it.
