# Public Launch Checklist

This file separates repository readiness from external launch actions. Do not mark an item complete unless it was actually performed.

## Deployment

- [ ] provision the public host
- [ ] point the production domain to the host
- [ ] configure production secrets outside Git
- [ ] configure SMTP delivery
- [ ] start the production Compose stack
- [ ] confirm HTTP redirects to HTTPS
- [ ] confirm a valid TLS certificate
- [ ] confirm PostgreSQL, Neo4j, and Redis ports are not publicly reachable
- [ ] run the public-safe demo bootstrap
- [ ] create and verify a real demo investigator account
- [ ] test password reset email end to end
- [ ] validate mobile and desktop flows against the deployed domain

## SEO

- [ ] confirm production `sitemap.xml` contains the deployed HTTPS domain
- [ ] confirm `robots.txt` references the production sitemap
- [ ] confirm protected application routes are excluded from indexing
- [ ] inspect canonical tags on public pages
- [ ] inspect title/description/social preview metadata
- [ ] submit the sitemap in Google Search Console
- [ ] submit the sitemap in Bing Webmaster Tools
- [ ] request indexing for the homepage and methodology page after launch

## Analytics

- [ ] confirm consent choice works in the deployed browser
- [ ] confirm no telemetry is sent before consent
- [ ] inspect first-party telemetry payloads for sensitive/high-cardinality data
- [ ] verify page-view events use normalized case/provider route templates

## Performance

- [ ] run Lighthouse or equivalent on the deployed homepage
- [ ] review LCP, INP, CLS, and transfer size
- [ ] verify gzip/zstd delivery through Caddy
- [ ] confirm static assets receive long-lived cache headers
- [ ] verify case list pagination and graph query bounds

## Accessibility

- [ ] keyboard-test all public and investigator navigation
- [ ] rerun automated WCAG checks against the deployed domain (repository Playwright checks use local preview and public-safe API fixtures)
- [ ] verify visible focus states
- [ ] verify contrast in the deployed environment
- [ ] test browser zoom to 200%
- [ ] verify status/risk information is not communicated by color alone

## Backlink Strategy

No backlinks should be fabricated.

Legitimate launch targets:

- link the live demo from the GitHub repository README
- link the repository and live demo from the personal portfolio site
- publish a technical LinkedIn post explaining the engineering problem and methodology
- write a concise architecture/lessons-learned article that links to the repository
- reference the project in relevant job applications where healthcare/payment-integrity work is pertinent
- if discussing CMS DE-SynPUF methodology publicly, link to the official CMS data documentation

The goal is useful technical discovery, not artificial link volume.
