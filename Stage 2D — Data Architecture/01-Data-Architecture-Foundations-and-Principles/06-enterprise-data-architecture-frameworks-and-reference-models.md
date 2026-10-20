# 06 — Enterprise Data Architecture Frameworks and Reference Models

> **Stage:** Stage 2D — Data Architecture  
> **Module:** 01 — Data Architecture Foundations and Principles  
> **Lesson file:** `06-enterprise-data-architecture-frameworks-and-reference-models.md`  
> **Level:** Beginner → Intermediate → Advanced

## Source alignment and framework-identification note

The authoritative roadmap section for Module 6 explicitly says that the repository **does not yet name a specific framework or reference model** and that the topic file should name the frameworks it covers when written. It gives examples only at the category level: “widely known enterprise architecture frameworks and data management reference models.” Therefore, no specific product or framework can honestly be described as *mandated by the original roadmap*.

To make the lesson concrete, this file selects two **lesson examples**, not source-prescribed requirements:

1. **The TOGAF® Standard, 10th Edition** — an enterprise architecture standard/framework and method published by The Open Group. Its official material describes a configurable approach to enterprise architecture and includes the Architecture Development Method (ADM) and guidance for configuring the architecture practice.
2. **DAMA-DMBOK® 2nd Edition (2024 Revised Edition; Data Management Body of Knowledge)** — a structured body of knowledge for data management published by DAMA International. It offers shared terminology and organised data-management knowledge areas. It is not identical in purpose or form to an enterprise architecture development method, and this lesson does not mislabel it as a technology blueprint.

These identities and high-level scopes were checked against primary publisher/owner pages:
- The Open Group, TOGAF: <https://www.opengroup.org/togaf>
- The Open Group, TOGAF Standard publications: <https://publications.opengroup.org/standards/togaf>
- DAMA International, DAMA-DMBOK overview: <https://dama.org/learning-resources/dama-data-management-body-of-knowledge-dmbok/>; DAMA-DMBOK 2 Revised Edition FAQ: <https://dama.org/dama-dmbok2-revised-edition-faqs/>

For version clarity, the DAMA example in this lesson is the 2nd Edition (2024 Revised Edition); DAMA describes the 2024 revision as a maintenance release that preserves the underlying framework and scope. The examples below illustrate how to evaluate different kinds of architecture and data-management guidance. They are not a claim that the roadmap requires either named item, nor a recommendation that an organisation adopt either without assessment. The official pages establish the publisher and broad purpose; the evaluation and banking examples are instructional analysis, not publisher claims.

## 1. Learning objective

By the end of this lesson, you should be able to:

1. Explain what an enterprise architecture framework and a reference model provide, and what they do not decide for an organisation.
2. Distinguish a **framework**, **reference model**, **reference architecture**, **standard**, **principle**, and **implementation blueprint** consistently.
3. Use the vocabulary of **stakeholder, concern, viewpoint, and view** to explain why architecture information is organised in different ways.
4. Evaluate candidate frameworks or reference models against business objectives, effort, skills, flexibility, evidence of use, compatibility with existing practices, and regulatory alignment.
5. Compare alternatives using explicit criteria, assumptions, evidence, and limitations rather than treating a scorecard as an objective industry ranking.
6. Decide what to **adopt, adapt, defer, or ignore**, and record why.
7. Use a reference architecture as guidance while documenting justified deviations from its assumptions.
8. Prepare a tailored adoption recommendation for a mid-sized bank with limited architecture staff and explain how it might differ for a large regulated group or a start-up.
9. Produce the roadmap's required outputs: a term-classification table, a framework/reference-model comparison, an adoption plan, a deviation record, and answers to Topic 06 practice questions.

The goal is not to “implement a framework” as a ceremonial project. The goal is to use proven structure where it helps, adapt it to the organisation's context, and preserve traceability from business needs to architecture decisions.

## 2. Why this topic matters in real-world Data Architecture

Organisations repeatedly face similar architecture questions: how to describe the current state, how to organise views for different stakeholders, how to move from requirements to target architecture, how to govern decisions, how to compare options, and how to manage data-related capabilities. Frameworks and reference models can provide a vocabulary and a reusable starting point. They reduce the need to invent every concept and artefact from scratch.

But a framework can also be misused. A team may complete every template without improving decisions. A reference architecture may assume a level of staffing, platform maturity, standardisation, or funding that the organisation does not have. A data-management body of knowledge may help identify important functions but does not automatically decide who owns a specific customer attribute, which system is authoritative, or which platform should be purchased.

The key discipline is to distinguish **guidance** from **decision authority**.

### 2.1 What a framework can help structure

Depending on the framework, it may help organise:
- architecture concerns and stakeholder needs;
- the views and viewpoints used to communicate an architecture;
- a process for developing and revisiting architectures;
- architecture artefacts and relationships between them;
- a common vocabulary across business, data, application, and technology concerns;
- data-management knowledge areas and responsibilities;
- governance checkpoints and traceability;
- reusable patterns or building blocks.

The exact scope varies. Do not assume that every framework contains every item in this list.

### 2.2 What a framework cannot decide automatically

A framework does not automatically determine:
- the organisation's business strategy or priorities;
- the authoritative owner of every data element;
- the appropriate latency, availability, or data-quality targets;
- the best vendor, cloud, database, or ingestion technology;
- whether a proposed data use is permissible under the organisation's actual obligations;
- the correct allocation of decision rights;
- the acceptable trade-off between delivery speed, cost, reliability, and risk;
- which legacy constraints can be retired and when;
- whether a specific implementation is secure, operable, or compliant.

Those outcomes require requirements, evidence, accountable owners, specialist input where relevant, and explicit decisions. Frameworks help structure the work; they do not replace judgement or local accountability.

### 2.3 The practical value proposition

A framework is worth adopting when it improves one or more observable outcomes, such as:
- stakeholders can understand architecture decisions more consistently;
- important concerns are less likely to be omitted;
- current-state and target-state artefacts can be compared;
- decision records become easier to review and reuse;
- teams share definitions for data-management responsibilities;
- architecture reviews become more predictable;
- dependencies and gaps are easier to identify;
- onboarding new architects and engineers becomes easier.

The organisation should also account for costs: training, new vocabulary, documentation effort, tool configuration, change resistance, and the risk that a formal method becomes a gate that delays delivery.

### 2.4 Banking example

**Illustrative scenario:** a mid-sized bank is trying to improve its customer and transaction data architecture. Teams use different terms for the same customer concepts; the current-state inventory is incomplete; data ownership varies by system; and a small architecture group cannot review every design in detail.

A framework may help the bank structure architecture work and a data-management body of knowledge may help it identify data capabilities that need attention. Neither source can determine the bank's actual customer identifier, required data retention, approved access rules, service targets, or platform choice without the bank's own evidence and accountable decisions.

The right question is not “Which framework is the best?” It is: **“Which parts of which approach help this organisation make better decisions at an acceptable cost, given its goals, maturity, obligations, and constraints?”**

## 3. Prerequisite knowledge

The roadmap specifies **Modules 1–5** as prerequisites. In particular, you should already understand:

- what data architecture is and the role of a data architect;
- the boundary between data architecture, data engineering, and solution architecture;
- business capabilities, domains, and data ownership;
- architecture principles and quality attributes;
- lifecycle, governance, decision rights, review outcomes, and exception handling.

These concepts are needed because framework evaluation uses earlier work as its criteria. For example, a framework is not a good fit merely because it has many artefacts. It must help express the organisation's requirements, support its decision rights, and make architecture principles actionable.

### 3.1 Vocabulary used in this lesson

| Term | Working definition | Example of the kind of thing it is |
|---|---|---|
| Framework | A structured approach and vocabulary for organising architecture work, concerns, stakeholders, views, process, and artefacts | TOGAF provides an enterprise architecture method and supporting guidance |
| Reference model | An abstract set of concepts and relationships that establishes a shared language for a domain | A conceptual model of data-management functions and their relationships |
| Reference architecture | A reusable architecture template or pattern for a class of problem, including suggested components and relationships | A vendor-neutral logical pattern for an analytical data platform |
| Standard | A specification or rule adopted as mandatory or agreed within a defined scope | An organisation's required metadata fields for a production data product |
| Principle | A durable decision rule that guides choices and trade-offs | “Authoritative customer attributes must have a named owner and source of authority” |
| Implementation blueprint | A concrete design for a specific organisation, system, or delivery | A bank-specific target-state diagram, technology choices, interfaces, migration sequence, and operating responsibilities |

The terms are related but not interchangeable. A framework may include or refer to standards; a reference architecture may be adopted as an internal standard; a principle may be informed by a framework; and a blueprint may use a reference architecture as a starting point. None of those relationships makes the terms synonymous.

### 3.2 The vocabulary of views

The roadmap requires learning four related terms.

- **Stakeholder:** a person, group, or organisation with an interest in the architecture or affected by it.
- **Concern:** an issue important to a stakeholder, such as data ownership, service continuity, cost, auditability, or interoperability.
- **Viewpoint:** a specification for constructing and interpreting a view for a particular set of concerns. It defines what to include and how to communicate it.
- **View:** a representation of the architecture from a particular perspective, created according to a viewpoint.

For example, the operations team may need a view showing data pipelines, dependencies, alerts, recovery points, and service ownership. A business executive may need a view showing capabilities, business outcomes, major risks, and investment choices. Both views can describe the same architecture without duplicating every detail.

A **viewpoint** is the reusable rule for constructing the representation; a **view** is the actual representation for the system or organisation under discussion.

### 3.3 Which term is most abstract?

There is no universal single ordering for every possible artefact, but for the roadmap's five categories, a useful teaching approximation is:

```text
More general / reusable
    Framework and reference model
             |
    Reference architecture
             |
    Standard (if adopted for a defined scope)
             |
    Organisation-specific implementation blueprint
More specific / implementation-bound
```

This is a conceptual aid, not a strict mathematical hierarchy. A standard can be broad or detailed; a framework can include concrete templates; a reference architecture can be very detailed. Classify an artefact by its purpose and authority, not by its title or length.

**Can a reference architecture be a standard?** The artefact's original role and its organisational status must be distinguished. A reference architecture is guidance by nature of its purpose; an organisation can formally adopt some or all of it as a mandatory internal standard. That does not mean every published reference architecture is automatically mandatory.

## 4. Beginner-level learning sequence

### 4.1 Frameworks and reference models in plain language

A framework is like a structured method for asking the right architecture questions and organising the work. A reference model is like a shared conceptual map that helps people use consistent terms and understand relationships. A reference architecture goes further by suggesting a reusable arrangement of architectural building blocks for a particular class of problem. A standard states an agreed rule; a blueprint describes a specific implementation.

Consider a banking data platform:

- A **framework** may help the team organise architecture development, stakeholder concerns, views, and decisions.
- A **reference model** may help the bank organise data-management concepts and establish a common vocabulary for governance, quality, metadata, and architecture.
- A **reference architecture** may show a typical flow from source systems through ingestion, validation, curated storage, consumption, monitoring, and governance.
- A **standard** may require each production data product to publish an owner, schema contract, quality checks, and support contact.
- An **implementation blueprint** may specify the bank's chosen cloud services, network boundaries, data stores, schemas, deployment sequence, operational controls, and migration steps.

The reference architecture does not prove that the bank needs every component in the example. The blueprint must be designed against actual requirements, constraints, existing systems, and risk.

### 4.2 Why the categories matter

Confusing these categories creates predictable errors:

| Confusion | Resulting mistake | Corrective question |
|---|---|---|
| Framework = architecture | Team claims to have an architecture because it filled in framework artefacts | What target state and decisions did the work actually produce? |
| Reference model = implementation | Abstract concepts are translated into products without requirements | What business need justifies each implementation choice? |
| Reference architecture = mandatory design | Teams copy components that do not fit their scale or constraints | Which assumptions hold here, and which deviations are justified? |
| Standard = guideline | Mandatory controls are treated as optional advice | Who adopted the rule, what is its scope, and how is conformance checked? |
| Principle = technology preference | A durable decision rule becomes a disguised vendor choice | What outcome and trade-off does the principle protect? |
| Blueprint = reusable framework | One project's detailed design is copied across contexts | Which parts are reusable, and which depend on local constraints? |

### 4.3 Framework example 1: TOGAF Standard, 10th Edition

**Identity and source status:** TOGAF is a lesson-selected example. It is not named as mandatory by the roadmap. The Open Group describes the TOGAF Standard as an enterprise architecture standard with fundamental content and Series Guides; the TOGAF approach is intended to be configured for the organisation's practice. Official sources: [The Open Group TOGAF overview](https://www.opengroup.org/togaf) and [TOGAF standards publications](https://publications.opengroup.org/standards/togaf).

**Purpose and scope:** TOGAF is intended to structure enterprise architecture work, including the development and communication of architecture that responds to stakeholder and business needs. It is broader than data architecture alone; data architecture is one concern within an enterprise architecture practice.

**Relevant concept:** the Architecture Development Method (ADM) provides a structured approach to architecture development. TOGAF also provides concepts and guidance for architecture content, views, governance, and configuration of the architecture practice. The precise materials used depend on the edition and the guidance selected; this lesson does not claim that every guide or artefact is required for every adoption.

**Appropriate use cases:**
- an organisation needs a repeatable way to frame architecture work;
- several domains need common architecture language and decision traceability;
- architecture must connect business drivers, requirements, target architecture, and implementation planning;
- a growing architecture practice needs to define which methods and artefacts it will use.

**Limitations and trade-offs:**
- a full enterprise method can impose more process and artefacts than a small team can sustain;
- the method does not decide the organisation's target architecture automatically;
- its vocabulary may need translation into local language;
- following a process does not prove that a design is technically sound;
- the organisation must choose what to use and establish its own decision rights and standards.

**Data architecture application:** use the method to structure discovery, requirements, current/target views, option analysis, and decision records. Keep only artefacts that have a defined audience and a real use. Validate data ownership, semantics, quality requirements, and platform choices through the organisation's own evidence.

### 4.4 Data-management example 2: DAMA-DMBOK 2nd Edition (2024 Revised Edition)

**Identity and source status:** DAMA-DMBOK 2nd Edition (2024 Revised Edition) is a lesson-selected example, not a roadmap-mandated framework. DAMA International calls it the *Data Management Body of Knowledge* and describes it as a curated, structured subset of generally accepted data-management knowledge. DAMA identifies the 2024 revised edition as a maintenance revision of DMBOK 2, not a new 3.0 publication. Primary sources: [DAMA-DMBOK overview](https://dama.org/learning-resources/dama-data-management-body-of-knowledge-dmbok/) and [DAMA-DMBOK 2 Revised Edition FAQ](https://dama.org/dama-dmbok2-revised-edition-faqs/).

**Purpose and scope:** DAMA-DMBOK 2nd Edition (2024 Revised Edition) organises data-management knowledge and practices, providing shared vocabulary and a way to understand the breadth of data management. It is not the same thing as an enterprise architecture development method, and it does not prescribe a specific bank's physical platform design.

**Relevant concepts:** its knowledge areas provide a way to consider data management as a set of connected concerns, rather than reducing the problem to storage and pipelines. Relevant topics for this roadmap include data architecture, governance, data quality, data modeling, metadata, integration/interoperability, and other data-management functions. Refer to the official publication for the exact edition's scope and structure.

**Appropriate use cases:**
- an organisation needs to identify data-management responsibilities or capability gaps;
- teams use inconsistent terms for data-management work;
- a programme needs to make sure important data-management concerns are considered alongside architecture and engineering;
- a data-management improvement plan needs a shared conceptual reference.

**Limitations and trade-offs:**
- a body of knowledge is not a ready-made implementation architecture;
- a list of knowledge areas does not assign ownership or decision rights for a particular organisation;
- using every category as a separate team or project may create unnecessary bureaucracy;
- it cannot replace domain discovery, measurable requirements, local operating-model decisions, or specialist interpretation of actual obligations.

**Data architecture application:** use the knowledge areas as a prompt to inspect whether a current-state inventory or target-state proposal has omitted important data-management concerns. Then map the relevant concerns to named owners, requirements, principles, controls, and deliverables.

### 4.5 Comparison: what kind of problem does each address?

TOGAF Standard, 10th Edition and DAMA-DMBOK 2nd Edition (2024 Revised Edition) are not identical alternatives. One is an enterprise architecture method/framework and standard; the other is a data-management body of knowledge. They can complement one another, but their scopes overlap only partially.

| Dimension | TOGAF Standard, 10th Edition | DAMA-DMBOK 2nd Edition (2024 Revised Edition) |
|---|---|---|
| Primary purpose | Structure enterprise architecture practice and development | Structure data-management knowledge and shared terminology |
| Main question it helps ask | How do we organise architecture work and develop architecture responsive to stakeholder needs? | What data-management knowledge areas and practices must we understand and coordinate? |
| Typical value | Process, architecture viewpoints/content, reusable guidance, and a configurable method | Breadth of data-management concerns and a common language |
| Not a substitute for | Business requirements, local decisions, technical design, or accountable governance | Enterprise architecture method, local ownership assignments, physical platform design, or implementation plans |
| Possible fit | Organisation needs consistent architecture development across domains | Organisation needs to assess or organise data-management capabilities |
| Main adoption risk | Process and artefact overhead; framework compliance becomes the goal | Knowledge-area checklist becomes bureaucracy without owners or measurable outcomes |

Use them together only when there is a specific need for both forms of guidance. Do not adopt two approaches simply to appear comprehensive.

### 4.6 Beginner exercise: classify ten artefacts

Classify each item as one of the roadmap's five categories: framework, reference model, reference architecture, standard, or implementation blueprint. Explain the reason for each answer. Some descriptions are intentionally ambiguous; state what additional evidence would settle the classification.

1. A published method that describes architecture development activities and provides guidance for organising architecture views.
2. An abstract diagram of data-management concepts and relationships used to align terminology.
3. A reusable logical pattern for ingesting, validating, storing, and serving analytical data.
4. An internal rule requiring every production data product to have a named owner and support contact.
5. A bank-specific design naming cloud services, schemas, access paths, deployment steps, and recovery procedures.
6. A slide deck that shows the bank's target-state architecture but has no named audience or decision status.
7. A published guide that describes common capabilities but leaves local roles and technology choices to the organisation.
8. A formally approved internal document that adopts a subset of a published reference architecture as mandatory.
9. A formally approved specification requiring customer-event messages to include a business identifier, event timestamp, and schema version.
10. A template pack that supports a method but does not itself specify the bank's target architecture.

**Classification boundary:** the principle concept is defined separately in §3.1 because it is useful architecture vocabulary, but it is not one of the five categories required by this exercise. Do not force principles into the framework/reference-model/reference-architecture/standard/implementation-blueprint taxonomy. Item 9 is a standard only if an accountable authority has adopted the specification as mandatory within a stated scope; otherwise, it is merely a proposed specification.

**Ability to demonstrate:** use the five terms correctly and consistently, and explain why a title alone does not establish an artefact's category.

## 5. Intermediate-level learning sequence

### 5.1 How frameworks structure concerns

A framework helps organise the architecture conversation so that stakeholders' concerns are not mixed together or forgotten. A practical sequence is:

1. Identify stakeholders and the decisions they need to make.
2. Identify their concerns: business outcome, ownership, quality, security, cost, interoperability, operations, change impact, and so on.
3. Select viewpoints that express those concerns clearly.
4. Create views from verified current-state facts and explicit assumptions.
5. Link requirements and principles to options, decisions, and implementation consequences.
6. Keep the views and artefacts current enough that people actually use them.

For a bank, a business executive may need a capability and investment view; a data owner may need definitions, ownership, lineage, and consumers; a platform engineer may need data flows, service dependencies, throughput, recovery, and operational controls. One giant diagram rarely serves all these needs.

### 5.2 How a reference model creates shared language

A reference model supplies concepts and relationships that can be mapped to the organisation's vocabulary. It is not necessary for every team to adopt every term unchanged. The important outcome is that differences and equivalences become explicit.

Example:

| Business unit A term | Business unit B term | Candidate common concept | Decision needed |
|---|---|---|---|
| Client | Customer | Customer party, if definitions and scope truly match | Are legal entity customers and individual customers included in both terms? |
| Account number | Account ID | Account identifier | Is the identifier globally unique or unique only within a source system? |
| Active customer | Current client | Status concept, potentially different definitions | What are the inclusion rules and effective dates? |
| Transaction date | Posting date | Different event-time concepts unless proven otherwise | Which date is used for which business question? |

A mapping table should preserve semantic differences rather than forcing false equivalence. If two terms differ in definition, ownership, lifecycle, or legal meaning, record the difference and decide whether a common abstraction is useful.

### 5.3 Evaluating suitability: roadmap criteria

The roadmap explicitly requires these criteria:
- fit to the problem;
- effort to adopt;
- skills required;
- flexibility;
- evidence of use;
- compatibility with existing practices;
- regulatory alignment.

The criteria below explain how to apply each one.

| Criterion | Questions to ask | Evidence to seek | Warning sign |
|---|---|---|---|
| Fit to problem | Does the approach address the decision or capability gap we actually have? | Map requirements and stakeholder concerns to concepts or artefacts the approach supports | “It is popular” is the main reason for selection |
| Effort to adopt | How much training, process change, documentation, tooling, and ongoing maintenance will it require? | Small pilot, time estimate, affected roles, expected recurring effort | No one owns the ongoing work or its cost |
| Skills required | Do staff have the skills, or can they realistically develop them? | Skills inventory, training plan, dependency on external expertise | The method depends on expertise that is unavailable and unfunded |
| Flexibility | Can the approach be configured to fit the organisation without breaking its intent? | Guidance on tailoring; test of a minimal subset; examples of supported adaptation | Local constraints are treated as defects rather than inputs |
| Evidence of use | Is there credible evidence that the approach is used for comparable problems? | Primary documentation, credible case evidence, practical pilot results | Vendor claims or popularity are accepted as proof of fit |
| Compatibility with existing practices | Does it integrate with current lifecycle, delivery, governance, and documentation? | Map existing artefacts and meetings to proposed ones; identify duplicates | Two parallel systems of record are created |
| Regulatory alignment | Can it help structure required evidence and controls relevant to the organisation's actual obligations? | Validated requirements from accountable legal/compliance/risk functions and traceable control mappings | A framework is claimed to guarantee compliance |

“Regulatory alignment” does not mean a framework itself confers compliance. The organisation must identify the applicable obligations and validate how its controls and evidence satisfy them. This lesson does not provide legal advice or verify a particular bank's compliance.

### 5.4 Worked evaluation matrix

**Illustrative organisation:** a mid-sized bank has a small architecture team, several legacy source systems, a developing data platform, uneven data ownership, and limited capacity to adopt a large documentation process. It wants a more consistent way to structure architecture work and a better shared language for data-management capabilities.

**Candidates:** TOGAF Standard, 10th Edition and DAMA-DMBOK 2nd Edition (2024 Revised Edition). They are different types of guidance, so this matrix evaluates them against the bank's two related needs rather than pretending they are interchangeable.

Scoring scale: 1 = weak fit; 3 = mixed/conditional fit; 5 = strong fit. Scores are illustrative hypotheses based on the described scenario, not independently measured performance or an industry ranking.

| Criterion | Weight | TOGAF 10th Ed. score | TOGAF rationale | DAMA-DMBOK 2nd Ed. (2024 Revised) score | DAMA-DMBOK rationale |
|---|---:|---:|---|---:|---|
| Fit to architecture-development process | 25% | 5 | Strong candidate for structuring architecture development and views | 2 | Useful for data concerns, but not a complete enterprise architecture method |
| Fit to data-management capability language | 20% | 3 | Can structure architecture concerns but does not replace a data-management knowledge reference | 5 | Strong candidate for organising data-management knowledge and shared vocabulary |
| Effort to adopt with limited staff | 15% | 2 | A broad method can create overhead if adopted wholesale | 4 | Can be used selectively as a knowledge reference, though implementation still requires work |
| Skills and learning capacity | 10% | 3 | Requires practitioners to configure and apply the method well | 3 | Requires interpretation and local mapping; terminology alone does not assign accountability |
| Flexibility / selective adaptation | 10% | 4 | The Open Group describes TOGAF as configurable | 4 | Can be used as a structured reference rather than a mandatory organisation chart |
| Compatibility with existing practices | 10% | 3 | Depends on whether existing architecture artefacts and lifecycle can be mapped | 3 | Depends on mapping knowledge areas to current roles and processes |
| Support for evidence of actual obligations | 10% | 3 | Can help structure architecture evidence, but does not prove compliance | 3 | Can inform data-management scope, but does not prove compliance |

Weighted illustrative totals:

- TOGAF: \(0.25(5)+0.20(3)+0.15(2)+0.10(3)+0.10(4)+0.10(3)+0.10(3)=3.45\)
- DAMA-DMBOK 2nd Edition (2024 Revised Edition): \(0.25(2)+0.20(5)+0.15(4)+0.10(3)+0.10(4)+0.10(3)+0.10(3)=3.40\)

The near-equal totals do **not** mean the two are interchangeable. The matrix intentionally combines two different needs, so the useful result is the criterion-level view: TOGAF is the stronger candidate for structuring architecture development; DAMA-DMBOK 2nd Edition (2024 Revised Edition) is the stronger candidate for structuring data-management knowledge. A practical recommendation could use a small subset of TOGAF for architecture workflow and DAMA-DMBOK as a reference for checking data-management coverage—only if the bank has a clear user for each.

#### 5.4.1 Limitations of the matrix

- The weights reflect the illustrative bank's priorities and would change for another organisation.
- The scores are hypotheses, not objective measurements or industry rankings.
- The matrix cannot settle which requirements are mandatory or which decision rights exist.
- It does not replace a pilot, stakeholder review, or assessment of actual documentation and staffing.
- A criterion that is a hard constraint should not be hidden inside a weighted average. If an approach cannot satisfy a non-negotiable requirement, record that as a gate rather than compensating with high scores elsewhere.

### 5.5 Identify relevant and irrelevant parts

For each candidate, ask which concepts directly solve a known problem and which add overhead without a user.

**Adopt** a component when it fills a real gap and someone will use its output.

**Adapt** it when the underlying purpose is valuable but the format, terminology, depth, or process does not fit the organisation.

**Defer** it when it may be useful later but the prerequisites, staff, or business need do not yet exist.

**Ignore** it when it does not address a relevant problem, duplicates a stronger existing practice, or creates more cost than value.

Example for the mid-sized bank:
- **Adopt:** a lightweight, consistent method for stakeholder concerns, current/target views, options, and architecture decisions.
- **Adapt:** architecture deliverables to fit the bank's existing change tickets and repository rather than creating a second document system.
- **Defer:** enterprise-wide formalisation of every viewpoint until the bank has identified the few views needed for its immediate decisions.
- **Ignore:** any template that no stakeholder uses and that does not support a decision, control, or operational responsibility.

This is not a statement that the named publications prescribe these exact choices. It is a worked application of the roadmap's adoption method.

### 5.6 Mapping concepts to local artefacts

Framework adoption becomes practical when each selected concept is mapped to an artefact, owner, use, and review point.

| Selected concept | Local artefact | Owner / user | Decision or activity supported | Evidence of value |
|---|---|---|---|---|
| Stakeholder concerns and viewpoints | Viewpoint catalogue | Architecture lead with business and technical stakeholders | Defines which views are needed and for whom | Stakeholders can use the view to make a named decision |
| Current and target architecture | Current-state inventory and target-state view | Domain/platform owners and architect | Exposes gaps and informs roadmap sequencing | Material dependencies and gaps have owners and actions |
| Data-management knowledge areas | Data capability coverage map | Data-management lead / domain owners | Identifies missing or duplicated responsibilities | Gaps are linked to accountable owners and measurable actions |
| Architecture decision method | Decision record and review workflow | Governance owner and decision authority | Makes material choices traceable | Review outcomes and implementation consequences can be followed |
| Reference architecture | Pattern description with assumptions and deviations | Architecture and engineering leads | Provides a starting point for solution design | Teams reuse the useful pattern without copying invalid assumptions |

If the same information is already captured in an existing system, link to it rather than duplicating it. Every new artefact should have a defined user and a decision or operation it supports.

### 5.7 Keep terminology consistent without renaming everything

When a framework's vocabulary differs from local terms, do not automatically force the whole organisation to rename its concepts. Use a mapping table with:
- source term and definition;
- local term and definition;
- equivalence status: equivalent, partial overlap, or distinct;
- owner responsible for the mapping;
- downstream artefacts affected;
- decision on whether to retain both terms or adopt a common term;
- review trigger.

A common vocabulary is valuable only if it preserves meaning. Forcing “customer,” “client,” and “party” to mean the same thing without checking their definitions can create semantic errors that are harder to detect than terminology differences.

### 5.8 Intermediate exercise: compare two candidates

Use the named lesson examples or two candidates you can verify from authoritative sources. Do not claim that the roadmap prescribes your chosen candidates.

1. State the organisation's problem and intended outcome.
2. Describe each candidate's purpose and scope in your own words.
3. Score both against all seven roadmap criteria.
4. Explain the evidence behind each score.
5. State the limitations of the scorecard.
6. Identify the parts you would adopt, adapt, defer, and ignore.
7. Describe one practical pilot that would test the most uncertain assumption.
8. State what evidence would cause you to reverse the recommendation.

**Ability to demonstrate:** produce a structured, evidence-based comparison of two options and make the limits of the comparison explicit.

## 6. Advanced-level learning sequence

### 6.1 Adapt to organisational context

The roadmap requires adaptation to organisation size, industry, maturity, regulatory obligations, and technical constraints. These are not footnotes; they determine what can be adopted responsibly.

| Context dimension | Questions to ask | Likely adaptation consequence |
|---|---|---|
| Organisation size | How many domains, teams, systems, and architecture practitioners exist? | A small team may need a minimal method and fewer views; a large group may need shared definitions and federated decision paths |
| Industry | Which business processes, data meanings, operational risks, and specialist obligations are relevant? | Select concerns and evidence relevant to the industry rather than copying another industry's artefacts |
| Maturity | Are ownership, inventories, decision records, and operational measures already reliable? | Start with foundational inventory and decision traceability before expanding to complex modelling |
| Regulatory obligations | Which obligations actually apply, who interprets them, and what evidence is required? | Map validated obligations to requirements and controls; do not assume a framework guarantees compliance |
| Technical constraints | What legacy systems, contracts, skills, platforms, and migration limits exist? | Use transition states, adapters, bounded exceptions, or a phased target rather than pretending the target can be deployed immediately |
| Delivery constraints | What must be delivered, by when, and with which dependencies? | Use the smallest useful set of artefacts and risk-proportionate review while preserving decision traceability |
| Existing practices | Which current processes and repositories work well? | Reuse or map them rather than creating parallel systems of record |
| Skills and ownership | Who will maintain the framework-derived artefacts? | Do not adopt components without owners, capability, or a sustainable maintenance plan |

A useful adoption decision is contextual and revisable. It is not a declaration that one framework is universally superior.

### 6.2 Avoid rigid templates

A template should help a person think, communicate, decide, or operate. It should not be filled merely because a framework mentions it.

Before retaining an artefact, ask:
1. Who is the user?
2. What concern or decision does it support?
3. What information must be present?
4. Is that information already maintained somewhere else?
5. What is the minimum version that still supports the decision?
6. Who will update it when the architecture changes?
7. How will we know the artefact is useful?

For a team of ten people, a one-page decision record and a small set of diagrams may be more useful than a large architecture repository with dozens of mostly empty views. For a large regulated group, more formal traceability may be justified, but the artefacts still need owners and use cases.

### 6.3 Use reference architectures as guidance, not prescription

A reference architecture captures a reusable pattern or a proposed arrangement of components for a class of problem. It is useful because it can make a design discussion concrete. It is dangerous when teams copy it without checking the assumptions.

Before adopting a reference architecture, record:
- intended problem and scope;
- business and technical assumptions;
- prerequisites and dependencies;
- expected qualities and trade-offs;
- operating and support model;
- which components are essential versus optional;
- which local constraints differ;
- deviations and their rationale;
- evidence and triggers that could justify revisiting the choice.

**Example:** a reference architecture for analytical data may include separate ingestion, raw, curated, semantic, and consumption layers. A bank may already have a stable governed warehouse and no business case for an additional raw zone in a particular workload. It should not add a layer just because the reference diagram contains it. Conversely, it should not omit a component that is needed for replay, lineage, quality controls, or recovery without an evidence-based alternative.

### 6.4 Explain framework-derived decisions to stakeholders

Stakeholders usually care about the problem, consequences, and decision—not the framework's vocabulary by itself. Explain the decision in this order:

1. **Business need:** what outcome or risk must be addressed?
2. **Local facts:** what is known about current systems, data, people, and constraints?
3. **Framework contribution:** which concept helped structure the analysis?
4. **Options:** what alternatives were considered?
5. **Local decision:** what was selected and why?
6. **Trade-offs:** what costs, risks, or limitations remain?
7. **Implementation and accountability:** who will do what, and how will conformance be checked?
8. **Revisit trigger:** what new evidence or change would reopen the decision?

Avoid saying “TOGAF requires this design” or “DAMA requires this platform” unless the exact claim is supported by the relevant primary source. More often, the framework informed the analysis, while the organisation made the decision.

### 6.5 Adoption record: adopted, adapted, deferred, ignored

The roadmap requires a one-page adoption plan and measures of whether it helps. Keep a traceable record of how each selected component is treated.

| Status | Meaning | Required rationale | Example |
|---|---|---|---|
| Adopt | Use the component substantially as intended because it solves a known need | What need it addresses and who will use it | Adopt a common decision record structure |
| Adapt | Preserve the useful intent while changing format, terminology, scope, or depth | What changed, why, and how the intent is preserved | Replace a large template with a concise version integrated into the existing repository |
| Defer | Delay adoption until a prerequisite, capability, or business need exists | What prerequisite is missing and when the choice will be reviewed | Defer a full viewpoint catalogue until stakeholder needs are clearer |
| Ignore | Do not use the component because it is irrelevant, duplicative, or not worth its cost | Why it does not add sufficient value and what existing approach covers the need | Ignore a duplicate artefact already maintained reliably in another system |

The record should identify the exact source concept or component, the version consulted, the local adaptation, the accountable owner, related architecture decisions, and the review trigger. Avoid a vague claim such as “we use TOGAF” if you cannot name the parts used.

### 6.6 Worked advanced example: framework adoption for a mid-sized bank

**All organisational details and scores in this example are illustrative.** No actual bank's policies, staffing, systems, or regulatory status are asserted.

#### Context and constraints

A mid-sized bank has:
- a small central architecture team;
- multiple legacy transaction and customer systems;
- inconsistent terminology between business units;
- a data platform initiative with several delivery teams;
- limited time for creating and maintaining new documentation;
- an internal requirement to demonstrate decisions and ownership clearly, whose exact scope must be validated by the bank's accountable governance functions.

The desired outcome is a repeatable way to make architecture decisions and a shared way to assess data-management gaps, without launching a framework-compliance programme.

#### Alternatives

- **Option A — Adopt TOGAF broadly:** use a broad architecture development method and supporting artefacts across the practice.
- **Option B — Use a tailored subset of TOGAF Standard, 10th Edition, plus DAMA-DMBOK 2nd Edition (2024 Revised Edition) as a data-management reference:** use a small architecture lifecycle/view/decision method and use data-management knowledge areas to check coverage.
- **Option C — Use only existing local practices:** improve the current templates and vocabulary without introducing a named framework or body of knowledge.
- **Option D — Adopt a vendor reference architecture as the primary design:** start from a concrete platform pattern and tailor it to the bank.

#### Decision criteria and evidence

| Criterion | Evidence to collect | Risk if ignored |
|---|---|---|
| Fit to business problem | Stakeholder interviews, current-state inventory gaps, recurring decision problems | Adoption becomes an abstract documentation exercise |
| Staff effort | Estimated hours to learn, tailor, create, and maintain artefacts | Process exceeds available capacity |
| Skills | Existing architecture and data-management skills; training needed | Templates are filled without sound judgement |
| Flexibility | What can be tailored without losing the useful purpose | Local constraints are labelled non-compliance instead of addressed |
| Existing practice fit | Current repositories, change workflows, data catalogues, and decision records | Duplicate systems of record and inconsistent status |
| Evidence and obligations | Validated internal requirements and specialist input where relevant | Framework is mistakenly treated as proof of compliance |
| Reversibility | Cost of trial and ability to stop or change approach | The organisation commits before learning whether the approach helps |

#### Illustrative decision

Select **Option B as a time-bounded pilot**, not as a permanent enterprise mandate.

- Adopt a lightweight architecture decision process and a small set of stakeholder-relevant views.
- Adapt terminology and artefact formats to the bank's current tools and delivery workflow.
- Use DAMA-DMBOK 2nd Edition (2024 Revised Edition) as a coverage prompt for data-management concerns; map relevant topics to existing owners and controls rather than creating a team for every knowledge area.
- Defer formal expansion to additional viewpoints until the pilot demonstrates value.
- Ignore duplicated templates where existing artefacts already provide reliable evidence.
- Do not adopt a vendor reference architecture as the primary framework; consider it later for a specific platform design if its assumptions fit.

#### Trade-offs and risks

**Benefits:** the bank gains a shared architecture workflow, clearer decision traceability, and a way to identify data-management gaps without requiring every team to learn every part of a broad method.

**Costs and risks:** the pilot still requires staff time; the mapping can become stale; different teams may interpret the terms inconsistently; selective adoption may leave gaps if no one checks coverage.

**Mitigations:** name an owner, define the minimum artefacts, keep the adoption/deviation record, sample decisions for quality, and review measures after a fixed pilot period.

#### Measures and revisit triggers

Use a small baseline and review the pilot against:
- percentage of material decisions with clear rationale and owner;
- time from complete decision submission to outcome;
- number of duplicated or unused artefacts;
- stakeholder feedback on whether views answer their questions;
- gaps or rework found during implementation that could have been identified earlier.

These are proposed measures, not claims that a framework will automatically improve them. The bank should compare a baseline and pilot period and interpret changes in context.

Revisit the adoption decision if the bank grows substantially, a merger adds new domains, the data platform operating model changes, validated obligations require different traceability, the pilot adds more effort than value, or delivery teams cannot use the artefacts reliably.

### 6.7 Compare adoption by organisation type

The roadmap requires explaining how the recommendation changes for a mid-sized bank, a large regulated group, and a start-up.

| Context | Likely need | Possible adoption approach | Main risk to guard against |
|---|---|---|---|
| Mid-sized bank with limited architecture staff | Consistency and traceability with low overhead | Tailored subset of architecture method; data-management reference used selectively; clear owner for each artefact | Overloading a small team with broad documentation |
| Large regulated group | Cross-domain consistency, evidence traceability, portfolio coordination, and controlled variation | More formal viewpoints, repositories, governance, and mapping from validated obligations to architecture evidence | Turning central standards into a slow, one-size-fits-all gate |
| Start-up | Speed, clear ownership, and enough structure to avoid expensive early inconsistencies | Minimal principles, a few useful views, concise decision records, and a small set of data-management concerns | Overengineering for scale or adopting processes without owners |

These are tendencies, not universal rules. A small start-up handling high-impact data may need strong controls in specific areas; a large group may delegate many decisions to domain teams. Size alone does not determine governance intensity.

### 6.8 Deviation record against a reference architecture

A deviation record explains why a project differs from a reference architecture and how it will manage the consequences. It is not an apology for failing to copy the diagram.

**Illustrative example:**

| Field | Example |
|---|---|
| Deviation ID | DEV-RA-004 |
| Reference architecture | Internal analytical data platform reference pattern, version 1.2 (illustrative) |
| Reference component | Separate raw-data landing zone for every source |
| Local decision | For one low-volume, governed source, ingest directly into an existing controlled landing area with equivalent lineage, validation, replay, and access controls |
| Context | Existing landing capability already satisfies the relevant operational needs; creating another zone would duplicate support and access management |
| Assumptions | The source contract is stable; the existing zone supports required volume, isolation, and recovery |
| Alternatives considered | Copy the reference exactly; use existing zone with controls; defer integration |
| Rationale | Avoid duplicate infrastructure while preserving the reference pattern's underlying control objectives |
| Risks | Existing zone may become overloaded or fail to provide required isolation |
| Mitigations | Validate capacity and access boundaries; test replay and recovery; monitor volume and isolation |
| Decision authority | Named architecture/platform authority under the organisation's actual governance model |
| Evidence required | Capacity test, access review, lineage/validation tests, recovery test, updated diagram |
| Review triggers | Volume exceeds agreed threshold, source sensitivity changes, new consumer or isolation need, repeated recovery failure |
| Status | Proposed until the actual authority approves it |

The example assumes the alternative really provides equivalent controls; the team must demonstrate that with evidence. If it cannot, the deviation is not justified by the record alone.

### 6.9 Advanced scenario: leadership demands “full framework compliance”

**Scenario:** leadership announces that every data programme must be “fully compliant with a framework,” but does not identify which framework, what “compliant” means, which business outcome is expected, or who will own the work.

**What to ask first:**
1. Which framework, edition, and specific components are intended?
2. Is the requirement a formal internal policy, a procurement requirement, a stakeholder preference, or a shorthand for better architecture consistency?
3. What business problem or risk is leadership trying to address?
4. Which deliverables and decisions need to improve?
5. What current practices already satisfy the intent?
6. What effort, skills, tooling, and ongoing ownership are available?
7. Who can approve adaptation or exceptions?
8. How will success be measured?

**What to propose:** a time-bounded assessment and pilot. Select a defined scope, map current artefacts to the proposed method, identify gaps and duplicated work, agree on a minimum viable set of components, and measure whether the pilot improves decision quality and traceability without unacceptable delay.

**Why not promise full compliance immediately?** The phrase is ambiguous, the target may be too broad, and framework adoption is not equivalent to a sound architecture or regulatory compliance. The organisation needs a precise scope, evidence, and decision authority before it can make a credible commitment.

**Decision path:** clarify intent → identify framework/version and scope → map existing practices → evaluate effort and gaps → pilot the minimum useful subset → measure → decide adopt/adapt/defer/ignore → record the decision and revisit triggers.

### 6.10 Advanced scenario: a project says the reference architecture is too heavy

**Scenario:** a delivery team argues that the reference architecture includes too many components and that the deadline cannot be met.

Do not accept or reject the claim based on opinion. Ask:
- Which components are proposed to be removed?
- What need or risk does each component address?
- Which assumptions in the reference architecture do not hold?
- What requirements and quality targets must still be met?
- What is the impact on operations, recovery, lineage, access, and downstream consumers?
- Can a smaller design meet the same requirements with equivalent controls?
- Is the proposed deviation reversible, and what evidence would trigger a revisit?

If the team proposes a simpler design, compare the alternatives against the same criteria and record the deviation. If a required capability would be lost, the team must either design an adequate alternative, change the requirement with the accountable owner, or defer the release. “The reference is too heavy” is a hypothesis to evaluate, not a decision.

### 6.11 Advanced scenario: two business units use different vocabularies

**Scenario:** one unit uses “client” and another uses “customer.” Leadership wants a single enterprise data model immediately.

A reference model can supply candidate concepts and relationships, but it cannot prove that local definitions are equivalent.

Process:
1. Collect the definitions, scope, lifecycle, ownership, identifiers, and use cases behind both terms.
2. Compare them and classify the relationship as equivalent, overlapping, or distinct.
3. Involve accountable business/data owners to resolve semantic questions.
4. If useful, create a common concept with explicit subtypes or mapping rules; retain distinct concepts when meanings genuinely differ.
5. Map source fields and downstream consumers to the agreed meaning.
6. Record unresolved differences and who owns them.
7. Revisit the mapping when business processes, products, or source systems change.

**Limit:** a reference model provides language and structure, not authority to decide business semantics. A forced common label can conceal a real difference and create downstream data-quality errors.

### 6.12 Minimum viable adoption

The roadmap asks: “What is the minimum viable use of this framework? Which artefact would you drop first?”

A useful minimum is the smallest set of concepts and artefacts that:
- addresses a named business or architecture problem;
- gives stakeholders the information needed for a decision;
- preserves traceability to requirements and owners;
- can be maintained by named people;
- does not duplicate a reliable existing source;
- can be evaluated with observable measures.

Drop or defer artefacts that have no audience, no decision use, no owner, and no requirement to retain them. Do not drop evidence simply because it is inconvenient if it is needed to manage material risk or meet an actual obligation.

### 6.13 Advanced exercise: one-page adoption plan

Create a one-page plan with these fields:

- organisation context and problem statement;
- candidate framework/reference model, publisher, edition/version, and authoritative source;
- selected components and why they fit;
- adopted, adapted, deferred, and ignored items;
- mapping to local artefacts, owners, and decision processes;
- required skills and estimated effort;
- key assumptions and limitations;
- pilot scope, duration, and success measures;
- deviations from any reference architecture;
- risks and mitigations;
- review date and triggers for changing the adoption decision.

**Ability to demonstrate:** produce a tailored adoption plan and a deviation record against a reference architecture.

## 7. Industry-application exercises

### Exercise A — Adoption recommendation for a mid-sized bank

Prepare an adoption recommendation for a hypothetical mid-sized bank with limited architecture staff. Use the named lesson examples or other candidates that you verify from primary sources.

Your recommendation must:
1. State the bank's business and architecture problem.
2. Identify the candidate's exact name, publisher, edition/version, purpose, and scope.
3. Explain how the approach helps with current-state assessment, target-state thinking, architecture documentation, governance, or platform planning.
4. Score candidates against the seven roadmap criteria and justify each score.
5. Separate hard constraints from weighted preferences.
6. State what to adopt, adapt, defer, and ignore.
7. Identify staffing, training, documentation, and maintenance costs.
8. Define a pilot and measurable success criteria.
9. Record limitations, assumptions, and revisit triggers.

Do not claim the framework is mandatory unless you have evidence of an actual requirement from the hypothetical organisation's accountable authority.

### Exercise B — Compare the recommendation for a large regulated group and a start-up

Use the same candidate set, but explain how the recommendation changes for:
- a large regulated group with multiple domains, shared platforms, and significant coordination needs;
- a start-up with limited staff and a small number of systems.

For each, discuss scope, decision rights, effort, minimum artefacts, flexibility, relevant evidence, and failure modes. Do not assume “large means full framework” or “start-up means no governance.”

### Exercise C — Review a reference architecture and record three deviations

Select a published reference architecture with an identifiable primary source, or use the clearly labelled illustrative analytical-data pattern from this lesson. List three justified deviations a real project might make.

For each deviation, include:
- the reference component and its intended purpose;
- local context and evidence;
- alternatives considered;
- rationale and trade-offs;
- risk and compensating design;
- decision authority;
- implementation evidence;
- review triggers.

At least one deviation should be rejected if the evidence does not support it. This tests whether you can distinguish a justified adaptation from a shortcut.

### Exercise D — Term classification table

Classify ten architecture artefacts into the five roadmap categories and justify each classification. Include at least one example where the title is misleading and one example where an organisation has formally adopted a reference architecture as a standard.

### Exercise E — Framework comparison and practice questions

Complete the comparison matrix in section 5.4 or create an equivalent. Answer the practice questions in section 11. Review whether each answer distinguishes the framework's contribution from the organisation's decision.

## 8. Practical scenarios and case-based reasoning

### 8.1 Leadership wants “full framework compliance”

**Context:** leadership wants a framework adopted but has not defined its name, scope, outcome, or success measures.

**Stakeholders:** executive sponsor, architecture lead, data/domain owners, delivery leads, governance owner, and specialist stakeholders whose obligations or controls may be affected.

**Risks:** broad unfunded effort, duplicate documentation, a false compliance claim, and focus on templates rather than decisions.

**Decision rights:** leadership clarifies the desired outcome and mandate; the architecture lead evaluates approach and effort; actual policy or regulatory interpretation belongs to the accountable internal authority, not to a framework vendor or the lesson author.

**Required evidence:** named framework and version, stated scope, current practices, gap analysis, staffing, existing artefacts, business objectives, and success measures.

**Governance steps:** clarify intent; select candidate components; map existing practices; identify gaps and duplicate effort; pilot a minimum set; measure; decide adopt/adapt/defer/ignore; record the decision and owner.

**Resulting artefacts:** framework evaluation matrix, adoption plan, decision record, and pilot measures.

**Review conditions:** pilot fails to improve outcomes, cost exceeds capacity, business priorities change, or the intended framework/scope changes.

### 8.2 A project says the reference architecture is too heavy

**Context:** the delivery team wants to omit components to meet a deadline.

**Stakeholders:** delivery lead, data architect, platform/operations owner, data owner, impacted consumers, and decision authority for any material deviation.

**Risks:** removing needed lineage, recovery, validation, isolation, or support capabilities; alternatively, copying unnecessary components can increase cost and delay.

**Decision rights:** the team proposes the deviation and supplies evidence; the authority named in the organisation's governance process decides when the deviation crosses a review boundary.

**Required evidence:** requirement-to-component mapping, reference assumptions, alternatives, risks, test results or prototype, operating impact, and reversibility.

**Governance steps:** identify the purpose of each challenged component; assess whether the purpose is still needed; compare a smaller design; record the deviation and compensating controls; test; review when triggers occur.

**Resulting artefacts:** deviation record, revised target-state view, test evidence, and updated decision record.

**Review conditions:** failed controls, volume or use changes, incidents, or evidence that the simplification no longer meets requirements.

### 8.3 Two business units use different vocabulary

**Context:** business units use different labels for concepts that may or may not be equivalent.

**Stakeholders:** business owners, data/domain owners, data architect, analysts, source-system owners, and downstream consumers.

**Risks:** false equivalence, broken metrics, conflicting identifiers, and accidental changes in meaning.

**Decision rights:** accountable business/data owners resolve meaning and ownership; architecture supports the mapping and records consequences.

**Required evidence:** definitions, data examples, lifecycle, scope, source fields, identifiers, consumers, and business use cases.

**Governance steps:** compare definitions; classify as equivalent/overlapping/distinct; map terms; preserve differences where real; validate downstream impact; record unresolved questions and owner.

**Resulting artefacts:** terminology map, conceptual model update, source-to-concept mapping, and decision record.

**Review conditions:** business process changes, new product or customer type, source-system migration, or downstream consumers reveal a semantic mismatch.

### 8.4 Banking application: framework-informed platform planning

**Illustrative scenario:** the bank wants to plan a data platform that serves operational reporting, analytics, and future data products.

**How guidance may help:**
- an enterprise architecture method can structure stakeholder concerns, current and target views, options, and decision traceability;
- a data-management body of knowledge can prompt the team to check whether ownership, governance, quality, metadata, integration, and architecture responsibilities are addressed;
- a reference architecture can provide candidate components and relationships to evaluate.

**What the bank must still decide:** which sources are authoritative, which domains own definitions, which quality and freshness targets apply, what access and retention rules are required, which platform components are justified, how migration will work, and who will operate each service.

**Required evidence:** current-state inventory, business requirements, data ownership, quality targets, source capabilities, options, cost and operational analysis, validated internal obligations, and implementation plan.

**Governance:** use the existing decision-rights model to classify choices; record adopted/adapted concepts; review cross-domain decisions; document deviations; check implementation against the approved target.

**Resulting artefacts:** current-state and target-state views, framework evaluation/adoption plan, decision records, reference-architecture deviation records, and measurable implementation outcomes.

**Review conditions:** business objectives change, the bank's operating model changes, legacy constraints are removed, a reference assumption proves false, or measures show that the adopted process adds cost without improving decisions.

## 9. Expected outputs or deliverables

The roadmap explicitly specifies these outputs:

- **Term classification table.**
- **Framework/reference model comparison with criteria.**
- **Adoption plan (adopt, adapt, defer, ignore) with rationale.**
- **Deviation record against a reference architecture.**
- **Answers to Topic 06 practice questions.**

Use the checklist below to make each deliverable reviewable.

| Deliverable | Minimum contents | Quality test |
|---|---|---|
| Term classification table | Ten artefacts; one of the five categories; justification; ambiguity notes where needed | Correctly distinguishes purpose and authority, not just document title |
| Framework/reference model comparison | Candidate names and versions; publisher/primary source; seven roadmap criteria; evidence, scores, limitations | Explains why candidates fit different needs; scores are labelled illustrative where not measured |
| Adoption plan | Context, scope, adopted/adapted/deferred/ignored components, rationale, owners, effort, measures, revisit triggers | Every selected component has a user and a clear reason |
| Deviation record | Reference architecture and component; local assumption; alternatives; rationale; risks; controls; authority; evidence; review triggers | Explains why the deviation is justified and how the intended purpose is preserved |
| Practice-question answers | Corrected answers covering terminology, comparison, scenarios, decisions, trade-offs, governance/ownership, framework selection and adaptation | Distinguishes source facts, assumptions, framework guidance, and local decisions |

### 9.1 Reusable adoption plan template

```markdown
# Framework / Reference Model Adoption Plan

- Organisation / domain:
- Business problem and intended outcome:
- Candidate name, publisher, edition/version:
- Primary source:
- Type: framework | reference model | reference architecture | other
- Decision owner:
- Contributors:
- Scope of evaluation:
- Constraints and assumptions:

## Evaluation
| Criterion | Evidence | Score / conclusion | Limitation |
|---|---|---|---|

## Adopt
- Component:
- Why it fits:
- Local artefact / owner:
- Evidence of value:

## Adapt
- Original component:
- Local change:
- Why:
- How the intent is preserved:

## Defer
- Component:
- Missing prerequisite:
- Review date / trigger:

## Ignore
- Component:
- Reason:
- Existing alternative, if any:

## Implementation plan
- Pilot scope:
- Skills and effort:
- Artefacts and owners:
- Training / communication:
- Risks and mitigations:

## Measures and review
- Baseline:
- Success measures:
- Review date:
- Revisit triggers:
- Decision status:
```

### 9.2 Reusable reference-architecture deviation record

```markdown
# Reference Architecture Deviation Record

- Deviation ID:
- Reference architecture title, publisher, version, source:
- Component or assumption being changed:
- Status:
- Requester / owner:
- Decision authority:
- Affected systems, domains, and consumers:

## Reference intent
What problem or risk does the original component address?

## Local context and evidence
Which assumptions hold or do not hold? Separate facts from hypotheses.

## Proposed deviation
What will be different, and what remains unchanged?

## Alternatives considered
Include copying the reference, adapting it, and deferring if relevant.

## Rationale and trade-offs
Why is the proposed option preferable in this context?

## Risks and compensating design
What risk is introduced? How will the original intent be preserved?

## Conformance / validation evidence
Tests, metrics, review, or operational evidence required.

## Review triggers
What change or failure would cause reassessment?

## Related decisions
Link the architecture decision, implementation ticket, and exception record if applicable.
```

## 10. Common mistakes and misconceptions

The roadmap identifies five core mistakes: treating a framework as the architecture, treating framework compliance as the goal, copying templates without a user, assuming a reference architecture fits every organisation, and claiming framework use without naming the parts used.

### 10.1 Treating a framework as the architecture

**Mistake:** the team completes framework artefacts and declares the architecture done.

**Why it fails:** artefacts are not the same as a justified target state or implementation decision.

**Better practice:** connect each artefact to a business concern, requirement, option, decision, owner, and implementation consequence.

### 10.2 Treating framework compliance as the goal

**Mistake:** success is measured by the number of templates completed or how closely a process resembles a published method.

**Why it fails:** process conformity can increase without improving architecture quality, decision traceability, or delivery.

**Better practice:** define intended outcomes and measures before adoption. Keep the parts that support those outcomes.

### 10.3 Copying templates without a user

**Mistake:** every suggested artefact is produced even when nobody uses it.

**Why it fails:** documentation becomes stale and expensive to maintain.

**Better practice:** identify the audience and decision for each artefact; remove or simplify duplicates unless a real obligation requires them.

### 10.4 Assuming a reference architecture fits every organisation

**Mistake:** a reference diagram is copied without validating assumptions.

**Why it fails:** legacy constraints, staffing, data volumes, skills, operating model, and business requirements differ.

**Better practice:** list assumptions, compare them with local evidence, record deviations, and validate the alternative.

### 10.5 Claiming to follow a framework without naming its parts

**Mistake:** a project says “we are TOGAF-compliant” or “we follow DAMA” without identifying what was used.

**Why it fails:** the claim is not reviewable, and different teams may mean different things.

**Better practice:** name the source and version; list the components adopted or adapted; record deviations and rationale. Avoid broad compliance claims unless the scope and assessment basis are defined and evidenced.

### 10.6 Conflating unlike candidates

**Mistake:** a framework, a body of knowledge, a reference model, and a vendor reference architecture are scored as if they solve the same problem.

**Why it fails:** apparent winners may simply have a different purpose.

**Better practice:** state the need being evaluated. Compare candidates for the same need, or explicitly compare complementary roles and do not treat the total score as a ranking.

### 10.7 Treating “regulatory alignment” as a compliance guarantee

**Mistake:** a framework is assumed to guarantee regulatory compliance.

**Why it fails:** actual obligations, interpretation, controls, implementation, and evidence remain organisation-specific.

**Better practice:** use the framework to structure traceability, but validate the obligation and control mapping with accountable internal specialists. Do not infer compliance from adoption.

### 10.8 Forcing a common vocabulary where meanings differ

**Mistake:** similar terms are collapsed into one concept before definitions and use cases are compared.

**Why it fails:** semantic differences become hidden and may distort reporting or decisions.

**Better practice:** map terms, compare definitions, retain meaningful differences, and name the owner of unresolved semantics.

### 10.9 Adopting too much too early

**Mistake:** an immature architecture practice adopts a large set of methods, views, repositories, and governance forums all at once.

**Why it fails:** skills and maintenance capacity are insufficient, and teams experience process as overhead.

**Better practice:** start with a minimum viable subset, pilot it, measure value, and expand only when a demonstrated need exists.

### 10.10 Adapting so much that traceability is lost

**Mistake:** the organisation changes terminology and artefacts but no longer knows what source concepts were retained.

**Why it fails:** teams cannot explain what was adopted, which intent remains, or how the local practice relates to its source.

**Better practice:** keep a mapping and adoption record with source, version, original concept, local form, rationale, owner, and review trigger.

## 11. Mastery criteria

The roadmap's mastery criteria are:

1. **Uses the five terms correctly.**
2. **Compares options with explicit criteria and evidence.**
3. **Produces a tailored adoption plan and justifies deviations.**

You have demonstrated mastery when your work can be reviewed by someone who did not participate in your analysis and that reviewer can understand the source, decision, rationale, limits, and follow-up.

### 11.1 Practice questions

Answer closed-book first, mark each answer correct/partly correct/wrong, and write a one-sentence correction for every partial or wrong answer.

1. What is an enterprise architecture framework?
2. What is a reference model, and how does it differ from a reference architecture?
3. Distinguish a framework, reference model, reference architecture, standard, and implementation blueprint.
4. What are stakeholder, concern, viewpoint, and view?
5. Which of the five artefact categories is most abstract and which is most specific? Why is the ordering only approximate?
6. Can a reference architecture become an internal standard? Explain the difference between its original purpose and adopted authority.
7. What problem does the TOGAF Standard help structure, and what does it not decide automatically?
8. What does DAMA-DMBOK provide, and why should it not be treated as a physical data platform blueprint?
9. Why are TOGAF and DAMA-DMBOK not interchangeable alternatives?
10. Name and explain the seven roadmap evaluation criteria.
11. Why should a hard constraint not be hidden inside a weighted score?
12. What does adopt/adapt/defer/ignore mean? Give one example of each.
13. How can a reference model help two business units with different vocabularies?
14. Why might the same framework adoption plan differ for a mid-sized bank, a large regulated group, and a start-up?
15. What information belongs in a reference-architecture deviation record?
16. Leadership requests “full framework compliance.” What do you clarify before recommending a plan?
17. A delivery team says a reference architecture is too heavy. What evidence would you require?
18. Give an example of a justified deviation and name the conditions that would make you reverse it.
19. What evidence would show that framework adoption is improving architecture work rather than adding ceremony?
20. What must be recorded so a future architect can understand which framework components were used and why?

### 11.2 Answer-quality checklist

For each answer, verify that it:
- uses the five terms consistently;
- identifies the actual purpose and scope of each named candidate;
- distinguishes source-prescribed requirements from lesson-selected examples;
- cites or links primary sources for framework identity and claims;
- separates verified facts from illustrative assumptions and judgement;
- explains the reason for the decision and its limitations;
- identifies local owners and the evidence needed to implement or revisit it;
- avoids unsupported claims of certification, mandatory adoption, or compliance.

## 12. Completion gate

Do not mark Topic 06 complete until all roadmap gate items are satisfied.

- [ ] Comparison, adoption plan, and deviation record complete and reviewed.
- [ ] The frameworks named in your notes match those named in the topic file (once written), or the discrepancy is recorded.
- [ ] Topic 06 practice questions answered and corrected.

Use the detailed acceptance checks below:

| Gate item | Pass condition | Evidence to retain |
|---|---|---|
| Comparison | Two candidates are compared against explicit criteria, with primary-source identity/scope, rationale, limitations, and assumptions | Comparison matrix and source links |
| Adoption plan | Adopt/adapt/defer/ignore decisions have rationale, owners, effort, measures, and revisit triggers | One-page adoption plan |
| Deviation record | At least one deviation explains reference intent, local evidence, alternatives, risks, compensating design, authority, and triggers | Completed deviation record |
| Framework names | The names in your notes match the lesson file; any source/notes discrepancy is recorded rather than silently reconciled | Candidate/source register |
| Practice questions | All questions answered and corrected; advanced answers reviewed by another person where feasible | Answer sheet and correction notes |

**Completion standard:** you can explain the five artefact categories, compare candidate approaches with evidence, produce a tailored adoption plan, and justify deviations from a reference architecture without claiming that a framework automatically determines the organisation's architecture.

---

## Scope and source note

The roadmap's Module 6 explicitly requires teaching the evaluation and adaptation method, but it does **not** name a specific framework or reference model as a mandatory syllabus item. It instructs the author of this topic file to name the examples covered. TOGAF Standard, 10th Edition and DAMA-DMBOK 2nd Edition (2024 Revised Edition) are named here as lesson-selected examples and their identities/broad scopes were checked against their primary publisher/owner pages listed at the top of the file. They must not be represented as names prescribed by the original roadmap.

The Stage 2D project tree places this lesson at `Stage 2D — Data Architecture/01-Data-Architecture-Foundations-and-Principles/06-enterprise-data-architecture-frameworks-and-reference-models.md`, after lessons 01–05 and alongside `practice-questions.md` and the current-state inventory project. The examples, scores, bank characteristics, and outcomes in the worked scenarios are illustrative, not verified facts about a real organisation.
