# Unit 10 — On-Call Rotations, Handoffs, and Sustainable Paging

**Target file:** `10-on-call-rotations-handoffs-and-sustainable-paging.md`  
**Estimated time:** 14–20 hours  
**Prerequisites:** M01–M09; especially M08 progressive delivery, M09 access security, and M10 Units 1–9  
**Core tools:** Python 3 standard library, CSV/JSON, local synthetic paging simulator  
**Awareness only:** commercial paging/incident tools; HR/legal frameworks  
**Last reviewed:** 2026-10-28  
**Tool baseline assumed:** Python 3.10+; no network access required  
**Footprint:** negligible for scripts; optional prior local lab stack only  
**Solo-learner adaptation:** fictional responders, deterministic simulated time, synthetic events, role-play prompts, and local tests replace real team shifts. These exercises do not prove a team has practiced handoffs or that a real provider, carrier, device, identity system, or notification path works.

> **Scope and source note.** This chapter follows the Unit 10 requirements in the supplied authoritative M10 syllabus-generation prompt and the uploaded Unit 10 chapter-generation prompt. The actual `Roadmap_ptree.md` checkout and a generated syllabus file were not available for direct verification in this run; the target location and neighboring filenames below come from the supplied prompt. Added design choices are tagged `[ASSUMPTION]`; thresholds are `[ILLUSTRATIVE]`; environment-specific details are `[VERIFY]`. No exact incident-per-shift limit or industry statistic is asserted.

## Table of contents

1. Why sustainable on-call is reliability engineering
2. Learning outcomes, prerequisites, and concept map
3. L1 — Foundations and human sustainability
4. L2 — Build the rotation, handoff, simulator, and measurement tools
5. L3 — Sustainable paging design and trade-offs
6. L4 — Program governance and organizational resilience
7. Eight end-to-end labs
8. Exercises and answer key
9. Glossary
10. Roadmap coverage audit, execution evidence, and limitations

## 1. Why this matters in production

A page is a request for a human to interrupt their current work and act within a response expectation. If pages are noisy, misrouted, missing context, or concentrated on one expert, the system spends human attention without reliably reducing user harm. Fatigue can degrade judgment; a rota can appear fair by shift count while assigning most sleep-disrupting events to one person. On-call therefore requires the same engineering discipline as a service: explicit scope, observable outcomes, tested failure paths, ownership, review, and safe operating limits.

The purpose is not to minimize page count at any cost. The purpose is to preserve detection of urgent user-impacting failures while removing interruptions that do not require immediate human action.

## 2. Learning outcomes and prerequisite check

By the end, a learner can:

- **L1:** distinguish on-call, incident engagement, primary, secondary, and incident commander roles.
- **L1:** produce a handoff that separates “no known issue” from “not checked.”
- **L2:** generate and validate a fictional rota with PTO, swaps, rest constraints, and infeasibility reporting.
- **L2:** simulate acknowledgement, escalation, quiet-hours behavior, and receiver failure without sending real notifications.
- **L2:** calculate load, night pages, acknowledgement time, actionable ratio, repeat alerts, and concentration indicators.
- **L3:** defend page classification and a coverage model against user-impact, expertise, cost, and human-sustainability trade-offs.
- **L3:** design service-owner remediation for chronic noise without gaming the metrics or hiding real signals.
- **L4:** define on-call program policy, program-level SLOs, governance rituals, onboarding/offboarding gates, and resilience drills.
- **L4:** analyze organizational incidents and propose verifiable corrective actions.

### Prerequisite check

Answer before proceeding:

1. Is a dashboard-only warning necessarily a page? **No**; page only when a human must act within a defined response expectation.
2. Does a green service SLO prove the pager path works? **No**; routing and notification are separate dependencies.
3. Does equal shift count imply equal burden? **No**; night interruptions, severity, duration, expertise concentration, and recovery differ.
4. Can a solo simulation prove a real responder can access production? **No**; real access verification must be authorized and audited in the actual environment.

## 3. Concept map and vocabulary

```text
User journey / SLO risk
        |
  signal + ownership metadata
        |
 alert rule and route -----> ticket / dashboard (not urgent)
        |
  qualifying page
        |
 primary acknowledges? ---- no ----> secondary / escalation target
        |                                  |
   incident engaged <----------------------+
        |
 mitigate safely; use runbook; request help when uncertain
        |
 resolve / monitor / hand off
        |
 review every page -> remove noise, fix route/runbook, train owners
        |
 sustainable load + improved user outcomes
```

| Term | Precise meaning | Common misconception |
|---|---|---|
| On-call | Assigned availability to respond to qualifying production pages within an agreed expectation | “On-call” means continuously working incidents |
| Primary | First responder for the service/shift | Primary must solve every issue alone |
| Secondary | Backup/escalation target for the primary | Secondary is automatically a second primary |
| Incident-engaged | Actively performing incident work, not merely holding availability | Every scheduled responder is always incident-engaged |
| Incident commander (IC) | Coordinates incident objectives, roles, and communication according to Unit 4 | IC must be the deepest technical expert |
| Page | Human-interrupting notification that requires timely action | Every alert deserves a page |
| Alert | A detected condition; may route to page, ticket, dashboard, or suppression with safeguards | Alert count equals page count |
| Handoff | Explicit transfer of state, risks, ownership, and next actions | A short “all good” message is enough |
| Actionable-now | A human needs to act within the page response expectation | Anything interesting is actionable-now |
| Acknowledgement time | Page timestamp to first valid acknowledgement timestamp | Acknowledgement means mitigation started |
| Time to resolution | Defined incident start to declared resolution; definition must be consistent | Acknowledgement-to-resolution is always comparable |
| Night page | Page occurring in a defined local night interval for the assigned rota timezone | UTC hour alone captures sleep disruption |
| Bus factor proxy | Count of distinct trained handlers for an alert class or service in the observed sample | A small count proves an individual is at fault |
| Page budget | `[ASSUMPTION]` an operational guardrail for interruption load; not an SLO error budget | It is the same thing as a service error budget |
| Follow-the-sun | Coverage handoff across regions/time zones so work can continue across local days | Merely adding people in different time zones guarantees continuity |

### Boundaries with neighboring units

- Unit 1 owns SLI/SLO/error-budget foundations. Here, SLO risk helps determine whether a human must be paged.
- Unit 3 owns alert quality and routing fundamentals. This unit focuses on the human rota and operational sustainability.
- Unit 4 owns severity, incident roles, and command. Use its severity matrix and IC role.
- Unit 5 owns detailed triage and postmortems. Here, the post-shift learning loop is concise.
- Unit 7 owns toil reduction and bounded automation. Use its patterns to eliminate repetitive pages.
- Unit 8 owns runbooks and readiness reviews. On-call eligibility requires tested runbooks and routes.
- Unit 9 owns formal error-budget policies and release freezes. An on-call page budget is a separate, assumed operational analogue.
- M09 owns detailed secrets and identity controls; use least privilege, just-in-time access, audited break-glass, and access verification.
- Unit 11 owns DORA metrics. Do not turn human-health indicators into individual performance rankings.
- M11 owns broader observability architecture; this chapter only needs minimum metrics and reports.

---

## 4. L1 — On-call foundations and human sustainability

### 4.1 What on-call does and does not mean

A responder is on-call when the organization has assigned them a defined availability period and a documented expectation for responding to qualifying production pages. A responder becomes incident-engaged when they are actively investigating, mitigating, coordinating, or communicating about an event. An incident commander coordinates the response; this may be a different person from the primary technical responder.

The contract must state: covered services, support hours, qualifying page conditions, acknowledgement expectations, escalation sequence, available runbooks, access prerequisites, handoff method, relief procedure, and what happens when coverage cannot be staffed. If the team cannot meet the response expectation, reduce the support promise or obtain shared coverage; do not label an unstaffed interval “24/7.”

### 4.2 Why sustainability is a reliability requirement

Interruptions consume attention, break deep work, and can affect sleep. Repeated exposure without recovery can increase operational risk and remove the time needed to fix the causes of paging. The exact effect varies by person and context; this chapter makes no universal numeric claim about safe pages per shift. Published SRE books discuss on-call load and sustainable response practices, but any specific quoted threshold must be verified against the relevant edition and section before use.

Measure system conditions, not “good” and “bad” employees. Ask which alerts can be removed, which runbooks are missing, which services lack owners, and where expertise is concentrated. Use aggregate data with transparency, access controls, and an explicit retention policy.

### 4.3 Rotation structures

| Structure | Benefit | Cost/risk | Use when |
|---|---|---|---|
| Daily primary | Short individual shift duration | More handoffs; continuity loss; frequent schedule changes | Work is well documented and handoffs are reliable |
| Weekly primary/secondary | Continuity during a week; clear backup | Longer availability burden; requires relief/rest design | Team can staff a predictable rota |
| Business-hours only | Honest, bounded support promise | After-hours incident detection/response must be explicitly limited | Service criticality and customer expectations permit it |
| 24/7 primary/secondary | Clear continuous coverage if truly staffed | Expensive; leave, illness, training, and overlapping incidents require capacity | Staffing and relief mechanisms have been demonstrated |
| Follow-the-sun | Work crosses local days; less overnight burden for each region | Handoff quality, timezone overlap, regional expertise and ownership complexity | Multiple staffed regions have real capability and shared tooling |

A rota’s calendar fairness is not a proof of humane coverage. Record shift count, primary/secondary count, night and weekend shifts, interruption duration, incident severity, and actual time engaged.

### 4.4 Shadowing, reverse-shadowing, and first-page readiness

- **Shadowing:** trainee observes an experienced responder and explains what they see.
- **Reverse-shadowing:** trainee leads a simulated or supervised response while an experienced responder observes.
- **First-page drill:** trainee receives a synthetic page, identifies impact, opens the correct runbook, verifies scope, acknowledges, escalates when uncertain, and records evidence.
- **Access readiness:** verify least-privilege access, MFA/device readiness, just-in-time workflow, and audited break-glass access according to M09. Never put secrets in handoff notes.
- **Runbook readiness:** runbook is current, has a clear trigger, safe diagnostics, mitigation/rollback, escalation, verification, and owner.

A solo learner can rehearse the decision path with a scripted scenario. That is not real shadowing and does not verify production access.

### 4.5 Handoff essentials

A handoff must cover:
- current service health and customer impact;
- active incidents, severity, IC, status, and next update;
- unresolved issues and explicit uncertainty;
- recent deployments/configuration changes and upcoming risk;
- dependencies degraded or at risk;
- noisy/flaky/silenced alerts, expiry, owner, and reason;
- in-flight experiments, backfills, model releases, or maintenance;
- next actions, accountable owner, deadline, and link/reference;
- route/contact state and fallback path;
- “no known issue after checking X” versus “X not checked.”

Use a written handoff as the durable record. Add synchronous discussion when risk is high, state is ambiguous, a severe incident is active, or the next shift needs context. The recipient should cold-read the note and restate the current risk and next action.

### 4.6 Two fictional pages

**Inference API page:** “The fraction of valid requests returning server errors rose above the service’s `[ILLUSTRATIVE]` paging threshold for the configured confirmation window; request volume is sufficient; deployment `rel-042` occurred recently.” This is a symptom, not a diagnosis. Responder checks the SLO dashboard, recent rollout, dependency health, and runbook; pauses or rolls back only through the approved M08 mechanism; asks for help if uncertain.

**ETL freshness page:** “Dataset `features_daily` is 45 minutes past its freshness objective `[ILLUSTRATIVE]`; downstream retraining is waiting.” This is a user-facing symptom. Responder checks scheduler state, source availability, queue/lag, recent schema changes, and data-quality gates. A green worker pod alone does not prove data is fresh or correct.

### L1 practical artifact: written handoff

```markdown
# Shift handoff — synthetic example
Shift: 2026-10-28 08:00–16:00 Asia/Kolkata
Outgoing: responder-sim-02 | Incoming: responder-sim-04
Service status: degraded latency on inference-api; availability ratio is currently within target.
Customer impact: elevated p95 latency for a subset of requests; scope still being quantified.
Active incident: INC-SIM-104, SEV2, IC: ic-sim-01.
Recent change: release rel-sim-042 at 13:10 local.
Dependency: feature-store latency elevated; provider status not independently confirmed.
Alerts silenced: none. Flaky alerts: `feature-store-timeout-sim`; ticket OPS-SIM-19; expires 18:00 local.
Not checked: downstream model-quality proxy after release.
Next actions:
- responder-sim-04: compare latency before/after rel-sim-042 by 16:20 local.
- service-owner-sim: confirm feature-store health by 16:30 local.
- IC: publish next status update by 16:15 local.
Escalation: primary -> secondary-sim-01 -> platform-sim-01; use incident command process for SEV1.
Fallback: if local receiver fails, run the documented watchdog check and contact the designated human through the organization-approved alternate path.
```

**L1 checkpoint — what you can now do:** explain roles, describe a sustainable rota, and write a handoff with risks, owners, deadlines, and explicit unknowns.

---

## 5. L2 — Build the rotation, handoff, simulator, and measurement tools

All code below is intended for synthetic local data. Commands run in a disposable directory, not a repository checkout. Python scripts use the standard library and do not make network calls.

### 5.1 Rotation scheduler: a conservative reference implementation

This scheduler is intentionally a small deterministic teaching tool, not a general-purpose workforce optimizer. It supports daily shifts, synthetic responders, PTO, explicit primary swaps, a maximum consecutive-shift constraint, and a minimum rest interval measured between shift start times. It reports infeasibility rather than silently assigning unavailable people. Weekend counts are reported for review; the example does not claim legal compliance.

Save as `rotation_scheduler.py` in `/tmp/oncall-unit10/`:

```python
#!/usr/bin/env python3
"""Deterministic synthetic on-call rota generator; no network access."""
from datetime import date, datetime, time, timedelta
from collections import Counter, defaultdict
import json

PEOPLE = ["responder-sim-01", "responder-sim-02",
          "responder-sim-03", "responder-sim-04", "responder-sim-05"]
# Inclusive date ranges; synthetic examples only.
PTO = {
    "responder-sim-02": {date(2026, 11, 3)},
    "responder-sim-03": {date(2026, 11, 5)},
}
# (shift_date, role) -> responder. An override must still pass constraints.
SWAPS = {(date(2026, 11, 4), "primary"): "responder-sim-04"}
MAX_CONSECUTIVE = 3
MIN_REST_HOURS = 20
SHIFT_HOURS = 24
START = date(2026, 11, 1)
DAYS = 7

def eligible(person, day, role, assignments):
    if day in PTO.get(person, set()):
        return False
    if role == "secondary":
        primary = assignments.get((day, "primary"))
        if primary == person:
            return False
    # Count immediately preceding assigned calendar days, regardless of role.
    prior = 0
    for offset in range(1, MAX_CONSECUTIVE + 2):
        d = day - timedelta(days=offset)
        if any(assignments.get((d, r)) == person for r in ("primary", "secondary")):
            prior += 1
        else:
            break
    if prior >= MAX_CONSECUTIVE:
        return False
    # Daily shift starts are 24h apart in this model. If the schedule later
    # supports overlapping/shorter shifts, calculate actual interval overlap.
    return True

def build_schedule(start=START, days=DAYS, people=PEOPLE, pto=PTO, swaps=SWAPS):
    if len(set(people)) < 2:
        raise ValueError("At least two distinct responders are required for primary and secondary.")
    assignments, rows = {}, []
    counts = Counter()
    last_day = {}
    for i in range(days):
        day = start + timedelta(days=i)
        row = {"date": day.isoformat()}
        for role in ("primary", "secondary"):
            forced = swaps.get((day, role))
            candidates = [forced] if forced else sorted(people, key=lambda p: (
                counts[(p, role)], counts[(p, "weekend")], p))
            chosen = None
            for person in candidates:
                if person not in people:
                    continue
                if day in pto.get(person, set()):
                    continue
                if role == "secondary" and row.get("primary") == person:
                    continue
                if not eligible(person, day, role, assignments):
                    continue
                chosen = person
                break
            if chosen is None:
                raise ValueError(f"Infeasible coverage on {day} for {role}; no safe assignment found.")
            row[role] = chosen
            assignments[(day, role)] = chosen
            counts[(chosen, role)] += 1
            if day.weekday() >= 5:
                counts[(chosen, "weekend")] += 1
            last_day[chosen] = day
        rows.append(row)
    return rows, counts

def main():
    rows, counts = build_schedule()
    print("SYNTHETIC ROTA — local dates; not a real contact schedule")
    for r in rows:
        print(f'{r["date"]} primary={r["primary"]} secondary={r["secondary"]}')
    print("Fairness components (shift counts only; inspect nights, incidents, and actual load separately):")
    for p in PEOPLE:
        print(f"{p}: primary={counts[(p,'primary')]} secondary={counts[(p,'secondary')]} weekend_roles={counts[(p,'weekend')]}")
if __name__ == "__main__":
    main()
```

**Important scheduler caveat:** `MIN_REST_HOURS` and `SHIFT_HOURS` are declared to make the desired guardrail visible, but this simplified daily scheduler does not yet enforce arbitrary rest intervals between overlapping shifts. The daily model has one assignment per calendar day and cannot validate real local-time/DST transitions. Therefore the rest-interval requirement is **Partial** for this compact implementation; the production design must model actual shift start/end instants and reject overlaps/rest violations. Do not use this as a real staffing scheduler.

Run from `/tmp/oncall-unit10/`:

```bash
python3 rotation_scheduler.py
```

Expected behavior: seven dated rows with distinct primary and secondary responders, honoring the supplied PTO and forced swap when feasible. Output is synthetic and may vary only if the constants change. If a forced swap violates constraints, the script reports an infeasibility rather than silently substituting someone.

#### Scheduler tests

Append to a separate `test_rotation_scheduler.py` in the same temporary directory:

```python
import unittest
from datetime import date
from rotation_scheduler import build_schedule

class SchedulerTests(unittest.TestCase):
    def test_primary_secondary_differ(self):
        rows, _ = build_schedule()
        self.assertTrue(all(r["primary"] != r["secondary"] for r in rows))
    def test_pto_not_assigned(self):
        rows, _ = build_schedule()
        for r in rows:
            d = date.fromisoformat(r["date"])
            if d == date(2026, 11, 3):
                self.assertNotEqual(r["primary"], "responder-sim-02")
                self.assertNotEqual(r["secondary"], "responder-sim-02")
    def test_swap_honored_when_feasible(self):
        rows, _ = build_schedule()
        row = next(r for r in rows if r["date"] == "2026-11-04")
        self.assertEqual(row["primary"], "responder-sim-04")
    def test_infeasible_staffing_is_reported(self):
        with self.assertRaises(ValueError):
            build_schedule(people=["solo"], pto={})
if __name__ == "__main__":
    unittest.main()
```

**Verification:** `python3 -m unittest -v test_rotation_scheduler.py`. **Expected:** four tests pass. This test verifies the implemented constraints only; it does not validate the declared arbitrary rest interval or human fairness.

### 5.2 Handoff template and report generator

Copyable template:

```markdown
# Handoff: <service> / <shift-id>
Time zone: <IANA timezone> | Shift start/end: <ISO-8601 with offset>
Outgoing/incoming: <synthetic or authorized responder IDs>
Service health: <known facts and measurement window>
Customer impact: <who/what/how many; if unknown, say unknown>
Active incidents: <ID, severity, IC, status, next update>
Open risks/dependencies: <symptom, impact, test next>
Recent changes: <release/config/migration/flag; timestamp and owner>
Alerts: <active, repeated, silenced; reason, owner, expiry>
Experiments/backfills/model releases: <scope, stop condition, owner>
Access/routing: <checked / not checked; never include secrets>
Next actions: <action | owner | deadline | evidence>
Escalation: <primary -> secondary -> service owner/IC>
Explicit unknowns: <what was not checked>
Recipient read-back: <risk understood, next action, deadline>
```

A useful generator should not infer that absent input means “no known issue.” The small script below takes JSON arrays and renders sections; missing keys are called out as **NOT PROVIDED**. Save as `handoff_report.py`:

```python
#!/usr/bin/env python3
import json, sys
from pathlib import Path

SECTIONS = [
    ("alerts", "Alerts"), ("incidents", "Incidents"),
    ("silences", "Silences"), ("changes", "Recent changes"),
    ("tasks", "Follow-up tasks"),
]
def render(data):
    if not isinstance(data, dict):
        raise ValueError("top-level JSON must be an object")
    lines = ["# Synthetic shift handoff", "",
             f'- Shift: {data.get("shift", "NOT PROVIDED")}',
             f'- Time zone: {data.get("timezone", "NOT PROVIDED")}',
             f'- Service status: {data.get("service_status", "NOT PROVIDED")}', ""]
    for key, title in SECTIONS:
        lines += [f"## {title}"]
        if key not in data:
            lines += ["**NOT PROVIDED — do not interpret as empty.**", ""]
            continue
        items = data[key]
        if not isinstance(items, list):
            raise ValueError(f"{key} must be a list")
        if not items:
            lines += ["No entries in supplied dataset; this is not proof that the source was checked.", ""]
            continue
        for i, item in enumerate(items, 1):
            if not isinstance(item, dict):
                raise ValueError(f"{key}[{i-1}] must be an object")
            lines.append(f"{i}. " + "; ".join(f"{k}={v}" for k, v in sorted(item.items())))
        lines.append("")
    lines += ["## Recipient read-back", "- Current risk: NOT RECORDED",
              "- Next action/owner/deadline: NOT RECORDED", ""]
    return "\n".join(lines)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 handoff_report.py synthetic_handoff.json", file=sys.stderr)
        return 2
    try:
        data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        print(render(data))
    except (OSError, json.JSONDecodeError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
```

Synthetic input `synthetic_handoff.json`:

```json
{
  "shift": "2026-10-28T08:00/16:00",
  "timezone": "Asia/Kolkata",
  "service_status": "inference latency degraded; cause not confirmed",
  "alerts": [{"id":"AL-SIM-4","class":"latency","owner":"service-sim","status":"firing"}],
  "incidents": [{"id":"INC-SIM-104","severity":"SEV2","next_update":"16:15 local"}],
  "silences": [{"id":"SIL-SIM-2","reason":"duplicate alert investigation","expires":"18:00 local","owner":"responder-sim-02"}],
  "changes": [{"id":"REL-SIM-42","time":"13:10 local","owner":"release-sim"}],
  "tasks": [{"action":"compare pre/post latency","owner":"responder-sim-04","deadline":"16:20 local"}]
}
```

Run from the temp directory: `python3 handoff_report.py synthetic_handoff.json`. Expected: report contains all five sections, incident `INC-SIM-104`, and an explicit recipient read-back placeholder. For missing-data testing, remove `silences`; the report must say `NOT PROVIDED`, not “none.”

### 5.3 Local paging/escalation simulator

This simulator uses a deterministic logical clock. It writes events to stdout; it does **not** send SMS, push, email, or phone notifications. Quiet-hours override is restricted to SEV1. The purpose is to test state transitions and fallback detection.

Save as `pager_sim.py`:

```python
#!/usr/bin/env python3
"""Local-only pager state machine; no network access or real notification."""
from dataclasses import dataclass, field
import json

@dataclass
class Pager:
    receiver_up: bool = True
    now: int = 0
    audit: list = field(default_factory=list)
    pages: dict = field(default_factory=dict)
    def event(self, kind, **kwargs):
        self.audit.append({"t": self.now, "event": kind, **kwargs})
    def create(self, page_id, severity, primary, secondary, quiet_hours=False):
        if severity not in {"SEV1", "SEV2", "SEV3", "SEV4"}:
            raise ValueError("unsupported severity")
        if quiet_hours and severity != "SEV1":
            self.event("quiet_hours_suppressed", page_id=page_id, severity=severity)
            return "suppressed"
        if not primary or not secondary or primary == secondary:
            self.event("route_invalid", page_id=page_id)
            return "route-invalid"
        self.pages[page_id] = {"severity": severity, "primary": primary,
                               "secondary": secondary, "acked": False, "created": self.now}
        if self.receiver_up:
            self.event("page_created", page_id=page_id, primary=primary)
            return "sent-to-simulator"
        self.event("receiver_failure", page_id=page_id)
        self.event("fallback_required", page_id=page_id)
        return "receiver-failed-fallback-required"
    def ack(self, page_id, responder):
        p = self.pages.get(page_id)
        if not p:
            raise ValueError("unknown page")
        if responder not in {p["primary"], p["secondary"]}:
            self.event("invalid_ack", page_id=page_id, responder=responder)
            return False
        p["acked"] = True
        self.event("ack", page_id=page_id, responder=responder)
        return True
    def advance(self, minutes, escalation_after=5):
        if minutes < 0:
            raise ValueError("time cannot move backwards")
        self.now += minutes
        for pid, p in self.pages.items():
            if not p["acked"] and self.now - p["created"] >= escalation_after:
                self.event("escalate_to_secondary", page_id=pid, target=p["secondary"])
    def report(self):
        return json.dumps(self.audit, indent=2, sort_keys=True)

if __name__ == "__main__":
    sim = Pager()
    print("quiet-hours SEV2:", sim.create("P-SIM-1", "SEV2", "primary-sim", "secondary-sim", True))
    print("SEV1:", sim.create("P-SIM-2", "SEV1", "primary-sim", "secondary-sim", True))
    sim.advance(6)
    sim.ack("P-SIM-2", "secondary-sim")
    print(sim.report())
```

**Expected:** the SEV2 quiet-hours page is suppressed by this explicitly defined simulator policy; SEV1 is created; advancing the clock causes a secondary escalation event before acknowledgement; a secondary acknowledgement is accepted. `[ASSUMPTION]` This is a classroom policy, not a universal severity policy. A real organization may have different safety and coverage requirements.

**Receiver outage drill:** set `sim.receiver_up = False` before `create`. Expected return is `receiver-failed-fallback-required`, with `receiver_failure` and `fallback_required` audit events. The simulator does not prove that an actual out-of-band contact path works; a real, authorized periodic test is needed.

### 5.4 On-call health metrics and synthetic history

Define metrics before computing them:

| Metric | Formula / unit | Interpretation limit |
|---|---|---|
| Pages per shift | Page records / covered shifts | Depends on consistent deduplication and shift boundaries |
| Pages per person | Pages routed to person / period | Not a performance ranking |
| Night pages | Page timestamp falls within local `22:00–06:00` for the assigned rota timezone | DST and travel can change local time; synthetic dataset uses fixed UTC offset for simplicity |
| Acknowledgement time | `ack_timestamp - page_timestamp`, seconds/minutes | Missing acknowledgement is missing, not zero |
| Time to resolution | Incident resolution timestamp minus incident start timestamp | Use one consistent start/resolve definition; not comparable across different scopes without context |
| Actionable-page ratio | Pages judged actionable-now / reviewed pages | Depends on classification and review completeness |
| Repeat-alert share | Pages with repeated alert fingerprint / total pages | Dedup window and fingerprint policy must be documented |
| Load imbalance | Report component counts and range/median; optional coefficient of variation | Small samples and severity differences matter |
| Handling concentration | Distinct trained handlers per alert class; handler share | Observed handlers are not necessarily trained/available responders |
| Bus-factor proxy | Count of distinct trained handlers who successfully handled the class in period | A proxy; does not prove independent expertise or availability |

A standard-library report should group by synthetic IDs and show aggregates. Save the following as `load_report.py`; it expects CSV fields `page_id,person,shift_id,timestamp,ack_seconds,resolution_minutes,actionable,alert_class,repeat,night,sleep_disrupting`:

```python
#!/usr/bin/env python3
import csv, sys
from collections import Counter, defaultdict
from pathlib import Path

FIELDS = {"page_id","person","shift_id","timestamp","ack_seconds",
          "resolution_minutes","actionable","alert_class","repeat","night","sleep_disrupting"}
def analyze(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not FIELDS.issubset(reader.fieldnames):
            raise ValueError("CSV missing required columns")
        rows = list(reader)
    if not rows:
        raise ValueError("no page rows: cannot infer a healthy load")
    for n, r in enumerate(rows, 2):
        if not r["page_id"] or not r["person"] or not r["shift_id"]:
            raise ValueError(f"row {n}: missing page/person/shift ID")
        for key in ("actionable","repeat","night","sleep_disrupting"):
            if r[key] not in {"0","1"}:
                raise ValueError(f"row {n}: {key} must be 0 or 1")
        for key in ("ack_seconds","resolution_minutes"):
            if r[key] and float(r[key]) < 0:
                raise ValueError(f"row {n}: {key} cannot be negative")
    by_person = Counter(r["person"] for r in rows)
    by_shift = Counter(r["shift_id"] for r in rows)
    by_class = defaultdict(set)
    for r in rows:
        if r["actionable"] == "1":
            by_class[r["alert_class"]].add(r["person"])
    acks = [float(r["ack_seconds"]) for r in rows if r["ack_seconds"]]
    resolutions = [float(r["resolution_minutes"]) for r in rows if r["resolution_minutes"]]
    repeats = sum(r["repeat"] == "1" for r in rows)
    actionable = sum(r["actionable"] == "1" for r in rows)
    print(f"pages={len(rows)} people={len(by_person)} shifts={len(by_shift)}")
    print(f"night_pages={sum(r['night']=='1' for r in rows)} sleep_disrupting={sum(r['sleep_disrupting']=='1' for r in rows)}")
    print(f"actionable_ratio={actionable/len(rows):.3f} repeats={repeats} repeat_share={repeats/len(rows):.3f}")
    print("pages_by_person=" + repr(dict(sorted(by_person.items()))))
    print("pages_by_shift=" + repr(dict(sorted(by_shift.items()))))
    print(f"ack_seconds_mean={sum(acks)/len(acks):.1f}" if acks else "ack_seconds_mean=UNKNOWN (no observed acknowledgements)")
    print(f"resolution_minutes_mean={sum(resolutions)/len(resolutions):.1f}" if resolutions else "resolution_minutes_mean=UNKNOWN")
    print("alert_class_handler_counts=" + repr({k:len(v) for k,v in sorted(by_class.items())}))
    print("Use aggregates for system improvement; do not rank individuals.")
def main():
    if len(sys.argv) != 2:
        print("Usage: python3 load_report.py synthetic_pages.csv", file=sys.stderr); return 2
    try: analyze(sys.argv[1])
    except (OSError, ValueError, csv.Error) as e:
        print(f"ERROR: {e}", file=sys.stderr); return 2
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
```


#### Cross-tool tests

Save as `test_local_tools.py` beside the scripts:

```python
import unittest
from pager_sim import Pager
from handoff_report import render
import json

class LocalToolTests(unittest.TestCase):
    def test_handoff_missing_data_is_not_claimed_empty(self):
        report = render({"shift":"synthetic", "alerts":[]})
        self.assertIn("Silences", report)
        self.assertIn("NOT PROVIDED", report)
    def test_pager_quiet_hours_only_suppresses_non_sev1(self):
        p = Pager()
        self.assertEqual(p.create("P1","SEV2","a","b",True), "suppressed")
        self.assertEqual(p.create("P2","SEV1","a","b",True), "sent-to-simulator")
    def test_pager_escalates_after_logical_clock_advance(self):
        p = Pager()
        p.create("P1","SEV1","a","b")
        p.advance(6)
        self.assertTrue(any(e["event"]=="escalate_to_secondary" for e in p.audit))
    def test_receiver_failure_requires_fallback(self):
        p = Pager(receiver_up=False)
        self.assertEqual(p.create("P1","SEV1","a","b"), "receiver-failed-fallback-required")
        self.assertTrue(any(e["event"]=="fallback_required" for e in p.audit))
    def test_invalid_route_rejected(self):
        p = Pager()
        self.assertEqual(p.create("P1","SEV1","same","same"), "route-invalid")
if __name__ == "__main__":
    unittest.main()
```

Run: `python3 -m unittest -v test_local_tools.py`. Expected: five tests pass. These tests validate local state transitions and missing-data representation only; they do not test a real notification service.

### 5.5 Forty-page triage exercise

Classify each record as:
- `actionable-now`: a human must act within the agreed response expectation to limit user harm.
- `ticket`: work is needed but can wait for the documented work queue.
- `delete/redesign`: duplicate, broken route, non-actionable symptom, or alert requiring a different signal. For ambiguous records, preserve a safety check and validate with replay before removal.

The records below are synthetic and intentionally include ambiguity.

| # | Synthetic page | Key facts | Answer |
|---:|---|---|---|
| 1 | API 5xx burst | SLO risk confirmed, current | actionable-now |
| 2 | API latency high | user journey affected, current | actionable-now |
| 3 | ETL freshness missed | downstream retraining blocked now | actionable-now |
| 4 | Consumer lag rising | no SLO risk yet, trend dashboard available | ticket |
| 5 | Disk at 70% | capacity forecast weeks away | ticket |
| 6 | Disk full on stateful service | writes failing now | actionable-now |
| 7 | Duplicate API 5xx alert | same fingerprint, same incident | delete/redesign |
| 8 | Every pod restarted once | recovered; no user symptom | ticket |
| 9 | Missing runbook link on page | active user impact also present | actionable-now |
| 10 | Missing runbook link only | no current impact | ticket |
| 11 | Route to retired team | no recipient; service is degraded | actionable-now |
| 12 | Dead route test | scheduled synthetic test, no issue | ticket |
| 13 | Certificate expires in 20 days | planned renewal ticket possible | ticket |
| 14 | Certificate expired; TLS failing | user traffic failing | actionable-now |
| 15 | CPU 90% for 30 seconds | no saturation/user impact | delete/redesign |
| 16 | CPU saturation plus latency SLO burn | current user impact | actionable-now |
| 17 | Queue backlog growing | known drain rate exceeds arrival rate | actionable-now |
| 18 | Queue backlog stable | within recovery objective | ticket |
| 19 | Vendor timeout burst | fallback failing and requests failing | actionable-now |
| 20 | Vendor status page changed | no service impact | ticket |
| 21 | Nightly job succeeded | informational | delete/redesign |
| 22 | Nightly job failed | retry safe, deadline tomorrow | ticket |
| 23 | Nightly job failed | regulatory/critical deadline in 15 min; downstream blocked | actionable-now |
| 24 | Model quality proxy drops | validated threshold and rollback decision required | actionable-now |
| 25 | Model quality proxy noisy | low sample count; no corroboration | ticket |
| 26 | Alert has no owner | no impact now | ticket |
| 27 | Alert has no owner | SEV1 symptom now | actionable-now |
| 28 | Same alert repeats every minute | one incident already open | delete/redesign |
| 29 | Error rate on canary | automatic rollout pause already active; human review needed by policy | actionable-now |
| 30 | Error rate on canary | automated analysis says healthy; duplicate page | delete/redesign |
| 31 | Data completeness below floor | customer-facing dataset incomplete | actionable-now |
| 32 | Data completeness warning | one partition late, downstream unaffected | ticket |
| 33 | Backup job warning | backup success unverified before RPO boundary | actionable-now |
| 34 | Backup job warning | redundant verified copy exists, ample time | ticket |
| 35 | Secret access denied | service outage; authorized break-glass needed | actionable-now |
| 36 | Secret rotation due next month | no current failure | ticket |
| 37 | Synthetic probe failed once | no corroboration; next probe healthy | ticket |
| 38 | Multiple independent probes fail | confirmed regional user journey down | actionable-now |
| 39 | Test environment memory alert | no production users, no agreed immediate response | delete/redesign |
| 40 | Unknown signal | missing context and route; severity unclear | ticket plus urgent rule audit; do not silently discard |

**Answer-key arithmetic:** 40 current pages are listed. The proposed immediate-page set is rows 1, 2, 3, 6, 9, 11, 14, 16, 17, 19, 23, 24, 27, 29, 31, 33, 35, and 38 = **18 pages**. Under this classification, 22 pages are converted to ticket or redesigned: reduction = `(40 - 18) / 40 × 100 = 55%`. The set preserves all 18 records marked as true urgent signals in this exercise. Potential false-negative risk remains in ambiguous rows 25, 37, and 40; replay against historical incidents, shadow alerts, and a review window are required before production removal. This is an exercise answer, not a claim that 55% is a safe target.

### 5.6 Dead-routing and pager-path tests

A local route check should validate:
- service owner and rotation exist;
- primary and secondary differ;
- route points to a current synthetic rotation ID;
- contact metadata has a freshness timestamp;
- a synthetic test page is acknowledged in the expected time;
- receiver failure raises a separate watchdog signal;
- an alternate path is explicitly named and tested by an authorized human in a real environment.

**Failure injection:** in the simulator, set `receiver_up=False`, create a page, and verify `receiver_failure` and `fallback_required` in the audit log. Restore `receiver_up=True` and rerun the synthetic page. Do not disable a real production receiver. A local success proves only the local code path.

### 5.7 Onboarding checklist and first-page drill

```markdown
- [ ] Service owner, support hours, critical journeys, and SLOs understood
- [ ] Severity matrix and incident-command process reviewed
- [ ] Tested runbooks and dashboards reviewed; gaps assigned to owners
- [ ] Primary, secondary, escalation, and fallback routes verified
- [ ] Least-privilege access tested; JIT/break-glass path understood and audited
- [ ] Shadow shift completed with a real qualified responder (or marked simulated)
- [ ] Reverse-shadow completed and feedback recorded
- [ ] Game day completed; recovery/rollback understood
- [ ] Handoff template and recipient read-back practiced
- [ ] First-page drill passed against rubric
- [ ] Rest, relief, compensation, and support policy acknowledged
- [ ] No secrets or real personal data stored in training artifacts
```

**First-page scenario:** synthetic inference API 5xx ratio rises after a canary. Expected: acknowledge; confirm current user impact and time window; check release/runbook; notify the correct incident lead if severity criteria are met; pause further promotion through the approved M08 mechanism; do not make an unreviewed destructive change; escalate if uncertainty or access failure exists; verify recovery and hand off follow-up. Common mistakes: diagnosing from one metric, hiding the page, assuming acknowledgement means resolution, or using privileged access without the approved path.

Scoring: 0–2 points each for acknowledgement/routing, impact confirmation, runbook use, safe mitigation/escalation, and verification/handoff. Pass at 8/10 with no critical safety failure. This is a classroom threshold `[ILLUSTRATIVE]`.

**L2 checkpoint — what you can now do:** build a synthetic rota, generate a useful handoff, exercise a local pager state machine, and analyze load without ranking individuals.

---

## 6. L3 — Sustainable paging design and operational trade-offs

### 6.1 Page classification decision rule

Ask in order:

1. Is there credible current or imminent user harm or a time-critical safety/security condition?
2. Does the response expectation require human action now?
3. Is there a safe automated response that is bounded, tested, observable, and has a stop condition?
4. Is the signal actionable with available context and an owner?
5. If it is not actionable now, should it become a ticket or be removed/redesigned?

A ticket is not a dumping ground. Give it an owner, impact, due date, and closure evidence. A page with missing context may still be urgent if the symptom indicates current harm; missing context is a defect to fix, not a reason to ignore the user impact.

### 6.2 Reduce pages at the source

Use:
- SLO/user-impact-based alerting (Unit 3);
- deduplication and grouping that preserve distinct impacts;
- explicit suppression rules with expiry, owner, and visibility;
- better defaults, runbooks, capacity headroom, and dependency fallback;
- bounded automation from Unit 7 with dry-run, allowlist, limits, audit, rollback, and manual stop;
- removal of alerts that never lead to useful action, after replay/validation;
- ownership accountability: the service generating the burden owns or funds remediation.

Never suppress an alert only to improve a page metric. A successful noise-reduction change should preserve true urgent signals, reduce non-actionable interruption, and have an evidence window.

### 6.3 Load balancing and expertise concentration

Shift fairness has multiple dimensions: scheduled shift count, primary/secondary role, local nights, weekends/holidays, severity, duration, after-hours interruption, and whether one person is the only effective handler for a class. A simple concentration metric can identify where training or runbook work is needed.

**Concentration example [ILLUSTRATIVE]:** of 20 actionable database pages, responder A handled 14 and responder B handled 6. A handled 70% of the observed pages. This is a reason to investigate knowledge concentration, shift allocation, and alert complexity—not a reason to blame A or force an immediate equal split without training. Add pairing, reverse-shadowing, and a tested runbook, then check whether multiple qualified responders can handle the class.

### 6.4 Coverage design memo: three staffing cases

These are explicit arithmetic examples, not staffing standards. A 24/7 primary rota requires 168 coverage-hours per week before secondary coverage, leave, training, breaks, incident overlap, and recovery. The calendar arithmetic is `24 × 7 = 168`. It is not a safe staffing calculation by itself.

#### Case A: small team — three engineers [ILLUSTRATIVE]

Assumptions: three engineers; each can contribute 40 paid working hours/week, but only a portion is available for service operations; PTO, training, sickness, and incident recovery reduce capacity. A primary rota covering every hour would distribute 168/3 = 56 clock-hours of availability per person per week if split evenly. That arithmetic alone is already incompatible with assuming each person can maintain a normal workload plus uninterrupted 24/7 availability. **Recommendation:** do not promise continuous human response unless shared coverage/managed support and relief are genuinely arranged. Prefer business-hours coverage or a documented best-effort overnight policy, reduce service scope, and add escalation/partner coverage.

Benefits: honest promise and less unsafe load. Risks: slower after-hours response. Prerequisites: user agreement, support-hours statement, detection/mitigation that works safely without a person where appropriate, and an escalation path for critical exceptions.

#### Case B: mid-sized team — eight engineers [ILLUSTRATIVE]

Assumptions: eight qualified responders, weekly primary with secondary backup. A single weekly primary rota requires 52 primary weeks/year, so average primary assignments are 52/8 = 6.5 per person/year before leave and skill restrictions. Secondary coverage and relief require separate capacity. A week is 168 availability-hours; this is not 168 hours of active work, but availability itself has a cost. Review night pages, incident duration, and recovery after heavy weeks. Do not put the same person as primary for two critical services at the same time unless the overlap and capacity have been explicitly tested.

Benefits: more ability to spread work and train. Risks: headcount does not guarantee expertise or availability. Prerequisites: competency matrix, PTO-aware schedule, overlap rules, relief plan, load reviews, and a tested escalation path.

#### Case C: multi-region follow-the-sun

Assumptions: three regions each provide an eight-hour staffed support window, with one-hour overlap between adjacent regions. Three nominal 8-hour windows yield 24 hours of coverage only if local staffing, handoffs, holidays, language/context, tooling, and escalation are all real. If each handoff needs one hour of overlap, the schedule needs planned overlap capacity; simply subtracting two hours from each region and still claiming full coverage is incorrect. Specify the exact UTC windows and convert using IANA time zones; daylight-saving changes alter offsets in some regions.

Benefits: fewer local overnight interruptions and continuity across the day. Risks: handoff omissions, regional context loss, and ambiguous ownership. Prerequisites: common incident IDs, synchronized timelines, read-back handoffs, shared access, documented escalation, and regular handoff drills.

### 6.5 Primary/secondary and tiered support

Secondary is a backup and escalation target, not an automatic co-primary. Prevent a responder from being primary for two critical rotations simultaneously unless a capacity review accepts the risk. Use L1 triage only if it can route and help safely; do not create a ticket wall that delays a service owner. A workable pattern may be L1 triage → L2 service owner → L3 SME, with explicit timeouts and permission to escalate when uncertain.

For shared platforms, separate responsibilities:
- CI/CD, registry, cluster, and secrets-backend failures: platform owner leads platform mitigation.
- Data correctness, schema semantics, feature freshness, and model quality: service/data/model owner leads domain diagnosis.
- Cross-boundary incidents: incident command coordinates a shared timeline and explicit owners. The platform team must not silently own application correctness; the service team must not assume platform incidents are someone else’s problem.

### 6.6 Business-hours coverage and “you build it, you run it”

“You build it, you run it” is not a complete support design. It is only responsible when engineers have ownership, tools, runbooks, time budget, training, access, backup, compensation/rest arrangements, and sustainable coverage. `[VERIFY]` source-specific framing: validate any organization’s interpretation against its actual policy.

A business-hours policy should state:
- support window and timezone;
- what is monitored outside the window;
- which events can trigger a human response after hours;
- whether response is guaranteed or best effort;
- user-facing expectations and SLO measurement windows;
- escalation and partner coverage;
- service restrictions when no safe response is possible.

Never market “24/7 support” when no one can respond. A service may have a 24-hour SLO measurement window and still have business-hours human support, but the operational gap must be explicitly risk-assessed and reflected in customer promises.

### 6.7 Human factors and safe decisions

Fatigue, interrupted sleep, and cognitive load should be treated as operational risk factors. `[ASSUMPTION]` For risky overnight actions, require a second-person review when one is reachable within the incident’s risk window; if no reviewer is available, use pre-approved reversible mitigations, escalate, or choose a safer bounded action. This is a guardrail to adapt, not a universal rule. Plan breaks, relief, and recovery after major incidents. Provide appropriate organizational support resources without asking responders to disclose sensitive health information in operational metrics.

Legal, compensation, union, and labor requirements vary by jurisdiction and employer. Consult qualified HR/legal representatives; this chapter is not legal advice.

### 6.8 Statistical and ethical limits of on-call metrics

- Small samples can be dominated by one incident.
- Missing acknowledgement timestamps must not be converted to zero.
- A person with fewer pages may have carried a long incident or a more complex service.
- Timezone and daylight-saving handling must be explicit.
- Page counts can be gamed by suppressing or reclassifying alerts.
- A bus-factor proxy measures observed handling, not true competence.
- Individual rankings encourage blame, gaming, and privacy intrusion.

Use aggregate trends to choose system-level actions: remove a noisy alert, fix a runbook, distribute expertise, change coverage, train owners, or reduce support promises. Define who can see raw data, retention, consent/transparency expectations, and prohibitions on disciplinary use.

### 6.9 Anti-pattern catalogue

| Bad practice | Harm | Corrected pattern |
|---|---|---|
| Every alert pages | Interruptions obscure urgent signals | Route by user impact and response deadline |
| Suppress alerts to lower metrics | Missed incidents and metric gaming | Replay, validate urgent-signal preservation, time-box suppressions |
| Same expert handles every page | Single point of human failure | Pairing, reverse-shadowing, runbooks, broader ownership |
| Secondary is primary elsewhere | No real backup during overlap | Schedule collision checks and declare infeasibility |
| “All good” handoff | Hidden dependency/incident state | Written handoff with explicit unknowns and read-back |
| Page with no owner | Delay and silent routing failure | Ownership metadata and dead-route tests |
| On-call added before readiness | Unsafe access and poor mitigation | Gate eligibility on SLOs, runbooks, access, route, drill |
| Overnight support implied but unstaffed | Broken promise | Explicit support hours or funded coverage |
| Page reduction as individual KPI | Gaming and surveillance | Aggregate system-health review |
| Freeze never ends | Work hoarding and growing release risk | Exit criteria, owner, review cadence, staged recovery |

### 6.10 Scenario exercises with defended decisions

#### Scenario A — Dependency-caused burn

Facts: inference API budget is under pressure after a feature-store dependency begins timing out. The API’s own deployment did not change; fallback is present but not tested at current load.

Options: freeze all releases; pause only changes that increase dependency load; improve fallback; escalate to provider; revise dependency contract; continue low-risk reliability work.

**Recommended decision:** stop risky changes that worsen the dependency path, test/enable approved fallback safely, contact provider, and prioritize resilience work. Do not freeze every change by default: a verified fallback fix may reduce user impact. Third-party cause does not erase responsibility for controllable mitigation. Record evidence, owner, expiry, and review.

Scoring (0–4): acknowledges user impact (1), preserves safe reliability work (1), defines provider and service-owner actions (1), names verification and review (1). A blanket “not our fault” answer scores zero on ownership.

#### Scenario B — Low-traffic noise

Facts: 3 requests in a short interval; 1 failed, yielding a 33% observed error fraction. The target is `[ILLUSTRATIVE]` 99.9%, but the sample is too small to estimate a stable trend.

**Recommended decision:** mark the evidence as low-volume/uncertain, use longer windows or traffic-independent synthetic probes, inspect user impact, and avoid a long freeze from a single short-window ratio alone. If a single failure is safety-critical, the service policy may still require action. Do not call missing traffic healthy.

Scoring: separates sample noise from impact (1), names corroborating evidence (1), avoids silently suppressing critical failure (1), explains policy-specific action (1).

#### Scenario C — Launch with little budget

Facts: a launch is commercially time-sensitive; remaining budget is `[ILLUSTRATIVE]` 8%; the launch has a canary and reversible rollback, but the canary’s low traffic weakens statistical power.

**Recommended decision:** compare options: defer, run a smaller staged canary with longer analysis and explicit stop conditions, or proceed only with documented risk acceptance and staffed rollback. The recommendation depends on user impact, data quality, canary sample size, rollback latency, and business cost. Do not treat “8%” as a universal freeze threshold.

Scoring: documents uncertainty (1), proposes reversible rollout (1), defines stop/rollback criteria (1), records approver and follow-up (1).

#### Scenario D — Critical security patch during freeze

Facts: feature releases are paused after a budget breach. A security fix addresses a confirmed exposure; a rollback path and test suite exist, but the patch may change dependency behavior.

**Recommended decision:** use the pre-defined security exception, with designated approver, time-box, validation, rollback/mitigation plan, audit record, and post-review. A freeze must not blindly block risk-reducing changes. If patch risk is high, coordinate a staged emergency change rather than silently bypassing controls.

Scoring: preserves the exception (1), verifies change and rollback (1), records approval/audit (1), communicates impact and follow-up (1).

**L3 checkpoint — what you can now do:** defend a paging classification, identify unsustainable coverage, design source-level noise reduction, and explain why metrics should trigger system improvements rather than blame.

---

## 7. L4 — On-call program governance and organizational resilience

### 7.1 Example on-call program policy

**Policy ID:** `ONCALL-POLICY-SIM-001`  
**Version:** 1.0 `[ILLUSTRATIVE]`  
**Owner:** Service Reliability Council (fictional)  
**Approvers:** Service owner, product stakeholder, SRE/engineering leadership  
**Review cadence:** weekly page review; monthly health review; quarterly policy review  
**Scope:** synthetic inference API and ETL pipeline; adapt per service.

**Eligibility gate:** no service joins a rotation without a named owner, critical user journeys/SLOs, tested alert rules, tested runbooks, working primary/secondary routes, verified least-privilege access, a fallback route, readiness evidence, and a first-page drill. A failed prerequisite blocks onboarding or narrows the support promise.

**Load guardrail:** `[ASSUMPTION][ILLUSTRATIVE]` if a service exceeds its locally agreed page-load guardrail in two consecutive review windows, feature expansion pauses for that service until the owner has funded and started a noise/toil reduction plan. The threshold must be derived from observed load, criticality, team capacity, and user promises; it is not an industry standard. Critical security fixes, rollbacks, and reliability work remain eligible under a documented risk review.

**Rest and relief:** organization-specific requirements. The policy must define how to request relief, how heavy incident exposure affects the next shift, who approves time off or compensation, and how coverage is transferred. `[VERIFY]` Consult HR/legal for local rules. No individual is expected to “heroically” absorb repeated unsafe load.

**Escalation:** primary → secondary → service owner/SME; incident commander coordinates qualifying incidents under Unit 4. If no responder acknowledges within the service’s defined window, trigger the documented fallback. Acknowledgement, escalation, and fallback are separately audited.

**Swaps/PTO/holidays:** swaps are recorded and accepted by both parties and rota owner; validate rest and collision constraints after swap. Holiday distribution is reviewed alongside actual night and incident burden. PTO cannot be silently overridden. If no safe schedule exists, reduce coverage promises or obtain partner coverage.

**Compensation:** `[VERIFY — organization/jurisdiction-specific]` on-call compensation, overtime, rest, time-off-in-lieu, and union terms are set by the organization with qualified HR/legal advice.

**Stop-the-line:** `[ASSUMPTION][ILLUSTRATIVE]` repeated page-load breaches trigger a service-level pause on discretionary feature work until alert/toil reduction actions have an owner, deadline, and verification plan. This does not block emergency mitigation, security fixes, rollback, or reliability work. The stop condition and lift criteria are written before the breach.

**Review:** every page is reviewed weekly: should it have paged, was routing correct, did runbook help, was the action safe, what removes recurrence, who owns the work, and by when? Monthly review examines aggregate load, nights, repeats, acknowledgement and resolution times, ownership concentration, and relief. Quarterly review checks whether coverage promises remain feasible.

### 7.2 On-call SLOs (distinct from service SLOs)

These are measures of the response system itself, not user-facing API availability.

| Measure | Example definition | Denominator/window | Limitation |
|---|---|---|---|
| Routing success | Synthetic test pages reaching the expected simulator route / all scheduled test pages | Monthly; count and percentage | Local success does not test carrier/device/provider |
| Timely acknowledgement | Valid pages acknowledged within the agreed response expectation / all pages with observable ack status | Monthly; report missing separately | Missing telemetry can bias result |
| Page-to-incident precision | Pages associated with a validated incident or necessary immediate action / reviewed pages | Weekly/monthly review window | Classification requires review and can be disputed |
| Coverage availability | Scheduled required intervals with a valid primary and secondary / required intervals | Per rota period | Does not prove responder is awake/reachable |
| Handoff completeness | Handoffs passing required-field and recipient read-back checks / handoffs reviewed | Monthly | Checkbox completion alone does not prove understanding |
| Route freshness | Routes with current owner/rotation/contact metadata / routes sampled | Weekly/monthly | Fresh metadata does not prove real delivery |

For each measure, store the source, query/script version, timezone, missing-data rule, owner, and review cadence. A missing denominator is **unknown**, not 100%.

### 7.3 Weekly page review and noisy-alert debt

For every page, ask:
1. Should this have paged a human now?
2. Did it identify user impact and response deadline?
3. Was the route correct and reachable?
4. Did the runbook lead to safe diagnostics/mitigation?
5. Was it duplicate, repeated, or missing context?
6. What change would prevent the next unnecessary interruption?
7. Who owns the change, by what date, and what evidence closes it?

Example debt register:

| ID | Impact | Owner | Due | Status | Closure evidence |
|---|---|---|---|---|---|
| ALERT-DEBT-SIM-01 | duplicate feature-store timeout pages | feature-platform-sim | 2026-11-06 | open | replay shows dedup; urgent dependency outage still pages |
| ALERT-DEBT-SIM-02 | no runbook link on ETL freshness page | data-platform-sim | 2026-11-04 | in progress | link check passes and trainee drill succeeds |
| ALERT-DEBT-SIM-03 | route points to retired owner | service-catalog-sim | 2026-11-02 | open | synthetic test page reaches current rotation |

### 7.4 Scaling the operating model

- **Startup:** one team may own service and platform tasks, but must still name primary/backup, scope support hours, and protect time for reliability work.
- **Multiple teams:** embedded service ownership plus a platform rota can work if boundaries are explicit and cross-team incidents have a common command path.
- **Central SRE:** useful for shared standards, tooling, coaching, and cross-service incident coordination; it cannot compensate for every service having no owner or runbook.
- **Shared coverage/managed service:** can extend coverage if scope, escalation, data access, and handoff quality are agreed. Product capabilities and contracts must be verified before relying on them.
- **Attrition/hiring gap:** reduce scope, switch to business-hours support, secure partner coverage, or pause risky service expansion. Do not quietly transfer the same burden to remaining staff.

### 7.5 Cost model

A simple transparent model:

`annual on-call opportunity cost = scheduled coverage hours × assumed opportunity-cost rate + active incident hours × incremental burden rate + tooling/support cost`

This is not a payroll formula. Avoid double-counting hours already included in salary or compensation. Use ranges and assumptions; compare the cost with the promised tier, incident impact, and business-hours alternative. Link detailed infrastructure/capacity economics to M15.

Example `[ILLUSTRATIVE]`: 168 coverage-hours/week × 52 weeks = 8,736 coverage-hours/year for one continuously covered primary seat. This is availability coverage, not active labor hours. Secondary, leave, training, overlap, relief, and incidents add requirements. A real cost estimate must state how availability and active work are valued and what compensation rules apply.

### 7.6 Paging-system resilience

Treat the paging path as a dependency chain: signal → route/ownership metadata → receiver/provider → network/DNS/identity → device/person → acknowledgement → escalation. A green service dashboard does not prove the entire chain works.

Minimum local/organizational controls:
- periodic synthetic test page with a known expected route;
- contact and rota freshness check;
- explicit watchdog for receiver/provider failure;
- documented out-of-band fallback that is not dependent on the failed path;
- audited break-glass and least-privilege access;
- safe test window and named owner;
- evidence of successful acknowledgement and escalation;
- periodic drill of the failure path, not just the happy path.

Never use an unapproved personal phone number or real employee contact in the training dataset. Never disable production routing to test a classroom scenario.

### 7.7 Eight synthetic organizational case analyses

The timelines and names below are invented training evidence, not historical claims.

#### Case 1 — One engineer carries 70% of night pages and resigns

- **Synthetic timeline:** over eight weeks, aggregate review shows responder A handled 70% of night pages; the rota report tracked shift count but not interruptions; A requests relief twice; no action is funded; A resigns.
- **Trigger:** concentrated night paging plus departure. **Contributors:** one-dimensional fairness metric, missing review, undocumented expertise, weak management response.
- **Immediate containment:** redistribute only after readiness checks; add backup/partner coverage; reduce noncritical support scope if necessary.
- **Prevention/owner/evidence:** engineering manager + service owner; aggregate night-load review, pair training, tested runbooks, coverage redesign; evidence: multiple qualified handlers and reviewed load distribution.
- **Unintended consequence:** forcing equal distribution before training can spread unsafe work rather than remove the cause.

#### Case 2 — Handoff omits degraded dependency

- **Synthetic timeline:** outgoing shift knows feature-store latency is elevated but writes “all good”; incoming shift sees ETL freshness miss 20 minutes later and initially treats it as a new unrelated issue; escalation is delayed.
- **Trigger:** missed escalation. **Contributors:** ambiguous handoff, no explicit unknowns, no recipient read-back.
- **Containment:** restore incident context, assign an owner, and communicate current impact.
- **Prevention/owner/evidence:** rota owner; mandatory dependency/risk section and cold-read check; evidence: handoff sample passes review and drill.
- **Unintended consequence:** overly long handoffs may hide key facts; use concise structured fields and severity-based synchronous review.

#### Case 3 — Secondary is primary elsewhere

- **Synthetic timeline:** primary A is handling a database incident; secondary B is simultaneously primary for a registry outage; both are unreachable during a new service failure.
- **Trigger:** no responder available. **Contributors:** no cross-rotation collision validation, false assumption that “secondary exists” means backup is real.
- **Containment:** invoke authorized fallback/incident command and reduce scope if no safe response is available.
- **Prevention/owner/evidence:** rota owner; collision test across critical rotations; evidence: schedule validation rejects overlap.
- **Unintended consequence:** overly rigid collision rules can make small-team coverage infeasible; surface infeasibility and revise support promises rather than hiding it.

#### Case 4 — Route points to a retired team for 40 minutes

- **Synthetic timeline:** ownership transfer occurred; alert labels still route to `team-legacy-sim`; no test page was run; the page waits 40 minutes.
- **Trigger:** dead route. **Contributors:** stale metadata, no route owner, missing periodic synthetic page.
- **Containment:** correct route, notify current service owner, assess impact and update incident timeline.
- **Prevention/owner/evidence:** service catalog/route owner; rename/retire checklist and freshness alert; evidence: test page reaches current rota.
- **Unintended consequence:** automated route changes without review may misroute sensitive incidents; require change audit and rollback.

#### Case 5 — Paging provider fails and no fallback exists

- **Synthetic timeline:** provider API/notification path fails; service alerts remain green in metrics; no acknowledgement occurs; team discovers failure during a customer report.
- **Trigger:** unavailable notification path. **Contributors:** single dependency, no watchdog, no out-of-band fallback drill.
- **Containment:** use approved alternate communication and assess active alerts.
- **Prevention/owner/evidence:** platform/on-call program owner; periodic provider test and documented fallback; evidence: failure drill detects outage and reaches responsible humans.
- **Unintended consequence:** redundant paths may duplicate pages or expose sensitive data; deduplicate and apply access controls.

#### Case 6 — Fatigued responder takes destructive action at 4 a.m.

- **Synthetic timeline:** repeated pages interrupt responder; a disk cleanup command removes data without verifying retention; recovery is needed.
- **Trigger:** destructive action. **Contributors:** fatigue, unsafe runbook, missing dry-run/approval, no relief path.
- **Containment:** stop further changes, preserve evidence, invoke restore/incident process, communicate impact.
- **Prevention/owner/evidence:** service owner + reliability lead; safe runbook with dry-run, bounded commands, restore test, and `[ASSUMPTION]` second-person review for risky overnight actions.
- **Unintended consequence:** mandatory review can delay a time-critical action; define pre-approved reversible mitigations and escalation criteria.

#### Case 7 — New responder lacks access

- **Synthetic timeline:** onboarding checkbox says “access reviewed,” but no authorized test occurred; page arrives; responder cannot inspect the service or use the approved break-glass path.
- **Trigger:** access denial. **Contributors:** checkbox-based readiness, least-privilege role not validated, unclear escalation.
- **Containment:** escalate to authorized responder; do not share credentials or bypass controls informally.
- **Prevention/owner/evidence:** service owner + identity/security owner; authorized access drill and audited JIT/break-glass test; evidence: test results and permissions review.
- **Unintended consequence:** overbroad access “to make pages easier” expands blast radius; verify minimum privilege.

#### Case 8 — Noisy service generates excessive pages for a year

- **Synthetic timeline:** recurring alert class generates high page volume; the owning service is not charged remediation time; responders mute alerts informally; a real incident later resembles the muted signal.
- **Trigger:** repeated interruption and reduced detection confidence. **Contributors:** incentives, missing noisy-alert debt, unowned remediation, unsafe suppression.
- **Containment:** restore visibility for urgent signals, review recent incidents, and establish a bounded remediation plan.
- **Prevention/owner/evidence:** service owner + product leadership; remediation funding, weekly page review, replay validation, expiry for suppression; evidence: fewer non-actionable pages with urgent-signal preservation.
- **Unintended consequence:** a simplistic page quota can encourage reclassification or under-reporting; use qualitative review and anti-gaming controls.

### 7.8 Wellbeing and ethics reflection

Write one page answering:
- Who can view raw page-level records, and why?
- How long are records retained? Can they be aggregated or pseudonymized?
- How are responders informed about measurement and permitted use?
- Which uses are explicitly prohibited (individual ranking, disciplinary decisions from raw counts, health inference)?
- How will the organization distinguish workload problems from performance problems?
- How can a responder request relief without stigma?
- What evidence proves the system is improving without exposing sensitive personal details?

**L4 checkpoint — what you can now do:** write an on-call policy, define on-call SLOs, govern noisy-alert debt, review coverage promises, and analyze systemic failures with owners and completion evidence.

---

## 8. Eight end-to-end labs

All labs use synthetic data. Run commands in a disposable directory and never point them at a production endpoint.

### Lab 1 — Rotation design and scheduler

**Goal:** generate a rota with PTO and a forced swap; inspect constraints and fairness components.

**Prerequisites:** Python 3.10+; save `rotation_scheduler.py` and its test file from §5.1 in `/tmp/oncall-unit10/`.

```bash
mkdir -p /tmp/oncall-unit10
cd /tmp/oncall-unit10
python3 rotation_scheduler.py
python3 -m unittest -v test_rotation_scheduler.py
```

**Expected:** seven dates, primary/secondary differ, PTO is respected, swap is honored, and four tests pass. **Failure injection:** set `PEOPLE = ["solo"]`; test should report infeasible staffing. **Verification:** inspect every row; do not infer human fairness from shift counts. **Cleanup:** `rm -rf /tmp/oncall-unit10` only after confirming the directory is disposable. **Troubleshooting:** ensure the test imports `rotation_scheduler.py` from the same directory. **Evidence:** schedule output, test output, written constraint review. **Safety:** this is not a real scheduling system; arbitrary rest intervals are not enforced by this compact version.

### Lab 2 — Handoff generator and cold read

**Goal:** generate a report and identify missing information.

**Setup:** save `handoff_report.py` and `synthetic_handoff.json` from §5.2 in `/tmp/oncall-unit10/`.

```bash
cd /tmp/oncall-unit10
python3 handoff_report.py synthetic_handoff.json > handoff.md
grep -E 'INC-SIM-104|NOT RECORDED|Alerts|Recent changes' handoff.md
```

**Expected:** incident and section names appear; recipient read-back remains visibly unfilled. **Failure injection:** remove `silences` from JSON; output must say `NOT PROVIDED`. **Verification:** incoming learner writes the current risk, next action, owner, and deadline without oral hints. **Cleanup:** delete only temporary synthetic files. **Troubleshooting:** malformed JSON returns an error and exit code 2. **Evidence:** report, cold-read answers, missing-data test. **Safety:** no real personal data or secrets.

### Lab 3 — Pager simulator

**Goal:** create, acknowledge, advance logical time, escalate, and test quiet-hours behavior.

**Setup:** save `pager_sim.py` from §5.3.

```bash
cd /tmp/oncall-unit10
python3 pager_sim.py
```

**Expected:** SEV2 quiet-hours page is suppressed; SEV1 page is created; advancing simulated time produces an escalation event; valid secondary acknowledgement is logged. **Failure injection:** in an interactive Python session, set `receiver_up=False` and create a page; expected fallback-required event. **Verification:** inspect JSON audit events. **Cleanup:** no service to stop; remove temporary file when done. **Troubleshooting:** unknown page IDs raise `ValueError`. **Evidence:** audit log and written explanation of each state transition. **Safety:** no real notification is sent; do not claim parity with a provider.

### Lab 4 — Load analysis

**Goal:** compute pages, night interruptions, acknowledgement data, repeats, and alert-class handler counts.

Create a small CSV from this header and at least six fictional rows:

```csv
page_id,person,shift_id,timestamp,ack_seconds,resolution_minutes,actionable,alert_class,repeat,night,sleep_disrupting
P1,responder-sim-01,S1,2026-10-20T23:15:00+05:30,45,20,1,api-5xx,0,1,1
P2,responder-sim-01,S1,2026-10-21T00:10:00+05:30,60,30,1,api-5xx,1,1,1
P3,responder-sim-02,S2,2026-10-21T10:00:00+05:30,30,15,0,cpu-warning,0,0,0
P4,responder-sim-03,S3,2026-10-22T02:00:00+05:30,,45,1,etl-freshness,0,1,1
P5,responder-sim-02,S2,2026-10-22T12:00:00+05:30,25,10,1,etl-freshness,0,0,0
P6,responder-sim-03,S3,2026-10-23T15:00:00+05:30,40,20,1,api-5xx,0,0,0
```

Run `python3 load_report.py sample_pages.csv`. **Expected:** `pages=6`, `night_pages=3`, `sleep_disrupting=3`, `repeats=1`, and acknowledgement mean based on five observed acknowledgement values. **Failure injection:** remove a required column or enter `night=maybe`; script must fail clearly. **Verification:** confirm missing acknowledgement is not zero. **Cleanup:** remove CSV/report. **Troubleshooting:** check column names and numeric values. **Evidence:** report and a paragraph describing system-level action. **Safety:** use fictional IDs only.

### Lab 5 — Forty-page triage

**Goal:** classify the 40 rows in §5.5.

**Steps:** copy the table into a worksheet; record one of the three labels, reason, owner/action, and whether the signal must remain detectable. Compare with the answer key only after classification.

**Expected:** answer-key proposal leaves 18 pages and converts 22; 55% numerical reduction; urgent signals are preserved according to the exercise’s stated classification. **Failure injection:** mark row 38 delete/redesign and explain the false-negative risk. **Verification:** calculate reduction independently and list ambiguous rows. **Cleanup:** keep only synthetic work product. **Troubleshooting:** if classifications differ, explain the user-impact and response-time evidence, not just the label. **Evidence:** completed table and ambiguity register. **Safety:** the answer key is illustrative, not a production alert policy.

### Lab 6 — Dead route and receiver outage

**Goal:** test route metadata, receiver failure detection, and fallback documentation.

**Steps:** use `pager_sim.py`; create a route with empty primary or secondary and observe `route-invalid`; then set `receiver_up=False`, create a page, and inspect audit events. Restore the simulator and run a valid test. Separately write a route inventory with `service_id`, `owner_id`, `rotation_id`, `primary_id`, `secondary_id`, `last_verified`, and `fallback_ref`.

**Expected:** invalid route is rejected; receiver failure is recorded; fallback is explicitly required; restored receiver accepts a synthetic page. **Failure injection:** use a nonexistent rotation ID in the inventory and ensure your checker flags it. **Verification:** every route has owner, current rotation, distinct primary/secondary, timestamp, and fallback reference. **Cleanup:** do not alter real systems; discard only temporary fixtures. **Troubleshooting:** a simulator event is not a real delivery acknowledgement. **Evidence:** route audit, receiver failure log, fallback runbook. **Safety:** never disable a production receiver as a lab exercise.

### Lab 7 — Onboarding and first-page drill

**Goal:** assess readiness without exposing real credentials.

**Steps:** complete checklist in §5.7; run the SEV2/SEV1 scenario; write a short timeline and read-back handoff. Score the drill using the five categories (0–2 each).

**Expected:** 8/10 or higher `[ILLUSTRATIVE]` with no critical safety failure. **Failure injection:** mark access unavailable; expected action is escalation to an authorized responder, not credential sharing. **Verification:** checklist differentiates real shadowing from simulation. **Cleanup:** keep synthetic evidence only. **Troubleshooting:** if a step cannot be verified, mark “not checked,” not complete. **Evidence:** checklist, score, timeline, gaps and owners. **Safety:** no production access changes; actual access checks require authorization.

### Lab 8 — Program governance and design review

**Goal:** produce the on-call policy, three coverage memos, monthly health review, alert debt list, and wellbeing assessment.

**Steps:** adapt §7.1 policy; calculate 168 weekly primary coverage-hours; compare small, mid-sized, and follow-the-sun cases in §6.4; select at least three noisy-alert debt items; define on-call SLOs and data retention.

**Expected:** each decision has assumptions, owner, evidence, and review date; unsupported 24/7 promises are rejected; raw page counts are not used to rank individuals. **Failure injection:** remove secondary coverage from one interval; document reduced support promise or partner coverage rather than silently accepting the gap. **Verification:** peer role-play: product, service owner, SRE, and responder each state risks and a compromise. **Cleanup:** no live changes. **Troubleshooting:** distinguish coverage hours from active labor hours. **Evidence:** policy, design memo, debt register, governance minutes, privacy reflection. **Safety:** compensation/legal fields remain organization-specific.

---

## 9. Additional practical artifacts

### 9.1 Stakeholder agreement checklist

- [ ] Service scope and user journeys are explicit.
- [ ] Support hours and response promises match staffed reality.
- [ ] Primary, secondary, escalation, and IC responsibilities are defined.
- [ ] Service owner, product stakeholder, and reliability leadership agree on page criteria.
- [ ] SLO risk and service criticality drive paging policy.
- [ ] Runbooks, routes, access, and fallback are tested.
- [ ] PTO, swaps, holidays, rest, and relief have a documented process.
- [ ] Aggregate metrics, privacy, access, retention, and prohibited uses are agreed.
- [ ] Noisy-alert debt has owners, due dates, and closure evidence.
- [ ] A route/receiver outage drill has an owner and cadence.
- [ ] Review and dispute path is defined.
- [ ] If staffing is infeasible, the support promise can be reduced safely.

### 9.2 Negotiation role-play

**Product perspective:** “The inference API is a core journey. We need dependable response for customer-impacting outages. We also need enough engineering capacity to ship planned features.”

**Reliability perspective:** “The current rota shows repeated night interruptions concentrated in one handler. Several pages lack runbooks. We cannot safely promise 24/7 response until routes, backup coverage, and relief are demonstrated.”

**Service owner perspective:** “I can prioritize deduplication, runbook fixes, and dependency fallback, but need a committed engineering allocation and a review date.”

**Responder perspective:** “The schedule looks equal by shifts but not by sleep disruption. I need a safe escalation path and a way to request relief without stigma.”

**Decision record template:**

```markdown
Decision ID:
Date/time/timezone:
Participants/roles (fictional IDs in training):
User risk:
People/coverage risk:
Options considered:
Decision and rationale:
Assumptions / uncertainty:
Temporary controls:
Owner + deadline:
Escalation/dispute path:
Review/lift criteria:
Evidence required:
```

A good agreement is specific enough to execute and revisable when evidence changes. It is not a promise that incidents will never happen.

### 9.3 Rotation design decision rules

| Decision | Benefit | Risk/cost | Rule |
|---|---|---|---|
| Weekly vs daily shift | Continuity vs frequent handoff | Longer availability vs context loss | Choose based on observed incident duration and handoff reliability |
| Primary/secondary | Backup and escalation | False assurance if both collide | Validate distinct assignment and independent availability |
| Business-hours only | Bounded burden | Delayed response outside window | Use only with explicit customer promise and safe after-hours behavior |
| Follow-the-sun | Reduced local nights | Handoff and regional context costs | Require real staffed overlap and common incident state |
| Page load guardrail | Makes chronic burden visible | Can be gamed or suppress critical signals | Review every page and protect urgent detection |
| Second-person review overnight | Reduces risky solo actions | May delay mitigation | Predefine safe reversible actions and escalation if reviewer unavailable |

### 9.4 Eight exercise answer-key highlights

The full exercise set follows in §10. Core principles:
- coverage math is not staffing feasibility;
- a fairness score is not a moral or legal verdict;
- a missing route or access path is a readiness failure;
- low page count can mean good alerting or broken detection;
- page reduction must preserve urgent signal detection;
- incident command coordinates; primary responders do not have to solve everything;
- raw data is for system learning under a privacy policy, not individual ranking;
- stop-the-line policies need exceptions, review dates, and lift criteria.

---

## 10. Exercises and answer key

Use 0–4 points per exercise. **80% or above:** proceed. **60–79%:** remediate missed objectives and repeat targeted labs. **Below 60%:** repeat the relevant level. Answers should defend decisions and identify uncertainty.

### EX-01 — Roles (L1, 5 min)

**Prompt:** The primary acknowledges a SEV2 page and begins diagnosis. Who is incident commander by default?

**Model answer:** Not necessarily the primary. Use the incident-command policy and assign/announce the IC when criteria require one. Acknowledgement is not command assignment.

**Common wrong answer:** “The primary is always IC.” It confuses technical response with coordination.

### EX-02 — Shift arithmetic (L1, 5 min)

**Prompt:** Calculate weekly clock coverage for one primary seat.

**Model answer:** `24 × 7 = 168` coverage-hours. This does not equal 168 hours of active work and does not account for secondary, leave, training, rest, or incident overlap.

**Common wrong answer:** “Two engineers can cover 84 hours each, so it is safe.” Arithmetic alone cannot establish sustainable staffing.

### EX-03 — Scheduler collision (L2, 8 min)

**Prompt:** The forced swap assigns the same person as primary and secondary.

**Model answer:** Reject it as infeasible and require a new assignment or changed coverage promise. Never silently duplicate the person.

**Common wrong answer:** accept because the person is technically capable; there is no independent backup.

### EX-04 — Fairness (L2, 8 min)

**Prompt:** Every person has four shifts, but one person received 70% of night pages.

**Model answer:** Investigate night burden, service expertise, schedule, and alert class. Add training/coverage and reduce the source of noisy pages. Do not rank or blame the person.

**Common wrong answer:** claim the rota is fair because shift counts match.

### EX-05 — Handoff defect (L2, 6 min)

**Prompt:** Handoff says “all good,” but a dependency is degraded and an alert is silenced.

**Model answer:** Record dependency state, customer impact, silence reason/owner/expiry, next action and deadline; perform read-back. If details are unknown, state “not checked.”

**Common wrong answer:** leave the note concise by omitting unresolved risks.

### EX-06 — Page classification (L2, 8 min)

**Prompt:** CPU is high for 30 seconds, no user impact, but an SLO symptom alert is green.

**Model answer:** Usually ticket or redesign, based on validated capacity risk; CPU alone does not necessarily warrant waking a person. Preserve detection if capacity is a known leading indicator and the response is time-critical.

**Common wrong answer:** page every threshold crossing.

### EX-07 — Noise reduction (L3, 8 min)

**Prompt:** Duplicates create 100 pages per week. Is a 90% page reduction successful?

**Model answer:** Only if replay shows true urgent signals remain detectable, routing and incident precision improve, and no hidden incident class was suppressed. Page reduction is not the goal by itself.

**Common wrong answer:** celebrate count reduction without testing false negatives.

### EX-08 — Dead route (L2, 5 min)

**Prompt:** Ownership metadata points to a team retired last month.

**Model answer:** Treat as routing failure; correct ownership with audit, page the current owner through approved fallback, and add periodic freshness/test-page checks.

**Common wrong answer:** assume someone will notice the page eventually.

### EX-09 — After-hours escalation (L3, 8 min)

**Prompt:** Primary has not acknowledged; secondary is primary for another critical service.

**Model answer:** The route is not a valid backup. Use an independent fallback/IC path and record a rota collision. Reduce support promise or redesign schedule.

**Common wrong answer:** keep waiting because secondary exists in the configuration.

### EX-10 — Fatigue risk (L3, 8 min)

**Prompt:** At 04:00, a tired responder considers a destructive cleanup command.

**Model answer:** Use a safe, reversible, pre-approved mitigation; dry-run and verify target; seek a second-person review when reachable under the assumed guardrail; escalate if uncertain. Preserve evidence and follow restore procedures if damage occurs.

**Common wrong answer:** “Move fast because it is an incident,” without blast-radius assessment.

### EX-11 — Follow-the-sun overlap (L3, 8 min)

**Prompt:** Three regions claim 24-hour support with 8-hour shifts but no overlap.

**Model answer:** The arithmetic covers nominal hours only. Define handoff windows, local timezone/DST, holidays, staffed capability, and fallback. If overlap cannot be funded, explicitly accept and document the handoff gap or revise promise.

**Common wrong answer:** assume regional labels prove continuous operational capability.

### EX-12 — Health report (L3, 8 min)

**Prompt:** A person has twice the pages of peers.

**Model answer:** Review service/alert class, shift exposure, severity, repeats, incident duration, and whether the person is the only trained handler. Use aggregate system changes and transparent privacy controls; do not infer performance.

**Common wrong answer:** rank the person as less efficient.

### EX-13 — Bus-factor proxy (L3, 6 min)

**Prompt:** An alert class has one observed handler in the dataset.

**Model answer:** Treat it as possible knowledge concentration, not proof that only one person can handle it. Verify training and availability; pair, document, and run a drill.

**Common wrong answer:** claim the individual is hoarding knowledge.

### EX-14 — Receiver outage (L4, 6 min)

**Prompt:** Local receiver is down and no audit event appears.

**Model answer:** A watchdog must detect lack of receiver health/test acknowledgement via an independent path. Test fallback, restore receiver, and record evidence. A simulator cannot prove provider/carrier/device delivery.

**Common wrong answer:** conclude no pages means no incident.

### EX-15 — Stop-the-line (L4, 10 min)

**Prompt:** A service repeatedly exceeds an agreed page-load guardrail, but product has a launch date.

**Model answer:** Apply the pre-agreed policy: pause discretionary feature expansion until alert/toil reduction work has owners and evidence, while allowing security fixes, rollback, mitigation, and reliability work under documented controls. Reassess scope and user promises. Thresholds are local assumptions.

**Common wrong answer:** freeze all changes indefinitely or ignore the policy because the date is important.

### EX-16 — Privacy (L4, 8 min)

**Prompt:** A manager requests a leaderboard of responders by page count.

**Model answer:** Decline the leaderboard as an unsafe interpretation. Provide aggregate workload and service-level analysis, explain data limitations, define access/retention, and investigate causes without ranking individuals.

**Common wrong answer:** assume more data automatically improves accountability.

### EX-17 — Business-hours promise (L3, 8 min)

**Prompt:** Service has a 24-hour SLO window but only staffed support from 09:00–17:00 local time.

**Model answer:** State the support window honestly, define after-hours behavior and risk, and determine whether the SLO/customer promise is compatible with response capacity. An SLO measurement window does not create staffing.

**Common wrong answer:** imply 24/7 response because metrics run continuously.

### EX-18 — Design review (L4, 15 min)

**Prompt:** Choose between a small shared rota, business-hours support, and a partner-team follow-the-sun arrangement for a critical inference service.

**Model answer:** State user impact and required response time, calculate coverage hours, include PTO/training/overlap/rest, assess expertise and route readiness, estimate opportunity cost with explicit assumptions, and document the chosen support promise and fallback. No model is universally best.

**Common wrong answer:** choose the option with most coverage hours without validating staffed capability.

---

## 11. Glossary and quick-reference checklists

### Glossary additions

- **Actionable-page ratio:** reviewed pages classified as actionable-now divided by all reviewed pages in the stated period. Always report review coverage and classification rules.
- **Acknowledgement:** explicit responder receipt under the documented mechanism; it does not prove mitigation started.
- **Coverage availability:** required intervals with a valid scheduled responder/backup configuration; not a guarantee of human reachability.
- **Escalation:** transfer or addition of response responsibility when acknowledgement, expertise, severity, or risk requires it.
- **Handoff completeness:** presence of required state/risk/action fields plus a recipient understanding check.
- **Night interval:** locally defined clock interval for the rota timezone; DST and timezone changes must be handled.
- **Page-to-incident precision:** proportion of reviewed pages that led to a validated incident or necessary immediate action under the documented classification rule.
- **Page budget:** an assumed operational interruption guardrail, distinct from SLO error budget.
- **PTO:** planned leave; the scheduler must not assign someone marked unavailable.
- **Rest interval:** elapsed time between shifts or after an incident, defined by local policy and applicable rules.
- **Route freshness:** age/status of ownership and routing metadata against a stated verification policy.
- **Synthetic test page:** a known non-production test event used to check a local or authorized paging path.
- **Time-to-resolution:** elapsed time from the documented incident start to declared resolution, using a consistent definition.
- **Weighted burden:** a locally defined combination of role, nights, duration, severity, and interruption; weights are assumptions and must not replace component metrics.

### Quick-reference: before a shift

- Check rota and backup; confirm no overlap collision.
- Read handoff, active incident state, recent changes, silences, and unknowns.
- Verify runbooks, dashboard access, route freshness, and escalation path.
- Know how to request help/relief and how to use approved break-glass access.
- Never put secrets or personal contact details into the handoff.

### Quick-reference: after a page

- Acknowledge through the defined mechanism.
- Confirm user impact and severity; do not diagnose from one metric alone.
- Use the runbook and safe, reversible mitigation.
- Escalate when uncertain, blocked, or outside expertise.
- Verify recovery, record timestamps, and communicate status.
- Create follow-up work for noise, missing context, route, runbook, or ownership defects.

---

## 12. Roadmap coverage audit

Status reflects the material actually included in this standalone chapter, not verification against a live repository checkout. The uploaded prompt is the detailed requirements source. The generated syllabus file itself and exact `Roadmap_ptree.md` were not available for direct inspection during this run.

| Source requirement | Exact chapter section/artifact | Evidence included | Status | Gap or reason |
|---|---|---|---|---|
| L1 role definitions and sustainability | §3, §4.1–4.3 | Roles, human impact, rotation types, no unsupported numeric threshold | Covered | Published specific numerical guidance intentionally not quoted |
| L1 load dimensions | §5.4 | Metrics table and report | Partial | Dataset schema supports dimensions; real timezone/DST parsing not implemented |
| L1 shadow/reverse-shadow/readiness | §4.4, §5.7, Lab 7 | Checklist and simulated first-page drill | Covered | Solo simulation is not real team practice |
| L1 handoff essentials | §4.5, §5.2 | Template, report generator, explicit missing-data semantics | Covered | Report generator is a compact JSON input example |
| L1 escalation and visibility | §4.1, §5.3, §5.6 | Routing chain, simulator, route inventory guidance | Partial | No full persistent contact-data service |
| L1 inference API and ETL pages | §4.6 | Two fictional pages and response paths | Covered | Values are illustrative |
| L2 rotation scheduler | §5.1, Lab 1 | Complete runnable script and tests | Partial | Arbitrary minimum rest and DST-aware intervals are not enforced |
| L2 fairness metrics and infeasibility | §5.1, §6.3–6.4 | Counts, burden discussion, infeasibility error | Partial | Simplified scheduler has no holiday calendar integration or optimizer |
| L2 handoff generator | §5.2, Lab 2 | Complete script, synthetic JSON, missing-data behavior | Covered | No external links or timezone conversion |
| L2 local paging simulator | §5.3, Lab 3 | Create/ack/escalate/quiet-hours/receiver-failure audit | Partial | No real delivery, persistent store, or independent watchdog process |
| L2 on-call load metrics | §5.4, Lab 4 | Complete CSV report script and metric definitions | Partial | Night flag supplied in dataset; no timezone-aware calculation from timestamp |
| L2 forty-page triage | §5.5, Lab 5 | 40 records, complete classifications, reduction arithmetic | Covered | Answer key is illustrative and requires local replay before real changes |
| L2 dead-route/outage tests | §5.6, Lab 6 | Route checks and failure drill instructions | Partial | No complete automated route-inventory checker script |
| L2 onboarding/first-page drill | §5.7, Lab 7 | Checklist, scenario, scoring rubric | Covered | Real access and shadowing cannot be simulated |
| L3 classification and source noise reduction | §6.1–6.2 | Decision sequence and safe reduction controls | Covered | Service-specific alert rules deferred to Unit 3 |
| L3 load balancing and bus factor | §5.4, §6.3–6.4 | Concentration proxy and design examples | Partial | Handling concentration by alert class is measured; training competence is not automatically known |
| L3 human factors and safe actions | §6.7 | Fatigue risks, assumed two-person review, relief | Covered | Organization-specific support/HR rules need verification |
| L3 follow-the-sun and staffing models | §6.4–6.6 | Three coverage cases and explicit arithmetic | Covered | Real local time/DST schedule not generated |
| L3 platform boundaries and tiered support | §6.5 | Platform/service owner boundary and L1/L2/L3 | Covered | Local team-specific ownership must be defined |
| L3 legal/HR awareness | §6.7, §7.1 | Jurisdiction-specific caveat and referral | Covered | Not legal advice |
| L4 program policy | §7.1 | Eligibility, load guardrail, rest, escalation, swaps, holidays, compensation placeholder | Covered | Values must be approved by actual organization |
| L4 on-call SLOs | §7.2 | Definitions and denominators/limitations | Covered | Production instrumentation not wired |
| L4 weekly/monthly reviews and debt | §7.3 | Review questions and debt register | Covered | Synthetic examples |
| L4 scaling, attrition, cost | §7.4–7.5 | Operating models and cost equation | Covered | Cost values require local inputs |
| L4 paging resilience and security | §7.6 | Dependency chain, fallback, JIT/break-glass | Partial | No actual provider/device test performed |
| L4 wellbeing/privacy | §6.8, §7.8 | Aggregate-only principles and reflection | Covered | Organization needs its own retention/access policy |
| L4 eight organizational cases | §7.7 cases 1–8 | Timeline, trigger/contributors, containment, owner/evidence, unintended consequence | Covered | All case details explicitly synthetic |
| Mandatory artifact 1: scheduler | §5.1 | Code and tests | Partial | Rest interval limitation disclosed |
| Mandatory artifact 2: handoff | §5.2 | Template, generator, synthetic input | Covered | Compact generator, not a production connector |
| Mandatory artifact 3: load analysis | §5.4 | Script and metrics | Partial | Does not parse timezone from timestamp |
| Mandatory artifact 4: 40-page exercise | §5.5 | 40 records and key | Covered | Needs replay before real changes |
| Mandatory artifact 5: dead-route/outage | §5.6, Lab 6 | Drill and audit checklist | Partial | Automated route checker not supplied |
| Mandatory artifact 6: onboarding/drill | §5.7 | Checklist and scoring | Covered | Real shadowing is external |
| Mandatory artifact 7: coverage memo | §6.4 | Small, mid-sized, follow-the-sun | Covered | All staffing assumptions are illustrative |
| Mandatory artifact 8: policy | §7.1 | Program policy with guardrails | Covered | Compensation and labor fields require local approval |
| Mandatory artifact 9: wellbeing/ethics | §6.8, §7.8 | Reflection and privacy guardrails | Covered | Organization must implement access/retention controls |
| Eight end-to-end labs | §8 Labs 1–8 | Objective, setup, commands, expected output, failure injection, cleanup, evidence | Partial | Lab 1 exposes scheduler rest-interval limitation; some failure drills are manual by design |
| At least 15 exercises with answers | §10 EX-01–EX-18 | 18 exercises with model answers and common wrong answers | Covered | Use the stated rubric |
| Source verification and exact claims | Source note, §12 | No fabricated statistics; source access limitations disclosed | Partial | Exact generated syllabus and Roadmap_ptree not verified |

## 13. Execution and evidence report

**Verified in this generation run:** the uploaded prompt was read; the authoritative syllabus-generation prompt was retrieved and inspected for the M10 Unit 10 structure and requirements. The local target chapter was written as a standalone Markdown file.

**Verified local execution:** extracted the scheduler, handoff generator, pager simulator, and load-report scripts into `/tmp/unit10_validate/`; all five scripts compiled successfully. Four scheduler unit tests passed. The scheduler CLI, handoff report, pager simulator, and load report smoke tests all exited successfully using synthetic fixtures. The load report produced `pages=6`, `night_pages=3`, `sleep_disrupting=3`, `actionable_ratio=0.833`, and `repeats=1` for the six-row fixture. Five additional cross-tool tests are included in this chapter but were not yet run at the time of writing. No M08 service, Prometheus, Alertmanager, `kind` cluster, production endpoint, paging provider, device, or identity system was accessed.

**Expected results, not verified:** the five `test_local_tools.py` cases should cover handoff missing-data semantics, SEV1-only quiet-hours override, logical-clock escalation, receiver failure/fallback, and invalid route rejection. The load report's malformed-input behavior should be tested separately before operational use. The scheduler explicitly does not enforce arbitrary rest intervals, and the load report accepts the `night` flag rather than calculating local time from the timestamp.

## 14. Repository-change boundary report

The exact repository checkout was not available for inspection or mutation. This artifact is a standalone file at `/mnt/data/10-on-call-rotations-handoffs-and-sustainable-paging.md`; therefore I cannot claim that the requested repository path was modified or that no other repository file changed. No repository file was intentionally edited by this chapter-generation step.

## 15. Remaining limitations and `[VERIFY]` items

1. Verify the actual `Roadmap_ptree.md` tree and generated `SYLLABUS-Site-Reliability-Engineering-and-Incident-Management.md` Unit 10 entry when the repository is available.
2. Run the embedded scripts and tests in a temporary lab directory and record actual output before treating them as validated.
3. Upgrade the teaching scheduler before real use: enforce actual shift intervals, minimum rest, timezone/DST, holidays, PTO ranges, cross-rotation collisions, and infeasibility diagnostics.
4. Upgrade the load report before real use: parse IANA time zones, calculate night windows from timestamps, handle daylight-saving changes, and add explicit missing-resolution/incident definitions.
5. Implement an automated route-inventory checker and independent watchdog if required by the lab environment; the current route-outage procedure is a manual teaching drill.
6. Verify any selected provider's actual notification, retry, escalation, audit, and fallback behavior against its current documentation and contract. This chapter makes no parity claims.
7. Set compensation, rest, leave, union, and employment rules with qualified HR/legal guidance for the relevant jurisdiction.
8. All thresholds and sample values marked `[ILLUSTRATIVE]` or `[ASSUMPTION]` require stakeholder agreement and should be revised from service history and user needs.

**Completion statement:** This chapter teaches the operating model, includes reusable synthetic artifacts and eight labs, and explicitly records incomplete engineering pieces rather than claiming production readiness. The included compact scripts are learning aids; they are not a production paging, workforce-scheduling, or HR-compliance system.
