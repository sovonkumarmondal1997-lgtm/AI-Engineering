---
title: "Synthetic and Sampled Test Data"
module: "Stage 2 — Python for Data Engineering"
topic: "2.19.05"
filename: "05-synthetic-and-sampled-test-data.md"
level: "Beginner → Intermediate → Advanced → Production"
stack: "Python 3.12+, uv, NumPy, Faker, pandas, Polars, DuckDB, Pandera, boto3, MinIO, Parquet, dbt, pytest"
---

# 05 — Synthetic and Sampled Test Data

> **Production principle:** The goal of test data is not to copy production. The goal is to reproduce the behaviors, relationships, distributions, defects, and edge cases that matter for testing—without turning test environments into uncontrolled copies of sensitive production data.

This module teaches how to design, generate, sample, mask, validate, version, and safely distribute test datasets for Data Engineering systems.

The progression is:

```text
Why raw production data is a poor default
        ↓
Test-data requirements
        ↓
Synthetic vs sampled data
        ↓
Deterministic generation
        ↓
Realistic distributions
        ↓
Relational consistency
        ↓
Intentional defects
        ↓
Sampling
        ↓
Key-consistent sampling
        ↓
Masking / pseudonymization
        ↓
Edge-case mining
        ↓
Dataset tiers
        ↓
Versioning + manifests
        ↓
dbt / CI integration
        ↓
Production-grade test-data architecture
```

---

## Learning Outcomes

By the end of this module, you should be able to:

- explain why copying raw production data is a poor default for testing;
- distinguish synthetic data from sampled and masked data;
- generate deterministic datasets with NumPy and Faker;
- version generators and reproduce datasets from metadata;
- model realistic skew, seasonality, lateness, duplicates, nulls, and bad records;
- generate relationally consistent multi-table datasets;
- deliberately generate orphan records and other defects;
- use random, stratified, and key-consistent hash-based sampling;
- preserve relationships when sampling related tables;
- design per-column masking and pseudonymization rules;
- understand the privacy limitations of masking;
- mine unusual patterns from controlled/anonymized data and turn them into durable fixtures;
- validate the datasets used by tests;
- define tiny, small, and large dataset tiers;
- version datasets and publish larger datasets to object storage;
- create dataset manifests containing generator and schema metadata;
- integrate stable test data with dbt seeds, unit-test fixtures, CI, and integration environments;
- design a production-grade test-data factory.

---

# 1. Why Not Copy Production Data?

A tempting approach is:

```text
Production database
       ↓
copy database
       ↓
test environment
```

It feels realistic, but it creates several problems.

```text
Production data
       ↓
PII / confidential information
       ↓
Security risk
       ↓
Compliance / governance risk
       ↓
Large dataset
       ↓
Slow tests
       ↓
Changing data
       ↓
Unstable tests
       ↓
Still may miss rare edge cases
```

The key engineering principle is:

> **Realistic test data is not the same thing as copied production data.**

A test environment should receive the **minimum data necessary to exercise the behavior under test**, preferably synthetic data or a safely controlled sample.

---

## 1.1 Privacy and Sensitive Data

Production datasets may contain:

- names;
- email addresses;
- phone numbers;
- physical addresses;
- customer identifiers;
- account identifiers;
- payment-related information;
- business-sensitive values;
- free-form text that unexpectedly contains sensitive information.

The engineering problem is not merely where the database lives.

Every additional copy creates another place where data can be:

- downloaded;
- logged;
- backed up;
- cached;
- exposed to developers;
- included in CI artifacts;
- accidentally committed to Git;
- copied into Docker images;
- retained longer than intended.

A strong default is:

```text
Need only a schema?
    → use schema only

Need realistic records?
    → use synthetic data

Need a rare production behavior?
    → extract a minimal, safely transformed fixture
```

---

## 1.2 Legal and Compliance Considerations

The exact legal requirements depend on jurisdiction, organization, contract, and data classification.

The engineering principle is simpler:

> Test environments should not become uncontrolled copies of production-sensitive data merely because copied data is convenient.

Treat test-data handling as part of the organization's data-governance boundary.

Do not assume:

```text
"test environment"
```

means:

```text
"no privacy obligations"
```

---

## 1.3 Dataset Size

Production data can contain:

```text
millions
billions
or more rows
```

A unit test may need:

```text
5–50 rows
```

An integration test may need:

```text
hundreds or thousands of rows
```

A performance test may need:

```text
millions or more
```

These are different testing objectives.

A good test-data strategy uses different dataset tiers rather than copying the entire source system everywhere.

---

## 1.4 Production Data Is Not Stable Test Data

Production data changes continuously.

If yesterday's test dataset was copied at 02:00 and today's copy is taken at 14:00, the tests may execute against different records.

That can create:

```text
same code
+
different test data
=
different result
```

Synthetic or versioned test datasets provide controlled reproducibility.

---

## 1.5 Production Data May Still Miss Important Edge Cases

Even a realistic production sample may not contain:

- malformed timestamps;
- unusual Unicode;
- extreme numeric values;
- empty datasets;
- all-null fields;
- duplicate events;
- orphan records;
- very late events;
- rare status combinations.

Synthetic generation can deliberately create those cases.

---

# 2. Synthetic vs Sampled Data

There are two major approaches.

## Synthetic Data

Data is generated specifically for testing.

```text
Generator
   ↓
Synthetic records
   ↓
Validation
   ↓
Test dataset
```

## Sampled / Masked Data

A controlled subset is selected from a real dataset and safely transformed.

```text
Controlled production source
        ↓
Safe extraction
        ↓
Sampling
        ↓
Masking / pseudonymization
        ↓
Validation
        ↓
Test dataset
```

### Comparison

| Dimension | Synthetic | Sampled / Masked |
|---|---|---|
| Privacy | easier to control | requires strong controls |
| Realism | depends on generator | often naturally realistic |
| Edge cases | easy to deliberately generate | can be mined from real behavior |
| Relationships | must be modeled | may already exist |
| Reproducibility | high with seed/versioning | requires dataset/version control |
| Scale | easy to generate | extraction/storage can be expensive |
| Rare production behavior | may require modeling | can preserve observed patterns |
| Governance burden | generally lower | generally higher |

Both approaches are useful.

The production-grade answer is often:

```text
Synthetic data
+
small safe masked fixtures
+
explicit edge-case fixtures
```

---

# 3. What Good Test Data Must Provide

Good test data should be:

```text
Correct enough for its purpose
Reproducible
Safe
Realistic where realism matters
Edge-case rich
Relationally consistent
Capable of representing defects
Appropriately sized
Versioned
Traceable
```

Not every dataset must maximize every dimension.

For example:

```text
Tiny unit fixture
→ optimized for speed and edge cases

Integration dataset
→ optimized for relational realism

Performance dataset
→ optimized for scale and distribution shape
```

---

# 4. First Synthetic Generator with NumPy

Start with deterministic random generation.

```python
import numpy as np

rng = np.random.default_rng(42)

customer_ids = rng.integers(
    low=1,
    high=100_000,
    size=10,
)

quantities = rng.integers(
    low=1,
    high=10,
    size=10,
)

prices = rng.uniform(
    low=5.0,
    high=500.0,
    size=10,
)
```

The important part is:

```python
np.random.default_rng(42)
```

### What is the seed?

A seed initializes a pseudo-random generator so the same generator configuration can produce the same sequence.

Conceptually:

```text
seed = 42
     ↓
random generator
     ↓
same sequence
     ↓
same dataset
```

Run the generator again with the same seed and configuration.

```python
rng1 = np.random.default_rng(42)
rng2 = np.random.default_rng(42)

assert np.array_equal(
    rng1.integers(0, 100, 20),
    rng2.integers(0, 100, 20),
)
```

### Why `default_rng()`?

Prefer an explicit generator instance over relying on mutable global random state.

This makes dependencies clearer and reduces accidental coupling between tests.

---

# 5. Faker

Faker is useful for generating human-readable values.

Install:

```bash
uv add --dev Faker
```

Example:

```python
from faker import Faker

fake = Faker()
fake.seed_instance(42)

customers = [
    {
        "name": fake.name(),
        "email": fake.email(),
        "city": fake.city(),
    }
    for _ in range(5)
]
```

Faker can generate:

- names;
- emails;
- addresses;
- phone numbers;
- company names;
- dates;
- other formatted values.

### Important limitation

Faker gives you **plausible-looking values**, not production distributions.

This:

```python
fake.name()
```

does not mean your generated customer population has realistic:

- geographic concentration;
- customer segments;
- purchase behavior;
- seasonality;
- order frequency;
- missingness;
- correlation.

Use Faker as one component of a generator, not as a substitute for domain modeling.

---

# 6. A Deterministic Test-Data Factory

Build generators as normal production-quality Python code.

```python
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Customer:
    customer_id: int
    age: int


def generate_customers(
    n: int,
    seed: int = 42,
) -> list[Customer]:
    if n < 0:
        raise ValueError("n must be non-negative")

    rng = np.random.default_rng(seed)

    return [
        Customer(
            customer_id=i + 1,
            age=int(rng.integers(18, 90)),
        )
        for i in range(n)
    ]
```

Properties of a good generator:

- explicit row count;
- explicit seed;
- explicit schema;
- deterministic output;
- predictable configuration;
- testable behavior;
- version-controlled implementation.

Test it:

```python
def test_generator_is_deterministic():
    first = generate_customers(100, seed=42)
    second = generate_customers(100, seed=42)

    assert first == second
```

---

# 7. Generator Versioning

A seed alone is not complete reproducibility.

Suppose:

```text
generator v1 + seed 42
```

produces dataset A.

Then the generator is changed:

```text
generator v2 + seed 42
```

The output may become dataset B.

Therefore:

```text
same seed
≠
same dataset
```

unless the generator implementation and configuration are also unchanged.

A useful reproducibility identity is:

```text
Generator version
+
Seed
+
Configuration
+
Schema version
=
Reproducible dataset definition
```

A manifest might record:

```yaml
generator:
  name: ecommerce_test_data
  version: "2.1.0"

seed: 42

config:
  customer_count: 10000
  order_count: 50000

schema_version: 5
```

---

# 8. Realistic Distributions

A dataset can contain realistic names and still be unrealistic.

Production data often contains:

```text
common values
rare values
skew
heavy tails
seasonality
correlations
missingness
duplicates
late arrivals
```

A uniform distribution frequently produces a world that does not resemble the system you operate.

The right question is:

> What statistical and relational behaviors matter to this pipeline?

---

# 9. Skew

Suppose an e-commerce platform has:

```text
Most customers:
    1–5 orders

A small number:
    hundreds or thousands of orders
```

Uniformly assigning each customer the same number of orders misses the behavior.

One simple approach is to choose a heavy-tailed distribution.

```python
import numpy as np

rng = np.random.default_rng(42)

order_counts = rng.zipf(a=2.0, size=10_000)
order_counts = np.clip(order_counts, 1, 5_000)
```

The exact distribution should be chosen based on the behavior you need to model.

### Why skew matters

Skew can affect:

- partition sizes;
- join performance;
- aggregation memory;
- customer-level windows;
- API rate limits;
- downstream storage;
- distributed processing.

A performance test that uses perfectly uniform keys may hide the real bottleneck.

---

# 10. Seasonality

Data volume often changes with time.

Examples:

```text
weekday vs weekend
month-end
quarter-end
holiday periods
promotion periods
billing cycles
```

A simple generator can model higher activity on weekends:

```python
from datetime import date, timedelta
import numpy as np

rng = np.random.default_rng(42)

start = date(2026, 1, 1)

dates = [
    start + timedelta(days=int(i))
    for i in rng.integers(0, 90, size=1000)
]

weekend_multiplier = [
    2.0 if d.weekday() >= 5 else 1.0
    for d in dates
]
```

The exact model should reflect the test objective.

Seasonality is important when testing:

- date filtering;
- partitioning;
- daily aggregation;
- scheduling;
- capacity;
- month-end behavior;
- backfills.

---

# 11. Lateness

For event-driven pipelines, separate:

```text
event_time
ingestion_time
```

Example:

```python
from datetime import datetime, timedelta, timezone

event_time = datetime(
    2026,
    1,
    10,
    tzinfo=timezone.utc,
)

ingestion_time = event_time + timedelta(hours=8)
```

A realistic dataset should include:

```text
on-time
slightly late
very late
```

This allows testing of:

- watermark policies;
- late-event handling;
- backfills;
- event-time windows;
- deduplication;
- replay behavior.

---

# 12. Duplicates

Duplicates should be intentional.

Useful categories:

```text
exact duplicate row
same business key, different payload
same event replayed
same record ingested twice
```

For example:

```python
rows = [
    {"event_id": "e1", "amount": 10},
    {"event_id": "e2", "amount": 20},
    {"event_id": "e2", "amount": 20},
]
```

This lets you test:

```text
deduplication
idempotency
primary-key enforcement
replay handling
```

Do not accidentally remove duplicates from every generated dataset. Duplicates are often part of the production failure surface.

---

# 13. Nulls and Missingness

A naive generator might simply set:

```text
10% of values = NULL
```

That may be unrealistic.

Missingness can be:

```text
random
correlated
systematic
source-specific
time-dependent
```

For example:

```text
phone number:
    missing for customers who never supplied one

shipping address:
    missing only for digital products

customer_id:
    missing only in malformed source events
```

Test data should model the missingness mechanism that matters to the pipeline.

---

# 14. Bad Records

Good test-data systems can generate intentionally invalid data.

Examples:

```text
negative quantity
invalid email
invalid timestamp
unknown status
missing required key
invalid currency
unexpected Unicode
malformed JSON
```

Use separate strategies for:

```text
valid data
invalid data
boundary data
```

This makes the test intent explicit.

For example:

```python
VALID_STATUSES = ["pending", "paid", "cancelled"]
INVALID_STATUSES = ["UNKNOWN", "", "paid "]
```

A data-quality test can then deliberately inject invalid values.

---

# 15. Relational Consistency

Multi-table test data must preserve relationships.

Consider:

```text
customers
    |
customer_id
    |
orders
    |
order_id
    |
order_items
    |
product_id
    |
products
```

A generator that creates every table independently may produce:

```text
order.customer_id = 100
```

while no customer 100 exists.

That may be correct for an orphan-record test, but it is wrong for a normal valid dataset.

### Generation order

A reliable pattern is:

```text
customers
    ↓
products
    ↓
orders referencing customers
    ↓
order_items referencing orders/products
    ↓
payments referencing orders
```

Generate parent entities first, then dependent entities.

---

# 16. Related-Entity Generator

Example:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Customer:
    customer_id: int


@dataclass(frozen=True)
class Product:
    product_id: int


@dataclass(frozen=True)
class Order:
    order_id: int
    customer_id: int


@dataclass(frozen=True)
class OrderItem:
    order_id: int
    product_id: int
```

A simple relational generator:

```python
def generate_dataset(
    customer_count: int,
    product_count: int,
    order_count: int,
    seed: int = 42,
):
    rng = np.random.default_rng(seed)

    customers = [
        Customer(i)
        for i in range(1, customer_count + 1)
    ]

    products = [
        Product(i)
        for i in range(1, product_count + 1)
    ]

    orders = [
        Order(
            order_id=i,
            customer_id=int(
                rng.choice([c.customer_id for c in customers])
            ),
        )
        for i in range(1, order_count + 1)
    ]

    return customers, products, orders
```

The generator itself should be tested for:

```text
foreign-key validity
uniqueness
expected row counts
domain constraints
```

---

# 17. Intentionally Incorrect Relationships

Sometimes broken relationships are exactly what the test needs.

Examples:

```text
order → missing customer
order_item → missing product
payment → missing order
```

The generator should make defects deliberate.

Example:

```python
orphan_order = {
    "order_id": 999999,
    "customer_id": 999999,
}
```

Then test:

```text
Generate defect
    ↓
Run data-quality validation
    ↓
Expect validation failure
```

This is better than accidentally producing invalid data and wondering why another test failed.

---

# 18. Orphan Records

An orphan is a record whose referenced entity does not exist.

For example:

```text
orders.customer_id = 12345
```

but:

```text
customers.customer_id
```

contains no `12345`.

A useful orphan generator can select:

```text
valid keys
+
one or more intentionally invalid keys
```

Example:

```python
def add_orphan_order(orders, orphan_customer_id: int):
    return orders + [
        {
            "order_id": max(o["order_id"] for o in orders) + 1,
            "customer_id": orphan_customer_id,
        }
    ]
```

Make the orphan key deterministic so the failure is reproducible.

---

# 19. Sampling Fundamentals

Sampling means selecting a subset of a larger dataset.

It is useful when:

- production is too large;
- realistic relationships matter;
- full extraction is impractical;
- integration tests need representative records.

But:

> **Naive sampling can destroy relational integrity.**

---

# 20. Random Sampling

With pandas:

```python
sample = df.sample(
    n=1000,
    random_state=42,
)
```

or:

```python
sample = df.sample(
    frac=0.01,
    random_state=42,
)
```

Important considerations:

- sample size;
- reproducibility;
- representativeness;
- rare categories;
- relationship preservation.

A random 1% row sample from `orders` does not guarantee that the corresponding customers and order items are included.

---

# 21. Stratified Sampling

Stratified sampling intentionally preserves important groups.

Suppose a dataset contains:

```text
customer_segment
```

with:

```text
enterprise
business
consumer
```

A simple stratified approach can sample within each group.

```python
sample = (
    df.groupby("customer_segment", group_keys=False)
      .apply(
          lambda group: group.sample(
              n=min(len(group), 100),
              random_state=42,
          )
      )
)
```

The exact allocation should match the test objective.

Useful strata include:

- country;
- customer segment;
- event type;
- product category;
- status;
- source system.

### When stratification matters

If a rare category contains a production-critical defect, pure random sampling may exclude it.

Stratification gives that category an explicit representation.

---

# 22. Key-Consistent Hash-Based Sampling

For related data, a powerful approach is deterministic selection by a stable business key.

Conceptually:

```text
hash(customer_id) % 100 < 1
```

selects approximately 1% of customers.

Then:

```text
selected customers
        ↓
all related orders
        ↓
all related order_items
```

The exact hash function and threshold should be standardized for the organization.

### Why this is useful

The selection is:

- deterministic;
- repeatable;
- entity-based;
- relationship-friendly;
- easy to apply across tables.

---

# 23. Relationship-Preserving Sampling

Incorrect:

```text
sample customers independently
sample orders independently
sample order_items independently
```

This can produce:

```text
order references customer not in sample
order_item references order not in sample
```

Correct:

```text
select customer keys
        ↓
select all orders for those customers
        ↓
select all order_items for those orders
        ↓
select payments/events for those entities
```

### Example

```python
selected_customer_ids = {
    customer_id
    for customer_id in customers["customer_id"]
    if stable_hash(customer_id) % 100 < 1
}

sampled_customers = customers[
    customers["customer_id"].isin(selected_customer_ids)
]

sampled_orders = orders[
    orders["customer_id"].isin(selected_customer_ids)
]

sampled_items = order_items[
    order_items["order_id"].isin(sampled_orders["order_id"])
]
```

The result is a **connected subgraph** of the relational dataset.

---

# 24. Choosing Sample Size

There is no universal:

```text
"Use 1%"
```

rule.

A sample of 1% means something very different for:

```text
1 million rows
```

versus:

```text
10 billion rows
```

Choose size based on:

```text
test runtime
+
statistical representation
+
rare-category coverage
+
relationship depth
+
edge-case coverage
+
CI budget
+
memory
+
storage
```

For CI, the smallest dataset that reliably exercises the required behavior is usually preferable.

For performance testing, the dataset must be large enough to trigger the behavior being measured.

---

# 25. Masking and Pseudonymization

If real production data is ever used as the source of a test dataset, establish a strict boundary:

```text
controlled production environment
        ↓
safe extraction
        ↓
mask / pseudonymize
        ↓
validate
        ↓
release only approved test dataset
```

Do not move raw production-sensitive data into developer environments merely to make masking easier later.

---

# 26. Dropping Sensitive Columns

The safest sensitive value is often the value you never copy.

If a test does not need:

```text
email
phone
address
payment_details
```

drop them before the test dataset leaves the controlled source environment.

This is stronger than masking an unnecessary field.

---

# 27. Generalization

Generalization reduces precision.

Examples:

```text
age:
    37 → 35–39

location:
    exact address → region

timestamp:
    exact instant → date/hour bucket
```

The trade-off is:

```text
more privacy
    vs
less detail
```

Only preserve precision that the test actually needs.

---

# 28. Keyed Hashing

For deterministic pseudonymization of stable identifiers, a keyed construction such as HMAC is generally preferable to an ordinary unsalted hash for low-entropy identifiers.

Conceptually:

```text
HMAC(secret_key, customer_id)
```

Example:

```python
import hashlib
import hmac


def pseudonymize(
    value: str,
    secret_key: bytes,
) -> str:
    return hmac.new(
        secret_key,
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
```

Never hard-code a real secret.

Use a controlled secret-management mechanism in production workflows.

### Why not plain hashing?

For values such as:

```text
user@example.com
```

the input space may be guessable.

An attacker can compute hashes of candidate values and compare them.

A keyed construction makes that attack substantially harder without access to the key.

---

# 29. Referential Consistency After Masking

Masking must preserve relationships.

Suppose:

```text
customer_id = C123
```

becomes:

```text
HMAC(C123) = abc...
```

Then every table containing the same logical customer reference must use the same transformation.

```text
customers
   customer_id → pseudonymize()

orders
   customer_id → pseudonymize()

payments
   customer_id → pseudonymize()
```

Do not generate a new random pseudonym independently in each table.

Otherwise:

```text
customers.customer_id = A
orders.customer_id = B
```

and the relationship is broken.

---

# 30. Format-Preserving Fake Values

Some systems validate input formats.

Examples:

```text
customer ID
phone number
email address
```

A test may need the value to remain structurally valid.

For example:

```text
C123456
```

can become:

```text
C938271
```

while retaining the format.

For email:

```text
real.user@example.com
```

can become:

```text
synthetic-id-123@example.test
```

Use a reserved test domain such as `.test` for examples rather than generating credentials or messages that could accidentally reach real systems.

Format preservation is useful, but it must not preserve unnecessary sensitive detail.

---

# 31. Per-Column Masking Rules

Different columns require different transformations.

| Column | Classification | Example transformation |
|---|---|---|
| `customer_id` | identifier | keyed hash |
| `email` | personal data | deterministic fake |
| `phone` | personal data | format-preserving fake |
| `age` | quasi-identifier | age band |
| `address` | personal data | drop/generalize |
| `revenue` | business-sensitive | preserve only if needed; otherwise transform |
| `event_time` | temporal | shift/generalize if exact time is unnecessary |

The masking policy should be documented, version-controlled, and tested.

---

# 32. Privacy Limitations of Masking

Masking does not automatically mean anonymization.

Risks include:

```text
linkage attacks
rare combinations
quasi-identifiers
small populations
deterministic identifiers
external reference datasets
```

For example, masking a name does not necessarily protect a record if the combination:

```text
age
city
employer
exact timestamp
```

is unique enough to identify a person.

Therefore:

> Treat masking as a risk-reduction technique, not an automatic privacy guarantee.

Use data classification and approved organizational controls for actual production workflows.

---

# 33. Edge-Case Mining

Real production behavior can be extremely valuable without copying an entire production dataset.

A safe workflow is:

```text
Controlled/anonymized source
        ↓
identify unusual patterns
        ↓
remove / transform sensitive values
        ↓
extract minimal example
        ↓
validate safety
        ↓
store as fixture
        ↓
add regression test
```

The goal is to preserve the **behavior**, not the original person's record.

---

# 34. What Is an Edge Case?

Useful examples include:

```text
extreme amount
rare status
duplicate business key
missing required field
very late event
unusual Unicode
month-end record
DST boundary
very large customer
orphan relationship
```

Edge cases can be identified with:

- quantiles;
- frequency counts;
- null-rate analysis;
- duplicate detection;
- date-boundary queries;
- referential-integrity checks;
- domain-specific anomaly rules.

---

# 35. Edge-Case Mining Example

Suppose an anonymized summary identifies:

```text
orders with:
    revenue above p99.99
    ingestion delay > 7 days
    duplicate order IDs
    null customer IDs
```

Do not copy the entire source partition.

Instead:

```text
find one representative case
        ↓
strip sensitive fields
        ↓
replace identifiers
        ↓
preserve relevant relationships
        ↓
store minimal fixture
```

A durable fixture might contain:

```python
{
    "order_id": "edge-001",
    "customer_id": "customer-001",
    "amount": "999999.99",
    "event_time": "2026-01-31T23:59:59Z",
}
```

The fixture is valuable because it encodes the failure shape, not because it preserves the original record.

---

# 36. Distribution-Aware Synthetic Generation

Synthetic generation can be informed by production summary statistics.

Useful summaries include:

```text
order amount distribution
customer order frequency
event frequency
null rates
status distribution
category frequencies
time-of-day distribution
day-of-week distribution
```

Conceptually:

```text
Observed safe summary
        ↓
Approximate distribution
        ↓
Synthetic generator
        ↓
Validation
        ↓
Test dataset
```

This provides realism without copying individual production rows.

---

# 37. Validate Synthetic Realism

Synthetic data must itself be tested.

Compare safe summaries such as:

```text
status proportions
null rates
quantiles
cardinality
distribution shape
daily volume
orders/customer
```

Conceptually:

```text
synthetic distribution
        vs
approved production summary
```

Do not require exact equality unless that is the actual requirement.

The purpose is to determine whether the synthetic dataset exercises the intended behavior.

---

# 38. Limitations of Synthetic Data

Synthetic data can be:

- statistically unrealistic;
- too clean;
- missing hidden correlations;
- missing rare interactions;
- incorrectly distributed;
- generated from incorrect assumptions.

For example, a generator may correctly model:

```text
order amount
```

but completely miss the correlation:

```text
customer segment ↔ order frequency
```

That can cause misleading test results.

Synthetic data is not automatically realistic merely because it looks plausible.

---

# 39. Synthetic Data Is Not Automatically Private

Synthetic data can still create privacy risks if the generator:

- reproduces source records;
- memorizes sensitive examples;
- emits overly specific combinations;
- accidentally includes real values;
- is built from sensitive data without appropriate controls.

A generated record that exactly matches a real person is not made safe merely by calling the generator “synthetic.”

The engineering requirement remains:

```text
Do not expose sensitive source records.
```

---

# 40. Dataset Tiers

Use different dataset sizes for different testing purposes.

## Tiny Dataset

Purpose:

- unit tests;
- fast PR feedback;
- edge-case tests;
- debugging.

Typical scale:

```text
a handful to tens of rows
```

The exact size is project-specific.

## Small Dataset

Purpose:

- integration tests;
- local development;
- realistic relationships;
- database behavior.

Often:

```text
hundreds to thousands of rows
```

Again, choose based on actual test cost.

## Large Dataset

Purpose:

- performance testing;
- distributed processing;
- partition behavior;
- scaling;
- skew;
- realistic storage layouts.

The exact size should be large enough to trigger the behavior being tested.

### Principle

```text
Unit test:
    smallest useful dataset

Integration test:
    realistic connected dataset

Performance test:
    sufficiently large workload
```

---

# 41. Dataset Purpose Documentation

Every durable test dataset should document at least:

```text
Dataset name
Purpose
Schema version
Generator version
Seed
Configuration
Row count
Expected edge cases
Source type
Sensitivity classification
Dataset version
Owner
```

This turns an unexplained Parquet file into a reproducible engineering artifact.

---

# 42. Dataset Versioning

Treat test data as versioned code-adjacent infrastructure.

Example:

```text
orders-test-data/
├── v1/
├── v2/
└── v3/
```

A change in the dataset can change test behavior.

Therefore, dataset versions should be explicit.

For example:

```text
dataset_version = 3
generator_version = 2.1.0
schema_version = 5
seed = 42
```

When a test starts failing after a data change, you should be able to determine whether:

```text
code changed
data changed
schema changed
generator changed
```

---

# 43. Object Storage and Parquet

Large test datasets should not be committed to Git.

Object storage is a natural place for larger datasets.

A local MinIO layout might look like:

```text
test-data/
├── orders/
├── customers/
├── order_items/
└── manifests/
```

Parquet is useful because it supports:

- typed columns;
- compression;
- efficient scans;
- partitioned datasets;
- interoperability across engines.

A typical publication workflow is:

```text
generate
   ↓
validate
   ↓
write Parquet
   ↓
upload to object storage
   ↓
write manifest
```

---

# 44. Dataset Manifest

A manifest makes a dataset discoverable and reproducible.

Example:

```yaml
dataset: orders-small
version: 3

generator:
  name: ecommerce_test_data
  version: 2.1.0

seed: 42

configuration:
  customer_count: 1000
  order_count: 10000
  include_late_events: true
  duplicate_rate: 0.02

format: parquet
schema_version: 5
row_count: 10000
purpose: integration-tests
sensitivity: synthetic
```

A manifest should describe **what was generated**, not merely where the file lives.

---

# 45. Reproducibility Chain

A robust test dataset can be recreated from:

```text
Generator version
+
Seed
+
Configuration
+
Schema version
+
Dataset version
```

This gives a reproducibility chain:

```text
CI failure
    ↓
dataset manifest
    ↓
generator version
    ↓
seed/configuration
    ↓
regenerate dataset
    ↓
reproduce failure locally
```

If the generator has external dependencies whose behavior can change, pin those dependencies as part of the repository environment.

---

# 46. dbt Seeds

Small stable datasets can be represented as CSV seeds.

Conceptually:

```text
CSV
 ↓
dbt seed
 ↓
development/test database
```

Good use cases:

- small reference tables;
- stable lookup data;
- deterministic examples;
- tiny fixtures.

Do not use dbt seeds as the default transport for enormous performance datasets.

---

# 47. dbt Unit-Test Fixtures

Synthetic data can also support dbt unit-test inputs.

The important principles are:

```text
small
deterministic
explicit
edge-case focused
```

A useful fixture can represent:

```text
null input
duplicate input
boundary timestamp
invalid status
```

The goal is to make the model behavior explicit, not to create a miniature production warehouse inside a unit test.

---

# 48. Non-Production Environments

A test-data lifecycle may look like:

```text
Test Data Factory
       ↓
Developer
       ↓
PR CI
       ↓
Integration environment
       ↓
Staging
```

At every boundary, apply the correct data classification.

Do not let:

```text
"staging is internal"
```

become an excuse to copy raw production-sensitive data.

---

# 49. Test-Data Validation

A broken generator can invalidate an entire test suite.

Validate generated datasets before publishing them.

Useful checks:

```text
schema
row count
uniqueness
referential integrity
null expectations
distribution
duplicate rate
date ranges
edge-case presence
```

Example:

```python
def validate_orders(df):
    assert {"order_id", "customer_id"} <= set(df.columns)
    assert df["order_id"].notna().all()
    assert df["order_id"].is_unique
```

For relational data:

```python
def validate_order_customers(orders, customers):
    known = set(customers["customer_id"])

    assert set(orders["customer_id"]) <= known
```

If the dataset is intentionally invalid, the validator should be parameterized for the expected defect rather than silently accepting arbitrary corruption.

---

# 50. Security Rules for Test Data

Never put raw production PII into:

- Git;
- developer laptops;
- CI artifacts;
- Docker images;
- test logs;
- test fixtures;
- public object storage.

Prefer:

- synthetic values;
- safely masked samples;
- controlled access;
- short-lived credentials;
- approved object storage;
- explicit dataset classification.

Also consider indirect leakage:

```text
exception messages
debug logs
failed-test snapshots
SQL output
notebook outputs
temporary files
CI caches
```

Sensitive data can escape through observability and tooling even when the primary dataset is protected.

---

# 51. Common Test-Data Mistakes

## Mistake 1 — Copying production directly

**Danger:** creates unnecessary security and governance exposure.

**Better:** synthetic data or safely transformed minimal samples.

## Mistake 2 — Unseeded random generation

**Danger:** failures become difficult to reproduce.

**Better:** explicit seeds and generator metadata.

## Mistake 3 — Uniform-only data

**Danger:** misses skew and heavy tails.

**Better:** model important distributions.

## Mistake 4 — Independent foreign keys

**Danger:** valid datasets become accidentally invalid.

**Better:** generate parent entities first.

## Mistake 5 — Sampling tables independently

**Danger:** destroys relationships.

**Better:** select root entities and traverse their relationships.

## Mistake 6 — Plain hashing of low-entropy identifiers

**Danger:** dictionary attacks may recover original values.

**Better:** use an approved keyed pseudonymization design.

## Mistake 7 — Sensitive values in logs

**Danger:** masking the dataset is useless if failures print the raw records.

**Better:** redact test output.

## Mistake 8 — Raw samples in Git

**Danger:** difficult to revoke and easy to distribute.

**Better:** approved storage and controlled fixtures.

## Mistake 9 — Assuming Faker equals realism

**Danger:** strings look realistic while distributions are wrong.

**Better:** model domain behavior explicitly.

## Mistake 10 — No edge cases

**Danger:** the suite only proves happy paths.

**Better:** deliberately include nulls, duplicates, late records, malformed values, and boundaries.

## Mistake 11 — No versioning

**Danger:** changes in test behavior become difficult to explain.

**Better:** version datasets and generators.

## Mistake 12 — No manifest

**Danger:** the dataset becomes an unexplained artifact.

**Better:** record seed, generator, schema, purpose, and version.

## Mistake 13 — No generator validation

**Danger:** tests may be testing the wrong data.

**Better:** validate the generated dataset before publication.

## Mistake 14 — Excessively large CI datasets

**Danger:** developers stop running tests because feedback becomes slow.

**Better:** use the smallest dataset appropriate for the test layer.

---

# 52. Production Test-Data Architecture

A production-style design can look like:

```text
                    Test Data Factory
                           |
             +-------------+-------------+
             |             |             |
         Synthetic      Safe Sample    Edge Cases
             |             |             |
             +-------------+-------------+
                           |
                    Validation Layer
                           |
                    Version + Manifest
                           |
              +------------+------------+
              |            |            |
            Local         CI/CD     Integration
              |            |            |
              +------------+------------+
                           |
                      Test Suites
```

### Responsibilities

**Test Data Factory**

Generates deterministic datasets.

**Safe Sample**

Provides realistic patterns without uncontrolled raw production copies.

**Edge Cases**

Preserves important rare failure shapes.

**Validation Layer**

Ensures the test data itself satisfies its declared contract.

**Version + Manifest**

Makes the dataset reproducible.

**Storage**

Provides controlled distribution.

**Test Suites**

Consume the correct dataset tier for the test objective.

---

# 53. Hands-On Project — Production-Grade Test Data Factory

## Scenario

An e-commerce platform contains:

```text
customers
products
orders
order_items
payments
events
```

Build a reusable test-data package.

## Required datasets

Generate:

1. tiny dataset;
2. small dataset;
3. large dataset;
4. valid relational dataset;
5. duplicate-heavy dataset;
6. null-heavy dataset;
7. orphan-record dataset;
8. late-event dataset;
9. skewed-customer dataset;
10. seasonal dataset;
11. bad-record dataset.

## Required engineering capabilities

The factory must support:

```text
deterministic output
generator version
seed
configuration
schema version
validation
manifest
Parquet output
MinIO publication
```

## Suggested repository

```text
test-data-factory/
├── pyproject.toml
├── src/
│   └── test_data/
│       ├── customers.py
│       ├── products.py
│       ├── orders.py
│       ├── events.py
│       ├── masking.py
│       ├── sampling.py
│       ├── validation.py
│       └── manifest.py
├── tests/
│   ├── test_generators.py
│   ├── test_relationships.py
│   ├── test_masking.py
│   └── test_sampling.py
└── README.md
```

## Acceptance criteria

The learner should be able to run:

```bash
uv run python -m test_data.generate \
    --dataset small \
    --seed 42 \
    --version 1
```

and obtain:

```text
Parquet dataset
+
manifest
+
validation report
```

The same command and same versioned generator must reproduce the same logical dataset.

---

# 54. Sampling Project — Safe 1% Customer-Centric Dataset

## Scenario

You have a very large:

```text
customers
orders
order_items
```

dataset.

Create a deterministic approximately 1% test dataset.

## Required process

```text
Select customers deterministically
        ↓
Select all related orders
        ↓
Select all related order_items
        ↓
Mask sensitive values
        ↓
Validate referential integrity
        ↓
Write Parquet
        ↓
Create manifest
```

## Root selection

Use a stable customer key.

Conceptually:

```python
def selected(customer_id: str) -> bool:
    return stable_hash(customer_id) % 100 < 1
```

The exact hash implementation should be standardized and stable.

## Validation

Verify:

```text
every sampled order has a sampled customer
every sampled order_item has a sampled order
no raw sensitive fields remain
the selection is reproducible
```

This is substantially safer than:

```text
sample 1% of each table independently
```

---

# 55. Masking Project

Input:

```text
customer_id
name
email
phone
address
age
```

Design a safe test dataset using:

```text
customer_id → keyed pseudonym
name        → deterministic synthetic value
email       → deterministic test-domain address
phone       → format-preserving synthetic value
address     → drop/generalize
age         → age band
```

Verify:

```text
same input → same masked value
same customer → same pseudonym across tables
no raw sensitive values remain
output format remains valid
```

Do not store or print the real key used for production pseudonymization in the test repository.

---

# 56. Edge-Case Mining Project

Given an approved anonymized or summarized dataset, identify:

```text
rare statuses
extreme amounts
late records
duplicate keys
null-heavy records
orphan relationships
unusual timestamps
```

For each selected case:

```text
identify pattern
    ↓
remove sensitive content
    ↓
reduce to minimum example
    ↓
assign synthetic identifiers
    ↓
store deterministic fixture
    ↓
add regression test
```

The final fixture should be small enough to understand during code review.

---

# 57. Failure-Injection Lab

Create deliberately defective datasets.

### Failure 1 — Duplicate business keys

```text
order_id = 100
order_id = 100
```

Expected behavior:

```text
deduplication or validation failure
```

### Failure 2 — Orphan foreign key

```text
order.customer_id = missing_customer
```

Expected behavior:

```text
referential-integrity failure
```

### Failure 3 — Unexpected null

```text
required customer_id = NULL
```

Expected behavior:

```text
schema/data-quality failure
```

### Failure 4 — Invalid timestamp

```text
event_time = malformed value
```

Expected behavior:

```text
parsing/validation failure
```

### Failure 5 — Extreme numeric value

```text
amount = boundary-breaking value
```

Expected behavior:

```text
overflow/range/validation failure
```

### Failure 6 — Late event

```text
event_time << ingestion_time
```

Expected behavior:

```text
late-data policy is exercised
```

### Failure 7 — Invalid status

```text
status = "UNKNOWN"
```

Expected behavior:

```text
domain validation failure
```

### Failure 8 — Broken relationship

```text
order_item.order_id
```

references an order that is absent.

For every failure:

```text
Generate defect
    ↓
Run pipeline/test
    ↓
Observe failure
    ↓
Diagnose
    ↓
Fix implementation or expected contract
    ↓
Preserve defect as durable test data
```

---

# 58. Checkpoint

You should now be able to explain and demonstrate:

- why raw production data should not be copied by default;
- synthetic vs sampled data;
- seeded NumPy;
- Faker;
- deterministic generators;
- generator versioning;
- reproducibility;
- realistic distributions;
- skew;
- seasonality;
- lateness;
- duplicates;
- nulls;
- bad records;
- relational consistency;
- intentional defects;
- orphan records;
- random sampling;
- stratified sampling;
- key-consistent hash sampling;
- relationship-preserving sampling;
- sample-size reasoning;
- dropping sensitive columns;
- generalization;
- keyed hashing;
- format-preserving values;
- per-column masking;
- referential consistency after masking;
- privacy limitations;
- edge-case mining;
- statistical generation;
- limitations of synthetic data;
- dataset tiers;
- manifests;
- versioning;
- object storage;
- dbt seeds;
- dbt unit-test fixtures;
- non-production environment safety;
- test-data validation.

### Coding checkpoint

Build a small dataset containing:

```text
customers
orders
order_items
```

Then:

1. generate it deterministically;
2. introduce one duplicate;
3. introduce one orphan;
4. introduce one null;
5. sample customers deterministically;
6. preserve all related orders;
7. mask identifiers;
8. validate referential integrity;
9. write Parquet;
10. create a manifest;
11. regenerate from the same metadata;
12. prove that the logical dataset is reproducible.

---

# 59. Production Interview Preparation

## 1. Why should you avoid copying production data?

Because it introduces unnecessary security/governance risk, is often much larger than required, changes over time, and may still fail to cover rare edge cases.

## 2. Synthetic vs sampled data?

Synthetic data is generated specifically for testing. Sampled data is selected from a real dataset and usually requires masking or pseudonymization.

## 3. Why seed NumPy?

To make pseudo-random generation reproducible.

## 4. Why is a seed alone insufficient?

Changing generator code or configuration can change the dataset even with the same seed.

## 5. Why is Faker insufficient for realism?

It generates plausible field values but does not automatically model business distributions and relationships.

## 6. What is stratified sampling?

Sampling within important groups so rare or critical categories remain represented.

## 7. Why is hash-based sampling useful?

It deterministically selects stable entities and makes it easier to preserve all related records.

## 8. Why can independent table sampling be dangerous?

It can break foreign-key relationships and produce an incoherent test dataset.

## 9. What is pseudonymization?

Replacing an identifier with a consistent substitute while retaining controlled linkage behavior.

## 10. Why use a keyed hash instead of a plain hash for low-entropy identifiers?

A keyed construction prevents an attacker without the key from cheaply computing candidate mappings.

## 11. Does masking guarantee anonymity?

No. Linkage and quasi-identifier risks can remain.

## 12. What is edge-case mining?

Finding unusual but important production behavior and converting it into a minimal safe fixture.

## 13. What are dataset tiers?

Different dataset sizes optimized for different test purposes, such as unit, integration, and performance testing.

## 14. Why use manifests?

To record how a dataset was produced and make it reproducible.

## 15. What should a manifest contain?

At minimum: dataset/version, generator/version, seed, configuration, schema version, format, size, purpose, and sensitivity classification.

## 16. When should dbt seeds be used?

For small, stable, deterministic datasets such as reference tables and fixtures.

## 17. What makes test data production-grade?

Safety, determinism, realistic behavior, relational integrity, validation, versioning, traceability, appropriate scale, and controlled distribution.


# 60. Final Assessment

## Scenario

A company has a 5-billion-row production order dataset containing sensitive customer information.

The Data Engineering team needs realistic datasets for:

```text
unit tests
integration tests
CI
performance testing
staging
```

without copying raw production PII.

Design and implement a production-grade test-data strategy.

## Required architecture

```text
Synthetic data strategy
        +
Safe sampling strategy
        +
Key-consistent relationships
        +
Masking strategy
        +
Edge-case strategy
        +
Dataset tiers
        +
Versioning
        +
Manifest
        +
Object storage
        +
CI integration
        +
Security controls
```

## Required implementation

### Part 1 — Synthetic generator

Implement:

```text
customers
products
orders
order_items
```

with:

- deterministic seed;
- generator version;
- schema version;
- realistic status distribution;
- duplicate capability;
- null capability;
- late-event capability;
- skewed customers.

### Part 2 — Safe sampling

Implement deterministic customer selection.

Then retain:

```text
selected customers
+
their orders
+
their order_items
```

### Part 3 — Masking

Apply:

```text
keyed pseudonymization
+
deterministic test emails
+
format-preserving test phone numbers
+
generalized age
+
removed/generalized address
```

### Part 4 — Validation

Validate:

```text
schema
row counts
uniqueness
referential integrity
expected null rates
distribution
absence of raw sensitive fields
```

### Part 5 — Manifest

Create metadata containing:

```text
dataset version
generator version
seed
configuration
schema version
row count
format
purpose
sensitivity
```

### Part 6 — Publication

Write the dataset as Parquet and publish it to a controlled object-storage location such as MinIO for local/integration use.

### Part 7 — CI strategy

Explain which datasets run:

```text
every PR
merge CI
scheduled CI
nightly
performance environment
```

and why.

The assessment must include actual implementation, not merely a written architecture diagram.

---

# 61. Final Self-Review Checklist

```text
[ ] Why production data should not be copied
[ ] Privacy concerns
[ ] Legal/compliance concerns
[ ] Dataset size
[ ] Production instability
[ ] Missing edge cases
[ ] Synthetic vs sampled data
[ ] Seeded NumPy generation
[ ] Faker
[ ] Deterministic generators
[ ] Generator versioning
[ ] Reproducibility
[ ] Realistic distributions
[ ] Skew
[ ] Seasonality
[ ] Lateness
[ ] Duplicates
[ ] Nulls
[ ] Bad records
[ ] Relational consistency
[ ] Intentional defects
[ ] Orphan records
[ ] Random sampling
[ ] Stratified sampling
[ ] Hash-based sampling
[ ] Relationship-preserving sampling
[ ] Sample-size reasoning
[ ] Dropping sensitive columns
[ ] Generalization
[ ] Keyed hashing
[ ] Format-preserving values
[ ] Per-column masking rules
[ ] Referential consistency after masking
[ ] Privacy limitations
[ ] Edge-case mining
[ ] Statistical generation
[ ] Synthetic-data limitations
[ ] Dataset tiers
[ ] Tiny dataset
[ ] Small dataset
[ ] Large dataset
[ ] Dataset manifests
[ ] Dataset versioning
[ ] Object storage
[ ] dbt seeds
[ ] dbt unit-test fixtures
[ ] Non-production environments
[ ] Security controls
[ ] Test-data validation
[ ] Hands-on project
[ ] Sampling project
[ ] Masking project
[ ] Edge-case mining project
[ ] Failure-injection lab
[ ] Checkpoint
[ ] Interview questions
[ ] Final assessment
```

---

# 62. Production Quality Gate

Before treating the module as complete, verify:

## Technical correctness

Python, NumPy, Faker, sampling, hashing, Parquet, MinIO, and dbt examples must be consistent with the intended tooling.

## Roadmap alignment

All Topic 05 concepts must be represented.

## Progressive learning

The learner should move through:

```text
Beginner
→ Intermediate
→ Advanced
→ Production
```

## Realism

The learner understands that realistic data requires:

```text
Distributions
+
Relationships
+
Temporal behavior
+
Missingness
+
Defects
+
Edge cases
```

not merely realistic-looking names and emails.

## Security

The learner understands that test-data pipelines must prevent raw production-sensitive data from reaching unsafe environments.

## Reproducibility

The learner can reproduce a dataset using:

```text
Generator version
+
Seed
+
Configuration
+
Schema version
+
Dataset version
```

## Sampling

The learner understands why relationship-preserving deterministic sampling is necessary.

## Production readiness

The learner can design dataset tiers and safely integrate them into CI/CD and integration environments.

---

# 63. Connection to Module 2.19

The testing layers now fit together:

```text
01 Fixture-based transformation tests
        ↓
02 DataFrame equality
        ↓
03 Integration tests
        ↓
04 Property-based testing
        ↓
05 Synthetic and sampled test data
        ↓
06 Schema / contract regression
        ↓
07 End-to-end smoke tests
```

Topic 05 supplies safe, realistic, reproducible inputs to those testing layers.

Its role is not merely:

```text
"make some fake rows"
```

It is:

```text
design the data conditions
under which the system can be
meaningfully tested
```

That includes:

```text
normal behavior
+
realistic distributions
+
relationships
+
missingness
+
duplicates
+
late records
+
invalid records
+
rare edge cases
+
appropriate scale
```

---

# 64. Final Engineering Principles

### Principle 1

> **The safest production record is the one you never copy.**

### Principle 2

> **Test data must be deterministic enough to reproduce failures.**

### Principle 3

> **Realism is about distributions and relationships, not just realistic-looking strings.**

### Principle 4

> **Sampling independently across related tables can destroy referential integrity.**

### Principle 5

> **A seed without generator/version metadata is not complete reproducibility.**

### Principle 6

> **Masking is not automatically anonymization.**

### Principle 7

> **Synthetic data must itself be validated.**

### Principle 8

> **Rare production edge cases are valuable, but should be converted into minimal safe fixtures.**

### Principle 9

> **Different test layers need different dataset sizes.**

### Principle 10

> **Test-data management is part of production-grade testing architecture.**

---

# 65. What Not to Teach Yourself to Do

Never make these the default:

```text
copy production database to laptop
```

```text
store raw production samples in Git
```

```text
hash emails with a plain hash and call them anonymous
```

```text
sample every table independently
```

```text
generate only uniform random data
```

```text
use unseeded random generation
```

```text
assume Faker output represents production distributions
```

```text
assume synthetic data is automatically realistic
```

```text
assume masking removes every privacy risk
```

A production-grade test-data system is deliberately engineered.

---

# 66. Final Engineering Mental Model

The entire module can be summarized as:

```text
Testing requirement
       ↓
Choose synthetic / sampled / edge-case approach
       ↓
Define data contract
       ↓
Generate or safely extract
       ↓
Preserve relationships
       ↓
Model distributions
       ↓
Inject controlled defects
       ↓
Validate dataset
       ↓
Version dataset + generator
       ↓
Write manifest
       ↓
Publish safely
       ↓
Consume from correct test tier
       ↓
Reproduce failures deterministically
```

The goal is not to make test data look real.

The goal is to make test data **behave like the conditions that matter**, while remaining:

```text
safe
deterministic
relationally coherent
versioned
validated
reproducible
appropriate in size
```

That is the foundation of production-grade test-data engineering.
