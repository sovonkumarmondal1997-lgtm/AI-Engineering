# Data Classification, Sensitivity and Criticality

> **Module:** Stage 2D — Data Architecture / `10-Data-Governance-Security-Privacy-and-Compliance/`  
> **Topic sequence:** 02 of 09  
> **Target file:** `02-data-classification-sensitivity-and-criticality.md`  
> **Learning progression:** Beginner → Intermediate → Advanced

## Source alignment and scope

The module roadmap is the primary authority for this lesson's sequence and completion expectations. It identifies this topic as the second topic in Module 2D.10, following the governance operating model and preceding identity and access control. Its stated learning outcomes are to build/apply a classification scheme, distinguish sensitivity from criticality, inventory and classify data at field level where needed, connect labels to handling requirements, explain propagation through pipelines and derived data, and design review and recertification.

The repository tree confirms this exact filename under `Stage 2D — Data Architecture/10-Data-Governance-Security-Privacy-and-Compliance/`. The module roadmap says the topic files were empty when it was written. Therefore, the detailed explanations, examples, synthetic records, exercises, and templates in this lesson are **instructional elaborations** designed to teach the roadmap's scope; they are not claims about pre-existing topic-file requirements.

**Educational and legal caution:** The classification scheme and handling rules below are illustrative organisational design choices, not a universal standard, legal taxonomy, or statement of compliance. Actual obligations depend on jurisdiction, sector, contracts, data types, and organisational context. Qualified privacy, legal, security, and compliance specialists must interpret applicable obligations. Use synthetic data only.

---

## 1. Topic overview: what classification is for

**Data classification** is the process of assigning meaningful labels to data based on defined criteria—such as harm from exposure, business impact from loss or corruption, and required handling—then connecting those labels to documented controls and operational procedures.

A classification label is metadata. It is not a security control by itself. A label such as `Restricted` does not automatically prevent access, encrypt a file, mask a column, delete an expired record, or create audit evidence. Systems and operating procedures must interpret the label, implement the appropriate controls, monitor them, and verify that they work.

### 1.1 Why it matters in industry

A production data platform may contain customer records, payment transactions, employee files, operational telemetry, public product information, analytical aggregates, event streams, exports, and model-training datasets. Applying the same controls to every asset can be wasteful and still miss important risks. Applying no consistent classification can lead to sensitive data being exposed through an overlooked table, export, log, dashboard, or derived dataset.

Classification creates a shared vocabulary for decisions such as:

- who may discover, read, modify, export, or share an asset;
- whether fields need masking in development or analytics;
- which encryption and key-management requirements apply;
- what may appear in logs and monitoring systems;
- how data may be shared with partners;
- which retention and deletion rules must be considered;
- which assets need stronger monitoring, recovery objectives, or review;
- how data labels and restrictions propagate into derived assets.

### 1.2 The key distinction

The module roadmap defines **sensitivity** as the harm from exposure or misuse and **criticality** as the harm from loss or unavailability. They are separate axes. Sensitivity primarily informs confidentiality-oriented handling; criticality informs the consequences of loss, corruption, or interruption and therefore supports integrity and availability decisions. A complete architecture also considers data integrity and availability directly rather than assuming that a single classification label captures every requirement.

### 1.3 Learning objectives

By the end of this topic, you should be able to:

1. Build and apply an explicitly defined, organisation-specific classification scheme.
2. Distinguish sensitivity from criticality and explain their relationship to confidentiality, integrity, and availability.
3. Create a data inventory and classify datasets and fields where necessary.
4. Assign handling requirements to classification levels without treating the labels as controls.
5. Define and apply inheritance and propagation rules through data pipelines and derived assets.
6. Represent classification as useful, machine-readable metadata.
7. Establish ownership, review, recertification, exception, and drift-management procedures.
8. Produce a defensible classification register, propagation rules, review procedure, and architecture decision record (ADR).

### 1.4 Prerequisites and learning dependencies

The module roadmap names the following dependencies:

| Prerequisite | What you need to understand | Why it matters here | If weak, review |
|---|---|---|---|
| Topic 01 — Governance operating model and accountability | Data owner, steward, policy owner, decision rights, escalation | Someone must decide and maintain classifications | Build a responsibility matrix for ten data decisions |
| Data modelling and dictionary concepts (2D.4) | Entities, attributes, field names, data dictionary | Classification may need to be applied at attribute level | Write dictionary entries for five synthetic fields |
| Platform metadata and catalogue concepts (2D.7) | Assets, zones, metadata, tenancy boundaries | Classification needs discoverable, durable metadata | Define mandatory metadata for a dataset |
| Related foundations | Data contracts, lineage, storage lifecycle, replication, streams | Labels must travel with copies and transformations | List every copy of one synthetic dataset |

**Recommended effort:** approximately 6–8 hours, as suggested by the module roadmap. This is an estimate, not a deadline or requirement.

---

## 2. Core vocabulary

| Term | Meaning | Practical example |
|---|---|---|
| **Data asset** | A managed unit of data, such as a table, file, stream, view, report, feature set, or data product | `customer_profile` table |
| **Data inventory** | A structured list of known assets and key attributes about them | Asset ID, owner, location, purpose, sensitivity, criticality |
| **Metadata** | Information describing an asset, its structure, meaning, origin, operation, or handling | Owner, schema, classification label, lineage |
| **Classification scheme** | Defined labels, criteria, and rules for assigning them | Public, Internal, Confidential, Restricted |
| **Sensitivity** | Potential harm from exposure, disclosure, or misuse | Exposure of account identifiers |
| **Criticality** | Business importance and impact if data are lost, corrupted, delayed, or unavailable | Payment ledger needed for daily settlement |
| **Handling requirement** | A rule describing how data must be accessed, protected, stored, used, shared, or retired | Mask customer identifiers in non-production |
| **Field-level classification** | Classification applied to individual columns or attributes | `email_address` marked Confidential |
| **Inheritance** | A rule for assigning a derived asset a label based on its inputs and transformation | Report inherits the most restrictive input label unless justified otherwise |
| **Propagation** | Carrying classification and handling metadata through system boundaries and transformations | A label follows a source field into a curated table and export |
| **Classification drift** | A label or handling rule no longer matches the current data, use, context, or risk | A previously internal dataset receives account numbers but keeps its old label |
| **Recertification** | A planned or event-triggered review to confirm a classification remains correct | Owner reviews asset after a new use case |

### 2.1 What classification is not

- It is not the same as access control: classification describes data handling needs; access control evaluates whether a principal may perform an action.
- It is not the same as privacy analysis: personal data may require purpose, rights, minimisation, and lifecycle decisions beyond a sensitivity label.
- It is not a guarantee of anonymity: aggregation, masking, or pseudonymisation can leave re-identification risk.
- It is not a legal conclusion: an organisational label must be mapped to applicable obligations by qualified specialists.
- It is not a one-time spreadsheet exercise: data, uses, schemas, ownership, and threats change.

---

## 3. Sensitivity, criticality, and the CIA triad

The **CIA triad** is a common security model describing confidentiality, integrity, and availability. It is a useful lens, not a complete risk model and not a substitute for business analysis.

| Concept | Question | Typical failure | Example impact | Controls it may inform |
|---|---|---|---|---|
| **Confidentiality** | Can data be seen only by authorised parties? | Unauthorised disclosure | Customer details exposed | Access restrictions, encryption, masking, safe sharing |
| **Integrity** | Are data accurate, complete, and protected from unauthorised or unintended change? | Corruption, unauthorised modification, silent transformation error | Incorrect payment status or misleading report | Write permissions, validation, reconciliation, versioning, change logs |
| **Availability** | Are data accessible when needed by authorised users and systems? | Outage, deletion, failed recovery, excessive latency | Settlement or operational decision delayed | Backups, replication, recovery procedures, capacity and resilience controls |
| **Sensitivity** | How much harm could exposure or misuse cause? | Disclosure or misuse | Identity fraud, privacy harm, competitive harm | Mainly confidentiality-oriented handling, plus context-specific controls |
| **Criticality** | How much harm could loss, corruption, delay, or unavailability cause? | Data or service failure | Financial reconciliation failure, operational interruption | Integrity, availability, recovery, quality and monitoring controls |

Sensitivity and criticality are related to CIA but are not synonyms for the CIA dimensions. Sensitivity usually overlaps strongly with confidentiality impact. Criticality often reflects integrity and availability impact, but may also reflect business importance, dependency, recovery needs, and time sensitivity.

### 3.1 Sensitivity and criticality are independent axes

| Example asset | Illustrative sensitivity label | Illustrative criticality | Reasoning |
|---|---|---|---|
| Public product-price feed | Public | High | Public disclosure is expected, but an incorrect or unavailable feed could disrupt sales operations |
| Synthetic customer contact table | Confidential | Medium | Disclosure could harm individuals, while a short outage may be tolerable in this exercise |
| Payment settlement ledger | Restricted | Very high | Exposure is harmful; corruption or unavailability can disrupt financial operations |
| Internal meeting agenda | Internal | Low | Limited disclosure impact and limited operational dependency |
| Publicly published annual report archive | Public | Medium | Public information, but availability and integrity may matter for reporting and trust |

The sensitivity column uses the illustrative scheme labels defined in Section 4. Criticality ratings use a separate impact scale; neither scale is a universal standard. Business impact depends on context, dependency, recovery alternatives, and the organisation's own criteria.

### 3.1.1 Example criticality scale (instructional proposal)

Use a defined scale before rating assets. The following is a recommended training scale, not a source-mandated or universal benchmark:

| Rating | Illustrative decision criterion | Example impact |
|---|---|---|
| **Low** | Loss, corruption, delay, or outage has limited local impact and a straightforward workaround | An internal reference page can be temporarily unavailable without material disruption |
| **Medium** | A team workflow is disrupted, but a documented workaround or recovery path exists within an agreed tolerance | A customer-support lookup is delayed for a limited period |
| **High** | Multiple workflows or an important customer-facing service are materially affected; recovery and integrity checks are important | A public product-price feed is wrong or unavailable during a sales period |
| **Very high** | Failure could materially disrupt a critical operation, cause substantial financial or safety impact, or exceed agreed recovery tolerances | A payment settlement ledger is corrupted or unavailable during settlement |

Organisations should define impact dimensions, time tolerances, escalation thresholds, and rating authority to fit their own business-impact analysis. If the organisation uses a different scale, map the examples explicitly rather than silently mixing vocabularies. Record integrity and availability requirements separately when one criticality score would conceal different control needs.

### 3.2 Do not collapse all dimensions into one number

A single score can simplify reporting but can hide important distinctions. A highly sensitive but non-critical dataset needs strong confidentiality handling even if an outage is tolerable. A low-sensitivity but highly critical dataset may need robust integrity checks, backups, and recovery testing even though broad read access is acceptable.

**Recommended design:** retain at least separate sensitivity and criticality fields. Add explicit integrity or quality requirements and recovery objectives where needed. If a combined tier is used for automation, document the calculation and preserve the underlying dimensions.

### 3.3 How to assess impact

For each asset or field, consider these questions:

1. **Exposure:** What happens if an unauthorised party reads or exports it?
2. **Misuse:** Could authorised or unauthorised use cause harm outside the stated purpose?
3. **Modification:** What happens if values are altered, omitted, duplicated, or reordered?
4. **Loss:** What happens if the data are deleted or become unrecoverable?
5. **Unavailability or delay:** What business process fails if the data are late or inaccessible?
6. **Aggregation:** Could combining this asset with other data reveal more than each source alone?
7. **Context:** Does the use, audience, environment, geography, retention, or linkage change the risk?
8. **Dependency:** Do downstream reports, models, operational processes, or customers rely on it?

Use impact categories and written reasoning rather than unsupported intuition. Where a score is used, define the scale and the decision thresholds before rating assets.

---

## 4. An illustrative classification scheme

The following four labels are a teaching example. They are **not a universal taxonomy or legal standard**. An organisation should align its scheme with its existing policies and applicable requirements, and specialists should map legal or contractual categories to it where necessary.

### 4.1 Example label definitions

| Label | Example definition | Illustrative examples | Minimum handling intent |
|---|---|---|---|
| **Public** | Approved for public release; disclosure is expected and authorised | Published product descriptions, approved public reports | Prevent unauthorised modification; publish only approved versions; maintain integrity appropriate to the use |
| **Internal** | Intended for routine internal use; unauthorised disclosure would have limited impact | General internal procedures, non-sensitive operational metrics | Workforce access according to business need; standard logging and approved storage |
| **Confidential** | Disclosure or misuse could materially harm individuals, customers, partners, or the organisation | Customer contact details, non-public financial forecasts, business-sensitive records | Need-to-know access; encryption according to organisational baseline; mask in non-production or broad analytical use where appropriate; controlled sharing and defined retention |
| **Restricted** | Exposure or misuse could cause severe harm or create significant security, privacy, financial, or operational risk | Authentication secrets, high-risk identifiers, highly sensitive account data, tightly controlled security material | Explicitly approved access paths; strong identity and key controls; minimise copies; use masking or tokenisation for permitted secondary uses; detailed monitoring and controlled exports |

The examples do not mean that every credential, identifier, or financial field always maps to the same label. Context and organisational policy determine the final assignment. A credential may require a dedicated secrets-handling policy in addition to a classification label.

### 4.2 Define criteria, not just names

A scheme is incomplete if it only lists labels. Each label needs:

- a definition and impact threshold;
- examples and counterexamples;
- rules for dataset-level and field-level classification;
- minimum handling requirements;
- an owner and steward role;
- a method for resolving uncertainty and conflicts;
- review triggers and recertification cadence;
- mapping to technical controls and evidence;
- a version and effective date.

### 4.3 Example handling matrix

This table is an **illustrative policy proposal** for the synthetic Northbridge Bank environment. It is a starting point for design, not a claim that these settings are legally required.

| Control area | Public | Internal | Confidential | Restricted |
|---|---|---|---|---|
| **Access** | Public read only for approved publication channel | Authenticated workforce or service access based on role | Need-to-know access; owner-approved use where policy requires | Explicitly approved identities and purposes; least privilege; stronger review |
| **Encryption** | Protect transport and integrity according to baseline | Organisational baseline at rest and in transit | Required at rest and in transit under the illustrative policy | Required at rest and in transit; key access separated and reviewed |
| **Masking / tokenisation** | Usually not required for the public fields themselves | Apply when fields or context warrant it | Mask in non-production and broad analytical access where feasible | Default to masked/tokenised representations for secondary use unless an approved need exists |
| **Retention** | Retain approved publication according to business need | Defined by business purpose and applicable schedule | Explicit retention rule and disposal path | Explicit, tightly governed retention and deletion path; holds handled separately |
| **Logging** | Log publication changes and relevant administrative events | Standard access and change logging | Record access to sensitive stores and exports proportionately | Detailed access/export/administrative monitoring; avoid logging sensitive values themselves |
| **Sharing / export** | Approved public release process | Approved internal channels | Owner-authorised sharing, recipient and purpose recorded | Restricted sharing paths, explicit approval, minimum necessary fields, and evidence |
| **Monitoring** | Publication integrity and availability | Baseline alerts | Alerts for anomalous access, unusual export, or policy failure as appropriate | Enhanced detection and response based on threat and impact |
| **Review** | On content or publication change | Periodic and change-triggered | Periodic and use-triggered | More frequent or event-driven review proportionate to risk |

A control matrix must be made operational. For example, a catalogue tag may trigger a deployment check, but a runtime policy must still deny unauthorised access. A retention field in metadata must connect to an implemented deletion workflow, and that workflow must be tested.

### 4.4 Avoid “everything is Restricted”

Over-classification can make the scheme unusable: users may ignore labels, approved sharing becomes difficult, platform teams accumulate exceptions, and the organisation cannot distinguish the highest-risk assets. Under-classification can expose sensitive data. The goal is **defensible, consistent, risk-based classification**, not maximum labels or minimum friction.

---

## 5. Inventory first: know what exists

A classification process cannot cover assets that are unknown. A **data inventory** is a managed list of assets and the metadata needed to govern them. A catalogue may present the inventory to users; scanning and discovery may suggest candidate assets and labels; stewards and owners validate the result.

### 5.1 Recommended inventory fields

| Field | Purpose | Example |
|---|---|---|
| `asset_id` | Stable identifier independent of display name | `NB-CUST-001` |
| `asset_name` | Human-readable name | `customer_profile` |
| `asset_type` | Table, file, stream, view, report, feature set, etc. | `table` |
| `domain` | Business domain responsible for meaning and use | `Customer` |
| `system_location` | Logical platform or repository location | `curated/customer/customer_profile` |
| `business_purpose` | Approved business purpose in plain language | `Maintain customer contact preferences` |
| `data_owner` | Accountable business role | `Customer Domain Data Owner` |
| `data_steward` | Maintains definitions and metadata | `Customer Data Steward` |
| `sensitivity_label` | Organisational sensitivity tier | `Confidential` |
| `criticality` | Impact if lost, corrupted, delayed, or unavailable | `Medium` |
| `contains_personal_data` | Discovery indicator requiring appropriate review | `true` |
| `classification_status` | Proposed, approved, unknown, or review-required | `approved` |
| `classification_basis` | Short explanation and evidence | `Contains synthetic email and contact fields` |
| `last_reviewed_at` | Last confirmed review date | `2026-09-30` |
| `next_review_due` | Planned recertification date | `2027-03-31` |
| `lineage_ref` | Link or identifier for upstream/downstream lineage | `LIN-CUST-001` |

Use stable identifiers; names and locations can change. Keep business metadata separate from implementation details where that improves portability. The exact schema is an instructional recommendation and should fit the organisation's catalogue and metadata conventions.

### 5.2 Sample Northbridge Bank data inventory

**All assets, data, dates, roles, and impact ratings below are synthetic illustrative assumptions.**

| Asset ID | Asset | Type / domain | Owner / steward | Sensitivity | Criticality | Status | Classification basis |
|---|---|---|---|---|---|---|---|
| `NB-CUST-001` | `customer_profile` | Table / Customer | Customer Data Owner / Customer Steward | Confidential | High | Approved | Contact and profile attributes; relied on by service workflows |
| `NB-PAY-002` | `payment_ledger` | Table / Payments | Payments Data Owner / Payments Steward | Restricted | Very high | Approved | Transaction records; integrity and availability are operationally important |
| `NB-PROD-003` | `public_product_catalogue` | Published feed / Product | Product Data Owner / Product Steward | Public | High | Approved | Public content; feed correctness and availability matter to channels |
| `NB-OPS-004` | `pipeline_run_metrics` | Table / Platform Operations | Platform Operations Owner / Operations Steward | Internal | Medium | Approved | Operational metrics with no intended customer fields |
| `NB-SEC-005` | `service_credentials_store` | Secret store / Security | Security Owner / Security Steward | Restricted | High | Approved | Authentication material; dedicated secrets handling also applies |
| `NB-ANL-006` | `customer_risk_summary` | Derived table / Risk | Risk Data Owner / Risk Steward | Restricted (proposed) | High | Review required | Combines customer and transaction inputs; derived label needs validation |
| `NB-EXP-007` | `customer_monthly_export` | File / Customer Analytics | Analytics Owner / Analytics Steward | Unknown | Medium | Quarantined pending review | Inventory discovered a new export without sufficient metadata |

The `customer_monthly_export` is deliberately marked `Unknown` rather than guessed. An unknown label is a state requiring action, not a fifth approved classification level. Until reviewed, use a documented safe default—such as restricted discovery and no external sharing—proportionate to the plausible worst case. Do not treat the safe default as proof that the actual classification is Restricted.

### 5.3 Asset-level and field-level classification

- **Asset-level classification** gives a dataset, file, stream, or product an overall handling baseline. It is useful for discovery and default controls.
- **Field-level classification** records differences between attributes and supports column masking, fine-grained access, safe projections, and better data contracts.
- **Both are often needed.** A table may contain public product categories and restricted authentication material; a single table-level label alone does not communicate the difference.

A common safe default is for an asset to inherit the most restrictive label of its fields for broad access decisions, while field-level policies can allow approved lower-risk projections. This avoids making the entire table freely accessible because one field is public, but it can over-restrict a dataset if the asset-level rule is used without column-aware controls.

### 5.4 What to do when inventory is incomplete

1. Record the asset as discovered but not yet classified.
2. Restrict broad publication and uncontrolled export while reviewing it.
3. Identify a provisional owner and steward or escalate if none exists.
4. Inspect schema, lineage, samples approved for discovery, and pipeline contracts.
5. Apply pattern-based or automated discovery as assistance—not as unquestioned truth.
6. Confirm the label with the accountable owner and appropriate specialists.
7. Record evidence, decision date, and follow-up review.
8. If the asset cannot be classified safely, limit or suspend the risky use until the uncertainty is resolved.

---

## 6. Field-level classification and data dictionaries

A **data dictionary** explains fields: their names, meanings, types, allowed values, quality rules, and relevant metadata. Classification enriches the dictionary with sensitivity and handling attributes.

### 6.1 Example field-level classification register

The records below are synthetic. Classification choices are illustrative and should be reviewed by the relevant owner and specialist functions.

| Asset | Field | Meaning | Data type | Sensitivity | Criticality contribution | Category / rationale | Handling note |
|---|---|---|---|---|---|---|---|
| `customer_profile` | `customer_ref` | Internal stable customer reference | String | Confidential | Medium | Linkable identifier; may connect records across systems | Restrict joins and exports; avoid placing raw values in logs |
| `customer_profile` | `display_name` | Customer display name | String | Confidential | Medium | Identifies a person in context | Need-to-know access; mask in non-production where appropriate |
| `customer_profile` | `email_address` | Contact email | String | Confidential | Medium | Contact information; misuse or exposure can harm a person | Mask in broad analytics and test data; controlled sharing |
| `customer_profile` | `postal_area` | Coarse postal area | String | Internal by itself; context-dependent | Low | May become identifying when combined with other attributes | Reassess combinations and small cohorts |
| `customer_profile` | `marketing_opt_in` | Recorded marketing preference state | Boolean | Confidential | Medium | Indicates a preference that may constrain permitted use | Preserve purpose/context metadata; do not infer permission from the flag alone |
| `payment_ledger` | `transaction_ref` | Internal transaction reference | String | Confidential | High | Can be linkable to financial activity | Restrict exports; log access events, not unnecessary raw values |
| `payment_ledger` | `account_ref` | Synthetic account reference | String | Restricted | Very high | Linkable financial account information in this scenario | Strong access restrictions; masking/tokenisation for secondary use |
| `payment_ledger` | `amount` | Transaction amount | Decimal | Confidential | Very high | Financial information; integrity affects reconciliation | Validate precision, access, and change lineage |
| `payment_ledger` | `settlement_status` | Settlement processing state | Enum | Confidential | Very high | Incorrect value may affect downstream processing | Constrain writes; reconcile state transitions |
| `service_credentials_store` | `secret_value` | Service authentication secret | Secret material | Restricted | High | Credential compromise may enable system access | Dedicated secrets controls; never expose in logs or analytics |

**Important:** a field's sensitivity and criticality are not necessarily the same as the containing asset's overall ratings. A field can be Public under the illustrative sensitivity scheme yet operationally critical to a downstream process. The `Criticality contribution` column is a qualitative contribution to impact analysis, not a replacement for the asset-level criticality assessment; apply the defined criticality scale and document the business context. A field's sensitivity label may change when combined with other attributes or used for a different purpose.

### 6.2 Data-dictionary metadata example

This YAML is a vendor-neutral illustrative record. It is a metadata representation, not an executable access policy.

```yaml
asset_id: NB-CUST-001
asset_name: customer_profile
asset_type: table
schema_version: 3
business_domain: Customer
business_purpose: Maintain customer profile and contact preferences
data_owner_role: Customer Domain Data Owner
data_steward_role: Customer Data Steward
classification:
  scheme_id: northbridge-example-v1
  scheme_version: 1
  asset_sensitivity: Confidential
  criticality: High
  status: approved
  rationale: Contains contact attributes and supports customer service workflows
  approved_at: 2026-09-30
  next_review_due: 2027-03-31
fields:
  - name: email_address
    logical_type: email-like string
    definition: Customer contact email in the synthetic training dataset
    sensitivity: Confidential
    data_category: contact_information
    contains_personal_data: true
    handling:
      mask_in_nonproduction: true
      restrict_export: true
      log_access_events: true
    classification_basis: Identifies or contacts an individual in context
lineage:
  upstream_assets:
    - NB-CUST-SOURCE-001
  downstream_assets:
    - NB-CUST-ANALYTICS-002
```

Metadata fields should be validated against a schema. Use controlled vocabularies for labels and statuses, stable IDs, versioning, timestamps, and explicit unknown states. Do not put actual secrets or real personal values into the catalogue. Avoid storing unnecessary sensitive data in metadata itself.

For fields, use an explicit state such as `unknown` or `review_required` rather than inventing a label. Until resolved, prevent the field from being silently published or used in a lower-protection context; apply the organisation's documented interim safeguard and assign an owner and due date. The interim safeguard is a temporary risk control, not the final classification decision.

### 6.3 Who assigns and maintains a label?

The governance operating model from Topic 01 establishes the role split:

- **Data owner:** accountable for the asset's business meaning, acceptable use, and classification decision within delegated authority.
- **Data steward:** maintains definitions, inventory completeness, classification metadata, and review workflow.
- **Platform operator / data engineer:** implements metadata pipelines and controls, detects missing or conflicting tags, and reports failures; does not unilaterally decide business sensitivity.
- **Security and privacy functions:** advise on protection needs, threat context, personal-data implications, and specialist review.
- **Policy owner / governance forum:** maintains the scheme and resolves cross-domain disputes according to authority.

A classification process needs both an accountable decision-maker and an operational mechanism to maintain the record. A label without an owner is likely to become stale; an owner without time or authority is only nominally accountable.

---

## 7. Classification decision procedure

Use a repeatable process so that different teams reach comparable results and can explain why a label was assigned.

### 7.1 Step-by-step procedure

1. **Identify the asset and purpose.** Record stable ID, data domain, system location, intended users, and business purpose.
2. **Inspect structure and context.** Review schema, field definitions, lineage, source systems, expected content, and known downstream uses.
3. **Assess exposure and misuse impact.** Consider harm to people, customers, partners, operations, finances, reputation, and security if data are disclosed or misused.
4. **Assess integrity and availability impact.** Consider corruption, loss, delay, and unavailability; record criticality separately from sensitivity.
5. **Check combinations and aggregation.** Determine whether fields that look low-risk alone become identifying or sensitive when joined, grouped, or linked.
6. **Map to the scheme's written criteria.** Choose the least restrictive label that fully meets the defined criteria; do not down-label merely for convenience.
7. **Choose granularity.** Use asset-level labels for baseline handling and field-level labels where differences materially affect access or controls.
8. **Derive handling requirements.** Map labels and other context to documented controls; record controls that require separate specialist decisions.
9. **Resolve uncertainty.** Mark unknown/proposed, apply a safe interim handling rule, and assign an owner and due date.
10. **Approve and record.** Store label, scheme version, rationale, approver role, timestamp, and review date.
11. **Propagate and validate.** Confirm that downstream assets and technical policies receive the relevant metadata.
12. **Review on triggers.** Reassess after schema, use, lineage, ownership, incident, threat, or requirement changes.

### 7.2 Worked examples

**Example A — Synthetic customer email field**

- Asset: `customer_profile.email_address`.
- Exposure/misuse: unauthorised disclosure could expose a contact address and enable unwanted contact or linkage.
- Criticality: a service outage might be tolerable for a limited period; the field itself is not automatically highly critical just because it is sensitive.
- Illustrative decision: `Confidential` sensitivity; medium criticality contribution.
- Handling: need-to-know access, masking in non-production or broad analytics, controlled exports, and review of purpose and retention.
- Why not Public? The data are not approved for public release.
- Why not automatically Restricted? The illustrative scheme's Restricted threshold is reserved for more severe exposure or misuse impact. The organisation's actual criteria could place it differently.

**Example B — Synthetic payment ledger**

- Asset: `payment_ledger`.
- Exposure/misuse: financial activity and account references can cause material harm if disclosed or misused.
- Integrity/availability: corrupted settlement status or an unavailable ledger could disrupt reconciliation and operations.
- Illustrative decision: `Restricted` sensitivity; very high criticality.
- Handling: explicitly approved access, strong identity and key controls, restricted exports, write validation and reconciliation, recovery procedures, and detailed access/change evidence.
- Why separate the axes? The ledger needs strong confidentiality controls and robust integrity/availability engineering for different reasons.

**Example C — Public product feed**

- Asset: approved public product catalogue.
- Exposure/misuse: disclosure is intended, so sensitivity is Public.
- Integrity/availability: incorrect prices or an unavailable feed can disrupt customer channels.
- Illustrative decision: Public sensitivity; high criticality.
- Handling: controlled publishing, integrity validation, change history, and suitable availability/recovery objectives.
- Lesson: Public does not mean unimportant or unprotected.

**Example D — Aggregated risk dashboard**

- Inputs: customer profile, transactions, and coarse location.
- Averages or counts can still expose individuals if groups are small or attributes are linkable.
- Begin with the inherited input classification; assess whether the transformation genuinely reduces sensitivity.
- If small-cell suppression, aggregation, and re-identification assessment are effective and documented, a lower label may be justified by policy and owner approval. Do not automatically down-label simply because direct identifiers were removed.

### 7.3 A compact decision matrix

| Question | If yes | Required action |
|---|---|---|
| Is the asset approved for public release? | Yes | Public may be appropriate, subject to integrity and publication controls |
| Could exposure or misuse cause material harm? | Yes | Assess Confidential or Restricted against written thresholds |
| Could exposure enable account/system compromise or severe harm? | Yes | Consider Restricted and specialist review under organisational policy |
| Could loss, corruption, or delay interrupt a critical process? | Yes | Raise criticality and define integrity/recovery requirements separately |
| Is the content unknown or the metadata unreliable? | Yes | Mark unknown/proposed, restrict risky use, investigate, and assign a deadline |
| Does the asset combine data or create a derived representation? | Yes | Apply inheritance, aggregation, and re-identification review rules |

This matrix supports decisions; it does not replace the complete procedure or expert review.

---

## 8. Classification propagation and derived data

Data move through ingestion, storage, transformation, replication, streaming, analytics, exports, and AI/ML workflows. Classification must travel with them or be recalculated using documented rules. If labels are lost at a boundary, downstream systems may apply weaker controls without knowing that the data are sensitive.

### 8.1 Default inheritance rule

**Recommended baseline rule:** a derived asset inherits the most restrictive sensitivity label among its inputs unless a documented transformation and assessment demonstrate that a lower label is justified under the organisation's scheme. Criticality is assessed separately based on the derived asset's operational role and dependencies; it should not simply inherit the maximum input criticality without analysis.

This is a default, not an unbreakable law. Some transformations reduce exposure risk; others increase it. Joining, enrichment, aggregation, free-text extraction, feature generation, and embedding can change risk in ways that simple label copying does not capture.

### 8.2 Propagation path example

```text
Synthetic source systems
  ├── customer_profile (Confidential sensitivity; High criticality)
  └── payment_ledger (Restricted sensitivity; Very high criticality)
                 |
                 v
        Ingestion / landing zone
        - preserve source labels and asset IDs
        - quarantine unknown or conflicting metadata
                 |
                 v
        Curated transaction + customer join
        - derived sensitivity defaults to Restricted
        - criticality assessed for risk operations
        - lineage records both inputs
                 |
                 v
        customer_risk_summary
        - Restricted (proposed pending owner review)
        - field-level tags retained where meaningful
        - approved access and purpose required
                 |
                 v
        Risk dashboard / approved export
        - aggregation and small-group checks
        - documented assessment before any down-classification
        - output label and restrictions stored with the artifact
```

### 8.3 Propagation across common paths

| Path | What can go wrong | Recommended design response |
|---|---|---|
| Batch ingestion | Source tags omitted during file load | Require classification metadata in ingestion contract or attach validated source metadata |
| Transformation / ELT | New columns appear without labels | Fail or quarantine publication when required metadata is missing; notify steward |
| Replication / CDC | Replica has different label or weaker access | Carry labels and owner metadata; validate target controls and access boundaries |
| Streaming events | Event schema evolves but new field has no classification | Require schema review; treat unclassified fields as unknown; gate production release where risk warrants |
| Analytics / views | A view drops column tags or joins linkable fields | Propagate field lineage and evaluate combinations; test view access policy |
| Export / file delivery | Labels lost in CSV or workbook | Include sidecar manifest or governed export metadata; enforce approved channel and expiry where appropriate |
| Search indexes / embeddings | Derived representation may retain or reveal source information | Treat as derived data; assess source labels, access filtering, retrieval leakage, and deletion implications |
| Logs / monitoring | Sensitive values copied into logs | Log event metadata rather than raw values; apply separate log classification and access controls |
| Backups / archives | Copies are omitted from lifecycle inventory | Include replicas, archives, backups, and recovery copies in lineage and retention design |

### 8.4 When can a derived asset receive a lower label?

Only after a documented, reviewable assessment shows that the transformation materially reduces the relevant risk and satisfies organisational criteria. Consider:

- whether direct identifiers remain;
- whether indirect identifiers or small cohorts permit linkage;
- whether a mapping or re-identification key exists;
- whether external datasets could be joined to it;
- whether free text, rare events, or granular time/location remain;
- whether model features, embeddings, or outputs reveal information;
- what the intended audience and use are;
- whether the result is reversible or can be linked back;
- whether the owner and specialist functions have approved the rationale.

Masking or removing a name does not automatically anonymise a dataset. A transformation should not be treated as lowering sensitivity solely because a column was renamed, hashed, encoded, or moved to another system.

### 8.5 Aggregation and combinations

A set of fields can be more revealing together than separately. Age band and broad region may seem low-risk, but a rare combination plus a timestamp or external information may identify a person. Classification should account for **combination effects** and the use context, not just the field's standalone content.

For aggregated dashboards, potential controls include minimum group-size rules, suppression of small cells, coarsening of time or geography, limiting query combinations, and review of release context. The right technique depends on the risk and purpose; none automatically guarantees zero re-identification risk.

---

## 9. Mapping classification to controls

Classification should influence controls through explicit policy and system design. The label is an input to decisions, not the enforcement mechanism itself.

| Classification concern | Design decision informed | Example implementation intent | How to validate |
|---|---|---|---|
| Sensitivity | Who may access which fields and for what purpose | Owner-approved access, least privilege, row/column restrictions | Test authorised and unauthorised cases; inspect access evidence |
| Sensitivity | Encryption and key access | Encrypt according to policy; restrict key administration separately | Review configuration, key permissions, and relevant logs |
| Sensitivity | Masking/tokenisation | Mask fields for non-production or broad analytics | Test output values and verify privileged mapping access is restricted |
| Sensitivity | Sharing and export | Approved recipients, minimum fields, secure channel, expiry where appropriate | Inspect approval record and export logs |
| Sensitivity | Logging and monitoring | Avoid raw values in logs; monitor unusual reads/exports | Scan logs for sensitive values; test alert paths |
| Sensitivity / context | Purpose limitation and privacy review | Record intended purpose and prohibit incompatible uses according to policy | Review data contract, approval, and use records |
| Lifecycle | Retention and deletion | Define schedule and disposal workflow for all copies | Sample source, replica, archive, and backup handling against policy |
| Criticality | Integrity | Validate schema, ranges, state transitions, and reconciliation | Run negative tests and reconciliation checks |
| Criticality | Availability and recovery | Define service/recovery objectives and restore procedures | Conduct restore tests and record results |
| Criticality | Monitoring | Alert on freshness, missing data, corruption, and pipeline failure | Inject synthetic failures and verify alerts and response |
| Both axes | Evidence | Keep classification decisions, reviews, access approvals, and control results | Trace sample assets from label to implemented control and evidence |

### 9.1 Why classification alone does not enforce controls

A metadata field such as `sensitivity: Restricted` only becomes operational when components consume it correctly. A production design may need:

1. a controlled vocabulary and validated metadata schema;
2. a reliable way to attach labels to discovered assets and fields;
3. policy logic mapping labels and context to requirements;
4. enforcement points at storage, query, API, export, and workload boundaries;
5. safe handling for unknown, missing, or conflicting metadata;
6. logging, alerting, and evidence generation;
7. periodic tests to verify the policy is still applied;
8. an exception process with authority, expiry, and compensating controls.

A label-to-policy mapping can be automated, but not every decision can be automated safely. Human review remains important for ambiguous data, changing purpose, exceptions, and specialist obligations.

### 9.2 Relationship to later topics in this module

| Later topic | How classification contributes | What it does not replace |
|---|---|---|
| Topic 03 — Identity, access and least privilege | Supplies data sensitivity context for access policies and review priority | Identity proofing, authorisation logic, access reviews, revocation |
| Topic 04 — Encryption, key management and secrets | Informs protection strength and key-access separation | Key lifecycle, secrets handling, cryptographic design |
| Topic 05 — Masking, tokenisation and de-identification | Identifies fields and uses that may need transformation | Re-identification assessment and technique limitations |
| Topic 06 — Consent, purpose and residency | Helps identify data requiring use/context review | Legal basis, purpose compatibility, consent state, residency analysis |
| Topic 07 — Retention, deletion, legal holds and auditability | Connects assets to lifecycle and deletion requirements | Actual schedules, legal-hold authority, deletion propagation and evidence |
| Topic 08 — Regulatory controls and evidence | Supports mapping requirements and control evidence to assets | Legal interpretation and independent control testing |
| Topic 09 — Governance by design and policy enforcement | Enables metadata-driven checks and enforcement workflows | Correct policy implementation, runtime enforcement, exception governance |

---

## 10. Unknowns, conflicts, exceptions, and drift

### 10.1 Unknown or missing metadata

A missing label must not silently mean Public or Internal. Define a fail-safe handling path. For example, a new field in a Restricted table that lacks a classification can be quarantined or treated under the parent asset's safe default until reviewed. The appropriate response should be proportionate to the plausible risk and operational impact.

Recommended statuses:

- `proposed`: classification suggested but not yet approved;
- `approved`: accountable decision recorded;
- `unknown`: insufficient evidence to assign a defensible label;
- `review_required`: a trigger or contradiction requires reassessment;
- `exception`: a formally approved, time-limited deviation from standard handling.

These statuses are illustrative metadata vocabulary, not universal standard values.

### 10.2 Conflicting labels

Conflicts may occur when:

- the source and target systems use different schemes;
- two upstream assets have different labels;
- an owner and steward disagree;
- an automated scanner conflicts with a manual decision;
- a dataset label conflicts with a field-level label;
- an export omits metadata present in the catalogue.

**Recommended resolution rule:** preserve provenance, do not silently choose the weaker label, apply the documented conservative interim handling rule, and send the conflict to the designated owner or governance forum. The final decision should record the rationale and any mapping between schemes.

For derived data, the default maximum-sensitivity inheritance rule is a practical safeguard, but the accountable owner must still assess context and document a justified transformation-based reduction. Criticality should be assessed separately rather than mechanically taking the highest source rating.

### 10.3 Exceptions and risk

An exception is a recorded, authorised deviation from a standard handling rule. It should specify:

- asset and fields in scope;
- the standard requirement being deviated from;
- business rationale and intended use;
- risk assessment and affected parties;
- compensating controls;
- approving authority under the organisation's risk delegation;
- accountable owner and implementation owner;
- start date, expiry date, and review conditions;
- monitoring and evidence requirements;
- rollback or remediation plan.

An exception must not become a permanent undocumented bypass. Expired exceptions should automatically return to the standard path or be escalated for explicit renewal. Acceptance of risk is a governance decision; engineering teams should not infer authority merely because they can technically implement a workaround.

### 10.4 Classification drift and change triggers

Review classification when any of the following occurs:

- a schema or event contract adds, removes, or changes a field;
- a new business purpose, audience, partner, or analytics use is proposed;
- new source data are joined or the aggregation granularity changes;
- a scanner finds unexpected sensitive patterns;
- a data breach, near miss, or threat change indicates the previous assessment is weak;
- ownership, system boundary, storage location, or sharing route changes;
- a contractual, legal, privacy, or internal policy interpretation changes;
- retention or deletion constraints change;
- a derived asset or model representation is introduced;
- the scheduled recertification date arrives.

### 10.5 Review and recertification workflow

```text
New asset / schema change / review date / incident
                     |
                     v
        Discover asset and lineage
                     |
                     v
      Steward checks schema and metadata
                     |
          +----------+----------+
          |                     |
     Evidence enough?       Unknown/conflict
          |                     |
         Yes                    v
          |           Apply safe interim handling;
          |           assign owner and due date
          v                     |
 Owner assesses sensitivity and criticality <----+
          |
          v
 Map to scheme and handling requirements
          |
          v
 Specialist review if privacy/security/legal context warrants
          |
          v
 Record approval, rationale, version, and review date
          |
          v
 Propagate labels and validate technical controls
          |
          v
 Sample/test evidence; close review or open remediation
```

### 10.6 Suggested review cadence

The roadmap requires review and recertification but does not prescribe universal time intervals. Choose a risk-based cadence based on data sensitivity, criticality, change rate, and organisational policy. For training purposes, Northbridge might propose annual review for stable Internal assets, semi-annual review for Confidential assets, and quarterly or event-driven review for Restricted assets. These are **illustrative assumptions**, not requirements. Triggered reviews should occur when material changes happen, even if the calendar review is not due.

---

## 11. Automation, metadata quality, and operating effectiveness

Automation can discover likely sensitive fields, compare schemas, propagate tags, and block publication when required metadata is missing. It can also produce false positives and false negatives. Pattern matching may detect email-like strings but miss contextual sensitivity; machine-learning-assisted discovery may be uncertain or biased by the data it has seen.

### 11.1 Recommended automation pattern

1. Discover assets and schemas from approved metadata sources.
2. Apply deterministic checks and scanning to suggest classifications.
3. Preserve scanner confidence, evidence, and version where useful.
4. Send ambiguous or high-risk findings to a steward and owner.
5. Require approval for material label changes according to policy.
6. Publish the approved label and policy mapping to downstream systems.
7. Block, quarantine, or limit assets when required metadata is absent or contradictory.
8. Test actual control outcomes and produce evidence.
9. Track drift, false positives, false negatives, and remediation time.

### 11.2 Governance metrics

Targets should be chosen after measuring the baseline. These sample metrics are instructional recommendations.

| Metric | Definition | Why it matters | Example target (illustrative only) | Evidence source |
|---|---|---|---|---|
| Classification coverage | Percentage of in-scope assets with an approved classification | Shows inventory completeness | At least 98% of in-scope production assets | Catalogue/inventory snapshot |
| Field coverage | Percentage of required fields with valid field-level labels | Finds gaps hidden by table-level tags | At least 95% for designated sensitive domains | Schema registry and dictionary validation |
| Owner/steward coverage | Percentage of assets with valid accountable owner and steward | Prevents orphaned metadata | 100% of Restricted assets | Inventory and ownership registry |
| Classification accuracy | Percentage of sampled classifications confirmed by review | Tests decision quality, not just completion | At least 95% on risk-weighted sample | Documented sample audit |
| Time to classify | Median elapsed time from asset discovery to approval | Measures workflow efficiency | Set after baseline; e.g. five business days for standard assets | Workflow timestamps |
| Unknown metadata age | Number and age of assets/fields in unknown state | Exposes unresolved risk | No Restricted candidate unknown beyond defined SLA | Exception and remediation register |
| Propagation success | Percentage of tested derived assets with correct labels and lineage | Detects metadata loss | At least 99% on automated test suite | Pipeline test results |
| Drift remediation time | Median time from detection to resolution | Measures responsiveness | Risk-based SLA, shorter for Restricted | Incident/ticket timestamps |
| Recertification on time | Percentage of due reviews completed by due date | Prevents stale classifications | At least 95%, with no overdue critical assets | Review log |
| Control mapping validation | Percentage of sampled label-to-control mappings whose controls pass tests | Connects metadata to operation | 100% of critical mappings tested on schedule | Control test evidence |

Metrics can be gamed if used alone. High coverage does not prove accuracy; a fast classification process may make poor decisions; a high test pass rate is meaningless if the sample is unrepresentative. Use risk-weighted sampling, explain denominators, preserve failed cases, and report exceptions rather than hiding them.

---

## 12. Architecture trade-offs and industry scenarios

### 12.1 Fine-grained versus coarse-grained classification

| Approach | Strengths | Limitations | Use when |
|---|---|---|---|
| Dataset-level only | Simple to operate; good baseline; fewer metadata fields | Can over-restrict or under-describe mixed-content datasets | Homogeneous datasets, early maturity, baseline policy |
| Field-level | Enables precise masking and access; supports safer projections | More metadata, governance, and schema-change work | Mixed sensitivity, customer/financial data, fine-grained access needs |
| Hybrid | Dataset baseline plus field-specific overrides | Requires clear precedence and testing | Most mature shared platforms with varied data |

A practical starting point is a dataset-level baseline plus field-level classification for sensitive or policy-relevant attributes. Expand granularity where risk or use cases justify it rather than requiring every field to carry complex metadata without a clear operational benefit.

### 12.2 Free-text customer-service notes

**Scenario:** synthetic call-centre notes may contain names, contact details, account references, complaints, or unexpected sensitive information. The content is unstructured and hard to classify perfectly at ingestion.

Options:

- treat all notes as Restricted until scanning and review are validated;
- scan and tag likely sensitive content, with human sampling and conservative fallback;
- exclude raw notes from broad analytics and publish a reviewed, minimised derivative.

The first option is safer but restrictive; the second improves utility but may miss values; the third limits exposure but reduces analytic richness. A reasonable illustrative approach is conservative access to raw notes, scanning with validation, and approved minimised derivatives for analytics. Revisit this decision if the scanning method, use, or threat context changes.

### 12.3 Aggregated dashboard with small groups

**Scenario:** a dashboard combines synthetic age bands and coarse location with account activity. Even without direct identifiers, rare combinations may expose individuals.

Recommended design: assess aggregation risk, suppress or coarsen small cells, restrict query combinations where appropriate, document the output classification, and review before external publication. Do not assume aggregation alone makes data Public.

### 12.4 Streaming schema change

**Scenario:** a transaction event gains a new `account_ref` field, but the event schema's classification metadata does not change.

Failure mode: downstream consumers receive the field and persist it in logs or analytics without applying the intended restrictions.

Recommended architecture: require schema-change review, classify new fields before unrestricted production use, carry tags in event contracts or linked metadata, test consumers for propagation, and alert or quarantine when required metadata is missing. Balance strict release gates against service criticality by defining an explicit risk-based exception route rather than silently bypassing checks.

### 12.5 Training data and derived AI assets

Training datasets, features, embeddings, indexes, and model outputs can preserve or reveal source information. Treat them as derived assets with lineage and a documented classification assessment. Do not assume a vector embedding is harmless because it is not human-readable, or that removing direct identifiers guarantees anonymisation. Access filtering, source restrictions, purpose, retention, and deletion implications are addressed in later module topics; classification provides important metadata but does not solve those questions alone.

### 12.6 Common mistakes

| Mistake | Why it fails | Prevention |
|---|---|---|
| Confusing sensitivity and criticality | Applies the wrong controls or misses recovery needs | Record both axes separately and justify each |
| Treating Public as unimportant | Public data can be business-critical or integrity-sensitive | Evaluate criticality and integrity independently |
| Using labels without definitions | Different teams apply inconsistent meanings | Define thresholds, examples, handling rules, and versioning |
| Classifying only at table level | Mixed-content tables hide field-specific risk | Use field-level metadata where it changes handling |
| Assuming labels enforce controls | Metadata can be ignored or lost | Test policy consumers, enforcement points, and evidence |
| Treating scanner output as authoritative | False positives and negatives remain | Use automation as assistance with validation and review |
| Down-classifying after removing names | Linkage and quasi-identifiers can remain | Assess combinations, audience, and re-identification risk |
| Ignoring derived assets and exports | Sensitive data escapes via copies and transformations | Track lineage and test propagation end to end |
| Never reviewing old labels | Data use and context change | Schedule recertification and event-triggered review |
| Leaving unknowns indefinitely | Unknown becomes a hidden bypass | Assign owner, interim handling, due date, and escalation |
| Inventing legal meaning for a label | Organisational scheme may not match legal categories | Obtain specialist interpretation and maintain an explicit mapping |

---

## 13. Practical exercise A — inventory and field classification register

### Scenario

Northbridge Bank has a synthetic customer domain with 40 tables across six domains. For this exercise, you will work with a small subset and extrapolate the workflow. The exercise is a recommended learning activity from the roadmap's Topic 02 scope; the exact synthetic records below are instructional additions.

### Inputs

Use these fictional assets and fields:

| Asset | Fields | Intended use |
|---|---|---|
| `customer_profile` | `customer_ref`, `display_name`, `email_address`, `postal_area`, `marketing_opt_in` | Customer service and contact preference management |
| `payment_ledger` | `transaction_ref`, `account_ref`, `amount`, `settlement_status` | Payment reconciliation and operational reporting |
| `public_product_catalogue` | `product_code`, `display_name`, `published_price` | Public website feed |
| `pipeline_run_metrics` | `pipeline_name`, `run_timestamp`, `row_count`, `failure_reason` | Platform monitoring; assume no raw customer values by design |

### Tasks

1. Create a data inventory with stable asset IDs, type, domain, purpose, owner, steward, status, sensitivity, criticality, rationale, and review date.
2. Define the scheme and handling rules before assigning labels.
3. Assign both sensitivity and criticality to every asset.
4. Create a field-level register for at least ten fields.
5. Explain the rationale for each Confidential or Restricted field.
6. Identify fields that may become more sensitive when combined.
7. Mark any uncertain decision as proposed or unknown and specify an interim handling rule.
8. Map each label to access, encryption, masking, retention, logging, sharing, and monitoring expectations.
9. Identify which controls require technical enforcement and which require workflow or human review.
10. Write a recertification trigger list and choose a risk-based cadence.

### Expected deliverables

- Versioned classification scheme and handling table.
- Data inventory and field-level classification register.
- Decision rationale for each high-sensitivity classification.
- List of unknowns, conflicts, and follow-up owners.
- Review and recertification procedure.

### Validation criteria

- Every asset has an owner/steward or an explicit ownership gap with a resolution path.
- Sensitivity and criticality are recorded separately.
- The classification scheme is clearly identified as organisational and illustrative.
- Handling rules are explicit enough to be implemented and tested.
- Unknowns are not silently treated as Public.
- The sample audit of ten classifications can explain each label against the written criteria.

---

## 14. Practical exercise B — propagation and derived data

### Scenario

The synthetic `customer_risk_summary` joins customer profile fields, payment activity, and coarse location information. A business team asks for an aggregated dashboard and a CSV export for a partner analysis.

### Tasks

1. Record the source labels and lineage for each input.
2. Apply the default inheritance rule to the joined asset.
3. Assess criticality independently from sensitivity.
4. Identify which fields remain directly identifying, linkable, or sensitive in combination.
5. Define aggregation and small-cell checks for the dashboard.
6. Decide whether any output can receive a lower sensitivity label; if yes, document evidence and approval needed. If not, explain why.
7. Define metadata propagation for the table, dashboard, and CSV export.
8. Specify access, masking, export, monitoring, and retention controls for each output.
9. Define tests that fail when required labels are missing or weaker than the approved rule.
10. Record the decision in a short classification decision record.

### Expected output example

| Asset | Inputs / lineage | Sensitivity decision | Criticality decision | Required follow-up |
|---|---|---|---|---|
| `customer_risk_summary` | `customer_profile` + `payment_ledger` | Restricted by default because a Restricted source is included; review field-level details | High, based on risk-operation dependencies; confirm with owner | Owner approval, purpose review, access controls, field tags |
| `risk_dashboard_aggregate` | `customer_risk_summary` | Remains Restricted until aggregation and re-identification assessment support a justified reduction | Medium or High depending on operational use; assess separately | Small-cell checks, output classification, audience approval |
| `partner_risk_export.csv` | Approved dashboard extract | Unknown until recipient, purpose, fields, and sharing path are reviewed; do not assume Public | Depends on downstream use | Explicit sharing approval, minimum necessary fields, expiry/retention decision, export evidence |

This output is a worked illustration, not a predetermined answer for every organisation. A justified lower label requires evidence and authority, not merely a transformation name.

### Validation criteria

- The inheritance rule is explicit and consistently applied.
- Any reduction in sensitivity is justified in writing and approved under policy.
- Criticality is assessed for each derived asset rather than copied mechanically.
- Lineage and metadata remain traceable through the export boundary.
- Unknown recipient or purpose information triggers review rather than silent release.

---

## 15. Practical gap analysis

Use this checklist to evaluate a hypothetical or synthetic platform. Mark each item `Pass`, `Gap`, or `Not applicable`, and attach evidence rather than relying on verbal assurance.

| Check | Evidence to inspect | Typical gap | Recommended remediation |
|---|---|---|---|
| Asset inventory exists for in-scope data | Catalogue or inventory export | Unknown tables and files | Discovery scan, domain review, owner assignment |
| Scheme defines each label | Approved policy/version | Labels have names but no criteria | Define thresholds, examples, and handling requirements |
| Sensitivity and criticality are separate | Register schema and sample records | One generic “risk” field only | Add separate dimensions and reassess sample assets |
| Field-level tags exist where needed | Data dictionary and schema metadata | Sensitive columns hidden by table label | Tag fields and validate schema changes |
| Owner and steward are assigned | Ownership registry | Orphaned assets | Assign provisional owner and escalate unresolved cases |
| Unknown metadata has a safe path | Ingestion and publication behavior | Missing tags treated as public | Quarantine, safe default, alert, and deadline |
| Derived labels propagate | Lineage and pipeline tests | Transformations drop labels | Add propagation rules and contract tests |
| Down-classification is controlled | Decision records and approvals | Label reduced without evidence | Require documented assessment and delegated approval |
| Labels map to controls | Policy mapping and control catalogue | Labels exist but controls do not consume them | Define enforcement points and test cases |
| Recertification is operating | Review timestamps and workflow | Labels are stale | Triggered and scheduled review workflow |
| Exceptions expire | Exception register and automation | Permanent waivers | Expiry, alerting, renewal authority, remediation path |
| Control effectiveness is tested | Test reports and evidence | Only policy documents exist | Test representative access, export, masking, and propagation paths |

### Gap analysis deliverable

Create a gap log with `gap_id`, asset or control area, risk, evidence, accountable owner, remediation, due date, interim safeguard, and status. Prioritise based on plausible harm and business criticality. Do not claim compliance merely because the table is complete; the purpose is to make risks and remediation explicit.

---

## 16. Architecture decision record (ADR) example

This example records a recommended design choice for the synthetic Northbridge environment. It is an instructional artifact, not an existing organisational decision.

### ADR-NB-CLS-001 — Classification and propagation baseline

**Status:** Proposed for the training scenario  
**Date:** 2026-09-30 (illustrative)  
**Decision owner:** Data Governance Council  
**Contributors:** Domain Data Owners, Data Stewards, Platform Engineering, Security, Privacy

#### Context

Northbridge operates shared analytical and operational data paths across several domains. Labels are inconsistent or missing in some derived assets. Downstream controls cannot reliably make decisions when metadata is absent, stale, or silently dropped. The platform needs a consistent organisational scheme while allowing risk-based field-level precision.

#### Decision drivers

- Separate exposure/misuse impact from loss/corruption/unavailability impact.
- Provide clear definitions and handling rules.
- Support dataset-level baselines and field-level labels where needed.
- Preserve lineage and classification through transformations and exports.
- Avoid treating labels as controls or as legal categories.
- Provide a safe process for unknowns, conflicts, exceptions, and recertification.

#### Options considered

| Option | Benefits | Costs / risks |
|---|---|---|
| A. Dataset-level labels only | Simple and low metadata burden | Mixed-content assets are over-restricted or under-described; column controls are difficult |
| B. Field-level labels for every field from day one | Fine-grained metadata | High operational burden; labels may become stale; adoption may stall |
| C. Hybrid: dataset baseline plus field-level tags where risk/use requires them | Balances baseline coverage with precision | Requires precedence rules, schema-change handling, and testing |

#### Decision

Choose Option C for the training scenario. Use the four-level illustrative scheme defined in this lesson; store sensitivity and criticality separately; apply a conservative default inheritance rule for sensitivity; assess criticality for derived assets independently; and require documented approval and evidence before a derived asset is assigned a lower sensitivity label.

#### Consequences

**Positive:** common vocabulary, better inventory coverage, improved control mapping, safer propagation, clearer exception handling.  
**Negative:** metadata maintenance and review effort; false positives from scanning; need to integrate catalogues, contracts, pipelines, and control enforcement.  
**Risks:** users may treat labels as proof of protection; automation may miss contextual sensitivity; broad inheritance may over-restrict.  
**Mitigations:** training, field-level overrides under policy, risk-weighted sampling, safe handling for unknowns, control tests, and periodic review.

#### Implementation and validation

1. Publish the scheme and handling matrix with version and effective date.
2. Assign owners and stewards for in-scope assets.
3. Add validated metadata fields and schema-change checks.
4. Implement propagation tests for batch, streaming, views, and exports.
5. Map labels to access, encryption, masking, retention, logging, and monitoring policies.
6. Test enforcement and record evidence; review ten representative classifications before completion.
7. Review the ADR after a material incident, scheme change, major new use, or recertification finding.

#### Revisit when

- a material new data category or use case emerges;
- the scheme no longer maps cleanly to organisational policy;
- field-level metadata burden becomes disproportionate or insufficient;
- propagation tests show systematic failures;
- specialist review identifies a change to handling requirements.

---

## 17. Review questions

Answer without looking at the lesson, then revisit any weak area.

1. Define data classification in your own words. Why is a label not itself a control?
2. Explain the difference between sensitivity and criticality using one example of each.
3. How do confidentiality, integrity, and availability relate to classification?
4. Why might a public dataset still be highly critical?
5. When is dataset-level classification insufficient?
6. What is the difference between field-level classification and asset-level classification?
7. Why should an unknown field not silently inherit Public?
8. State the recommended default inheritance rule for sensitivity and explain its limitations.
9. Why should criticality be assessed separately for a derived dataset?
10. What evidence would justify lowering a derived asset's sensitivity label?
11. Name three triggers for recertification.
12. What should happen when a scanner and data owner disagree?
13. Which roles decide, maintain, and implement classification metadata?
14. How can classification inform access, encryption, masking, retention, and monitoring?
15. How would you test that classification metadata actually affects production controls?
16. Why can an aggregated dashboard still reveal sensitive information?
17. What should an exception record contain, and why must it expire?
18. Which metrics distinguish classification coverage from classification accuracy?

---

## 18. Mastery criteria and completion gate

### 18.1 Mastery criteria from the module roadmap

You should be able to:

- classify fields on both sensitivity and criticality axes and justify the decisions;
- state and apply an inheritance rule for derived data;
- explain how classification informs access, encryption, masking, retention, and audit.

### 18.2 Expected deliverables

The module roadmap identifies these deliverables for Topic 02:

- classification scheme with definitions and handling table;
- data inventory and classification register;
- propagation/inheritance rules;
- review and recertification procedure;
- ADR.

The detailed field-level register, metadata example, gap log, and exercises in this lesson are recommended ways to demonstrate those deliverables.

### 18.3 Completion checklist

- [ ] The scheme defines labels and handling requirements and is explicitly described as organisational, not legal.
- [ ] Sensitivity and criticality are separate fields with clear definitions.
- [ ] The inventory covers the in-scope assets and includes owners, stewards, status, rationale, and review dates.
- [ ] Field-level labels are applied where they materially change handling.
- [ ] At least ten sample classifications have been reviewed against written criteria.
- [ ] Derived-data inheritance is documented and applied consistently.
- [ ] Any lower classification for a derived asset is justified in writing and approved under policy.
- [ ] Unknown, conflicting, missing, and stale metadata have explicit handling paths.
- [ ] Propagation has been considered for ingestion, transformations, replication, streaming, analytics, exports, logs, backups, and AI-derived assets where relevant.
- [ ] Label-to-control mappings identify actual enforcement and validation steps.
- [ ] Recertification triggers, cadence, ownership, and evidence are defined.
- [ ] Metrics include both coverage and quality/effectiveness indicators.
- [ ] The ADR records the selected approach, alternatives, trade-offs, consequences, and revisit conditions.
- [ ] Weakness in single-axis thinking has been addressed by reclassifying assets on both sensitivity and criticality.

### 18.4 Completion gate

Before progressing to Topic 03 — Identity, Access Control and Least Privilege:

1. Have another learner or reviewer sample ten classifications and challenge the rationale.
2. Demonstrate that a derived asset receives an explainable label and preserves lineage.
3. Explain how the label maps to actual controls and what evidence proves those controls operate.
4. Correct any cases where sensitivity and criticality were collapsed into one rating.
5. Confirm that unknown labels and exceptions cannot silently bypass the approved handling path.

Passing this gate means you can make and explain defensible classification decisions. It does **not** establish legal compliance or prove that every production control is effective; those require separate specialist interpretation and operational testing.

---

## 19. Key takeaways

- Classification is a repeatable governance process that labels data according to explicit criteria and connects the result to handling requirements.
- Sensitivity measures potential harm from exposure or misuse; criticality measures impact from loss, corruption, delay, or unavailability. Keep them distinct.
- Public does not mean unimportant; Restricted does not mean that every possible control is automatically implemented.
- Inventory, ownership, metadata quality, field-level detail, lineage, and review are necessary for dependable classification.
- Derived data should inherit a conservative sensitivity label by default unless a documented assessment justifies a reduction. Criticality should be assessed independently.
- Labels must propagate through pipelines, streams, analytics, exports, logs, backups, and derived AI assets where relevant.
- Classification informs access, encryption, masking, purpose, retention, evidence, and policy enforcement; it does not replace those controls.
- A scheme must be versioned, reviewed, measurable, and clearly distinguished from legal taxonomies.

**Next topic:** `03-identity-access-control-and-least-privilege.md` uses classification and governance ownership to design who or what may access which data, for which actions and purposes, under least-privilege principles.
