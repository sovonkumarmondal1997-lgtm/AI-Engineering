# POC Plan — 40 SaaS Sources

**Duration:** 10 business days. **Status:** Planned, not executed. No result in this repository is a measured vendor benchmark.

**Candidates:** Fivetran managed ingestion, Airbyte Core self-managed, and custom dlt-based ingestion. Verify exact versions, plans, licences, source coverage, and deployment model before the comparison; Airbyte Cloud and Airbyte Core are not interchangeable.

## Source sample
Select six representative sources from the actual 40-source inventory:
1. High-volume API.
2. Strict rate-limited API.
3. Nested/paginated API.
4. Source with deletes/tombstones.
5. Source with schema drift.
6. API with instability or inconsistent pagination.

Use the same non-production destination, test records, schedule, access model, and success criteria for every candidate.

## Schedule
- Days 1–2: source inventory, credentials, threat model, test fixtures, acceptance criteria.
- Days 3–6: implement and run equivalent source slices on Fivetran managed ingestion, Airbyte Core self-managed, and the custom dlt-based approach.
- Days 7–8: inject rate limits, transient failures, schema change, credential rotation; test replay/backfill and export.
- Day 9: capture engineer time, resource use, reconciliation, operational triage, usage estimate/quote, and unresolved gaps.
- Day 10: score evidence, review with Engineering/SRE, Finance, Security, Legal; decide, extend a failed test narrowly, or reject all.

## Acceptance criteria
- Correctness: 100% of agreed test records reconcile by key; expected updates/deletes match; no silent loss or duplicate business keys.
- Freshness: 95% of scheduled runs complete within the agreed four-hour freshness window.
- Recovery: transient failure resumes without manual state repair; backfill completes and reconciles.
- Schema drift: breaking changes fail visibly or alert; no silent corruption.
- Security: approved secret management, least privilege, audit, and security review.
- Operability: an engineer unfamiliar with the build triages a seeded failure from logs/runbook in under 30 minutes.
- Cost: written quote or usage estimate for same source inventory, with uncertain billing drivers documented.
- Exit: export representative data and configuration; document non-portable state.

## Decision rule
Correctness and security are hard gates. Among candidates passing all hard gates, compare TCO and documented residual risks for candidates that meet freshness and operability criteria. Quantify risk-adjusted costs only when defensible probability/impact inputs exist; the current example model does not calculate a risk premium. If no candidate passes, record the failure and adjust scope or architecture; do not select a candidate solely because it has the highest weighted score.

## Results template (unrun)
| Measure | Fivetran managed | Airbyte Core self-managed | Custom dlt-based | Status |
|---|---|---|---|---|
| Reconciliation | Not run | Not run | Not run | POC required |
| Freshness | Not run | Not run | Not run | POC required |
| Rate-limit recovery | Not run | Not run | Not run | POC required |
| Schema drift | Not run | Not run | Not run | POC required |
| Triage time | Not run | Not run | Not run | POC required |
| Usage quote | Not requested | Not requested | Not applicable | Procurement/estimate |
| Export exercise | Not run | Not run | Not run | POC required |
