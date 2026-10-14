# Pydantic Models, Validators, and Serialization

> **Module:** 2.11 — Data Validation, Contracts, and Quality  
> **Topic:** 02 — Pydantic: Models, Validators, and Serialization  
> **Python:** 3.12+  
> **Pydantic:** v2  
> **Primary focus:** Production-grade record validation at data-ingestion boundaries

---

## Learning Objective

By the end of this chapter, you should be able to design a production-grade Pydantic validation boundary for APIs, webhooks, SFTP records, JSON/JSONL inputs, and event payloads.

You will learn to:

- treat external records as untrusted input;
- define typed validation models with `BaseModel`;
- distinguish required, optional, and defaulted fields;
- validate dictionaries and JSON;
- interpret structured `ValidationError` output;
- apply field constraints with `Field` and `Annotated`;
- constrain values with `Literal` and `Enum`;
- make deliberate decisions about lax coercion versus strict validation;
- model monetary values with `Decimal`;
- validate timezone-aware timestamps;
- validate UUIDs, emails, and URLs;
- build nested models and lists of models;
- write field and model validators;
- perform cross-field validation;
- configure handling of unexpected fields;
- serialize validated data safely;
- use aliases between external and internal naming conventions;
- exclude sensitive fields from serialized output;
- model heterogeneous events with discriminated unions;
- use `TypeAdapter` for non-model types and bulk validation;
- validate large JSON payloads while considering memory;
- collect per-record errors without losing traceability;
- benchmark validation instead of guessing;
- understand when Pydantic is the wrong validation layer;
- generate JSON Schema;
- separate external payload, domain, and database models;
- understand ORM/database-model reuse caveats;
- design production validation boundaries.

The governing idea is:

```text
External Data
     |
     v
Untrusted Payload
     |
     v
Validation Boundary
     |
     v
Pydantic Model
     |
     +----------------------+
     |                      |
     v                      v
Valid Record           Invalid Record
     |                      |
     v                      v
Internal Pipeline       Structured Error
                            |
                            v
                        Quarantine /
                        Failure Handling
```

Pydantic is therefore not being taught here as merely a collection of Python decorators. It is being taught as an engineering mechanism for establishing a trustworthy boundary between untrusted external data and the internal pipeline.

---

# 1. Why Record Validation Matters

Data engineering systems constantly receive data from systems that you do not fully control.

Examples include:

- REST APIs;
- webhooks;
- Kafka or other event streams;
- SFTP files;
- JSON files;
- JSON Lines files;
- partner integrations;
- SaaS exports;
- configuration payloads;
- external microservices.

A source may claim that it sends a particular schema. That does not mean every record actually conforms to it.

Consider:

```json
{
  "customer_id": "123",
  "email": "not-an-email",
  "country": "US",
  "created_at": "yesterday"
}
```

There are several potential problems:

- `customer_id` may be expected to be an integer or UUID rather than a string;
- the email is malformed;
- the timestamp is not a valid timestamp;
- the source may have violated its documented contract.

If this record is accepted immediately and passed through several transformations, the defect can become harder to locate.

A better boundary is:

```text
External source
      |
      v
Untrusted data
      |
      v
Validation boundary
      |
      +---- invalid ----> structured error / quarantine
      |
      v
Trusted internal representation
      |
      v
Transformation / storage / analytics
```

## 1.1 Validation should happen close to the source boundary

A useful principle is:

> Validate an external record as early as practical, while the source context is still available.

Suppose a malformed record travels through:

```text
API
 |
 v
raw landing
 |
 v
Python transformation
 |
 v
DataFrame
 |
 v
warehouse
 |
 v
dashboard
```

A dashboard failure is far away from the actual defect.

If validation occurs at the boundary:

```text
API
 |
 v
Pydantic validation
 |
 +---- invalid --> record error
 |
 v
valid record
 |
 v
pipeline
```

the defect is localized.

This does not mean every quality rule belongs in Pydantic. It means record-level structural and semantic validation should happen at an appropriate record boundary.

---

# 2. Where Pydantic Fits in a Data Pipeline

A common ingestion architecture looks like:

```text
API / Webhook / File / Event
             |
             v
        Raw Payload
             |
             v
       Pydantic Model
             |
             v
      Validated Record
             |
             v
       Transformation
             |
             v
       DataFrame / Table
             |
             v
       Warehouse / Lake
```

Pydantic is particularly useful for:

- individual records;
- API responses;
- webhook payloads;
- event messages;
- configuration objects;
- small-to-moderate batches;
- source-boundary validation.

Later layers need different tools.

A simplified boundary model is:

```text
Individual record
        |
        v
     Pydantic

DataFrame
        |
        v
      Pandera

Table / dataset
        |
        v
   GX / Soda / SQL

Producer agreement
        |
        v
 Data contract
```

These layers are complementary.

Do not use Pydantic as a replacement for every other form of data quality validation.

---

# 3. The Pydantic Mental Model

Think about Pydantic as a pipeline:

```text
Input
  |
  v
Parse
  |
  v
Validate
  |
  v
Possibly coerce
  |
  v
Create typed model
  |
  v
Serialize
```

A Pydantic model provides several related capabilities:

1. **Model definition**  
   You describe the expected structure using Python types.

2. **Parsing**  
   External representations such as dictionaries and JSON are converted into Python objects.

3. **Validation**  
   Values are checked against the declared schema and validation rules.

4. **Coercion**  
   Depending on configuration and input type, Pydantic may convert compatible values.

5. **Normalized representation**  
   A successful model instance gives downstream code a known structure.

6. **Serialization**  
   A validated model can be converted back into dictionaries or JSON.

7. **Schema generation**  
   Pydantic can expose the model as JSON Schema.

The key distinction is:

> A Pydantic model is not simply a class used for storing data. It defines a structured validation boundary.

---

# 4. Installing and Running Pydantic v2

The roadmap uses Python 3.12+ and Pydantic v2.

With `uv`:

```bash
uv init quality_lab
cd quality_lab
uv add pydantic
```

For email validation, Pydantic's email type uses an additional dependency:

```bash
uv add "pydantic[email]"
```

If you use pytest:

```bash
uv add --dev pytest
```

Check the installed version:

```bash
python -c "import pydantic; print(pydantic.__version__)"
```

The examples in this chapter use Pydantic v2 APIs.

Important v2 APIs include:

- `model_validate`;
- `model_validate_json`;
- `model_dump`;
- `model_dump_json`;
- `model_json_schema`;
- `field_validator`;
- `model_validator`;
- `ConfigDict`;
- `TypeAdapter`.

Older Pydantic v1 APIs such as `@validator` are not the primary teaching approach here.

---

# 5. `BaseModel` Fundamentals

Start with the smallest useful model:

```python
from pydantic import BaseModel


class Customer(BaseModel):
    customer_id: int
    email: str
    country: str
```

The model declares three fields:

- `customer_id` is expected to be an integer;
- `email` is expected to be a string;
- `country` is expected to be a string.

Create an instance:

```python
customer = Customer(
    customer_id=123,
    email="alice@example.com",
    country="US",
)

print(customer)
```

The model instance is now a structured Python object.

Access fields normally:

```python
print(customer.customer_id)
print(customer.email)
print(customer.country)
```

## 5.1 What `BaseModel` provides

`BaseModel` gives you a framework for:

- declaring fields;
- parsing input;
- validating values;
- collecting validation errors;
- serializing values;
- generating JSON Schema;
- configuring model behavior.

The important engineering benefit is that downstream code does not have to repeatedly ask:

```python
if "customer_id" in payload:
    ...
```

or:

```python
if isinstance(payload.get("customer_id"), int):
    ...
```

The boundary model centralizes those assumptions.

## 5.2 Invalid input

```python
from pydantic import BaseModel, ValidationError


class Customer(BaseModel):
    customer_id: int
    email: str
    country: str


try:
    Customer(
        customer_id="not-an-integer",
        email="alice@example.com",
        country="US",
    )
except ValidationError as exc:
    print(exc)
```

Pydantic raises `ValidationError` when the supplied data cannot satisfy the model.

---

# 6. Type Annotations and Field Definitions

Pydantic uses Python type annotations as part of its schema.

Examples:

```python
class Record(BaseModel):
    record_id: str
    quantity: int
    price: float
    active: bool
```

The annotations communicate both to humans and to Pydantic what the fields are intended to represent.

Common annotations include:

```python
str
int
float
bool
Decimal
UUID
datetime
list[str]
dict[str, str]
```

You can also compose types:

```python
str | None
```

or:

```python
list[int]
```

or:

```python
dict[str, object]
```

Type annotations are not merely documentation. In a Pydantic model they participate in validation and schema generation.

---

# 7. Required Fields, Optional Fields, and Defaults

This distinction is extremely important.

Consider:

```python
class Customer(BaseModel):
    customer_id: int
    email: str
    country: str = "US"
```

Here:

- `customer_id` is required;
- `email` is required;
- `country` has a default of `"US"`.

This works:

```python
customer = Customer(
    customer_id=123,
    email="alice@example.com",
)
```

The resulting country is:

```python
customer.country
# "US"
```

## 7.1 Nullable is not the same as optional

Consider:

```python
class Customer(BaseModel):
    email: str | None
```

The type says that `email` may contain a string or `None`.

It does not, by itself, mean the field should be omitted.

If the field should be optional and default to `None`, write:

```python
class Customer(BaseModel):
    email: str | None = None
```

This expresses:

```text
field may be absent
        +
if present, it may be string or None
```

This distinction matters when translating source contracts into models.

## 7.2 Three different meanings

These are conceptually different:

```python
name: str
```

```python
name: str | None = None
```

```python
name: str = "unknown"
```

They mean approximately:

| Definition | Meaning |
|---|---|
| `name: str` | required string |
| `name: str \| None = None` | optional nullable field |
| `name: str = "unknown"` | optional field with a concrete default |

Do not introduce defaults merely to make validation errors disappear. A default should represent a legitimate domain decision.

---

# 8. Validating Dictionaries and JSON

External systems often provide dictionaries after parsing JSON.

For example:

```python
payload = {
    "customer_id": 123,
    "email": "alice@example.com",
    "country": "US",
}
```

Validate it with:

```python
customer = Customer.model_validate(payload)
```

This is the preferred v2-style API for validating Python data.

## 8.1 Validating JSON strings

If the boundary gives you JSON text:

```python
json_string = """
{
    "customer_id": 123,
    "email": "alice@example.com",
    "country": "US"
}
"""
```

use:

```python
customer = Customer.model_validate_json(json_string)
```

The distinction is:

```text
Python dictionary
       |
       v
model_validate()

JSON string / JSON bytes
       |
       v
model_validate_json()
```

This makes the boundary explicit.

## 8.2 Why validation should happen before transformation

Avoid:

```python
payload = get_external_payload()
transformed = transform(payload)
validated = validate(transformed)
```

when the objective is to prove that the source payload itself is valid.

Prefer:

```python
payload = get_external_payload()
validated = Customer.model_validate(payload)
transformed = transform(validated)
```

Now downstream code receives a validated representation.

---

# 9. Understanding `ValidationError`

Import the exception:

```python
from pydantic import ValidationError
```

A production ingestion boundary should usually handle validation failures intentionally.

Example:

```python
try:
    customer = Customer.model_validate(payload)
except ValidationError as exc:
    errors = exc.errors()
    print(errors)
```

`errors()` returns structured information.

A typical entry contains information such as:

- `type`;
- `loc`;
- `msg`;
- `input`;
- `ctx` when relevant.

Conceptually:

```python
[
    {
        "type": "int_parsing",
        "loc": ("customer_id",),
        "msg": "Input should be a valid integer, unable to parse string as an integer",
        "input": "abc",
    }
]
```

The exact error wording and context can vary by Pydantic version and validation case. Production systems should generally consume structured fields rather than build logic around human-readable message strings.

## 9.1 Location is operationally important

Suppose a nested order has:

```text
lines[3].quantity
```

A structured error location can tell you that the fourth line's quantity failed.

This is far more actionable than:

```text
validation failed
```

## 9.2 Build actionable error records

A useful error record may contain:

```python
{
    "source": "customer_api",
    "record_id": "123",
    "errors": exc.errors(),
}
```

Later, this can feed a quarantine or dead-letter workflow.

Do not assume the raw exception string is sufficient for operational analysis.

---

# 10. Field Constraints

Basic Python types often are not enough.

For example:

```python
quantity: int
```

does not express:

> quantity must be greater than zero.

Pydantic constraints let you express business-level boundaries.

Required roadmap constraints include:

- `gt`;
- `ge`;
- `max_length`;
- `pattern`.

Example:

```python
from typing import Annotated

from pydantic import BaseModel, Field


class Product(BaseModel):
    quantity: Annotated[int, Field(gt=0)]
    price: Annotated[float, Field(ge=0)]
    sku: Annotated[str, Field(max_length=50)]
```

Interpretation:

```text
quantity > 0
price >= 0
sku length <= 50
```

## 10.1 `gt`

`gt` means greater than.

```python
quantity: Annotated[int, Field(gt=0)]
```

Valid:

```python
1
5
100
```

Invalid:

```python
0
-1
```

## 10.2 `ge`

`ge` means greater than or equal to.

```python
price: Annotated[Decimal, Field(ge=0)]
```

Valid:

```text
0
10.50
```

Invalid:

```text
-0.01
```

## 10.3 `max_length`

```python
sku: Annotated[str, Field(max_length=50)]
```

This prevents an unbounded string from crossing the boundary.

## 10.4 `pattern`

A pattern can constrain a string.

For example:

```python
from typing import Annotated

from pydantic import BaseModel, Field


class Product(BaseModel):
    sku: Annotated[
        str,
        Field(pattern=r"^[A-Z0-9_-]+$")
    ]
```

This is appropriate when the source contract specifies a recognizable textual format.

Do not use regular expressions simply because they are available. A complex regex can become difficult to understand and maintain.

---

# 11. `Field(...)` and `Annotated`

There are two closely related ideas.

`Field(...)` supplies field metadata and constraints.

For example:

```python
class Product(BaseModel):
    quantity: int = Field(gt=0)
```

`Annotated` allows the type and its metadata to be composed:

```python
from typing import Annotated

from pydantic import Field


PositiveQuantity = Annotated[int, Field(gt=0)]
```

Then:

```python
class OrderLine(BaseModel):
    quantity: PositiveQuantity
```

## 11.1 Why reusable constrained types can help

If many models need the same rule:

```text
quantity > 0
```

a reusable type can reduce duplication.

For example:

```python
PositiveQuantity = Annotated[int, Field(gt=0)]
```

Then:

```python
class OrderLine(BaseModel):
    quantity: PositiveQuantity


class ShipmentLine(BaseModel):
    quantity: PositiveQuantity
```

The rule becomes easier to identify.

## 11.2 Do not over-abstract

Do not create a custom type for every field.

Bad:

```text
CustomerIdStringType
CountryStringType
ShortCustomerEmailType
...
```

when ordinary annotations are sufficient.

Use abstraction when it improves consistency and readability.

---

# 12. `Literal` and `Enum`

External records frequently contain finite sets of allowed values.

## 12.1 `Literal`

For a small, local set:

```python
from typing import Literal


class Payment(BaseModel):
    status: Literal["pending", "paid", "cancelled"]
```

This says that only these values are accepted.

`Literal` is particularly useful when:

- the set is small;
- the values are local to one model;
- no additional behavior is required.

## 12.2 `Enum`

For reusable concepts:

```python
from enum import Enum

from pydantic import BaseModel


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class Payment(BaseModel):
    currency: Currency
```

Enums are useful when the concept is reused across multiple models.

They also communicate domain intent clearly.

## 12.3 Literal versus Enum

A practical decision:

| Requirement | Typical choice |
|---|---|
| Tiny, local finite set | `Literal` |
| Reusable domain vocabulary | `Enum` |
| Multiple models share values | `Enum` |
| Event discriminator | `Literal` is often convenient |

Both can contribute to machine-readable schema generation.

---

# 13. Coercion and the Production Risk of "Helpful" Parsing

Pydantic may perform useful conversions under normal validation.

For example, an input may look like:

```python
{
    "quantity": "42"
}
```

while the model says:

```python
class OrderLine(BaseModel):
    quantity: int
```

Depending on the field and input, normal Pydantic validation may accept compatible representations and produce an integer.

This is convenient.

But convenience creates an engineering question:

> Did the source send an acceptable representation, or did the validation layer silently repair a source defect?

Consider:

```text
Source contract says:
quantity is integer

Actual source sends:
"42"

Pydantic produces:
42
```

The downstream pipeline sees a correct integer.

But the producer may still be violating its contract.

This is the distinction:

```text
Parsing convenience
        vs
Source correctness visibility
```

A validation layer should not accidentally become a mechanism for hiding producer defects.

---

# 14. Strict Validation

Strict validation reduces certain forms of coercion.

The important principle is not:

> strict is always better.

The correct principle is:

> choose strictness according to the source contract and the operational consequences of coercion.

For example, suppose a financial source claims:

```text
amount: Decimal
```

but starts sending arbitrary strings.

You may want validation to reject representations that should never have appeared.

A field can use strict behavior where appropriate:

```python
from pydantic import BaseModel, StrictInt


class Record(BaseModel):
    quantity: StrictInt
```

Or use strict configuration where the model's boundary requires it.

Pydantic also provides strict types and configuration mechanisms. The exact choice should be deliberate.

## 14.1 When lax validation can be useful

Lax validation can make sense for:

- messy legacy sources;
- external APIs with known representation quirks;
- controlled normalization;
- sources where the accepted coercion is part of the integration contract.

## 14.2 When strict validation can be useful

Strictness is often valuable for:

- critical data contracts;
- financial values;
- identifiers;
- sources that are expected to obey an explicit schema;
- systems where silent coercion would hide defects.

## 14.3 The production decision

Ask:

1. What does the producer contract say?
2. Is coercion expected?
3. Would coercion hide a producer defect?
4. Is the field safety-critical or financially significant?
5. Do downstream systems depend on the exact representation?
6. Will rejecting the record be operationally acceptable?
7. Can source defects be monitored separately?

Strictness is a contract decision, not a style preference.

---

# 15. Production-Oriented Pydantic Types

Certain types are particularly valuable in data engineering.

---

## 15.1 `Decimal`

For monetary quantities, use `Decimal` when exact decimal semantics are required.

```python
from decimal import Decimal

from pydantic import BaseModel


class Payment(BaseModel):
    amount: Decimal
```

Why avoid ordinary binary floating-point for exact monetary quantities?

Because binary floating-point cannot represent every decimal fraction exactly.

Conceptually:

```text
Decimal business value
       |
       v
"99.99"
       |
       v
Decimal("99.99")
```

instead of relying on a binary approximation.

Use:

```python
from decimal import Decimal

amount = Decimal("99.99")
```

rather than:

```python
amount = Decimal(99.99)
```

when exact decimal input matters.

For production financial pipelines, also consider:

- scale;
- currency;
- rounding policy;
- quantization;
- source representation.

A `Decimal` type alone does not define the complete financial contract.

---

## 15.2 `AwareDatetime`

A timestamp should usually carry timezone information when it crosses system boundaries.

Use Pydantic's timezone-aware datetime type where appropriate:

```python
from pydantic import AwareDatetime, BaseModel


class Event(BaseModel):
    created_at: AwareDatetime
```

A naive datetime:

```text
2026-01-01 12:00:00
```

does not tell you which timezone it represents.

An aware timestamp can express an offset:

```text
2026-01-01T12:00:00+00:00
```

or:

```text
2026-01-01T17:30:00+05:30
```

Timezone mistakes are especially dangerous in:

- event ordering;
- incremental ingestion;
- partitioning;
- SLA calculations;
- reconciliation;
- financial reporting.

---

## 15.3 `UUID`

UUIDs are useful for stable identifiers:

```python
from uuid import UUID

from pydantic import BaseModel


class Customer(BaseModel):
    customer_id: UUID
```

This gives the boundary an explicit identifier type instead of treating every identifier as an arbitrary string.

Use UUID validation when the upstream contract actually defines the identifier as a UUID.

Do not turn ordinary business codes into UUIDs merely because UUIDs are available.

---

## 15.4 `EmailStr`

For email-like fields:

```python
from pydantic import BaseModel, EmailStr


class Customer(BaseModel):
    email: EmailStr
```

Install the optional email dependency when necessary:

```bash
uv add "pydantic[email]"
```

`EmailStr` provides structured validation for email-like input.

It does not prove that:

- the mailbox exists;
- the address belongs to the user;
- the domain will accept mail.

Validation of syntax is different from external verification.

---

## 15.5 `HttpUrl`

For URL fields:

```python
from pydantic import BaseModel, HttpUrl


class Source(BaseModel):
    endpoint: HttpUrl
```

This is useful when a source contract requires an HTTP(S)-style URL.

Again, syntactic validity does not prove:

- the server exists;
- the endpoint is reachable;
- authentication works;
- the resource is authorized.

Pydantic validates the boundary representation, not the entire external world.

---

# 16. Nested Models

Real payloads are rarely flat.

Consider:

```json
{
  "customer_id": 123,
  "email": "alice@example.com",
  "address": {
    "city": "Kolkata",
    "country": "IN"
  }
}
```

Model it explicitly:

```python
from pydantic import BaseModel


class Address(BaseModel):
    city: str
    country: str


class Customer(BaseModel):
    customer_id: int
    email: str
    address: Address
```

Validate:

```python
payload = {
    "customer_id": 123,
    "email": "alice@example.com",
    "address": {
        "city": "Kolkata",
        "country": "IN",
    },
}

customer = Customer.model_validate(payload)
```

## 16.1 Why nested models matter

Nested models are useful for:

- API responses;
- webhook payloads;
- JSON documents;
- structured event messages;
- nested source schemas.

They preserve the source structure while giving each logical object its own validation rules.

## 16.2 Nested errors

If:

```python
payload["address"]["country"] = 123
```

and the model rejects the value, the validation error can identify the nested path.

This is one reason structured validation errors are operationally useful.

---

# 17. Lists of Models

Suppose an order contains multiple lines:

```python
from pydantic import BaseModel


class OrderLine(BaseModel):
    product_id: str
    quantity: int


class Order(BaseModel):
    order_id: str
    lines: list[OrderLine]
```

Now:

```python
payload = {
    "order_id": "o-100",
    "lines": [
        {"product_id": "p-1", "quantity": 2},
        {"product_id": "p-2", "quantity": 5},
    ],
}

order = Order.model_validate(payload)
```

Each line is validated as an `OrderLine`.

## 17.1 Empty lists

A plain:

```python
lines: list[OrderLine]
```

does not necessarily express that at least one line must exist.

If the business rule requires at least one item, add an appropriate collection constraint.

For example:

```python
from typing import Annotated

from pydantic import BaseModel, Field


class Order(BaseModel):
    order_id: str
    lines: Annotated[list[OrderLine], Field(min_length=1)]
```

Now the schema expresses the business rule.

---

# 18. Field Validators

Pydantic v2 provides `@field_validator`.

Example:

```python
from pydantic import BaseModel, field_validator


class Customer(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()
```

Now:

```python
customer = Customer(email="  ALICE@example.com  ")

print(customer.email)
# alice@example.com
```

## 18.1 Validation versus normalization

A validator can:

- reject invalid data;
- normalize data;
- enforce a field-specific rule.

But these are not identical goals.

Validation asks:

> Is this acceptable?

Normalization asks:

> Can this input be converted into the canonical representation?

For example, stripping accidental surrounding whitespace may be reasonable.

But silently converting a malformed business identifier into another identifier could hide source defects.

## 18.2 Do not use validators for everything

A validator should not become a dumping ground for:

- database queries;
- network calls;
- complex workflow logic;
- unrelated transformations;
- expensive enrichment;
- side effects.

Keep validation deterministic and focused.

---

# 19. Model Validators

Some rules involve multiple fields.

For example:

```text
shipped_at >= ordered_at
```

No single field can establish this relationship.

Use `@model_validator`.

```python
from pydantic import AwareDatetime, BaseModel, model_validator


class Shipment(BaseModel):
    ordered_at: AwareDatetime
    shipped_at: AwareDatetime

    @model_validator(mode="after")
    def validate_dates(self):
        if self.shipped_at < self.ordered_at:
            raise ValueError("shipped_at must be >= ordered_at")
        return self
```

The model validator sees the constructed model and can reason about the relationship.

## 19.1 Why model-level validation exists

Examples:

```text
start <= end
subtotal + tax == total
shipped_at >= ordered_at
currency matches payment method
status requires a corresponding timestamp
```

These are relationships between fields.

---

# 20. `before` Versus `after`

Validators can run at different stages.

Conceptually:

```text
before:

raw input
   |
   v
validator
   |
   v
Pydantic parsing/validation
```

versus:

```text
after:

raw input
   |
   v
Pydantic parsing/validation
   |
   v
validator
```

## 20.1 `mode="before"`

Example:

```python
from pydantic import BaseModel, field_validator


class Record(BaseModel):
    code: str

    @field_validator("code", mode="before")
    @classmethod
    def normalize_raw_code(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value
```

This operates on input before normal field validation.

Use `before` when the raw representation itself needs controlled preprocessing.

## 20.2 `mode="after"`

Example:

```python
class Record(BaseModel):
    code: str

    @field_validator("code", mode="after")
    @classmethod
    def validate_code(cls, value: str) -> str:
        if not value.startswith("ORD-"):
            raise ValueError("code must start with ORD-")
        return value
```

Here Pydantic has already established that the field is a string.

## 20.3 Model-level modes

The same conceptual distinction applies to model validators.

Use `before` when the raw input structure must be inspected or normalized before model construction.

Use `after` when you want to reason about an already validated model.

Prefer the simplest stage that correctly expresses the rule.

---

# 21. Cross-Field Validation

Cross-field validation should represent an actual relationship.

Example:

```python
from decimal import Decimal

from pydantic import BaseModel, model_validator


class Invoice(BaseModel):
    subtotal: Decimal
    tax: Decimal
    total: Decimal

    @model_validator(mode="after")
    def validate_total(self):
        expected = self.subtotal + self.tax

        if self.total != expected:
            raise ValueError(
                f"total must equal subtotal + tax ({expected})"
            )

        return self
```

This is useful because the model itself documents the invariant.

However, be careful with decimal arithmetic and business rounding. In a financial system, the actual contract should explicitly define:

- scale;
- rounding mode;
- currency;
- tax calculation rules.

A validator should implement a defined business rule, not invent one.

---

# 22. `ConfigDict` and Model Configuration

Pydantic v2 uses `ConfigDict` for model configuration.

```python
from pydantic import BaseModel, ConfigDict


class Customer(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    customer_id: int
    email: str
```

The configuration changes model behavior.

The roadmap requires understanding:

- `extra="forbid"`;
- `extra="ignore"`;
- `extra="allow"`;
- `frozen=True`;
- `str_strip_whitespace=True`.

---

# 23. Handling Unexpected Fields

Suppose the source sends:

```json
{
  "customer_id": 123,
  "email": "a@example.com",
  "marketing_segment": "premium"
}
```

but the model only declares:

```python
customer_id
email
```

There are three important strategies.

---

## 23.1 `extra="ignore"`

```python
from pydantic import BaseModel, ConfigDict


class Customer(BaseModel):
    model_config = ConfigDict(extra="ignore")

    customer_id: int
    email: str
```

The unexpected field is ignored.

### Benefit

The consumer is resilient to additional fields.

### Risk

A producer may add an important field and the consumer may never notice.

---

## 23.2 `extra="allow"`

```python
class Customer(BaseModel):
    model_config = ConfigDict(extra="allow")

    customer_id: int
    email: str
```

Unexpected fields are retained as extra data.

### Benefit

Potentially useful when forward compatibility is important.

### Risk

The boundary becomes less explicit.

You may accidentally accept fields you did not design for.

---

## 23.3 `extra="forbid"`

```python
class Customer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: int
    email: str
```

Unexpected fields cause validation failure.

### Benefit

Schema changes become visible immediately.

### Risk

A benign source-side addition can break ingestion.

---

## 23.4 The engineering decision

Do not treat one setting as universally correct.

Think about:

```text
Source ownership
+
contract maturity
+
schema evolution strategy
+
blast radius
+
monitoring
+
forward compatibility
```

For a tightly controlled contract, `forbid` may expose defects early.

For a loosely controlled integration, `ignore` or `allow` may be part of the compatibility strategy.

The important requirement is intentionality.

---

# 24. Frozen Models

A model can be configured as frozen:

```python
from pydantic import BaseModel, ConfigDict


class Event(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: str
    event_type: str
```

The purpose is to reduce accidental mutation of model fields.

This can be useful when a validated record should behave like a stable value object during a pipeline stage.

## 24.1 What freezing means

Freezing changes assignment behavior.

It should not be interpreted as:

> every object reachable from the model is deeply immutable.

Nested mutable objects may still have their own mutability characteristics.

Therefore, freezing is a useful boundary property, not a substitute for understanding object mutability.

## 24.2 Hashing considerations

Frozen models can interact differently with hashing and collection usage than mutable models.

Do not make a model frozen simply because "immutable sounds better."

Ask whether:

- the record should change after validation;
- mutation represents a valid lifecycle transition;
- downstream code benefits from value-like behavior.

---

# 25. String Normalization

Pydantic can strip surrounding whitespace using configuration:

```python
from pydantic import BaseModel, ConfigDict


class Customer(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
```

Input:

```text
" Alice "
```

can become:

```text
"Alice"
```

This is useful for accidental formatting noise.

But normalization has a risk:

> A transformation can hide a source-quality problem that should have been observed.

## 25.1 Appropriate normalization

Often reasonable:

```text
" Alice " -> "Alice"
```

when surrounding whitespace has no business meaning.

Potentially dangerous:

```text
"00123" -> "123"
```

if leading zeros are meaningful.

Potentially dangerous:

```text
"abc " -> "abc"
```

if the whitespace is itself evidence of a broken upstream field.

The correct question is:

> Is this transformation part of the accepted boundary contract?

---

# 26. Serialization

After validation, the model often needs to move to another boundary.

Use:

```python
model_dump()
```

for a Python dictionary representation.

Use:

```python
model_dump_json()
```

for JSON serialization.

Example:

```python
from pydantic import BaseModel


class Customer(BaseModel):
    customer_id: int
    email: str


customer = Customer(
    customer_id=123,
    email="alice@example.com",
)

data = customer.model_dump()
json_text = customer.model_dump_json()
```

Conceptually:

```text
Input payload
     |
     v
Pydantic model
     |
     v
Validated representation
     |
     +---- model_dump() ------> Python dict
     |
     +---- model_dump_json() -> JSON
```

## 26.1 Why serialization is part of validation architecture

Validation controls what enters the internal representation.

Serialization controls what leaves it.

Both matter because the output may be:

- persisted;
- logged;
- sent to another service;
- written to JSONL;
- published as an event;
- returned through an API.

---

# 27. Aliases

External systems may use naming conventions that differ from internal Python code.

Example payload:

```json
{
  "customerId": "123",
  "createdAt": "2026-01-01T00:00:00Z"
}
```

Internal Python code may prefer:

```python
customer_id
created_at
```

Pydantic aliases let the model bridge the two representations.

Example:

```python
from datetime import datetime

from pydantic import BaseModel, Field


class Customer(BaseModel):
    customer_id: str = Field(validation_alias="customerId")
    created_at: datetime = Field(validation_alias="createdAt")
```

Validate the external representation:

```python
payload = {
    "customerId": "123",
    "createdAt": "2026-01-01T00:00:00Z",
}

customer = Customer.model_validate(payload)
```

Internally:

```python
customer.customer_id
customer.created_at
```

remain Python-friendly.

## 27.1 Serialization using aliases

When output needs the external naming convention, use:

```python
customer.model_dump(by_alias=True)
```

This creates a clean separation:

```text
External contract:
customerId

Internal code:
customer_id
```

This is useful for:

- APIs;
- legacy integrations;
- vendor systems;
- event schemas;
- source-specific naming conventions.

---

# 28. Sensitive-Field Exclusion

Validated models can contain sensitive fields.

For example:

```python
from pydantic import BaseModel


class UserCredential(BaseModel):
    user_id: str
    email: str
    password: str
```

Never blindly serialize everything into logs.

Instead:

```python
safe_output = user.model_dump(
    exclude={"password"}
)
```

You can similarly exclude:

- passwords;
- access tokens;
- refresh tokens;
- API keys;
- PII;
- internal-only fields.

The important security distinction is:

> Serialization exclusion is not a substitute for proper secret storage or access control.

A secret should not be exposed merely because a serializer can exclude it.

Use proper:

- secret management;
- access control;
- redaction;
- logging policy;
- encryption where appropriate.

---

# 29. Discriminated Unions

Event-driven systems commonly contain heterogeneous payloads.

Consider:

```json
{
  "event_type": "payment_succeeded",
  "payment_id": "p123",
  "amount": "99.00"
}
```

and:

```json
{
  "event_type": "payment_failed",
  "payment_id": "p123",
  "reason": "declined"
}
```

These records share an event envelope but have different fields.

## 29.1 Event-specific models

```python
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class PaymentSucceeded(BaseModel):
    event_type: Literal["payment_succeeded"]
    payment_id: str
    amount: Decimal


class PaymentFailed(BaseModel):
    event_type: Literal["payment_failed"]
    payment_id: str
    reason: str


class RefundIssued(BaseModel):
    event_type: Literal["refund_issued"]
    payment_id: str
    amount: Decimal
```

Now create a discriminated union:

```python
from typing import Annotated

from pydantic import Field


PaymentEvent = Annotated[
    PaymentSucceeded | PaymentFailed | RefundIssued,
    Field(discriminator="event_type"),
]
```

Validate through a `TypeAdapter`:

```python
from pydantic import TypeAdapter


payment_event_adapter = TypeAdapter(PaymentEvent)

event = payment_event_adapter.validate_python(payload)
```

## 29.2 Why discriminated unions matter

The discriminator:

```text
event_type
```

tells Pydantic which model should validate the payload.

This is better than one enormous model:

```python
class PaymentEvent(BaseModel):
    event_type: str
    payment_id: str | None = None
    amount: Decimal | None = None
    reason: str | None = None
    refund_reason: str | None = None
    ...
```

A giant model creates many ambiguous combinations.

For example:

```text
event_type = payment_failed
amount = 99
reason = None
```

might be structurally valid but semantically nonsensical.

Discriminated unions make event-specific structure explicit.

## 29.3 Event-driven Data Engineering use cases

This pattern is useful for:

- payment events;
- order events;
- customer lifecycle events;
- shipment events;
- CDC-style envelopes;
- Kafka topics containing multiple event types.

---

# 30. `TypeAdapter`

Not every validation target needs to be a `BaseModel`.

For example:

```python
list[Customer]
```

is a type expression, not a model class.

Pydantic's `TypeAdapter` can validate it.

```python
from pydantic import TypeAdapter


adapter = TypeAdapter(list[Customer])
```

Then:

```python
validated_customers = adapter.validate_python(records)
```

This is particularly useful for:

- lists of models;
- unions;
- primitive constrained types;
- bulk validation;
- types that are not `BaseModel` subclasses.

## 30.1 Why this matters

A naïve approach might be:

```python
validated = []

for record in records:
    validated.append(Customer.model_validate(record))
```

This is straightforward and often perfectly acceptable.

But at scale, it is worth benchmarking against bulk-oriented validation:

```python
adapter = TypeAdapter(list[Customer])
validated = adapter.validate_python(records)
```

Do not assume one approach is always faster.

Measure.

---

# 31. Bulk Validation

Suppose a pipeline receives:

```text
1,000 records
10,000 records
100,000 records
1,000,000 records
```

A simple loop is easy to understand:

```python
validated = []

for record in records:
    validated.append(Customer.model_validate(record))
```

It may be entirely appropriate for a moderate workload.

At larger scale, however, validation cost becomes part of pipeline performance.

Potential factors include:

- records per second;
- total execution time;
- payload size;
- nested model depth;
- custom validators;
- JSON parsing;
- object allocation;
- memory pressure;
- batch size.

Use `TypeAdapter` when appropriate:

```python
from pydantic import TypeAdapter


adapter = TypeAdapter(list[Customer])
validated = adapter.validate_python(records)
```

But do not claim a fixed speedup without measuring the actual workload.

---

# 32. Bulk JSON Validation

If data arrives as JSON, Pydantic can validate JSON through `TypeAdapter`.

For example:

```python
from pydantic import TypeAdapter


adapter = TypeAdapter(list[Customer])

validated = adapter.validate_json(json_bytes)
```

This can avoid some unnecessary manual parsing steps.

However, large inputs require memory planning.

A one-million-record JSON array can be very large.

Think about:

```text
Raw JSON bytes
        +
Parsed structures
        +
Pydantic model objects
        +
Application buffers
```

Peak memory can become significant.

## 32.1 JSON array versus JSON Lines

JSON array:

```json
[
  {"customer_id": 1, "email": "a@example.com"},
  {"customer_id": 2, "email": "b@example.com"}
]
```

JSON Lines:

```text
{"customer_id":1,"email":"a@example.com"}
{"customer_id":2,"email":"b@example.com"}
```

JSONL is often easier to process incrementally because records are independently delimited.

For very large files, consider bounded batches rather than loading the entire source into memory.

---

# 33. Per-Record Error Collection

A production ingestion pipeline often should not discard an entire batch because one record is invalid.

Consider:

```text
1,000 incoming records
 |
 +-- 997 valid
 |
 +--   3 invalid
```

A useful outcome is:

```text
valid_records
invalid_records
```

rather than:

```text
batch failed
```

for every possible source.

## 33.1 A simple collection pattern

```python
from pydantic import BaseModel, ValidationError


class Customer(BaseModel):
    customer_id: int
    email: str


def validate_records(records: list[dict]):
    valid_records = []
    invalid_records = []

    for record in records:
        try:
            model = Customer.model_validate(record)
            valid_records.append(model)
        except ValidationError as exc:
            invalid_records.append(
                {
                    "record": record,
                    "errors": exc.errors(),
                }
            )

    return valid_records, invalid_records
```

This gives the pipeline two explicit outputs.

## 33.2 Preserve the original record

Do not retain only:

```python
exc.errors()
```

when operational traceability requires the original input.

A useful invalid record may contain:

```python
{
    "record": original_record,
    "errors": exc.errors(),
}
```

Production systems may add:

```text
source
run_id
record_id
schema_version
first_seen_at
partition
offset
file_name
line_number
```

This connects naturally to quarantine and dead-letter handling.

---

# 34. Quarantine-Oriented Validation

The architecture is:

```text
Incoming Records
      |
      v
Pydantic Validation
      |
      +---- valid ----> downstream pipeline
      |
      +---- invalid --> quarantine
```

A quarantined record should remain diagnosable.

Useful metadata includes:

- source;
- run ID;
- record identifier;
- validation errors;
- first-seen timestamp;
- model/schema version.

Example conceptual object:

```python
{
    "source": "payments-api",
    "run_id": "2026-10-01T12:00:00Z",
    "record_id": "p123",
    "model_version": "payment-event-v3",
    "record": original_record,
    "errors": validation_errors,
}
```

This chapter does not implement a complete quarantine platform. The important boundary concept is:

```text
Validation
    |
    +---- valid --> continue
    |
    +---- invalid --> preserve + explain + route
```

---

# 35. Validation Performance

Pydantic validation is not free.

A production pipeline must treat validation as compute.

Relevant factors include:

- records per second;
- payload size;
- nesting depth;
- number of fields;
- number of validators;
- complexity of custom Python logic;
- JSON parsing;
- allocation;
- batch size;
- memory pressure.

## 35.1 What to measure

At minimum:

```text
records/sec
total runtime
peak memory
error count
```

For a larger benchmark, also consider:

```text
CPU utilization
payload bytes/sec
JSON parsing time
validation time
```

Do not fabricate numbers.

A proper benchmark should record actual results from the target environment.

## 35.2 A simple benchmark harness

```python
from time import perf_counter

from pydantic import TypeAdapter


adapter = TypeAdapter(list[Customer])

start = perf_counter()

validated = adapter.validate_python(records)

elapsed = perf_counter() - start

records_per_second = len(records) / elapsed

print(f"records: {len(records)}")
print(f"elapsed_seconds: {elapsed:.6f}")
print(f"records_per_second: {records_per_second:.2f}")
```

The result is environment-specific.

Run multiple trials when evaluating a design.

## 35.3 Benchmark realistic data

Do not benchmark only:

```python
{"id": 1}
```

if production records contain:

- nested objects;
- arrays;
- timestamps;
- decimals;
- unions;
- custom validators.

The benchmark should resemble production payload shape and size.

---

# 36. When Pydantic Is Not the Right Layer

Pydantic is excellent for record boundaries.

It is not automatically the correct tool for massive table-level validation.

Examples where Pydantic should not be the primary validation mechanism:

- 100-million-row DataFrames;
- column-level distribution checks;
- uniqueness across enormous datasets;
- grouped validation;
- aggregate constraints;
- warehouse-wide reconciliation;
- table-level constraints;
- statistical anomaly detection.

A useful division is:

```text
External record
      |
      v
   Pydantic
      |
      v
DataFrame
      |
      v
   Pandera
      |
      v
Table / dataset
      |
      v
GX / Soda / SQL
```

Pydantic answers questions such as:

> Does this individual event have the expected structure and valid field values?

A DataFrame validation layer can answer questions such as:

> Does this column have the expected dtype across the dataset?

A dataset-level quality layer can answer:

> Does today's row count reconcile with the upstream source?

These are different scopes.

---

# 37. JSON Schema

Pydantic models can generate JSON Schema:

```python
schema = Customer.model_json_schema()
```

Example:

```python
from pydantic import BaseModel


class Customer(BaseModel):
    customer_id: int
    email: str


schema = Customer.model_json_schema()

print(schema)
```

JSON Schema is useful for:

- machine-readable contracts;
- documentation;
- interoperability;
- API specifications;
- validation tooling;
- data contracts.

Conceptually:

```text
Python type model
       |
       v
Pydantic
       |
       v
JSON Schema
       |
       +---- documentation
       +---- tooling
       +---- contract
       +---- interoperability
```

A Pydantic model can therefore serve as an executable representation of a record contract.

However, a schema is not the whole contract.

A complete data contract may also require:

- ownership;
- versioning;
- compatibility policy;
- quality expectations;
- delivery guarantees;
- operational responsibilities.

Those topics belong to later modules.

---

# 38. External Models vs Domain Models vs Database Models

One of the most important architectural decisions is resisting the temptation to use one class for everything.

A useful architecture is:

```text
External Payload Model
          |
          v
     Domain Model
          |
          v
     Database Model
```

## 38.1 External payload model

Represents:

- source schema;
- source naming;
- source quirks;
- source contract.

For example:

```json
{
  "customerId": "123"
}
```

The external model can use:

```python
customer_id: str
```

with an alias.

## 38.2 Domain model

Represents internal business meaning.

For example, internally:

```python
customer_id: UUID
```

if the domain uses UUIDs.

The domain model should not necessarily preserve every source quirk.

## 38.3 Database model

Represents persistence.

It may contain:

- primary keys;
- foreign keys;
- database-generated timestamps;
- indexes;
- internal audit columns;
- storage-specific types.

## 38.4 Why separation helps

Separation reduces:

- coupling;
- accidental exposure;
- migration risk;
- schema-evolution blast radius.

It improves:

- ownership clarity;
- maintainability;
- testing;
- security;
- architectural boundaries.

---

# 39. ORM and Database Model Caveats

Earlier database-connectivity work introduced ORMs such as SQLAlchemy.

Do not automatically reuse a database model as an API or external payload model.

An ORM model may contain:

- database-specific fields;
- lazy relationships;
- internal columns;
- persistence lifecycle state;
- foreign-key relationships;
- fields not intended for external consumers.

Reusing it directly can create:

```text
database schema
      |
      +---- accidental API contract
```

This creates unnecessary coupling.

## 39.1 Serialization surprises

An ORM object may contain relationships or attributes that are not safe or desirable to serialize.

External models should define what the external boundary accepts and emits.

## 39.2 Security

An internal database field such as:

```text
password_hash
internal_notes
risk_score
```

should not become an API field merely because the ORM model contains it.

The safer design is:

```text
External schema
    |
    v
Pydantic boundary model
    |
    v
Domain representation
    |
    v
ORM/database representation
```

Do not re-teach SQLAlchemy here; the architectural lesson is separation of concerns.

---

# 40. Complete `Order` Example

The roadmap requires a realistic order model with:

- positive quantities;
- decimal prices;
- two decimal places;
- allowed currencies;
- timezone-aware `created_at`;
- nested `OrderLine`;
- cross-field order-total validation.

A practical model can be built as follows.

```python
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field, model_validator


Money = Annotated[
    Decimal,
    Field(ge=0, decimal_places=2)
]

PositiveQuantity = Annotated[
    int,
    Field(gt=0)
]


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class OrderLine(BaseModel):
    product_id: str
    quantity: PositiveQuantity
    unit_price: Money

    @property
    def line_total(self) -> Decimal:
        return self.quantity * self.unit_price


class Order(BaseModel):
    order_id: str
    currency: Currency
    created_at: AwareDatetime
    total: Money
    lines: Annotated[list[OrderLine], Field(min_length=1)]

    @model_validator(mode="after")
    def validate_order_total(self):
        expected_total = sum(
            (line.line_total for line in self.lines),
            Decimal("0"),
        )

        if self.total != expected_total:
            raise ValueError(
                "total must equal the sum of line totals"
            )

        return self
```

The exact decimal constraint behavior should be tested against the installed Pydantic v2 version. The important engineering rule is that the model must express the monetary contract deliberately.

## 40.1 Valid order

```python
payload = {
    "order_id": "ORD-1001",
    "currency": "USD",
    "created_at": "2026-10-01T12:00:00Z",
    "total": "35.00",
    "lines": [
        {
            "product_id": "P-1",
            "quantity": 2,
            "unit_price": "10.00",
        },
        {
            "product_id": "P-2",
            "quantity": 1,
            "unit_price": "15.00",
        },
    ],
}

order = Order.model_validate(payload)

print(order)
```

The expected total is:

```text
2 × 10.00 + 1 × 15.00 = 35.00
```

## 40.2 Boundary example

A quantity of:

```python
1
```

is valid.

A quantity of:

```python
0
```

should fail because:

```python
quantity > 0
```

is part of the contract.

## 40.3 Invalid total

```python
payload["total"] = "34.99"
```

The model-level validator should reject the record.

This is an important example of why field validation alone is insufficient.

---

# 41. Payment Webhook Discriminated Union

Define the event models:

```python
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter


class PaymentSucceeded(BaseModel):
    event_type: Literal["payment_succeeded"]
    payment_id: str
    amount: Decimal


class PaymentFailed(BaseModel):
    event_type: Literal["payment_failed"]
    payment_id: str
    reason: str


class RefundIssued(BaseModel):
    event_type: Literal["refund_issued"]
    payment_id: str
    amount: Decimal


PaymentEvent = Annotated[
    PaymentSucceeded | PaymentFailed | RefundIssued,
    Field(discriminator="event_type"),
]

payment_event_adapter = TypeAdapter(PaymentEvent)
```

Validate:

```python
success_payload = {
    "event_type": "payment_succeeded",
    "payment_id": "p123",
    "amount": "99.00",
}

event = payment_event_adapter.validate_python(success_payload)
```

Now:

```python
if isinstance(event, PaymentSucceeded):
    print(event.amount)
elif isinstance(event, PaymentFailed):
    print(event.reason)
elif isinstance(event, RefundIssued):
    print(event.amount)
```

This provides type-safe branching.

## 41.1 Invalid discriminator

If:

```python
{
    "event_type": "payment_unknown",
    "payment_id": "p123",
}
```

is received, there is no known event model.

That should be treated as a boundary failure.

---

# 42. API Customer Model

A realistic customer model can combine several concepts:

```python
from datetime import datetime
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, EmailStr, HttpUrl


class CustomerProfile(BaseModel):
    display_name: str
    website: HttpUrl | None = None


class ApiCustomer(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    customer_id: UUID
    email: EmailStr
    created_at: AwareDatetime
    country: str
    status: str
    profile: CustomerProfile | None = None
```

A source payload might be:

```python
payload = {
    "customer_id": "b7f4f2d7-7d5a-4d9b-90af-2f0c3f1f3c40",
    "email": "alice@example.com",
    "created_at": "2026-10-01T12:00:00Z",
    "country": "IN",
    "status": "active",
    "profile": {
        "display_name": "Alice",
        "website": "https://example.com",
    },
}
```

Validate:

```python
customer = ApiCustomer.model_validate(payload)
```

The model provides:

- UUID validation;
- email validation;
- timezone-aware timestamp validation;
- nested validation;
- URL validation;
- explicit unexpected-field policy.

---

# 43. SFTP Record Model

File-based ingestion still has an untrusted boundary.

Imagine a logistics SFTP record:

```python
from decimal import Decimal

from pydantic import BaseModel, Field


class SftpShipmentRecord(BaseModel):
    shipment_id: str
    warehouse_id: str
    quantity: int = Field(gt=0)
    weight_kg: Decimal = Field(gt=0)
    status: Literal["created", "packed", "shipped", "delivered"]
    shipped_at: AwareDatetime | None = None
```

The source could be a CSV row converted to a dictionary:

```python
row = {
    "shipment_id": "S-100",
    "warehouse_id": "WH-01",
    "quantity": 10,
    "weight_kg": "25.40",
    "status": "shipped",
    "shipped_at": "2026-10-01T08:00:00Z",
}
```

Validate:

```python
record = SftpShipmentRecord.model_validate(row)
```

This demonstrates that Pydantic is not limited to HTTP applications.

The same boundary principle applies:

```text
SFTP row
   |
   v
parsed dictionary
   |
   v
Pydantic validation
   |
   +---- invalid --> quarantine
   |
   v
validated record
```

---

# 44. Serialization to JSON Lines

Suppose valid models need to be written as JSONL.

```python
with open("customers.jsonl", "w", encoding="utf-8") as file:
    for customer in validated_customers:
        file.write(customer.model_dump_json())
        file.write("\n")
```

Each line represents one validated record.

This pattern is useful for:

- bronze landing;
- replay;
- debugging;
- downstream ingestion;
- interchange.

The serialization contract should be explicit.

For example:

```text
validated model
      |
      v
model_dump_json()
      |
      v
one JSON object per line
```

Do not log sensitive models merely because JSON serialization is convenient.

---

# 45. Testing Pydantic Validation

Validation code needs tests for both acceptance and rejection.

A strong test suite includes:

1. valid cases;
2. boundary cases;
3. invalid cases;
4. cross-field failures;
5. unexpected fields;
6. serialization;
7. discriminated unions;
8. bulk validation;
9. sensitive-field exclusion.

## 45.1 Valid case

```python
def test_customer_accepts_valid_payload():
    customer = ApiCustomer.model_validate(valid_payload)

    assert customer.country == "IN"
```

## 45.2 Invalid case

```python
import pytest
from pydantic import ValidationError


def test_customer_rejects_invalid_email():
    with pytest.raises(ValidationError):
        ApiCustomer.model_validate(
            {
                **valid_payload,
                "email": "not-an-email",
            }
        )
```

## 45.3 Boundary case

Test minimum valid values:

```python
def test_quantity_one_is_valid():
    line = OrderLine(
        product_id="P-1",
        quantity=1,
        unit_price="0.01",
    )

    assert line.quantity == 1
```

And just below the boundary:

```python
def test_quantity_zero_is_invalid():
    with pytest.raises(ValidationError):
        OrderLine(
            product_id="P-1",
            quantity=0,
            unit_price="0.01",
        )
```

## 45.4 Cross-field test

```python
def test_order_total_must_match_lines():
    with pytest.raises(ValidationError):
        Order.model_validate(
            {
                "order_id": "ORD-1",
                "currency": "USD",
                "created_at": "2026-10-01T12:00:00Z",
                "total": "999.00",
                "lines": [
                    {
                        "product_id": "P-1",
                        "quantity": 1,
                        "unit_price": "10.00",
                    }
                ],
            }
        )
```

## 45.5 Serialization test

```python
def test_sensitive_field_is_excluded():
    credential = UserCredential(
        user_id="u1",
        email="alice@example.com",
        password="secret",
    )

    output = credential.model_dump(
        exclude={"password"}
    )

    assert "password" not in output
```

---

# 46. Parametrized Validation Tests

When multiple values test the same rule, parametrization improves coverage.

```python
import pytest
from pydantic import ValidationError


@pytest.mark.parametrize(
    "quantity",
    [0, -1, -100],
)
def test_invalid_quantities(quantity):
    with pytest.raises(ValidationError):
        OrderLine(
            product_id="P-1",
            quantity=quantity,
            unit_price="10.00",
        )
```

You can also test valid boundaries:

```python
@pytest.mark.parametrize(
    "quantity",
    [1, 2, 100],
)
def test_valid_quantities(quantity):
    line = OrderLine(
        product_id="P-1",
        quantity=quantity,
        unit_price="10.00",
    )

    assert line.quantity == quantity
```

The objective is not to maximize test count.

The objective is to prove the boundary behavior.

---

# 47. Defect Injection Lab

A useful way to learn production validation is to intentionally break records.

Use the models from this chapter and inject these defects.

## Defect 1 — Missing required field

Input:

```python
{
    "customer_id": "123"
}
```

Expected:

- validation failure;
- location identifies the missing field;
- record should not enter the trusted pipeline.

## Defect 2 — Wrong type

Input:

```python
{
    "customer_id": "not-an-id"
}
```

Expected:

- validation failure appropriate to the declared type.

## Defect 3 — Numeric value below constraint

```python
{
    "quantity": 0
}
```

Expected:

- `gt=0` constraint failure.

## Defect 4 — Invalid enum

```python
{
    "currency": "XYZ"
}
```

Expected:

- allowed-value validation failure.

## Defect 5 — Invalid email

```python
{
    "email": "not-an-email"
}
```

Expected:

- email validation failure.

## Defect 6 — Invalid URL

```python
{
    "website": "not-a-url"
}
```

Expected:

- URL validation failure.

## Defect 7 — Naive datetime

Use a timestamp without timezone information where the model requires `AwareDatetime`.

Expected:

- timezone-aware validation failure.

## Defect 8 — Invalid UUID

```python
{
    "customer_id": "abc"
}
```

Expected:

- UUID validation failure.

## Defect 9 — Unexpected field

With:

```python
extra="forbid"
```

send:

```python
{
    "customer_id": "...",
    "unexpected": "value",
}
```

Expected:

- extra-field validation failure.

## Defect 10 — Cross-field date inconsistency

Send:

```text
ordered_at = 2026-10-02
shipped_at = 2026-10-01
```

Expected:

- model-level validation failure.

## Defect 11 — Incorrect order total

Send:

```text
line total = 100.00
order total = 99.00
```

Expected:

- order-total validation failure.

## Defect 12 — Invalid payment-event discriminator

Send:

```text
event_type = "unknown_event"
```

Expected:

- union discrimination failure.

## Defect 13 — Invalid nested line item

Send:

```python
{
    "lines": [
        {
            "product_id": "P-1",
            "quantity": -5,
        }
    ]
}
```

Expected:

- nested location identifies the line and field.

---

# 48. Production Debugging

## Scenario 1 — Source sends `"42"` instead of `42`

You discover:

```text
expected:
quantity = integer

received:
quantity = "42"
```

Investigate:

1. Is the model using lax validation?
2. Was the value coerced?
3. Does the source contract permit strings?
4. Is this a one-off or systemic change?
5. Should the pipeline reject future records?
6. Should the producer be alerted?
7. Should the accepted normalization be monitored?

Do not automatically change the model to strict mode without understanding the source contract.

---

## Scenario 2 — Source suddenly adds a field

Suppose the producer adds:

```json
"marketing_segment": "premium"
```

Investigate:

- `extra="ignore"`;
- `extra="allow"`;
- `extra="forbid"`.

Questions:

```text
Was the field expected?
Does it contain useful information?
Should consumers be alerted?
Is the source contract versioned?
Could rejecting it cause unnecessary outage?
```

This is a schema-evolution decision.

---

## Scenario 3 — 1% of webhook events fail

Do not start by changing the Pydantic model.

First segment the failures.

Investigate:

- event type;
- producer version;
- schema version;
- payload shape;
- validation error type;
- first occurrence time;
- deployment timeline;
- source partition or tenant;
- whether all failures share a field.

A useful diagnostic table is:

| Dimension | Question |
|---|---|
| Event type | Are failures isolated to one event? |
| Producer version | Did a deployment precede the failures? |
| Field | Is one field responsible? |
| Error type | Parsing, missing field, extra field, constraint? |
| Time | Did failure rate change suddenly? |
| Tenant/source | Is one producer responsible? |

---

## Scenario 4 — Bulk validation is too slow

Investigate in order:

1. Measure actual runtime.
2. Measure records/sec.
3. Check batch size.
4. Compare per-record validation with `TypeAdapter`.
5. Inspect custom validators.
6. Inspect JSON parsing.
7. Inspect model complexity.
8. Measure memory.
9. Determine whether Pydantic is being used on a workload that belongs at DataFrame level.

Do not optimize based only on intuition.

---

## Scenario 5 — Sensitive data appears in logs

Investigate:

- calls to `model_dump()`;
- calls to `model_dump_json()`;
- exception logging;
- request logging middleware;
- debug statements;
- serialization configuration.

A dangerous pattern is:

```python
logger.error("Validation failed: %s", payload)
```

when `payload` contains secrets or PII.

Prefer structured errors with deliberate redaction.

---

# 49. Production Data Engineering Scenarios

## Scenario A — API ingestion

```text
API response
    |
    v
raw payload
    |
    v
Customer.model_validate()
    |
    +---- invalid --> error/quarantine
    |
    v
domain transformation
    |
    v
warehouse
```

Pydantic provides the first record-level boundary.

---

## Scenario B — Payment webhook

Use discriminated unions:

```text
payment_succeeded
payment_failed
refund_issued
```

Each event gets its own structure.

This avoids one giant model with dozens of optional fields.

---

## Scenario C — SFTP batch

For each row:

```text
CSV row
  |
  v
dictionary
  |
  v
Pydantic model
  |
  +---- invalid --> invalid-record collection
  |
  v
valid records
```

One malformed row does not necessarily have to destroy the entire file.

The batch policy must be explicit.

---

## Scenario D — Kafka event

An event boundary can validate:

```text
event envelope
event type
event identifier
event timestamp
event-specific payload
```

The validated event can then enter downstream transformation.

Discriminated unions are especially useful when multiple event types share a topic or logical stream.

---

## Scenario E — One million records

Do not immediately write:

```python
for record in million_records:
    Model.model_validate(record)
```

and assume it is acceptable.

Benchmark:

- per-record loop;
- `TypeAdapter`;
- different batch sizes;
- JSON validation;
- memory.

Record actual results.

---

## Scenario F — Large DataFrame

Suppose a dataset has:

```text
100,000,000 rows
```

Do not blindly instantiate 100 million Pydantic objects.

At this scale, columnar and dataset-level validation techniques are generally more appropriate.

The record-boundary Pydantic layer can still validate the source before data enters the DataFrame.

---

# 50. Architecture: The Complete Boundary Pattern

A robust pipeline can look like:

```text
                   EXTERNAL WORLD
                         |
              +----------+----------+
              |          |          |
             API      Webhook     SFTP
              |          |          |
              +----------+----------+
                         |
                         v
                  Raw Payload
                         |
                         v
               Pydantic Boundary
                         |
              +----------+----------+
              |                     |
            VALID                 INVALID
              |                     |
              v                     v
       Internal Record          Error Object
              |                     |
              v                     v
         Transformation        Quarantine
              |
              v
          DataFrame
              |
              v
          Table/Lake
```

The architecture becomes easier to reason about when each layer has one primary responsibility.

---

# 51. Hands-On Exercise — `record_validation.py`

Create a learning exercise with a single Python script named:

```text
record_validation.py
```

Do not add unrelated project files for this exercise unless your local learning environment requires them.

## Exercise objective

Build a small validation boundary for an order-ingestion pipeline.

Your model should contain:

```text
Order
 |
 +-- order_id
 +-- currency
 +-- created_at
 +-- total
 +-- lines
       |
       +-- product_id
       +-- quantity
       +-- unit_price
```

Requirements:

- positive quantity;
- non-negative monetary values;
- allowed currencies;
- timezone-aware timestamp;
- at least one line;
- total must equal line totals.

## Step 1 — Define the currency

Use:

```python
class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
```

## Step 2 — Define `OrderLine`

Use:

```python
class OrderLine(BaseModel):
    ...
```

## Step 3 — Define `Order`

Use nested validation.

## Step 4 — Add total validation

Use:

```python
@model_validator(mode="after")
```

## Step 5 — Test three payloads

Create:

1. valid;
2. boundary;
3. invalid.

## Step 6 — Print structured errors

Use:

```python
exc.errors()
```

## Step 7 — Serialize valid orders

Use:

```python
model_dump()
model_dump_json()
```

## Step 8 — Extend the exercise

Add:

- an external alias;
- a sensitive field;
- a discriminated payment event.

---

# 52. Advanced Exercise — Bulk Customer Validation

Create 10,000 customer records in memory.

Do not use fabricated benchmark claims in your documentation.

Compare:

### Approach A

```python
for record in records:
    Customer.model_validate(record)
```

### Approach B

```python
TypeAdapter(list[Customer]).validate_python(records)
```

Measure:

```text
records
elapsed time
records/sec
peak memory if available
validation failures
```

Run several trials.

Then answer:

1. Which approach was faster in your environment?
2. How did record complexity affect the result?
3. How did batch size affect memory?
4. What happened when 1% of records were invalid?
5. What error information did you retain?
6. Would the same approach be appropriate for 100 million rows?

---

# 53. Advanced Exercise — JSONL Boundary

Create JSON Lines input conceptually like:

```text
{"customer_id":"...","email":"alice@example.com"}
{"customer_id":"...","email":"bob@example.com"}
{"customer_id":"bad","email":"invalid"}
```

Build a bounded processing loop:

```text
read bounded batch
       |
       v
validate
       |
       +---- valid --> output
       |
       +---- invalid --> error/quarantine
       |
       v
next batch
```

Measure:

- batch size;
- runtime;
- records/sec;
- memory behavior;
- invalid-record count.

Do not assume the largest batch is best.

---

# 54. JSON Schema Exercise

Generate:

```python
schema = Customer.model_json_schema()
```

Inspect:

- properties;
- required fields;
- field types;
- constraints;
- enums;
- nested schemas.

Ask:

> Could another team understand the expected record structure from this schema without reading the Python implementation?

Then identify which contract information is still missing.

---

# 55. Interview Questions — Basic

## Basic 1 — What is `BaseModel`?

**Interviewer intent:** Determine whether the candidate understands the core Pydantic abstraction.

**Expected reasoning:** `BaseModel` defines a typed structure and provides parsing, validation, serialization, and schema generation.

**Strong answer:** A Pydantic `BaseModel` is a typed model that defines a structured validation boundary. It can parse external input, validate it against declared types and constraints, expose structured errors, and serialize the validated representation.

**Common weak answer:** "It is a Python class for storing data."

**Follow-up:** Why is that insufficient for an ingestion boundary?

---

## Basic 2 — What is a required field?

**Interviewer intent:** Check schema fundamentals.

**Expected reasoning:** A field without a default is required.

**Strong answer:** A required field must be supplied by the input for successful model construction.

**Common weak answer:** "A field whose type is not optional."

**Follow-up:** Is `str | None` automatically the same as an omitted optional field?

---

## Basic 3 — What is the difference between optional and nullable?

**Interviewer intent:** Test subtle schema semantics.

**Expected reasoning:** Nullable concerns whether `None` is allowed; optional concerns whether the field may be omitted.

**Strong answer:** `str | None = None` expresses both omission and `None` as a default, while `str | None` expresses a nullable field without necessarily giving it an omission default.

**Common weak answer:** "They are exactly the same."

**Follow-up:** Why does this matter in source contracts?

---

## Basic 4 — What does `model_validate()` do?

**Interviewer intent:** Check Pydantic v2 fundamentals.

**Expected reasoning:** It validates Python data against a model.

**Strong answer:** `Model.model_validate(data)` takes Python data such as a dictionary, validates/parses it according to the model, and returns a model instance or raises `ValidationError`.

**Common weak answer:** "It converts a dictionary into a class."

**Follow-up:** How does it differ from `model_validate_json()`?

---

## Basic 5 — What does `model_validate_json()` do?

**Interviewer intent:** Test boundary awareness.

**Expected reasoning:** It validates JSON input directly.

**Strong answer:** It validates JSON data against a model and returns a model instance.

**Common weak answer:** "It validates a Python dictionary."

**Follow-up:** What input representation would you use for each API?

---

## Basic 6 — What is `ValidationError`?

**Interviewer intent:** Check error handling.

**Expected reasoning:** Pydantic raises it when input cannot satisfy the model.

**Strong answer:** `ValidationError` contains structured validation failures that can be inspected using `errors()`.

**Common weak answer:** "It is just a string error."

**Follow-up:** Why should production systems prefer structured error data?

---

## Basic 7 — What is `Field` used for?

**Interviewer intent:** Test constraints.

**Expected reasoning:** `Field` supplies metadata and constraints.

**Strong answer:** `Field` can express rules such as greater-than, greater-than-or-equal, length, pattern, defaults, and metadata.

**Common weak answer:** "It declares a field."

**Follow-up:** How can `Annotated` be used with `Field`?

---

## Basic 8 — What is `Literal`?

**Interviewer intent:** Test finite-value modeling.

**Expected reasoning:** It restricts a field to specific literal values.

**Strong answer:** `Literal["pending", "paid"]` constrains the field to those exact values.

**Common weak answer:** "It is a Python enum."

**Follow-up:** When would you use an Enum instead?

---

## Basic 9 — What is an Enum?

**Interviewer intent:** Test reusable domain values.

**Expected reasoning:** Enum represents a reusable finite vocabulary.

**Strong answer:** Enums provide named members for finite domain values and improve reuse and readability.

**Common weak answer:** "It is just a list."

**Follow-up:** How does it help schema generation?

---

## Basic 10 — Why validate records at the boundary?

**Interviewer intent:** Test data-engineering reasoning.

**Expected reasoning:** Early validation localizes defects and protects downstream systems.

**Strong answer:** External data is untrusted. Validating it before transformation prevents malformed records from propagating and gives the pipeline structured, source-localized failures.

**Common weak answer:** "Because validation is good practice."

**Follow-up:** Which quality checks still belong later in the pipeline?

---

# 56. Interview Questions — Moderate

## Moderate 1 — What is coercion?

**Interviewer intent:** Check understanding of Pydantic parsing behavior.

**Expected reasoning:** Compatible input representations may be converted.

**Strong answer:** Coercion allows certain inputs to be converted into the target field type. It improves integration convenience but can hide producer contract violations.

**Common weak answer:** "Pydantic always converts everything."

**Follow-up:** When would you prefer strict validation?

---

## Moderate 2 — Is strict validation always better?

**Interviewer intent:** Evaluate engineering judgment.

**Expected reasoning:** Strictness is context-dependent.

**Strong answer:** No. Strict validation improves visibility of source defects but can reduce compatibility with messy sources. The correct choice depends on the contract and operational consequences.

**Common weak answer:** "Yes, strict is always safest."

**Follow-up:** Give a case where lax parsing is reasonable.

---

## Moderate 3 — Why use `Decimal` for monetary data?

**Interviewer intent:** Test numerical correctness.

**Expected reasoning:** Binary floating-point can represent decimal values approximately.

**Strong answer:** `Decimal` provides decimal arithmetic appropriate for exact monetary semantics when the business contract requires it.

**Common weak answer:** "Decimal is more precise because it has more digits."

**Follow-up:** What else does a financial contract need besides Decimal?

---

## Moderate 4 — Why use timezone-aware timestamps?

**Interviewer intent:** Test distributed-system reasoning.

**Expected reasoning:** Naive timestamps are ambiguous.

**Strong answer:** Aware timestamps carry timezone/offset information and reduce ambiguity in ordering, partitioning, SLA measurement, and cross-region pipelines.

**Common weak answer:** "UTC is always required."

**Follow-up:** Is UTC the same thing as timezone awareness?

---

## Moderate 5 — What is a nested model?

**Interviewer intent:** Check structured-schema design.

**Expected reasoning:** One Pydantic model can contain another.

**Strong answer:** Nested models let complex payloads be validated recursively while preserving logical structure.

**Common weak answer:** "A model inside another class."

**Follow-up:** How are nested errors represented?

---

## Moderate 6 — When would you use a field validator?

**Interviewer intent:** Test validator scope.

**Expected reasoning:** Field-specific rules or controlled normalization.

**Strong answer:** Use `field_validator` when the rule belongs to one field, such as normalization or a field-specific invariant.

**Common weak answer:** "Whenever there is validation."

**Follow-up:** When would a model validator be more appropriate?

---

## Moderate 7 — What is a model validator?

**Interviewer intent:** Test cross-field validation.

**Expected reasoning:** It validates relationships involving multiple fields.

**Strong answer:** `model_validator` is appropriate when correctness depends on multiple fields, such as start/end timestamps or total calculations.

**Common weak answer:** "A validator for the whole database."

**Follow-up:** Explain `mode="after"`.

---

## Moderate 8 — Explain `extra="forbid"`.

**Interviewer intent:** Test schema-evolution awareness.

**Expected reasoning:** Unexpected fields fail validation.

**Strong answer:** `extra="forbid"` makes the boundary strict about undeclared fields. It can expose source schema changes early but can also reduce forward compatibility.

**Common weak answer:** "It ignores extra fields."

**Follow-up:** Compare it with `ignore`.

---

## Moderate 9 — Why use aliases?

**Interviewer intent:** Test boundary separation.

**Expected reasoning:** External and internal naming can differ.

**Strong answer:** Aliases allow external names such as `customerId` while internal code uses `customer_id`.

**Common weak answer:** "Aliases are only for shorter names."

**Follow-up:** How do you serialize using aliases?

---

## Moderate 10 — What is safe serialization?

**Interviewer intent:** Test security awareness.

**Expected reasoning:** Output must intentionally exclude sensitive data.

**Strong answer:** Safe serialization means selecting what leaves the boundary, excluding secrets and sensitive fields where appropriate, and avoiding accidental logging.

**Common weak answer:** "Call `model_dump_json()`."

**Follow-up:** Why is serialization exclusion not access control?

---

# 57. Interview Questions — Hard

## Hard 1 — Why use discriminated unions?

**Interviewer intent:** Test event-schema architecture.

**Expected reasoning:** Different event types have different required structures.

**Strong answer:** A discriminator selects the correct event-specific model, making heterogeneous payloads explicit and preventing a giant model full of unrelated optional fields.

**Common weak answer:** "They let you combine classes."

**Follow-up:** What is the discriminator field?

---

## Hard 2 — Why use `TypeAdapter`?

**Interviewer intent:** Test advanced Pydantic usage.

**Expected reasoning:** Some validation targets are types rather than models.

**Strong answer:** `TypeAdapter` validates arbitrary Pydantic-supported types such as `list[Customer]` or discriminated unions and is useful for bulk validation.

**Common weak answer:** "It is another BaseModel."

**Follow-up:** How would you benchmark it?

---

## Hard 3 — How would you validate one million records?

**Interviewer intent:** Test scale reasoning.

**Expected reasoning:** Avoid assuming per-record instantiation is optimal.

**Strong answer:** Benchmark per-record and `TypeAdapter` approaches, use bounded batches when necessary, measure records/sec and memory, preserve per-record errors, and avoid loading an unnecessarily large dataset into memory.

**Common weak answer:** "Put all one million into a list and validate."

**Follow-up:** What changes if the input is JSONL?

---

## Hard 4 — How do you collect invalid records without failing the whole batch?

**Interviewer intent:** Test resilient ingestion.

**Expected reasoning:** Separate valid and invalid outcomes.

**Strong answer:** Validate records independently or in controlled batches, collect structured errors alongside original records, and route invalid records toward quarantine according to batch policy.

**Common weak answer:** "Catch the exception and continue."

**Follow-up:** What metadata should be retained?

---

## Hard 5 — What is JSON Schema?

**Interviewer intent:** Test contract thinking.

**Expected reasoning:** Machine-readable schema.

**Strong answer:** JSON Schema describes structure, types, required fields, and constraints in a language/tool-friendly form. Pydantic can generate it from models.

**Common weak answer:** "It is the JSON output of Pydantic."

**Follow-up:** Is JSON Schema a complete data contract?

---

## Hard 6 — When does Pydantic become too slow?

**Interviewer intent:** Test performance judgment.

**Expected reasoning:** Workload shape matters.

**Strong answer:** When row-level object validation becomes a material fraction of pipeline cost, especially at massive tabular scale, the validation boundary should be reconsidered and benchmarked. DataFrame- or table-level validation may be more appropriate.

**Common weak answer:** "Pydantic is slow for big data."

**Follow-up:** What measurements would you collect?

---

## Hard 7 — Why not use one giant Pydantic model for every event?

**Interviewer intent:** Test schema modeling.

**Expected reasoning:** Heterogeneous events have different invariants.

**Strong answer:** Giant optional-field models allow invalid combinations and obscure event-specific rules. Discriminated unions make event-specific structure explicit.

**Common weak answer:** "It becomes a big class."

**Follow-up:** What does the discriminator accomplish?

---

## Hard 8 — What is the danger of `extra="ignore"`?

**Interviewer intent:** Test schema-evolution reasoning.

**Expected reasoning:** New fields may disappear silently.

**Strong answer:** Ignoring unexpected fields can preserve compatibility but may hide upstream schema changes and cause consumers to miss important data.

**Common weak answer:** "It is insecure."

**Follow-up:** When might ignore be appropriate?

---

## Hard 9 — How do custom validators affect performance?

**Interviewer intent:** Test practical optimization.

**Expected reasoning:** Python-level logic adds cost.

**Strong answer:** Custom validators execute application logic and can become significant at high throughput, especially if they perform complex computation or accidental I/O.

**Common weak answer:** "Validators are free."

**Follow-up:** Should validators call external APIs?

---

## Hard 10 — Why separate external and domain models?

**Interviewer intent:** Test architecture.

**Expected reasoning:** Source representation and internal meaning evolve independently.

**Strong answer:** Separation prevents external naming quirks, source schema changes, and transport concerns from leaking into domain logic.

**Common weak answer:** "Because clean code."

**Follow-up:** Where does the database model fit?

---

# 58. Interview Questions — Advanced

## Advanced 1 — Design a production API validation boundary

**Interviewer intent:** Test end-to-end architecture.

**Expected reasoning:**

```text
raw API payload
 -> Pydantic
 -> valid/error split
 -> domain model
 -> transformation
 -> storage
```

**Strong answer:** Treat input as untrusted, validate explicitly, preserve structured errors, apply source-specific aliases and strictness, isolate sensitive fields, and instrument rejection rates.

**Common weak answer:** "Create a BaseModel and call it."

**Follow-up:** How would you monitor schema drift?

---

## Advanced 2 — Separate API, domain, and database models

**Interviewer intent:** Test coupling awareness.

**Expected reasoning:** Each layer has different ownership.

**Strong answer:**

```text
API schema
   |
domain schema
   |
database schema
```

with explicit transformations between them.

**Common weak answer:** "Use one model everywhere to avoid duplication."

**Follow-up:** When could sharing a model be acceptable?

---

## Advanced 3 — Handle schema evolution

**Interviewer intent:** Test compatibility strategy.

**Expected reasoning:** Unexpected fields, versions, producer ownership, and consumer behavior matter.

**Strong answer:** Choose `ignore`, `allow`, or `forbid` intentionally; monitor source changes; version schemas where appropriate; define compatibility expectations; test producer changes.

**Common weak answer:** "Always forbid extra fields."

**Follow-up:** What is the operational downside?

---

## Advanced 4 — Integrate validation with quarantine

**Interviewer intent:** Test production resilience.

**Expected reasoning:** Invalid records need traceability.

**Strong answer:** Preserve original payload plus structured errors and operational metadata, then route to a controlled quarantine store or dead-letter mechanism.

**Common weak answer:** "Write invalid data to a log."

**Follow-up:** Why is a plain log insufficient?

---

## Advanced 5 — Design validation for a million JSON records

**Interviewer intent:** Test performance architecture.

**Expected reasoning:** Memory and throughput.

**Strong answer:** Use appropriate JSON validation APIs, benchmark `TypeAdapter`, process bounded batches or JSONL incrementally where appropriate, collect errors efficiently, and measure peak memory.

**Common weak answer:** "Load the whole JSON into memory."

**Follow-up:** What changes if records are 50 KB each?

---

## Advanced 6 — Decide strict versus lax validation

**Interviewer intent:** Test judgment.

**Expected reasoning:** Contract, source quality, failure cost.

**Strong answer:** Strictness should be chosen per boundary and field based on whether coercion represents legitimate normalization or hides producer defects.

**Common weak answer:** "Strict is production-grade."

**Follow-up:** Give an example where coercion is legitimate.

---

## Advanced 7 — Move validation from Pydantic to DataFrame-level validation

**Interviewer intent:** Test scale and layer awareness.

**Expected reasoning:** Record-level versus column/table-level.

**Strong answer:** Keep Pydantic at the ingestion boundary, then use DataFrame-oriented validation when the dominant question is about columns, distributions, dataset-level rules, or large tabular scale.

**Common weak answer:** "Pydantic cannot validate DataFrames."

**Follow-up:** Could Pydantic still validate the source records before the DataFrame?

---

## Advanced 8 — Design sensitive serialization

**Interviewer intent:** Test security.

**Expected reasoning:** Explicit output schemas and redaction.

**Strong answer:** Use deliberate serialization projections, exclude secrets, avoid logging raw payloads, and enforce access controls separately.

**Common weak answer:** "Use exclude."

**Follow-up:** Where else can sensitive data leak?

---

## Advanced 9 — Use Pydantic as a data-contract component

**Interviewer intent:** Test contract architecture.

**Expected reasoning:** Model plus ownership/versioning/compatibility/quality.

**Strong answer:** Pydantic can provide executable record structure and JSON Schema, but a data contract also needs ownership, versioning, compatibility rules, quality expectations, and operational responsibilities.

**Common weak answer:** "Pydantic is the data contract."

**Follow-up:** What is missing?

---

## Advanced 10 — Explain the ORM boundary

**Interviewer intent:** Test database architecture.

**Expected reasoning:** Persistence and external contracts are different concerns.

**Strong answer:** ORM models represent persistence and may contain relationships, internal fields, or database-specific concerns. External Pydantic models should define the actual boundary contract.

**Common weak answer:** "ORM and Pydantic are interchangeable."

**Follow-up:** What security problem can arise from direct reuse?

---

# 59. Architecture Questions

## 59.1 Design validation for a high-volume API ingestion pipeline

Address:

```text
API
 |
raw payload
 |
Pydantic validation
 |
+---- valid ----> transformation
|
+---- invalid --> quarantine
```

Discuss:

- concurrency;
- model complexity;
- strictness;
- retries;
- error rates;
- schema version;
- source ownership;
- observability;
- backpressure.

Do not let validation failures become invisible.

---

## 59.2 Five payment event types

Design:

```text
PaymentEvent
 |
 +-- succeeded
 +-- failed
 +-- refund
 +-- authorized
 +-- reversed
```

Use a discriminator.

Explain:

- event-specific required fields;
- common envelope;
- type-safe branching;
- invalid discriminator behavior;
- schema evolution.

---

## 59.3 Strict versus lax for an external source

Evaluate:

```text
Source contract
Source reliability
Coercion frequency
Business criticality
Failure cost
Observability
```

Then choose intentionally.

Do not make the decision from ideology.

---

## 59.4 Should one invalid record fail the entire batch?

Consider:

```text
batch size
business criticality
atomicity requirements
source quality
retry strategy
quarantine capability
```

Possible policies:

```text
fail-fast
partial success
bounded error threshold
```

The right policy depends on the ingestion contract.

---

## 59.5 One million JSON records

Consider:

- JSON parsing;
- validation throughput;
- memory;
- batch size;
- TypeAdapter;
- JSONL;
- error storage;
- checkpointing;
- retry behavior.

Benchmark before committing to the implementation.

---

## 59.6 When should validation move to Pandera?

Ask:

```text
Are we validating individual records?
       |
       +-- yes --> Pydantic is appropriate

Are we validating columns across a DataFrame?
       |
       +-- yes --> DataFrame validation is appropriate
```

Pydantic and Pandera can coexist.

---

## 59.7 API/domain/database model separation

Design:

```text
ExternalCustomer
        |
        v
DomainCustomer
        |
        v
CustomerRow
```

Explain where transformations happen.

---

## 59.8 Unexpected source fields

Compare:

```text
ignore
allow
forbid
```

against:

```text
forward compatibility
schema drift visibility
operational stability
```

Choose according to contract strategy.

---

## 59.9 Sensitive serialization

Design separate outputs:

```text
Internal model
     |
     +---- operational log view
     +---- API response view
     +---- warehouse view
```

Do not assume one serialization shape is suitable everywhere.

---

## 59.10 Pydantic as a contract component

A mature design can use:

```text
Pydantic model
      |
      +---- runtime validation
      |
      +---- JSON Schema
      |
      +---- tests
      |
      +---- documentation
      |
      +---- compatibility process
```

The model becomes an executable part of the contract rather than a passive documentation artifact.

---

# 60. Production Checklist

## Boundary

- [ ] Is incoming data treated as untrusted?
- [ ] Is the schema explicit?
- [ ] Are required fields defined?
- [ ] Are types defined?
- [ ] Are constraints defined?
- [ ] Is validation performed before downstream transformation?

## Validation

- [ ] Are coercion decisions intentional?
- [ ] Are strictness decisions documented?
- [ ] Are cross-field rules implemented?
- [ ] Are unexpected fields handled intentionally?
- [ ] Are timezone-aware timestamps used where appropriate?
- [ ] Are monetary values represented appropriately?

## Errors

- [ ] Are validation errors structured?
- [ ] Can invalid records be isolated?
- [ ] Is the original record preserved when needed?
- [ ] Can failures be traced to the source?
- [ ] Is a schema/model version recorded where useful?

## Performance

- [ ] Is validation fast enough?
- [ ] Has bulk validation been benchmarked?
- [ ] Is memory bounded?
- [ ] Is batch size intentional?
- [ ] Are custom validators efficient?
- [ ] Is Pydantic being used at the correct data scale?

## Serialization

- [ ] Are aliases correct?
- [ ] Are sensitive fields excluded?
- [ ] Is serialization deterministic?
- [ ] Are different consumers given appropriate projections?
- [ ] Are secrets kept out of logs?

## Architecture

- [ ] Is the external model separated from the domain model?
- [ ] Is the database model separated where necessary?
- [ ] Is JSON Schema generated where useful?
- [ ] Is schema evolution considered?
- [ ] Is quarantine connected to invalid-record handling?
- [ ] Are table-level checks handled by an appropriate later layer?

---

# 61. Checkpoint

You should now be able to complete the following self-tests.

## Self-test 1

Write a model containing:

```text
id
email
country
created_at
```

and validate a dictionary.

- [ ] I can create `BaseModel`.
- [ ] I can define types.
- [ ] I can validate a dictionary.

## Self-test 2

Explain:

```text
str | None
```

versus:

```text
str | None = None
```

- [ ] I understand nullable versus omitted/defaulted fields.

## Self-test 3

Write:

```python
Annotated[int, Field(gt=0)]
```

- [ ] I can express a numeric constraint.

## Self-test 4

Model:

```text
payment_succeeded
payment_failed
refund_issued
```

with a discriminator.

- [ ] I can build a discriminated union.

## Self-test 5

Validate:

```python
list[Customer]
```

with `TypeAdapter`.

- [ ] I understand bulk validation.

## Self-test 6

Given one invalid record in a batch:

- [ ] I can preserve the original record.
- [ ] I can collect `ValidationError.errors()`.
- [ ] I can separate valid and invalid outputs.

## Self-test 7

Generate:

```python
Customer.model_json_schema()
```

- [ ] I understand why JSON Schema matters.

## Self-test 8

Given a 100-million-row DataFrame:

- [ ] I can explain why Pydantic row-by-row validation may be inappropriate.
- [ ] I can identify DataFrame-level validation as a different layer.

## Self-test 9

Given an ORM model containing:

```text
password_hash
internal_notes
created_by
```

- [ ] I can explain why it should not automatically become an API schema.

## Self-test 10

Explain this statement:

> Pydantic is a record-level validation boundary, not a replacement for all data quality systems.

If you can explain that precisely, you understand the central architectural idea of this chapter.

---

# 62. Common Mistakes

## Mistake 1 — Accepting silent coercion from sources you do not control

### Why it happens

Coercion makes integrations appear robust.

### Why it is dangerous

A source contract can be broken without anyone noticing.

### Better practice

Decide which coercions are legitimate and monitor meaningful source deviations.

---

## Mistake 2 — Using naive datetimes

### Why it happens

Naive timestamps are easy to construct.

### Why it is dangerous

The timestamp may be ambiguous across systems and time zones.

### Better practice

Use timezone-aware timestamps at system boundaries where time-zone semantics matter.

---

## Mistake 3 — Using `extra="allow"` everywhere

### Why it happens

It appears flexible.

### Why it is dangerous

Unexpected schema changes may become invisible.

### Better practice

Choose `allow`, `ignore`, or `forbid` according to compatibility requirements.

---

## Mistake 4 — Validating massive tables row by row with Pydantic

### Why it happens

Pydantic is convenient.

### Why it is dangerous

Object construction and Python-level validation can become a large computational and memory cost.

### Better practice

Use Pydantic at the record boundary and appropriate DataFrame/table validation downstream.

---

## Mistake 5 — Using validators for transformations that belong elsewhere

### Why it happens

Validators are convenient places to put logic.

### Why it is dangerous

Models become difficult to understand and expensive to execute.

### Better practice

Keep validators focused on boundary normalization and validation.

---

## Mistake 6 — Creating overly complex models

### Why it happens

Developers try to encode every possible business rule in one model.

### Why it is dangerous

Complex models become difficult to test, evolve, and debug.

### Better practice

Use the simplest model that expresses the boundary contract.

---

## Mistake 7 — Hiding source-quality problems through normalization

### Why it happens

Normalization makes downstream data cleaner.

### Why it is dangerous

The source can continue sending defective data unnoticed.

### Better practice

Normalize only when the transformation is an accepted part of the boundary contract, and measure meaningful source deviations.

---

## Mistake 8 — Logging sensitive serialized models

### Why it happens

`model_dump()` is convenient for debugging.

### Why it is dangerous

Passwords, tokens, and PII can enter logs.

### Better practice

Use explicit safe projections and redaction.

---

## Mistake 9 — Treating Pydantic as a replacement for table-level quality checks

### Why it happens

Pydantic feels comprehensive.

### Why it is dangerous

Record-level validity does not prove dataset-level quality.

### Better practice

Use appropriate DataFrame, dataset, reconciliation, and observability checks.

---

## Mistake 10 — Reusing ORM models blindly as API schemas

### Why it happens

It appears to eliminate duplicate code.

### Why it is dangerous

Internal database fields and relationships can leak into external contracts.

### Better practice

Separate external, domain, and persistence representations where necessary.

---

## Mistake 11 — Failing to benchmark bulk validation

### Why it happens

Developers assume the fastest-looking API is fastest.

### Why it is dangerous

Real payload shape, validators, and memory behavior can change the result.

### Better practice

Measure actual records/sec, runtime, and memory in a representative environment.

---

## Mistake 12 — Discarding invalid records without traceability

### Why it happens

The easiest implementation is:

```python
except ValidationError:
    continue
```

### Why it is dangerous

Records disappear without explanation.

### Better practice

Preserve the original record, structured errors, source context, and operational metadata as required.

---

# 63. A Practical Validation Boundary Template

A useful high-level pattern is:

```python
from pydantic import BaseModel, ValidationError


class InputModel(BaseModel):
    ...


def validate_record(payload: dict) -> InputModel:
    return InputModel.model_validate(payload)


def process_record(payload: dict):
    try:
        record = validate_record(payload)
    except ValidationError as exc:
        return {
            "status": "invalid",
            "record": payload,
            "errors": exc.errors(),
        }

    return {
        "status": "valid",
        "record": record,
    }
```

The production implementation will need more context, but the separation is valuable:

```text
validation
    !=
business processing
```

The boundary establishes a clean transition.

---

# 64. A Production-Grade Mental Model for Errors

Think of every invalid record as an operational event.

```text
Invalid Record
     |
     +-- What source?
     |
     +-- Which record?
     |
     +-- Which model/version?
     |
     +-- Which field?
     |
     +-- Which rule?
     |
     +-- What input?
     |
     +-- Can it be retried?
     |
     +-- Can it be quarantined?
     |
     +-- Is the producer responsible?
```

This is much more useful than:

```text
Validation failed
```

Structured errors turn validation into an observable engineering boundary.

---

# 65. Relationship to Data Quality Dimensions

The previous topic established dimensions such as:

- accuracy;
- completeness;
- validity;
- consistency;
- uniqueness;
- timeliness;
- freshness;
- integrity;
- conformity;
- availability.

Pydantic primarily helps with record-level properties such as:

```text
validity
conformity
structural completeness
type correctness
field-level consistency
cross-field consistency
```

It does not automatically prove:

```text
dataset uniqueness
warehouse freshness
cross-source reconciliation
distribution stability
historical anomaly absence
```

That distinction is essential.

A record can be perfectly valid and still contribute to a bad dataset.

For example:

```text
Every row has:
valid UUID
valid timestamp
valid currency
valid amount
```

but:

```text
today's row count is 90% below expected
```

Pydantic does not detect that table-level problem.

---

# 66. Relationship to Schema Evolution

A Pydantic model represents a consumer-side view of a source schema.

When producers change their payloads, consumers must consider:

```text
added field
removed field
renamed field
type change
semantic change
new event type
```

Pydantic configuration affects the behavior of some changes.

For example:

```text
extra="ignore"
```

may tolerate added fields.

```text
extra="forbid"
```

may expose added fields immediately.

Neither strategy solves schema evolution by itself.

A mature system also needs:

- versioning;
- ownership;
- compatibility rules;
- communication;
- tests;
- deployment coordination.

Those concerns are developed further in later topics.

---

# 67. Relationship to Quarantine

Validation creates a natural branching point:

```text
             Pydantic
                |
        +-------+-------+
        |               |
      valid           invalid
        |               |
        v               v
    pipeline         quarantine
```

The invalid branch should preserve enough context for:

- diagnosis;
- replay;
- correction;
- producer feedback;
- metrics.

Do not build the complete quarantine platform inside the Pydantic model.

Keep the model responsible for validation.

Keep the pipeline responsible for routing.

---

# 68. Relationship to PostgreSQL and Persistence

A validated Pydantic record may eventually be written to PostgreSQL.

The architecture can be:

```text
External Payload
      |
      v
Pydantic
      |
      v
Domain representation
      |
      v
SQLAlchemy / SQL
      |
      v
PostgreSQL
```

The validation model does not replace database constraints.

For example, PostgreSQL may still enforce:

- primary keys;
- unique constraints;
- foreign keys;
- not-null constraints;
- check constraints.

Defense in depth is valuable:

```text
source boundary validation
        +
domain validation
        +
database constraints
```

Each layer protects a different boundary.

---

# 69. Relationship to Bronze, Silver, and Gold

A common lakehouse conceptual flow is:

```text
External Source
      |
      v
Bronze / Raw
      |
      v
Validated / Transformed
      |
      v
Silver
      |
      v
Gold
```

Pydantic can operate near the ingestion boundary before or during raw-to-validated processing.

Do not assume that Pydantic makes the entire bronze layer "clean."

A raw landing layer may intentionally preserve source payloads for:

- replay;
- audit;
- debugging;
- forensic analysis.

The important distinction is:

```text
raw preservation
        !=
trusted processing
```

Pydantic establishes a trusted record representation for downstream processing.

---

# 70. JSONL and Replayability

One benefit of explicit serialization is reproducibility.

A validated record can be serialized to JSONL:

```text
record 1
record 2
record 3
...
```

If the pipeline retains sufficient metadata, a failed transformation can potentially be replayed from a known validated representation.

This is particularly useful for:

- debugging;
- backfills;
- deterministic tests;
- downstream reprocessing.

However, replay design must consider:

- schema version;
- source version;
- model version;
- transformations;
- external dependencies.

Serialization alone does not make a pipeline replayable.

---

# 71. A Small End-to-End Example

The following combines several concepts without trying to build an entire production platform.

```python
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    TypeAdapter,
    ValidationError,
    field_validator,
)


PositiveQuantity = Annotated[int, Field(gt=0)]


class Customer(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    customer_id: UUID
    email: EmailStr
    country: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> EmailStr:
        return EmailStr(str(value).lower())


class CustomerBatch(BaseModel):
    customers: list[Customer]


def validate_batch(records: list[dict]):
    adapter = TypeAdapter(list[Customer])

    try:
        customers = adapter.validate_python(records)
        return {
            "valid": customers,
            "invalid": [],
        }
    except ValidationError as exc:
        return {
            "valid": [],
            "invalid": exc.errors(),
        }
```

This demonstrates:

- `BaseModel`;
- configuration;
- typed fields;
- `UUID`;
- `EmailStr`;
- normalization;
- `TypeAdapter`;
- structured errors.

For production, per-record error collection may be preferable to treating the entire bulk operation as one atomic success/failure. The appropriate policy depends on business requirements.

---

# 72. Designing the Validation Boundary

When designing a new ingestion boundary, ask these questions in order.

## Question 1 — What is the input?

```text
API?
Webhook?
SFTP?
Kafka?
JSONL?
Configuration?
```

## Question 2 — What does the source contract say?

Identify:

- field names;
- required fields;
- types;
- allowed values;
- timestamp semantics;
- identifier semantics.

## Question 3 — Which values are allowed to be normalized?

Examples:

```text
whitespace
case
representation
```

Document the decision.

## Question 4 — Which values must be strict?

Examples:

```text
financial amount
critical identifier
contracted integer
```

## Question 5 — What happens to unknown fields?

Choose:

```text
ignore
allow
forbid
```

intentionally.

## Question 6 — What happens to invalid records?

Choose:

```text
fail batch
partial success
quarantine
retry
```

according to business requirements.

## Question 7 — How will errors be observed?

Track:

- validation error count;
- error type;
- field;
- source;
- producer;
- schema version.

## Question 8 — Is the workload still record-oriented?

If the workload becomes a huge table:

```text
record validation
       |
       v
DataFrame validation
       |
       v
dataset validation
```

choose the right layer.

---

# 73. Final Mental Model

The central model is:

```text
External Data
     |
     v
Untrusted Payload
     |
     v
Pydantic Model
     |
     v
Parse + Validate
     |
     +----------------------+
     |                      |
     v                      v
  Valid                  Invalid
     |                      |
     v                      v
Internal Model         Structured Errors
     |                      |
     v                      v
Pipeline              Quarantine /
                      Failure Handling
```

Pydantic can be summarized as:

```text
Pydantic
=
record-level boundary validation
+
typed representation
+
controlled normalization
+
structured errors
+
serialization
+
machine-readable schema
```

And the broader validation architecture is:

```text
Individual Record
      |
      v
   Pydantic

DataFrame
      |
      v
   Pandera

Table / Dataset
      |
      v
 GX / Soda / SQL

Pipeline / Producer Agreement
      |
      v
 Data Contracts
```

The production principle is:

> **Pydantic is most valuable when it creates a trustworthy boundary between untrusted external data and the internal data pipeline.**

Once a record crosses that boundary, downstream code can operate with explicit assumptions rather than repeatedly defending itself against unknown input.

The engineering maturity comes from knowing not only how to define the model, but also:

- where to validate;
- what to reject;
- what to normalize;
- what to preserve;
- how to report failures;
- how to handle schema changes;
- how to protect sensitive fields;
- how to measure performance;
- when to move validation to another layer.

That is the difference between merely knowing Pydantic syntax and designing a production-grade data validation boundary.
