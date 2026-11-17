# 03 — Normalization and Relational Modeling

> **Roadmap location:** Stage 2D — Data Architecture → `04-Conceptual-Logical-and-Physical-Data-Modeling/` → `03-normalization-and-relational-modeling.md`  
> **Audience:** Beginner to advanced; assumes Module 2 (entities, relationships, cardinality, identifiers and constraints) and basic SQL `SELECT`/`JOIN`.  
> **Scope:** First, Second and Third Normal Forms (1NF, 2NF, 3NF), plus Boyce–Codd Normal Form (BCNF). 4NF and 5NF are out of scope.  
> **Case-study note:** Northbridge Bank is an illustrative teaching scenario, not a claim about a real institution. Business rules not provided are explicit assumptions to validate with stakeholders.

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Translate a logical model into relations, tuples, attributes, domains, candidate keys, primary keys and foreign keys.
2. Explain how repeated facts create insertion, update and deletion anomalies.
3. State functional dependencies (FDs) from business rules, identify determinants, and distinguish a valid FD from a coincidence in sample data.
4. Derive candidate keys—including composite keys—from a relation's attributes and FD set.
5. Test a relation against 1NF, 2NF, 3NF and BCNF using its declared business rules and candidate keys.
6. Decompose relations while proving lossless join and evaluating dependency preservation.
7. Design PK, FK, `UNIQUE`, `NOT NULL`, `CHECK` and other constraints to protect data integrity.
8. Explain nullable foreign keys without confusing `NULL` with a missing parent row or an optional entity.
9. Recognize under-normalization, over-decomposition and generic name/value designs that hide business structure.
10. Separate logical normalization from physical denormalization and justify the latter with measured workload evidence, a named consistency owner and a control mechanism.
11. Review the Northbridge accounts/payments model, document defects and dependencies, and produce a defensible denormalization decision record.

## 2. Why the topic matters in real-world Data Architecture

Normalization makes the structure of stored facts agree with business rules. In an operational model, a fact such as a customer's legal name should have one authoritative place unless a second copy has a clearly different meaning—for example, a historical snapshot of the name at the time a transaction was legally recorded.

A normalized design is not simply “many tables.” It is a design in which each relation's attributes are justified by its keys and dependencies, and decomposition preserves the facts represented by the original relation. A poor decomposition can lose information, require expensive joins to enforce a rule, or create confusing tables without improving integrity.

### 2.1 Start with a deliberately flawed order/customer/product relation

Suppose an order export stores one row per order, with product details embedded in lists:

| order_id | order_date | customer_id | customer_name | customer_city | product_ids | product_names | quantities |
|---|---|---|---|---|---|---|---|
| O-101 | 2026-10-01 | C-10 | Asha Rao | Pune | P-1, P-2 | Loan A, Card B | 1, 2 |
| O-102 | 2026-10-02 | C-10 | Asha Rao | Pune | P-2 | Card B | 1 |
| O-103 | 2026-10-03 | C-20 | Ben Cole | Leeds | P-1 | Loan A | 2 |

This relation is deliberately flawed for a relational design: `product_ids`, `product_names` and `quantities` contain repeating groups encoded as lists. The lists rely on positional alignment—item 2 in `product_ids` must correspond to item 2 in `product_names` and `quantities`. A missing or reordered item can silently pair the wrong product and quantity. A query cannot safely treat each product as an independent row without parsing the cells.

Now imagine splitting the lists into one row per order line but continuing to copy customer and product descriptions into every row:

| order_id | order_date | customer_id | customer_name | customer_city | product_id | product_name | qty |
|---|---|---|---|---|---|---|---:|
| O-101 | 2026-10-01 | C-10 | Asha Rao | Pune | P-1 | Loan A | 1 |
| O-101 | 2026-10-01 | C-10 | Asha Rao | Pune | P-2 | Card B | 2 |
| O-102 | 2026-10-02 | C-10 | Asha Rao | Pune | P-2 | Card B | 1 |
| O-103 | 2026-10-03 | C-20 | Ben Cole | Leeds | P-1 | Loan A | 2 |

Assume an order can contain a given product at most once, so the declared key for this line-grain relation is `(order_id, product_id)`. If the business permits multiple separate lines for the same product in one order, this key is insufficient; use an `order_line_id` or `(order_id, line_number)` instead. A key must reflect actual grain and business rules, not merely fit today's sample.

### 2.2 The three anomalies

- **Update anomaly:** Asha moves from Pune to Mumbai. If only some rows are updated, the same `customer_id` has contradictory cities. Repeated copies turn one business fact into multiple write locations.
- **Insertion anomaly:** A new customer cannot be represented in this order-line relation until the customer places an order, unless the design allows a dummy order or nullable line fields. That is a schema-design problem, not a reason to invent fake business data.
- **Deletion anomaly:** If O-102 is the only order containing Card B and deleting its last line also removes the only copy of `product_name = Card B`, product information is lost even though the product still exists.

Redundancy is not automatically harmful: a repeated value may be an intentional historical snapshot or a measured physical optimization. Ask whether duplicated values represent the same fact, whether they can disagree, and who owns their consistency.

### 2.3 Relational vocabulary

| Term | Meaning | Practical implication |
|---|---|---|
| **Relation** | A set of tuples over named attributes, governed by a predicate/business meaning. A SQL table approximates this idea, though SQL tables can allow duplicates and `NULL`. | Define row meaning and grain before choosing columns. |
| **Tuple** | One row/fact instance in a relation. | A tuple must satisfy the relation's constraints. |
| **Attribute** | A named component of a tuple, analogous to a column. | Give it one stable meaning and a defined domain. |
| **Domain** | The permitted values and semantic type for an attribute. | A quantity, currency amount, account status and identifier should not be interchangeable strings. |
| **Candidate key** | A minimal set of attributes that uniquely identifies every tuple under business rules. | “Minimal” means no proper subset is also a superkey. |
| **Primary key (PK)** | The candidate key selected as the relation's primary identifier. | Must be unique and non-null; should be stable enough for references. |
| **Foreign key (FK)** | An attribute set whose non-null values must match a referenced candidate/unique key, subject to declared null semantics. | Protects referential integrity, not every business rule. |
| **Superkey** | Any attribute set that uniquely identifies tuples; it may contain unnecessary attributes. | A superkey is not necessarily a candidate key. |
| **Composite key** | A key made of two or more attributes. | Common for line items, memberships and effective-dated associations. |

A relation's name should describe its facts. `OrderLine` means a product line belonging to an order; it is not merely a place to store columns that do not fit elsewhere.

### 2.4 Functional dependencies: the central reasoning tool

A functional dependency (FD) `A → B` means: **under the stated business rules, any two valid tuples that agree on all attributes in set A must also agree on all attributes in set B.** A is the determinant; B is the dependent attribute set.

Examples under our assumptions:

- `customer_id → customer_name, customer_city`: each customer ID identifies one current customer name and city.
- `product_id → product_name`: each product ID identifies one product name.
- `order_id → order_date, customer_id`: each order has one date and one customer.
- `(order_id, product_id) → qty`: within an order, each product appears on at most one line, so the pair determines quantity.

An FD is a rule about all valid states of the modeled business, not a pattern inferred from a tiny sample. If two products happen to have the same name today, that does not prove `product_name → product_id`; names may be duplicated or changed. If the business guarantees unique immutable product names, that is a different rule and must be documented.

A determinant can be one attribute or a set. `A → B` is shorthand for A determining every attribute in set B. It does not mean B causes A, that the relationship is one-to-one in every direction, or that A is necessarily a key.

### 2.5 Keys from dependencies

To test a candidate key, compute the **attribute closure** `X+`: all attributes functionally determined by set X using the declared FDs. If `X+` contains every attribute in the relation, X is a superkey. If no proper subset of X is a superkey, X is a candidate key.

For `R(OrderID, OrderDate, CustomerID, CustomerName, CustomerCity, ProductID, ProductName, Qty)` with FDs:

- `OrderID → OrderDate, CustomerID`
- `CustomerID → CustomerName, CustomerCity`
- `ProductID → ProductName`
- `(OrderID, ProductID) → Qty`

The closure of `{OrderID, ProductID}` contains all attributes:

1. Start with `{OrderID, ProductID}`.
2. From `OrderID → OrderDate, CustomerID`, add `OrderDate` and `CustomerID`.
3. From `CustomerID → CustomerName, CustomerCity`, add customer name and city.
4. From `ProductID → ProductName`, add product name.
5. From `(OrderID, ProductID) → Qty`, add quantity.

The pair is a superkey. Neither `OrderID` alone nor `ProductID` alone determines all line facts, so the pair is a candidate key. This proof depends on the stated assumption that a product occurs at most once per order.

## 3. Prerequisite knowledge

Before continuing, be comfortable with:

- Module 2's entities, relationships, cardinality, optionality, candidate identifiers and referential constraints.
- The difference between a business fact and a screen/report field.
- Basic SQL `SELECT`, `JOIN`, `GROUP BY`, primary keys and foreign keys.
- Sets and simple implication: if A determines B and B determines C, then A determines C (FD transitivity).
- The idea that a schema defines valid states, not just rows currently loaded.

If any prerequisite is weak, review Module 2 before treating the decomposition exercises as formal design review.

## 4. Beginner-level learning sequence

### 4.1 First Normal Form (1NF)

**Rule.** Each attribute position holds one value from its domain for the tuple, rather than a list or repeating group; the relation has a well-defined tuple identity. “Atomic” is relative to model semantics: a postal address may be treated as one value if the application never needs its parts, but if street, city and postal code have independent business meaning, model them as separate attributes or a related entity. 1NF does not mean every string must be split into characters.

**Violation.** The first `OrderExport` table stores `P-1, P-2` and `1, 2` in cells. These are lists, not one product identifier or one quantity per tuple. The relation cannot directly enforce one FK from `product_ids` to `Product` for every list item.

**Reasoning.** Repeating groups make constraints, joins, filtering, updates and indexing ambiguous. A comma-separated string is not a relational substitute for an `OrderLine` relation.

**Correction.** Reshape the order export into one row per order line while preserving all facts:

`R1NF(OrderID, OrderDate, CustomerID, CustomerName, CustomerCity, ProductID, ProductName, Qty)`

Its declared key is `(OrderID, ProductID)` under the one-product-per-order-line assumption. This is an atomic, line-grain representation, not yet a fully normalized decomposition: customer and product descriptions are still repeated and are assessed under 2NF/3NF. `OrderLineDraft(OrderID, ProductID, Qty)` is only a minimal illustration of line grain; by itself it is not a complete replacement for the export because it omits header and descriptive facts. If the same product can be split into multiple lines, use a separate line identifier.

**Integrity checks:** every order-line row references an existing order and product; `Qty` is positive if the business disallows zero/negative quantities; no repeating-list encoding is used for product IDs.

### 4.2 Second Normal Form (2NF)

**Rule.** A relation is in 1NF and every non-prime attribute is fully functionally dependent on every candidate key—there is no dependency of a non-prime attribute on a proper subset of a candidate key. A prime attribute appears in at least one candidate key. In common designs with a single-attribute key, partial dependency on a proper subset cannot occur, but transitive dependencies may still violate 3NF.

**Violation.** In the line-grain relation keyed by `(OrderID, ProductID)`, `OrderDate` depends on `OrderID` alone and `ProductName` depends on `ProductID` alone. Both are proper subsets of the composite key. If these are non-prime attributes, the relation violates 2NF.

**Reasoning.** `OrderDate` repeats for every product in an order; `ProductName` repeats wherever the product is sold. The values depend on only one component of the composite key, not on the full line identity. Updating a product name requires changing multiple lines.

**Correction.** Separate facts that depend on only one component of the original composite key, while preserving the still-transitive customer facts in this intermediate 2NF design:

- `OrderDraft(OrderID PK, OrderDate, CustomerID, CustomerName, CustomerCity)`
- `Product(ProductID PK, ProductName)`
- `OrderLine(OrderID FK, ProductID FK, Qty, PK(OrderID, ProductID))`

This removes partial dependencies on the original line key. `OrderDraft` has a single-attribute key, so it has no partial dependency on a proper subset of that key; however, `CustomerID → CustomerName, CustomerCity` remains, while `OrderID → CustomerID`, so the customer attributes are transitively dependent. The design is therefore not yet 3NF. The next step is to move customer facts into Customer and retain `CustomerID` as the FK in Order.

### 4.3 Third Normal Form (3NF)

**Formal rule.** For every non-trivial FD `X → A`, at least one must hold: (1) X is a superkey, or (2) A is a prime attribute. A common shorthand is “no non-key attribute depends transitively on a candidate key through another non-key attribute,” but the formal definition is safer when candidate keys overlap.

**Violation.** Suppose `Order(OrderID, CustomerID, CustomerName, CustomerCity, OrderDate)` has `OrderID` as its key and the business rules are:

- `OrderID → CustomerID, OrderDate`
- `CustomerID → CustomerName, CustomerCity`

Then `OrderID → CustomerName, CustomerCity` follows transitively through `CustomerID`. `CustomerID` is not a superkey of this Order relation and customer details are not prime attributes. The relation violates 3NF.

**Reasoning.** Customer facts are being stored in an order relation. One customer with many orders creates multiple copies of the same customer name/city. Updating one order's customer city but not another produces inconsistent state.

**Correction.**

- `Customer(CustomerID PK, CustomerName, CustomerCity)`
- `Order(OrderID PK, CustomerID FK, OrderDate)`

The decomposition is lossless because the intersection is `CustomerID`, and `CustomerID` determines every attribute of `Customer`. It preserves the listed dependencies: `CustomerID → CustomerName, CustomerCity` is enforced in `Customer`; `OrderID → CustomerID, OrderDate` is enforced in `Order`.

### 4.4 BCNF (Boyce–Codd Normal Form)

**Scope decision.** This lesson includes BCNF because the target topic's requested scope explicitly includes it and the authoritative roadmap illustrates 1NF, 2NF, 3NF and BCNF. 4NF and 5NF are not added.

**Rule.** A relation is in BCNF if for every non-trivial FD `X → Y` that holds in the relation, X is a superkey. This applies to every candidate-key possibility and every non-trivial FD implied by the business rules—not just the FDs printed in a diagram.

**Violation.** Consider `Teaching(Student, Course, Instructor)` with rules:

- `(Student, Course) → Instructor`: for a student and course, one instructor is assigned.
- `Instructor → Course`: each instructor teaches exactly one course during the modeled term.

Candidate keys are `(Student, Course)` and `(Student, Instructor)`. The second follows because `Instructor → Course`, so `{Student, Instructor}+` contains all attributes. `Instructor` alone is not a superkey because it does not determine Student. Thus `Instructor → Course` violates BCNF.

**Why it can still be 3NF.** `Course` is prime because it belongs to candidate key `(Student, Course)`. For `Instructor → Course`, the RHS is prime, so the 3NF condition is satisfied even though the determinant is not a superkey. This is the classic distinction between 3NF and BCNF.

**BCNF decomposition.**

- `InstructorCourse(Instructor PK, Course)`
- `StudentInstructor(Student, Instructor, PK(Student, Instructor))`

The intersection is `Instructor`. Since `Instructor → Course`, the intersection determines all attributes of `InstructorCourse`; the decomposition is lossless. But `(Student, Course) → Instructor` is not preserved by the projected FDs: neither relation contains both Student and Course, and the join may be required to check whether a student/course pair has more than one instructor. Therefore BCNF can trade dependency preservation for stronger redundancy removal. If that dependency must be enforced without joining tables, a 3NF design may be preferable.

### 4.5 Normal-form summary

| Form | What must be true | Example violation | Typical correction |
|---|---|---|---|
| 1NF | No list-valued/repeating group in a single attribute position; tuples have defined identity. | One order row stores a comma-separated list of product IDs and quantities. | One row per order line. |
| 2NF | 1NF, and no non-prime attribute depends on a proper subset of a candidate key. | `(OrderID, ProductID)` is the key, but `ProductID → ProductName`. | Move product facts to Product. |
| 3NF | For each non-trivial `X → A`, X is a superkey or A is prime. | `OrderID → CustomerID` and `CustomerID → CustomerCity` in Order keyed by OrderID. | Move customer facts to Customer. |
| BCNF | Every determinant of every non-trivial FD is a superkey. | `Instructor → Course` in Teaching when Instructor is not a superkey. | Decompose on the determinant; assess dependency preservation. |

Normal forms are assessed against the complete FD/business-rule set. A table can look tidy and still violate a form because an important business dependency was never written down.

## 5. Intermediate-level learning sequence

### 5.1 Worked decomposition: Customer, Product, Order and OrderLine

We decompose the line-grain relation:

`R(OrderID, OrderDate, CustomerID, CustomerName, CustomerCity, ProductID, ProductName, Qty)`

**Declared assumptions**

1. Each order belongs to exactly one customer.
2. Each customer ID identifies one current customer name and city.
3. Each product ID identifies one product name.
4. A product appears at most once in an order; quantity is stored on that line.
5. Customer name/city are current-state facts, not transaction-time snapshots.
6. A draft order may exist before its first line if the business lifecycle requires it; do not infer that every order must already have a line.

**Relevant FDs**

- `OrderID → OrderDate, CustomerID`
- `CustomerID → CustomerName, CustomerCity`
- `ProductID → ProductName`
- `(OrderID, ProductID) → Qty`

The line-grain candidate key is `(OrderID, ProductID)`, as shown by closure in Section 2.5. No proper subset determines all line attributes.

**Final relations**

| Relation | Attributes | Primary key | Foreign keys | Important FDs |
|---|---|---|---|---|
| `Customer` | `CustomerID, CustomerName, CustomerCity` | `CustomerID` | None in this example | `CustomerID → CustomerName, CustomerCity` |
| `Product` | `ProductID, ProductName` | `ProductID` | None in this example | `ProductID → ProductName` |
| `Order` | `OrderID, OrderDate, CustomerID` | `OrderID` | `CustomerID → Customer.CustomerID` | `OrderID → OrderDate, CustomerID` |
| `OrderLine` | `OrderID, ProductID, Qty` | `(OrderID, ProductID)` | `OrderID → Order.OrderID`; `ProductID → Product.ProductID` | `(OrderID, ProductID) → Qty` |

The arrows in the foreign-key column indicate references, not functional dependencies. An FK says a referenced key must exist for non-null FK values. It does not by itself assert that every customer has an order or every product appears in an order.

### 5.2 Why the decomposition is lossless

For a binary decomposition of relation R into R1 and R2, a standard sufficient condition for a lossless join under FD set F is that the common attributes `R1 ∩ R2` functionally determine all attributes of R1 or all attributes of R2 (under the projected dependencies). We use that criterion where it applies and show the relevant determinant.

Perform the decomposition as a sequence of binary splits; each split is justified against the declared FD set, not by appearance alone:

| Split | Left relation | Remaining relation | Intersection | Lossless-join reason |
|---|---|---|---|---|
| 1 | `Customer(CustomerID, CustomerName, CustomerCity)` | `R1(OrderID, OrderDate, CustomerID, ProductID, ProductName, Qty)` | `CustomerID` | `CustomerID → CustomerName, CustomerCity`, so the intersection determines the extracted Customer relation. |
| 2 | `Product(ProductID, ProductName)` | `R2(OrderID, OrderDate, CustomerID, ProductID, Qty)` | `ProductID` | `ProductID → ProductName`, so the intersection determines the extracted Product relation. |
| 3 | `Order(OrderID, OrderDate, CustomerID)` | `OrderLine(OrderID, ProductID, Qty)` | `OrderID` | `OrderID → OrderDate, CustomerID`, so the intersection determines the extracted Order relation. |

The residual relation after the third split is `OrderLine(OrderID, ProductID, Qty)`, whose key is `(OrderID, ProductID)` under the one-product-per-order assumption. For each binary split, the common attributes determine all attributes on one side, which is a sufficient lossless-join condition. Because the splits are applied sequentially, the sequence yields a lossless decomposition under the stated FDs. The implementation must also enforce the PK/FK constraints so joins do not multiply matches or omit rows due to invalid references.

The final natural join is `Customer ⋈ Order ⋈ OrderLine ⋈ Product`, joining on `CustomerID`, `OrderID` and `ProductID`. It reconstructs the intended facts in the original line-grain relation. The join does not create extra rows because the referenced keys are unique, and no line has a missing parent under the FK assumptions. If FK constraints are violated or a referenced key is not unique, the argument fails and the join can lose or multiply rows.

**Illustrative SQL (not the proof itself):**

```sql
SELECT
    o.order_id,
    o.order_date,
    c.customer_id,
    c.customer_name,
    c.customer_city,
    p.product_id,
    p.product_name,
    ol.qty
FROM "Order" AS o
JOIN Customer AS c
  ON c.customer_id = o.customer_id
JOIN OrderLine AS ol
  ON ol.order_id = o.order_id
JOIN Product AS p
  ON p.product_id = ol.product_id;
```

The SQL shows how to express the reconstruction. It uses ANSI-style quoted identifier syntax for the relation name `Order`; quoting and reserved-word rules vary by database. A physical implementation may instead name this relation `SalesOrder` to avoid quoting. That naming choice does not change the logical dependencies or the lossless-join argument. The FD and key argument above is what justifies losslessness.

### 5.3 Dependency preservation

A decomposition is dependency-preserving if the original FDs can be enforced by checking the decomposed relations individually, using their projected dependencies, without joining the relations to test the original rule.

For the four-relation decomposition:

- `CustomerID → CustomerName, CustomerCity` is enforceable within Customer.
- `ProductID → ProductName` is enforceable within Product.
- `OrderID → OrderDate, CustomerID` is enforceable within Order.
- `(OrderID, ProductID) → Qty` is enforceable within OrderLine via its key.

Thus, the listed FDs are preserved. PK/unique constraints enforce each relation's key; FKs enforce references; domain and check constraints enforce applicable value rules. This conclusion assumes the listed FDs are the complete relevant FD set. If additional rules exist, test them too.

**Do not conflate these properties:**

- **Lossless join:** the join of decomposed relations yields exactly the original relation—no missing or spurious tuples.
- **Dependency preservation:** every original FD can be enforced on decomposed relations without needing a join.
- A decomposition may be lossless but not dependency-preserving, as the BCNF Teaching example demonstrates.

### 5.4 Integrity constraints and nullable foreign keys

- **Primary key:** unique and non-null; a composite PK requires every component to be non-null.
- **Foreign key:** a non-null FK value must match a referenced key. An FK does not require every parent to have a child.
- **`NOT NULL`:** use when the relationship/value is mandatory in every valid row.
- **`UNIQUE`:** enforces uniqueness under the database's defined `NULL` semantics; these semantics can vary by system, so do not rely on them for a cross-vendor rule without checking.
- **`CHECK`:** enforces row-local predicates such as `qty > 0` or `valid_to > valid_from`, subject to SQL's treatment of `UNKNOWN`/`NULL`.
- **Referential actions:** `RESTRICT`/`NO ACTION`, `CASCADE`, or `SET NULL` express different lifecycle choices. Choose them from business semantics, not convenience.

A nullable FK such as `Order.ApprovedByEmployeeID` may mean an order has not yet been approved. That is not the same as an approval row with a missing employee, and not the same as an optional employee entity. `NULL` can mean “not yet known,” “not applicable,” or “not supplied”; choose one documented meaning per attribute when possible.

For a composite FK, partial-null behavior can be subtle and is not uniformly implemented across systems. If the rule is “both components are present or both absent,” add a constraint that enforces all-null/all-non-null semantics or use a supported `MATCH FULL` feature after checking the target database. Never assume a nullable FK proves the relationship is optional in both directions.

### 5.5 Under-normalization and over-decomposition

**Under-normalization** leaves same-meaning facts in multiple write locations, creating avoidable anomalies. Warning signs include customer address repeated in order lines, product descriptions copied into operational transaction tables without a historical-snapshot requirement, and totals that have no authoritative calculation rule.

**Over-decomposition** splits attributes into tiny relations without a clear dependency, lifecycle or integrity benefit. It can increase join complexity, obscure business meaning and create operational costs. A relation containing two attributes is not inherently over-normalized; the test is whether the split is justified by semantics, dependencies and constraints.

Avoid the simplistic rule “more tables are better.” The goal is a defensible logical model, not maximizing table count or minimizing joins at all costs.

## 6. Advanced-level learning sequence

### 6.1 Candidate keys and FD discipline

For each relation under review:

1. State its grain in one sentence.
2. List the attributes and their domains.
3. State business rules that create FDs; do not infer FDs from a handful of rows.
4. Compute candidate keys using attribute closure.
5. Separate candidate keys, superkeys and the chosen primary key.
6. Identify prime attributes and non-prime attributes.
7. Test each normal form against every relevant FD, including dependencies implied by transitivity.
8. Re-check the model when a business rule changes—for example, allowing a product to appear on multiple lines of one order changes the key.

**Minimality check:** if X is a candidate key, X determines all attributes, but no proper subset of X does. If a key contains an attribute that can be removed while still determining all attributes, it is a superkey but not a candidate key.

### 6.2 Lossless join and decomposition proof technique

A decomposition is not correct merely because its tables “look normalized.” For each split:

1. Write original relation R and proposed R1/R2 schemas.
2. State the common attributes `I = R1 ∩ R2`.
3. State the relevant FDs projected onto the relations.
4. Show that `I → R1` or `I → R2` follows from the FDs; for a binary decomposition, this is a sufficient lossless-join condition.
5. Explain why keys and referential constraints prevent missing references or duplicate matches in the implementation.
6. If the split is multiway, prove it through a valid sequence of binary lossless decompositions or use a formal chase argument. Do not assume that individually plausible pairwise joins automatically prove every arbitrary multiway decomposition lossless.
7. Separately test dependency preservation.

**Counterexample discipline:** if the common attributes do not determine either side, do not claim losslessness based only on a sample table. Construct a legal counterexample or perform a chase/proof.

### 6.3 BCNF versus 3NF: why the trade-off exists

The Teaching example in Section 4.4 is in 3NF but not BCNF. Its BCNF decomposition is lossless because the intersection `Instructor` determines all of `InstructorCourse`. Yet `(Student, Course) → Instructor` is not preserved by the projections. This is not a defect in the proof: it is a known trade-off. The original dependency can only be checked by joining `StudentInstructor` with `InstructorCourse` and testing student/course combinations.

When a dependency is important to operational integrity, choose deliberately among:

- A 3NF design that preserves the dependency locally.
- A BCNF design plus a transaction/service/trigger or other cross-relation enforcement mechanism.
- A revised business rule/model that eliminates the conflict if stakeholders confirm the original rule was misstated.

Do not claim BCNF is always the only correct choice. BCNF removes a class of redundancy; dependency preservation and enforceability remain engineering requirements.

### 6.4 Scenario A — Customer segment repeated in every transaction

A reporting table may store `CustomerSegment` on every transaction. First determine what the column means:

- **Current segment copied into historical rows:** likely an unnecessary duplicate. A current-segment change requires updating many transactions, and partial updates produce contradictions.
- **Segment at transaction time:** a historical fact. It may legitimately differ from the customer's current segment. Model segment history with effective dates and a time-valid relationship, or store an explicitly named immutable snapshot such as `SegmentAtTransaction` with a provenance rule.

A normalized design might use `Customer(CustomerID, CurrentSegmentID)` and `CustomerSegmentHistory(CustomerID, SegmentID, ValidFrom, ValidTo)`. To resolve a transaction's historical segment, define a non-overlapping interval rule and join by transaction time. A transaction-level snapshot may be justified if reporting must remain stable despite history corrections; document whether the snapshot is authoritative or derived.

**Required decision questions:** Is the business asking “segment now” or “segment then”? Which system owns the segment assignment? How are late corrections handled? Is the reporting result reproducible as of a past date?

### 6.5 Scenario B — Generic name/value attributes

A generic table such as `EntityAttribute(EntityID, AttributeName, AttributeValue)` seems flexible but often hides the schema:

- `AttributeValue` may mix dates, decimals, identifiers and free text, weakening domain/type validation.
- A `CHECK` constraint cannot easily express the valid domain and requiredness for every attribute without additional metadata or application logic.
- Uniqueness and cardinality become unclear: can an entity have two `RiskRating` values? Which one is current?
- Required attributes may be absent without a simple `NOT NULL` constraint.
- Queries and indexes become less selective and harder to optimize.
- Renaming an attribute or changing its type becomes a data migration with semantic risk.

Use a generic attribute design only when variability is genuinely part of the domain, with a metadata registry for type, cardinality, allowed values, requiredness, ownership and lifecycle. Prefer typed columns or dedicated related tables for stable, important business attributes. Flexibility is not free: record what integrity moves from the relational schema to application or validation services.

### 6.6 Scenario C — Calculated account balance

A stored `Account.CurrentBalance` may duplicate a value derived from posted ledger entries. If the invariant is:

`CurrentBalance = OpeningBalance + SUM(signed posted entries)`

then someone must guarantee equality under concurrent postings, reversals, retries and failures.

A safe operational pattern, if a cached balance is justified, is:

1. Treat the immutable/posting ledger as the authoritative record.
2. In one atomic transaction, insert a uniquely identified posting and update the account balance by the same signed amount.
3. Make posting idempotent using a unique business/event key so a retry cannot apply the amount twice.
4. Define pending, reversed, backdated and multi-currency semantics explicitly.
5. Reconcile stored balances against ledger-derived balances on a schedule and alert on variance.
6. Define repair ownership and a controlled rebuild procedure.

A balance snapshot can improve a high-volume read path, but introduces a consistency invariant, concurrency risk and operational repair work. If measured read requirements do not justify that complexity, calculate the balance from the authoritative ledger or use a derived view/materialization with documented refresh semantics.

### 6.7 Northbridge Bank accounts/payments review

Use the following imperfect design as a review exercise, not a production recommendation:

`AccountPaymentExport(AccountID, AccountNumber, CustomerID, CustomerName, Segment, PaymentID, PaymentTime, PaymentAmount, AccountBalance, BranchID, BranchName)`

**Illustrative assumptions to validate:**

- `AccountID` uniquely identifies an account; `AccountNumber` is unique only within a defined account-number namespace.
- An account can have multiple holders; a customer can hold multiple accounts.
- `PaymentID` uniquely identifies a payment.
- `BranchID → BranchName`.
- A payment belongs to one account; amount is signed or typed according to an explicit payment/ledger policy.
- Customer segment can change over time.
- `AccountBalance` is a current calculated/cached value, not a historical balance at payment time.

**Review findings and corrections**

| Finding | Dependency/anomaly behind it | Recommended logical correction | Residual decision |
|---|---|---|---|
| `AccountNumber` repeated on every payment | `AccountID → AccountNumber`; repeated account fact creates update anomalies. | Store account number on Account. | Define uniqueness scope and lifecycle. |
| `CustomerName`/`Segment` stored in payment rows | Customer facts depend on CustomerID, not PaymentID; customer may have multiple accounts. | Customer/Party relation plus explicit account-holder association. | Historical segment requires time semantics. |
| `BranchName` repeated | `BranchID → BranchName`; repeated branch fact. | Branch relation; Account references Branch if business rule is one servicing branch. | If branch assignment changes, decide whether history is needed. |
| `AccountBalance` copied to every payment row | Balance is derived from a set of entries and is time-dependent; repeated current balance becomes stale. | Keep ledger/payment facts authoritative; optional Account balance cache only with atomic update and reconciliation. | Specify posted/pending/reversed and currency rules. |
| Customer-to-account relationship assumed one-to-one | Joint accounts violate that assumption. | `AccountHolding(AccountID, PartyID, Role, ValidFrom, ValidTo, …)` associative relation. | Define uniqueness and valid-time overlap rules. |
| `PaymentAmount` lacks sign/type semantics | Amount alone may not distinguish debit, credit, reversal and pending status. | Define ledger entry/payment semantics and constraints. | Validate business vocabulary and currency rules. |

**Revised logical core (illustrative):**

- `Party(PartyID PK, PartyType, …)`
- `Customer(CustomerID PK/FK to Party, …)` if Customer is a subtype/role with separate attributes.
- `Account(AccountID PK, AccountNumber, CurrencyCode, BranchID FK, …)`
- `AccountHolding(AccountID FK, PartyID FK, Role, ValidFrom, ValidTo, PK(AccountID, PartyID, Role, ValidFrom))`
- `Payment(PaymentID PK, AccountID FK, PaymentTime, Amount, CurrencyCode, Status, IdempotencyKey UNIQUE, …)`
- `Branch(BranchID PK, BranchName, …)`
- `CustomerSegmentHistory(CustomerID FK, SegmentID FK, ValidFrom, ValidTo, …)` if segment history is required.
- `AccountBalanceSnapshot(AccountID PK/FK, BalanceAmount, AsOfTime, LedgerVersion, …)` only if justified as a physical read optimization; otherwise omit.

The `AccountHolding` composite key assumes one holder/role association may recur only at distinct start times. The model must also enforce or validate non-overlapping effective intervals for the same business relationship; a PK alone does not prevent overlapping intervals. If one party can have multiple roles concurrently, role belongs in the key; if not, simplify the key to match the actual rule. A transaction-time legal-name snapshot is separate from current Party name if historical evidence is required.

### 6.8 Two documented examples of justified physical denormalization

These are example decision records with **hypothetical measured results** for teaching. They are not measurements from a real workload and must be replaced by actual benchmark evidence before implementation.

#### Decision D-01 — Pre-joined payment reporting projection

- **Problem:** A dashboard joins Payment → Account → Customer → Branch on every request. Baseline p95 latency is 1.8 seconds at 450 requests/second on a representative replay; 38% of dashboard time is attributed to repeated joins and lookup work. *(Illustrative benchmark.)*
- **Option chosen:** Build a reporting projection containing `PaymentID`, `AccountID`, payment timestamp/amount, branch name and the explicitly chosen segment semantics. Keep normalized operational relations authoritative.
- **Measured target/result (illustrative):** After building and indexing the projection, p95 is 420 ms at the same replay rate; storage increases by 14%; projection freshness p99 is 45 seconds.
- **Consistency risk:** Branch/customer labels may lag or historical segment values may be misinterpreted.
- **Consistency owner:** Data Platform reporting owner; Customer Data owner owns segment semantics.
- **Control mechanism:** Transactional outbox/CDC event stream, idempotent projection updates, version/watermark tracking, dead-letter handling, scheduled reconciliation against source keys/counts and sampled values, and a documented rebuild procedure.
- **Decision:** Justified only if measured latency/freshness meets the reporting SLA. The projection is disposable and rebuildable; it is not the system of record.
- **Rollback:** Switch the dashboard to the normalized query path if lag exceeds the freshness SLA or reconciliation fails.

#### Decision D-02 — Cached current account balance

- **Problem:** A ledger aggregation on every account overview read misses the read-latency SLO under peak traffic. A representative replay shows p95 700 ms at 2,000 reads/second; this is hypothetical.
- **Option chosen:** Maintain a current balance cache on Account or in a one-row-per-account snapshot table, while the posted ledger remains authoritative.
- **Measured target/result (illustrative):** p95 falls to 80 ms at the same replay; write-path p99 increases by 12 ms; reconciliation finds no unexplained variance in the test window. These are examples of evidence to collect, not a guarantee.
- **Consistency risk:** A partial failure, duplicate retry or concurrent posting can make the cache disagree with ledger entries.
- **Consistency owner:** Payments/ledger service owner; Finance/operations owns reconciliation policy.
- **Control mechanism:** Update posting and balance in one database transaction; enforce unique posting/idempotency keys; define reversal handling; record ledger version/as-of time; reconcile against ledger sums and alert/repair through a controlled rebuild.
- **Decision:** Accept only if the read SLO materially improves and write-path/reconciliation controls pass. Never use an unverified cache as the sole audit record.
- **Rollback:** Recompute reads from the ledger or disable the cache if invariant checks fail.

**Measurement checklist before any denormalization:** baseline p50/p95/p99 latency, throughput, query plan, CPU/I/O, lock waits, concurrency, read/write ratio, freshness tolerance, storage growth, update amplification, rebuild time and failure/recovery behavior. Compare the same representative workload before and after. “It feels faster” is not sufficient evidence.

### 6.9 Exercise 1 — Normalize an order export to 1NF, 2NF and 3NF

**Initial relation and declared grain**

`OrderExport(OrderID, OrderDate, CustomerID, CustomerName, CustomerCity, ProductIDs, ProductNames, Quantities)`

Declared key: `OrderID`, because each row represents one order. Product IDs, names and quantities are comma-separated lists. This initial relation is not 1NF under the model's intended product-line semantics.

**Business FDs after interpreting the lists as individual line facts**

- `OrderID → OrderDate, CustomerID`
- `CustomerID → CustomerName, CustomerCity`
- `ProductID → ProductName`
- `(OrderID, ProductID) → Qty` under the one-product-per-order assumption.

The list-valued initial relation does not support the final line FD as a clean attribute-level FD because product IDs and quantities are packed into strings. First reshape the facts into atomic line tuples.

**Anomalies/violations**
- 1NF violation: list-valued product/quantity cells.
- After flattening, 2NF violation: `OrderDate` depends on `OrderID` alone; `ProductName` depends on `ProductID` alone, both proper subsets of `(OrderID, ProductID)`.
- 3NF violation: customer details transitively depend on `OrderID` through `CustomerID`.

**Step-by-step decomposition**
1. Convert lists into one row per product line: `R(OrderID, OrderDate, CustomerID, CustomerName, CustomerCity, ProductID, ProductName, Qty)`, key `(OrderID, ProductID)`.
2. Extract `Customer(CustomerID PK, CustomerName, CustomerCity)` from `CustomerID → CustomerName, CustomerCity`.
3. Extract `Product(ProductID PK, ProductName)` from `ProductID → ProductName`.
4. Extract `Order(OrderID PK, OrderDate, CustomerID FK)` from `OrderID → OrderDate, CustomerID`.
5. Retain `OrderLine(OrderID FK, ProductID FK, Qty, PK(OrderID, ProductID))`.

**Resulting constraints**
- `Order.CustomerID` references Customer and is `NOT NULL` if every order must have a customer.
- `OrderLine.OrderID` references Order; `OrderLine.ProductID` references Product.
- `Qty > 0` if zero/negative quantities are disallowed.
- `UNIQUE(OrderID, ProductID)` is the composite PK under the declared line-grain rule.

**Lossless-join reasoning**
- Customer split: intersection `CustomerID` determines all Customer attributes.
- Product split: intersection `ProductID` determines all Product attributes.
- Order split: intersection `OrderID` determines all Order attributes.
- The final joins use unique parent keys, so each line maps to exactly one order and one product. Under the stated FDs/FKs, no spurious combinations are introduced and the intended flattened relation is reconstructed.

**Dependency preservation**
Every listed FD is local to one final relation: customer FDs in Customer, product FD in Product, order-header FD in Order, line FD in OrderLine. Therefore the listed FDs are preserved. Revisit this conclusion if additional FDs or different line semantics are discovered.

**Corrected answer:** use the four relations above. Do not keep list fields or duplicate current customer/product descriptions in each line without a distinct historical or physical-optimization requirement.

### 6.10 Exercise 2 — Normalize course enrollment with a composite key

**Initial relation and scope assumption**

`EnrollmentExport(StudentID, StudentName, CourseID, CourseTitle, Grade)`

For this exercise, the export is explicitly scoped to **one named academic term**; `TermID` is constant for every row and is intentionally omitted from the relation. Under the stated rule that a student has at most one enrollment record per course in that term, the candidate key is `(StudentID, CourseID)`. If the relation combines multiple terms, use `EnrollmentExport(StudentID, StudentName, CourseID, CourseTitle, TermID, Grade)` and, assuming one enrollment per student/course/term, the key and grade dependency become `(StudentID, CourseID, TermID) → Grade`. If a course can have multiple sections in a term, add the relevant offering/section identifier and revise the key to match the actual business grain. Do not apply the single-term key to a multi-term relation.

**FDs**
- `StudentID → StudentName`
- `CourseID → CourseTitle`
- `(StudentID, CourseID) → Grade`

**Anomalies/violations**
- Student name depends only on `StudentID`, a proper subset of the composite key: 2NF violation.
- Course title depends only on `CourseID`, a proper subset of the composite key: 2NF violation.
- Repeating student/course details across enrollments creates update and deletion anomalies.

**Step-by-step decomposition**
1. `Student(StudentID PK, StudentName)`
2. `Course(CourseID PK, CourseTitle)`
3. `Enrollment(StudentID FK, CourseID FK, Grade, PK(StudentID, CourseID))`

**Resulting constraints**
- Student and Course identifiers are primary keys.
- Enrollment's two FK columns reference their respective parent keys.
- `Grade` domain/check rules should reflect the institution's grading policy; do not invent a numeric range without a policy.
- `Grade` is `NOT NULL` only if every enrolled student must already have a final grade. If grades are pending, nullable grade is a separate business meaning, not a nullable FK.

**Lossless-join reasoning**
- First split Student facts from EnrollmentExport. The intersection is StudentID and `StudentID → StudentName`, so the intersection determines all Student attributes and the split is lossless.
- Then split Course facts from the remaining relation. The intersection is CourseID and `CourseID → CourseTitle`, so that split is lossless.
- The final join Student ⋈ Enrollment ⋈ Course reconstructs each original enrollment row under the declared key and FK constraints.

**Dependency preservation**
Each listed FD is enforced in its own relation. The composite key of Enrollment enforces `(StudentID, CourseID) → Grade`; Student and Course primary keys enforce their FDs. The decomposition preserves the listed dependencies.

**Corrected answer:** separate Student and Course descriptive facts from the associative Enrollment relation. This is justified because the facts have different determinants and lifecycles, not merely because three tables are fashionable.

### 6.11 Exercise 3 — A 3NF relation that violates BCNF

**Initial relation**

`Teaching(Student, Course, Instructor)`

Declared candidate keys: `(Student, Course)` and `(Student, Instructor)`, under these rules:
- `(Student, Course) → Instructor`
- `Instructor → Course` (each instructor teaches one course in the modeled term).

**Key derivation**
- `(Student, Course)+ = {Student, Course, Instructor}` using the first FD, so it is a superkey; neither single attribute alone determines all attributes, so it is a candidate key.
- `(Student, Instructor)+` includes Course by `Instructor → Course`; it contains all attributes and is a candidate key.
- `Instructor+ = {Instructor, Course}`, not Student; Instructor is not a superkey.

**Normal-form diagnosis**
- 1NF: yes, assuming scalar values and tuple identity.
- 2NF: yes under these candidate keys because no non-prime attribute exists: all three attributes are prime (Student appears in both keys; Course in the first; Instructor in the second).
- 3NF: yes. For `Instructor → Course`, Course is prime; for `(Student, Course) → Instructor`, the determinant is a candidate key.
- BCNF: no, because `Instructor → Course` is non-trivial and Instructor is not a superkey.

**Step-by-step BCNF decomposition**
1. Decompose on `Instructor → Course`:
   - `InstructorCourse(Instructor PK, Course)`
   - `StudentInstructor(Student, Instructor, PK(Student, Instructor), FK Instructor)`
2. The intersection is Instructor. It determines all attributes of InstructorCourse, so the binary decomposition is lossless.
3. Both relations are in BCNF under the stated FDs: Instructor is a key of InstructorCourse; StudentInstructor has no non-trivial projected FD under the given rules.

**Constraints and dependency preservation**
- `InstructorCourse.Instructor` is a PK, enforcing one course per instructor.
- `StudentInstructor.Instructor` is an FK to InstructorCourse.
- The original dependency `(Student, Course) → Instructor` is not preserved by the projected dependencies. A student can be linked to two instructors who teach the same course, violating the original FD only after joining the decomposed relations. A simple PK/FK on either table cannot reject this combination.
- Therefore the decomposition is lossless but not dependency-preserving. If the original FD must be enforced locally, retain a 3NF design or add a clearly specified cross-relation enforcement mechanism.

**Corrected answer:** do not label the BCNF decomposition “fully better” without documenting the dependency-enforcement cost. The appropriate choice depends on whether the business rule must be enforced declaratively and what integrity mechanism is acceptable.

### 6.12 Exercise 4 — Nullable relationship and a derived balance

**Initial relation**

`AccountSnapshot(AccountID, AccountNumber, CustomerID, CustomerName, CurrentBalance, AsOfTime)`

Declared key: `AccountID` for a single current snapshot. If multiple snapshots are retained, the key must include `AsOfTime` or a snapshot identifier.

**Assumed FDs/invariants**
- `AccountID → AccountNumber, CustomerID`
- `CustomerID → CustomerName`
- `AccountID → CurrentBalance, AsOfTime` only as a statement about the single current snapshot row, not a timeless dependency across history.
- `CurrentBalance = OpeningBalance + SUM(signed posted entries)` is an aggregate invariant, not a simple FD.

**Anomalies/violations**
- Customer name is transitively dependent through CustomerID; 3NF violation if stored in the Account relation.
- Account number repeats if copied into every payment/event row.
- `CurrentBalance` is derived/cached and requires a reconciliation invariant.
- A nullable `CustomerID` must be justified by the lifecycle; it should not be nullable merely to accommodate missing source data.

**Step-by-step correction**
1. `Customer(CustomerID PK, CustomerName)`
2. `Account(AccountID PK, AccountNumber UNIQUE under the correct namespace, CustomerID FK NOT NULL if every account must have a customer, …)`; for joint accounts, replace a single CustomerID with an AccountHolding associative relation.
3. `LedgerEntry(EntryID PK, AccountID FK, PostedAt, SignedAmount, Status, IdempotencyKey UNIQUE, …)`
4. Optional physical cache: `AccountBalanceSnapshot(AccountID PK/FK, BalanceAmount, AsOfTime, LedgerVersion)`.

**Lossless-join reasoning**
- Customer split is lossless because CustomerID determines CustomerName.
- Account-to-LedgerEntry is one-to-many; joining an account to all ledger entries produces one row per entry, not one row per account. Reconstruction must preserve the declared grain: a balance report groups/aggregates entries. Do not claim a one-row-per-account relation is reconstructed by joining to many entries without accounting for the grain change.
- If the optional snapshot is used, it is not a lossless decomposition of the authoritative ledger relation; it is a derived physical structure and must be refreshed/reconciled under its explicit invariant.

**Dependency preservation**
The Customer FD is local to Customer; account identifiers and ledger identifiers are local to their relations. The calculated balance equality is an aggregate invariant across multiple ledger rows and must be implemented by transaction logic, a materialized aggregate/refresh mechanism, or reconciliation.

**Corrected answer:** normalize descriptive facts; keep the ledger authoritative; retain a balance cache only if measured read requirements justify it and the consistency controls are owned.

## 7. Industry-application exercises

Complete these exercises on paper or in a schema-design document before reading the answer guidance above. Do not infer business rules that have not been declared; write questions for the domain owner.

### 7.1 Exercise A — Northbridge accounts and payments review

Using Section 6.7:
1. State the grain of every relation in the flawed export.
2. Write the FD or aggregate invariant behind each identified problem.
3. Propose the revised normalized model, including AccountHolding for joint accounts.
4. State all PKs, FKs, uniqueness rules and nullability assumptions.
5. Decide whether customer segment means current segment or segment at transaction time.
6. Decide whether CurrentBalance is computed, cached or a ledger snapshot.
7. Document unresolved rules and their owners.

**Evidence required:** reviewed model, dependency list, issue register with a correction for every issue, and a written trade-off decision.

### 7.2 Exercise B — Prove a decomposition

Use `R(A, B, C)` with FD set `A → B` and `B → C`.

Proposed decomposition:
- `R1(A, B)`
- `R2(B, C)`

**Answer verification**
- The intersection is `{B}`.
- `B → C`, so the intersection determines all attributes of R2; the binary decomposition is lossless.
- `A → B` is enforceable in R1 and `B → C` in R2, so both listed dependencies are preserved.
- The candidate key of R is A because `A+ = {A, B, C}`; neither B nor C alone determines A under the stated FD set.
- This is a formal demonstration of the proof method, not proof that every decomposition sharing an attribute is lossless.

### 7.3 Exercise C — Document two physical denormalization decisions

Use D-01 and D-02 in Section 6.8 as examples. For your own decisions, replace every hypothetical metric with actual workload measurements. Include:

- Baseline and proposed architecture.
- Same representative workload before/after.
- p50/p95/p99 latency, throughput and resource use.
- Freshness/consistency SLO.
- Duplicate fact and failure modes.
- Authoritative source and named consistency owner.
- Update/reconciliation/rebuild mechanism.
- Rollback trigger and operational runbook.
- Review date and decision expiry/revisit condition.

### 7.4 Additional review prompts

1. A `CustomerAddress` is stored as one string. Is that a 1NF violation? Explain relative to required business operations.
2. A table's declared PK is `(OrderID, ProductID, LineNumber)`, but `LineNumber` is uniquely assigned within OrderID. Is the PK minimal? What key rule must be clarified?
3. `AccountID → CurrencyCode` is true today. What if accounts can change denomination or have multi-currency sub-ledgers?
4. A report stores `CustomerSegmentAtPayment`. What rule ensures the value reflects the approved segment at payment time?
5. A generic attribute registry allows `RiskScore` to be both text and decimal. What domain and migration controls are missing?
6. A materialized report is stale for 10 minutes. Is that acceptable? Which business SLA decides?
7. A nullable FK is `NULL` for 20% of rows. Is that an anomaly? Only documented meaning and lifecycle can answer.
8. A BCNF decomposition loses local enforcement of a critical FD. Which design or control is acceptable to the domain owner?

## 8. Practical scenarios and case-based reasoning

### 8.1 Customer segment repeated in transactions

**Scenario:** Every transaction row stores `CustomerSegment`. A customer moves from “Standard” to “Preferred.”

**Reasoning path**
1. Clarify whether the report wants current segment or segment at transaction time.
2. If current segment is copied, the dependency is `CustomerID → CurrentSegment` and repeated transaction copies create update anomalies.
3. If segment-at-time is required, define valid-time history and ensure the transaction joins to exactly one segment interval.
4. Decide whether the historical value should be derived from a history table or frozen as a snapshot for audit reproducibility.
5. Name the owner of late corrections and explain whether previously published reports are restated.

### 8.2 Generic name/value attributes

**Scenario:** `EntityAttribute(EntityID, AttributeName, AttributeValue)` is used for all business attributes.

**Reasoning path**
1. Identify which attributes are stable, typed and operationally important.
2. Identify which values need uniqueness, referential integrity, ranges, cardinality or requiredness.
3. Determine whether the model can enforce these rules structurally or whether they move into metadata-driven validation.
4. If generic storage is retained, define typed value columns or a validated value representation, metadata constraints, ownership and migration rules.
5. Measure query complexity and index selectivity; flexibility alone does not justify loss of integrity.

### 8.3 Calculated account balance

**Scenario:** The team stores `CurrentBalance` beside the account.

**Reasoning path**
1. Define the equation, currency, posting statuses, reversals, backdated entries and rounding rules.
2. Identify the authoritative ledger and the exact moment the cache is updated.
3. Ensure the entry and balance update are atomic or use an explicitly designed asynchronous consistency model.
4. Use idempotency keys for retries and reconcile the cache to the ledger.
5. State the acceptable variance (normally zero for a financial invariant), alerting threshold and repair process.
6. Retain the cache only if measured performance gains outweigh write amplification and operational risk.

### 8.4 Northbridge historical name and segment

If the legal name or segment at the time of a payment is required for audit, storing the current name in `Customer` does not answer the historical question. Model time-valid facts or an immutable transaction snapshot with explicit provenance. Do not use a current-state FD to justify a historical attribute whose value intentionally changes over time.

## 9. Expected outputs and deliverables

Produce the following evidence before marking this lesson complete:

1. **Dependency register:** every relation, grain, FD, determinant and business rule behind it.
2. **Candidate-key worksheet:** closures and minimality arguments for each non-trivial relation.
3. **Three normalized tables:** at least three supplied relations taken through a stated target normal form, with initial keys, FDs, anomaly diagnosis, decomposition steps and corrected schemas. The exercises in Section 6 provide worked reference answers.
4. **Decomposition proofs:** one proof for each exercise, identifying intersection attributes and explaining why they determine one side; explicitly identify the BCNF example's lossless-but-not-dependency-preserving outcome.
5. **Constraint matrix:** PKs, FKs, `NOT NULL`, `UNIQUE`, `CHECK`, referential actions, nullable semantics and rules requiring cross-row/application enforcement.
6. **Northbridge review findings:** problem, evidence/FD, anomaly or integrity risk, correction, unresolved question and owner.
7. **Denormalization decision record:** at least two documented physical denormalization candidates; each must state baseline measurements, expected/measured benefit, duplicate consistency risk, source of truth, owner, control mechanism, rollback trigger and re-evaluation date. If you have no real benchmark, label metrics hypothetical and do not represent them as measured production evidence.
8. **Practice-question corrections:** answers and reasoning for Module 3 practice questions, including corrections to any initial mistakes.
9. **Model review summary:** explicit acceptance/rejection of each proposed decomposition and the assumptions on which the conclusion depends.

## 10. Common mistakes and misconceptions

- **“A dependency is obvious from the data.”** Sample data cannot prove a business FD; a domain rule must support it.
- **“Every relation with a composite key violates 2NF.”** Composite keys are normal; partial dependencies are the issue.
- **“3NF means no transitive dependency, full stop.”** Use the formal definition when candidate keys overlap or prime attributes matter.
- **“BCNF is always better than 3NF.”** BCNF may not preserve dependencies; local enforcement can become harder.
- **“Splitting a table automatically preserves information.”** A lossy decomposition can generate spurious tuples or lose associations.
- **“Lossless means dependency-preserving.”** They are separate properties and need separate arguments.
- **“Foreign keys enforce every business rule.”** FKs validate references; they do not enforce aggregate balance equations, non-overlapping intervals or all cross-row rules by themselves.
- **“NULL means the parent does not exist.”** A null FK usually means no reference is supplied; it does not mean a dangling reference is allowed.
- **“One cell must always be split into many columns.”** Atomicity depends on modeled semantics and access requirements.
- **“A generic EAV table is more flexible at no cost.”** It often weakens type safety, requiredness, cardinality and query clarity.
- **“Denormalization is a shortcut for slow queries.”** Measure the bottleneck and compare alternatives before adding duplicate state.
- **“A balance cache is just another column.”** It is a maintained invariant with concurrency, retry, recovery and reconciliation requirements.
- **“Historical copies are always bad redundancy.”** A transaction-time snapshot can be a distinct historical fact; name it accordingly.
- **“More tables means better modeling.”** Each split must be justified by semantics, dependencies, integrity or workload.
- **“A `CHECK` constraint always handles NULL the way I expect.”** SQL's three-valued logic means `UNKNOWN` may not fail a check; combine `NOT NULL` and checks when required.

## 11. Mastery criteria

You have mastered this topic when you can, without relying on slogans:

- Define each relation's grain and identify its candidate key(s).
- Derive candidate keys using closure and prove minimality.
- State FDs as business rules and distinguish them from observed coincidences.
- Diagnose 1NF, 2NF, 3NF and BCNF with the correct formal condition.
- Produce a corrected decomposition and identify PKs/FKs/constraints.
- Prove losslessness for each decomposition and separately test dependency preservation.
- Explain the BCNF counterexample where the decomposition is lossless but a dependency is not preserved.
- Distinguish current-state attributes from historical snapshots.
- Explain nullable-FK semantics and specify integrity controls beyond FKs.
- Review the Northbridge accounts/payments model and tie every finding to a dependency, anomaly or invariant.
- Document two physical denormalization decisions using workload evidence, consistency ownership, controls and rollback criteria.
- Correct your own practice answers and record why an initial answer was wrong.

## 12. Completion gate

Do not mark Module 3 complete until every item below has evidence attached to your notes or repository.

- [ ] **Three tables normalized:** three supplied relations are normalized to the stated target form, with initial relation, declared key, FD set, anomaly/normal-form diagnosis and final schema.
- [ ] **Dependency proofs complete:** candidate keys are derived by closure; every dependency used in the diagnosis is tied to a business rule; decomposition proofs identify intersections and justify losslessness.
- [ ] **Dependency preservation assessed:** every decomposition lists which FDs are preserved; any dependency requiring a join or procedural control is explicitly documented.
- [ ] **Northbridge review findings documented:** every issue has a dependency/anomaly/invariant, correction, constraint/control, and unresolved assumption/owner where relevant.
- [ ] **Constraint and NULL semantics reviewed:** PKs, FKs, nullability, uniqueness, check constraints and cross-row rules are documented.
- [ ] **Two physical denormalization decisions recorded:** each includes measured workload evidence or clearly labeled hypothetical evidence, expected benefit, consistency risk, authoritative source, named owner, maintenance/reconciliation mechanism and rollback condition.
- [ ] **Practice questions answered and corrected:** answers include reasoning, not only the normal-form label.
- [ ] **Second-pass model review completed:** schemas, FDs, keys, decompositions, constraints and examples have been checked against declared assumptions; unresolved decisions are recorded rather than silently guessed.

**Completion standard:** the model is not accepted merely because it has four tables or passes a sample query. It is accepted when its facts, dependencies, keys, integrity constraints, decomposition properties and any intentional duplicate state are explicitly justified and reviewable.
