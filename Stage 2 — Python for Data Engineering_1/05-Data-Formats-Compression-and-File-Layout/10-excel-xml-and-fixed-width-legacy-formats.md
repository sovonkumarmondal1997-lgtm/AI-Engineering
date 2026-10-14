# Excel, XML, and Fixed-Width Legacy Formats

> **Stage 2 → Python for Data Engineering → Module 2.5 → Topic 10**
>
> This chapter teaches how to ingest messy enterprise files safely and turn them into typed, validated, well-laid-out analytical data.

---

## 1. Why This Topic Matters

Modern data platforms often look like this:

```text
SaaS APIs ─────┐
Databases ─────┤
Kafka ─────────┤
               ├──► Data Lake / Lakehouse
Excel Reports ─┤
XML Feeds ─────┤
Mainframe ─────┘
```

The bottom half is often the uncomfortable part.

A spreadsheet may be designed for a human manager. An XML feed may represent a deeply nested business document. A fixed-width file may encode decades-old contracts between a mainframe and downstream systems. Yet the analytical platform still needs predictable columns, types, validation, lineage, and efficient Parquet output.

That makes this topic a **Data Engineering** problem, not merely a file-parsing problem.

The goal is not:

> “How do I read this file?”

The goal is:

> “How do I understand this source, extract the intended business records, validate them, preserve the evidence, and publish trustworthy analytical data?”

---

## 2. Learning Objectives

By the end of this chapter, you should be able to:

- explain why Excel, XML, fixed-width, and mainframe feeds still exist;
- inspect an unfamiliar source before writing parser logic;
- identify logical records and target table grain;
- design a target schema before implementation;
- read Excel with pandas and Polars;
- choose deliberately between `openpyxl` and `calamine`/`python-calamine`;
- handle sheets, headers, `skiprows`, `usecols`, messy report regions, totals rows, and hidden content;
- reason about Excel serial dates, including the 1900/1904 systems and the historical 1900 leap-year bug;
- preserve identifiers such as account numbers and postal codes as strings;
- parse XML with `xml.etree.ElementTree`, `lxml`, and `pandas.read_xml`;
- handle namespaces and basic XPath expressions;
- map nested XML to parent and child analytical tables without changing grain accidentally;
- stream large XML with `iterparse` and clear processed nodes so memory stays bounded;
- explain XXE and entity-expansion risks and use defensive parsers for untrusted input;
- validate XML against an XSD when a contract exists;
- parse fixed-width files with pandas and Polars;
- handle padding, alignment, signed fields, implied decimals, and multiple record types;
- externalize layouts as versioned specifications instead of scattering magic slices through code;
- understand COBOL copybooks, EBCDIC, and packed decimal (`COMP-3`) at a working data-engineering level;
- reconcile header/detail/trailer control totals;
- quarantine malformed or invalid records with enough metadata to replay them;
- preserve raw bronze inputs and create typed silver Parquet;
- apply compression, partitioning, and file-sizing principles from Topics 01–09;
- make ingestion idempotent, replayable, auditable, observable, and safe under change.

---

## 3. Prerequisites

You have already studied Topics 01–09 of this module:

1. Row-oriented vs columnar storage
2. Parquet internals
3. Reading and writing Parquet with PyArrow
4. Avro
5. ORC and format selection
6. Nested and semi-structured data
7. Compression codecs
8. Partitioning and Hive-style directory layouts
9. The small-files problem and target file sizing

Do **not** re-learn those modules here. Instead, use them as the destination-side foundation:

```text
Legacy source
   ↓
parse + validate
   ↓
typed records
   ↓
Parquet + compression + partitioning + sane file sizing
```

---

## 4. The Real-World Legacy Ingestion Problem

A production source rarely arrives as a perfect rectangular table.

You may receive an Excel report like:

```text
ACME RETAIL GROUP
Monthly Sales Report — September 2026

Region: East

[merged visual title]

Store     Date        Account      Sales
001       2026-09-01  00001234     1234.50
002       2026-09-01  00007890      950.00
...

TOTAL                              218450.75
Prepared by: Finance Operations
```

Or a fixed-width feed like:

```text
H202609280001234
D0000010000123400123450+
D0000020000789000009500+
T000000000021845075
```

Or XML:

```xml
<feed xmlns="urn:example:products">
  <product id="P100">
    <name>Keyboard</name>
    <prices>
      <price currency="INR">1499.00</price>
      <price currency="USD">18.00</price>
    </prices>
  </product>
</feed>
```

The parser is only one part of the problem. You must also answer:

- Which bytes represent real records?
- What is one business row?
- Which fields are identifiers versus measures?
- Which cells/lines/nodes are metadata rather than data?
- What counts as malformed?
- How do we know we did not lose records?
- How do we replay yesterday with a corrected parser?
- Where do failed rows go?
- How do we publish only validated output?

---

## 5. Core Mental Model

Use this workflow for every legacy source:

```text
Messy Source
     ↓
   Inspect
     ↓
Understand Structure
     ↓
Define Grain + Target Schema
     ↓
     Parse
     ↓
   Validate
     ↓
  Reconcile
     ↓
Quarantine Failures
     ↓
Write Typed Parquet
     ↓
Partition + Compress + Size Correctly
     ↓
Silver Lake / Lakehouse
```

The critical rule is **grain first**.

> Do not start by writing `read_excel()`, `iterparse()`, or `line[37:49]`. Start by deciding what one output row means.

A useful source-analysis worksheet is:

| Question | Decision |
|---|---|
| Physical format | Excel / XML / fixed-width / EBCDIC binary / other |
| Logical record | What entity or event does one record represent? |
| Grain | One row equals what? |
| Business key | Which fields identify that logical record? |
| Types | Which fields are string, integer, decimal, date, timestamp? |
| Nullable fields | Which values may be absent? |
| Special decoding | Serial date / namespace / fixed-width / EBCDIC / COMP-3? |
| Validation | Structural, type, business, reconciliation |
| Quarantine | What failures are isolated rather than loaded? |
| Lineage | What source identity and parser version are preserved? |
| Target layout | Parquet, codec, partitions, file sizing |

---

# Excel

## 6. Excel Fundamentals

From a Data Engineering perspective, an Excel workbook is a **container of worksheets plus metadata and presentation structure**. It is not guaranteed to be a clean database table.

### `.xlsx`

An `.xlsx` file is a ZIP-based package containing XML parts, relationships, shared strings, worksheet data, styles, workbook metadata, and other package components.

That architecture is why an apparently tiny workbook can contain more structure than the visible grid suggests.

### `.xls`

Classic `.xls` is a legacy binary Excel format. Conceptually, it is different from `.xlsx`: it is not simply “older `.xlsx`”. Reader compatibility therefore depends on the engine.

For pandas, the current documentation lists `openpyxl` for newer Excel formats and `calamine` for Excel `.xls`, `.xlsx`, `.xlsm`, and `.xlsb` among supported inputs.

### Why spreadsheets are hard ingestion sources

Humans use layout to communicate meaning:

```text
                 Human interpretation
                         ↑
                         │
Titles ─── merged cells ─┼─ colors ─ hidden rows
                         │
       notes ─ totals ─ spacing ─ formulas
                         │
                         ↓
                Machine tabular model
```

A parser mostly sees stored cells. It does not automatically know that a bold row is a title, a merged cell is a report heading, or a bottom row is a total.

---

## 7. Reading Excel with pandas

The central API is `pandas.read_excel()`.

Current pandas supports `sheet_name`, `header`, `usecols`, `skiprows`, `dtype`, `converters`, and explicit `engine` selection. A string/integer/list can select one or several sheets; `sheet_name=None` returns a dictionary of DataFrames.

### Basic example

```python
from pathlib import Path
import pandas as pd

path = Path("sales.xlsx")
df = pd.read_excel(path)

print(df.head())
print(df.dtypes)
```

**Problem solved:** read the first worksheet into a DataFrame.

**Failure cases:** the first worksheet may be the wrong worksheet, headers may not start at row 1, or inferred dtypes may be wrong for identifiers.

### Read one sheet by name

```python
import pandas as pd

sales = pd.read_excel(
    "sales.xlsx",
    sheet_name="September Sales",
)
```

`sheet_name` is safer than relying on worksheet position when the sender may reorder tabs.

### Read multiple sheets

```python
sheets = pd.read_excel(
    "sales.xlsx",
    sheet_name=["North", "South", "West"],
)

for sheet_name, df in sheets.items():
    print(sheet_name, df.shape)
```

For all sheets:

```python
all_sheets = pd.read_excel("sales.xlsx", sheet_name=None)
```

This is useful during inspection, but do not assume every sheet belongs in the production dataset.

### Header rows

```python
# First row contains the real column names.
df = pd.read_excel("sales.xlsx", header=0)

# No header row; create a DataFrame with integer-like default columns.
df = pd.read_excel("raw.xlsx", header=None)
```

For a two-row header:

```python
df = pd.read_excel(
    "report.xlsx",
    header=[1, 2],
)
```

Pandas combines multiple header rows into a `MultiIndex`.

### `skiprows`

```python
# Skip report title and period rows before the actual table header.
df = pd.read_excel(
    "report.xlsx",
    skiprows=3,
    header=0,
)
```

`skiprows` is zero-based and can also accept a list-like object or callable.

### `usecols`

```python
df = pd.read_excel(
    "report.xlsx",
    usecols="A:D",
)
```

Or with column names after the header has been established:

```python
df = pd.read_excel(
    "report.xlsx",
    usecols=["Store", "Date", "Account", "Sales"],
)
```

`usecols` reduces the input surface, but only use it after verifying that the workbook layout is stable.

---

## 8. Choosing `openpyxl` vs `calamine`

Pandas lets you select the Excel engine explicitly:

```python
import pandas as pd

openpyxl_df = pd.read_excel("report.xlsx", engine="openpyxl")
calamine_df = pd.read_excel("report.xlsx", engine="calamine")
```

Current pandas documentation lists:

- `openpyxl` for newer Excel files;
- `calamine` for `.xls`, `.xlsx`, `.xlsm`, and `.xlsb` inputs, among others.

A practical decision process is:

| Question | Lean toward |
|---|---|
| Need broad support for modern Excel behavior and a familiar Python ecosystem? | `openpyxl` |
| Need a Rust/Calamine-based reader and the supported file types fit the workload? | `calamine` / `python-calamine` |
| Need `.xls` specifically? | Verify engine compatibility and test representative files |
| Need exact behavior for a sender's unusual workbook? | Benchmark and validate the actual workbook |

Do not select an engine based only on a generic “fastest” claim. Test the workbook shapes you actually receive.

### Engine inspection

```python
import pandas as pd

with pd.ExcelFile("report.xlsx", engine="openpyxl") as xls:
    print(xls.sheet_names)
```

`ExcelFile` is useful when you need to inspect workbook structure or read several sheets without repeatedly reopening the file.

---

## 9. Reading Excel with Polars

Polars provides `read_excel()` as well.

Current Polars documentation describes `calamine`/`fastexcel` as the default engine for Excel reading, with support for selecting sheets and overriding inferred schemas.

```python
import polars as pl

df = pl.read_excel(
    "sales.xlsx",
    sheet_name="Sales",
)

print(df)
print(df.schema)
```

Explicit schema overrides are useful when inference is wrong:

```python
import polars as pl

df = pl.read_excel(
    "sales.xlsx",
    sheet_name="Sales",
    schema_overrides={
        "account_id": pl.String,
        "sales": pl.Decimal(18, 2),
    },
)
```

Polars can also read multiple sheets by passing multiple sheet names; the result is a mapping of sheet names to DataFrames.

### pandas vs Polars for Excel

| Dimension | pandas | Polars |
|---|---|---|
| Familiarity in data cleaning | Very high | Increasingly common |
| Excel parsing engine choices | Broad engine integration | `calamine`, `openpyxl`, `xlsx2csv` options documented |
| Integration with Python analytics ecosystem | Excellent | Strong, Arrow-oriented |
| Good default choice | Often pandas | Often Polars for teams already standardizing on Polars |

The reader is only one decision. The source contract and downstream architecture matter more than ideology.

---

## 10. Excel Messiness and Data-Quality Traps

### 10.1 The visual grid is not the data model

Consider:

```text
ACME BANK
Monthly Account Report
September 2026

Account | Customer | Amount
0012345 | Asha      | 1250.00
0098765 | Ravi      | 900.00

TOTAL             | 2150.00
```

The top four rows are not four business records. The bottom row is not another account.

### 10.2 A robust data-region strategy

Use this sequence:

```text
Inspect workbook
      ↓
List sheets
      ↓
Inspect first N rows without trusting headers
      ↓
Find semantic header
      ↓
Identify detail region
      ↓
Identify total/note region
      ↓
Parse detail rows
      ↓
Validate totals
```

One useful inspection pass is:

```python
import pandas as pd

raw = pd.read_excel(
    "report.xlsx",
    sheet_name="Report",
    header=None,
    nrows=30,
)

print(raw.to_string(index=False, header=False))
```

This deliberately avoids imposing a header too early.

### 10.3 Cleaning column names

```python
import re


def clean_column_name(name: object) -> str:
    text = str(name).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")

raw.columns = [clean_column_name(c) for c in raw.columns]
```

The exact naming policy belongs to your platform standard.

### 10.4 Numbers stored as text

```python
import pandas as pd

series = pd.Series(["1,200.50", "900.00", None])

amount = pd.to_numeric(
    series.astype("string").str.replace(",", "", regex=False),
    errors="coerce",
)

print(amount)
```

Always distinguish:

```text
Parsing error
vs
Missing value
vs
Actual zero
```

Those are different business states.

---

## 11. Excel Identifiers and Leading Zeros

Suppose the source shows:

```text
Account
000012340
```

If the value is an identifier, turning it into an integer is destructive:

```text
"000012340" → 12340
```

The numeric value may be mathematically equivalent, but the identifier is not.

Use strings deliberately:

```python
import pandas as pd

# Preserve the identifier representation as text.
df = pd.read_excel(
    "accounts.xlsx",
    dtype={"account_id": "string"},
)

print(df["account_id"])
```

For a messy workbook, normalize after reading if the source has already delivered mixed Python types:

```python
df["account_id"] = (
    df["account_id"]
    .astype("string")
    .str.strip()
)
```

Identifiers commonly requiring string semantics include:

- account numbers;
- customer IDs;
- postal codes;
- product codes;
- branch codes.

> **Formatting is not typing.** A cell displayed as `001234` may not be stored as a string.

---

## 12. Excel Dates and the 1900 / 1904 Systems

Excel dates can be represented internally as serial numbers plus workbook date-system rules.

Conceptually:

```text
Serial number
     +
Workbook date system
     +
Time fraction
     ↓
Calendar datetime
```

Two historical date systems matter:

- **1900 date system** — commonly used by Windows Excel workbooks;
- **1904 date system** — associated historically with Mac-oriented Excel workbooks.

The 1900 system also carries the historical **1900 leap-year bug**: Excel's date serial behavior preserves compatibility with Lotus 1-2-3's treatment of 1900 as a leap year.

### Why this matters

If you treat a serial as though it were an arbitrary integer, you can shift dates silently.

The correct workflow is:

1. identify the workbook/date-system context;
2. inspect representative cells;
3. verify known reference dates;
4. convert deliberately;
5. test dates around the historical discontinuity if your source can contain them.

### Safe conversion pattern

When the reader has already interpreted Excel date cells as datetimes, prefer the reader's values rather than manually converting them again.

For genuinely numeric serial values, use an explicit conversion contract. Example for a known **1900-based workbook**:

```python
from datetime import datetime, timedelta


def excel_1900_serial_to_datetime(serial: float) -> datetime:
    """Convert a known Excel 1900-system serial using Excel-compatible semantics.

    This is an educational implementation. Production code should use the
    workbook metadata and test against source-system examples.
    """
    if serial < 1:
        raise ValueError("This example expects a positive Excel serial")

    # Excel's serial 60 represents the fictitious 1900-02-29.
    if serial == 60:
        raise ValueError(
            "Serial 60 is Excel's historical 1900-02-29 compatibility value. "
            "Handle this case explicitly according to the source contract."
        )

    base = datetime(1899, 12, 31)
    days = int(serial)
    fraction = serial - days

    # Skip the fictitious day for serials after 60.
    if serial > 60:
        days -= 1

    return base + timedelta(days=days, seconds=round(fraction * 86400))
```

Do not present this as a universal converter for every workbook. The date system must be part of the source understanding.

### Date regression test

Test values around known boundaries:

```text
Known source date
       ↓
Expected analytical date
       ↓
Assert exact equality
```

A one-day error is easy to miss and can poison partitioning, reporting periods, and joins.

---

## 13. Excel Formulas, Cached Values, Merged Cells, and Hidden Data

### Formulas vs cached values

A formula cell contains an expression such as:

```text
=SUM(D5:D20)
```

The displayed value may be a cached calculation result.

This distinction matters because an ingestion job asking for formulas and a job asking for values have different semantics.

With `openpyxl`:

```python
from openpyxl import load_workbook

wb_formula = load_workbook("report.xlsx", data_only=False)
wb_values = load_workbook("report.xlsx", data_only=True)

formula = wb_formula["Report"]["D21"].value
cached = wb_values["Report"]["D21"].value

print("formula:", formula)
print("cached:", cached)
```

A cached value may be missing or stale depending on how the workbook was last calculated. Therefore:

> Never assume “the formula result” is guaranteed to be freshly recalculated during ingestion.

### Merged cells

Merged cells are layout objects, not ordinary repeated values.

```text
+-------------------------------+
|       Monthly Sales           |  ← merged region
+----------+----------+---------+
| Store    | Date     | Amount  |
```

Only the top-left cell of a merged range carries the meaningful value in common workbook representations.

Inspect them deliberately:

```python
from openpyxl import load_workbook

wb = load_workbook("report.xlsx", read_only=False, data_only=True)
ws = wb["Report"]

for merged_range in ws.merged_cells.ranges:
    print("merged:", merged_range)
```

### Hidden rows and sheets

Do not make this binary assumption:

> “Hidden means irrelevant.”

A hidden sheet may contain staging data, control values, or an old template. A hidden row may be an intentionally excluded subtotal—or a hidden transaction.

Operational policy should be explicit:

```text
Hidden content discovered
        ↓
Classify
 ┌──────┼────────┐
 ↓      ↓        ↓
Expected Ignored  Unexpected
```

Then record the decision in the source contract.

### Trailing empty rows and columns

Spreadsheet users often format entire ranges. A library may therefore encounter a used range larger than the meaningful table.

Your production parser should detect the real data region rather than trusting the maximum worksheet dimensions blindly.

### Blank cells vs empty strings

These can represent different states:

```text
blank cell   → missing / absent
""           → explicit empty string
"N/A"        → source-defined code
0            → actual numeric zero
```

Map them according to the data contract.

---

## 14. Excel Totals and Reconciliation

A totals row is not merely another row to “drop”. It can act as a **control signal** from the source system.

Suppose the report says:

```text
Detail rows:
100.00
250.00
150.00

TOTAL = 500.00
```

The ingestion job should calculate:

```text
parsed detail count = 3
parsed amount sum   = 500.00
```

and compare those with the control information.

Example:

```python
from decimal import Decimal

rows = [
    {"account_id": "001", "amount": Decimal("100.00")},
    {"account_id": "002", "amount": Decimal("250.00")},
    {"account_id": "003", "amount": Decimal("150.00")},
]

reported_total = Decimal("500.00")

computed_total = sum((row["amount"] for row in rows), Decimal("0.00"))

if computed_total != reported_total:
    raise ValueError(
        f"Control-total mismatch: computed={computed_total} "
        f"reported={reported_total}"
    )
```

Use `Decimal` for exact financial reconciliation rather than binary floating-point equality.

### Fail vs quarantine vs partial acceptance

A mismatch policy must be explicit:

| Situation | Possible response |
|---|---|
| One malformed detail record | Quarantine record; continue if contract permits |
| Unknown record type | Usually fail or quarantine file, depending on contract |
| Trailer count mismatch | Often fail the batch because completeness is uncertain |
| Amount mismatch | Usually fail the batch or quarantine the whole source |
| One business-rule violation | Quarantine record when safe to isolate |

There is no universal policy. The critical engineering point is:

> A parser succeeding technically does not prove that the ingestion is complete and correct.

---

# XML

## 15. XML Fundamentals

XML is a hierarchical data representation.

Tiny example:

```xml
<customer id="C100">
  <name>Sovon</name>
  <city>Kolkata</city>
</customer>
```

Think in terms of a tree:

```text
customer
├── name
│   └── text: Sovon
└── city
    └── text: Kolkata
```

### Core parts

- **Element** — `<customer>...</customer>`
- **Attribute** — `id="C100"`
- **Text** — `Sovon`
- **Parent/child relationship** — `customer` contains `name`
- **Repeated elements** — multiple `<price>` children
- **Namespace** — a URI that qualifies an element name

XML is useful in enterprise exchange because it can represent nested documents, explicit structure, optional fields, and independently versioned contracts.

---

## 16. XML Elements, Attributes, Text, and Namespaces

Consider:

```xml
<order xmlns="urn:shop:order" id="O100">
  <customer>
    <id>C10</id>
    <name>Asha</name>
  </customer>
  <items>
    <item sku="SKU1">
      <quantity>2</quantity>
    </item>
    <item sku="SKU2">
      <quantity>1</quantity>
    </item>
  </items>
</order>
```

The namespace prefix may be absent, yet the element still belongs to the namespace URI `urn:shop:order`.

> **Prefix and namespace URI are not the same thing.**

For example, these are semantically equivalent namespace-qualified elements:

```xml
<o:order xmlns:o="urn:shop:order"/>
```

and

```xml
<order xmlns="urn:shop:order"/>
```

A parser therefore needs the URI mapping, not merely the literal prefix.

---

## 17. XML Parsing with ElementTree

Python's standard library includes `xml.etree.ElementTree`.

### Basic parse

```python
import xml.etree.ElementTree as ET

root = ET.parse("products.xml").getroot()

print(root.tag)
for child in root:
    print(child.tag)
```

### Find elements

```python
import xml.etree.ElementTree as ET

root = ET.parse("products.xml").getroot()

for product in root.findall("product"):
    print(product.get("id"))
```

For a namespace-qualified document:

```python
import xml.etree.ElementTree as ET

root = ET.parse("products.xml").getroot()
ns = {"p": "urn:example:products"}

for product in root.findall("p:product", namespaces=ns):
    print(product.get("id"))
```

A simple tree walk is often enough when:

- the structure is shallow;
- the record path is stable;
- there are few conditions;
- maintainability is more important than query expressiveness.

---

## 18. XML Parsing with lxml

`lxml` adds a mature XML toolset including XPath, streaming iteration, validation, and other features useful in ingestion systems. Its API supports element XPath evaluation with namespace mappings and `iterparse()` for event-driven processing.

### Basic parse

```python
from lxml import etree

root = etree.parse("products.xml").getroot()

print(root.tag)
```

### XPath

```python
from lxml import etree

root = etree.parse("products.xml").getroot()

ns = {"p": "urn:example:products"}

products = root.xpath("//p:product", namespaces=ns)

for product in products:
    print(product.get("id"))
```

XPath becomes especially useful when the source has multiple paths, conditions, or namespaces.

### When to choose which

| Tool | Strength | Limitation |
|---|---|---|
| `ElementTree` | Standard library, simple tree operations | Less expressive than full XPath tooling |
| `lxml` | Powerful XPath, validation, streaming tools | Extra dependency, larger API surface |
| `pandas.read_xml` | Fast route from tabular XML paths to DataFrame | Less suitable for complex document-level orchestration |

---

## 19. XML with `pandas.read_xml`

For an XML structure that maps cleanly to rows, pandas can reduce boilerplate:

```python
import pandas as pd

items = pd.read_xml(
    "products.xml",
    xpath=".//item",
)

print(items)
```

Namespaces can be supplied when the XPath references qualified names:

```python
items = pd.read_xml(
    "products.xml",
    xpath=".//p:item",
    namespaces={"p": "urn:shop:order"},
)
```

Use `read_xml` when the XML-to-tabular mapping is straightforward. Once the document requires validation, streaming, multiple child tables, or complex recovery behavior, explicit `ElementTree`/`lxml` code usually gives you more control.

---

## 20. XPath for Data Engineering

You do not need to memorize XPath. Learn a small ingestion-oriented subset.

| Expression | Meaning |
|---|---|
| `//item` | any `item` descendant |
| `/root/item` | `item` directly under `root` |
| `.//item` | `item` descendants from current context |
| `//item[@status='A']` | items with a status attribute |
| `//item/name` | child `name` elements under items |
| `//item/@id` | id attributes |

Namespace-aware XPath is often the key production detail:

```python
ns = {"p": "urn:shop:order"}
items = root.xpath("//p:item[@active='true']", namespaces=ns)
```

If an XPath unexpectedly returns zero rows, inspect the actual namespace URI before changing the path randomly.

---

## 21. XML Tree → Analytical Tables

An XML document is not automatically one table.

Consider:

```text
product
├── id
├── name
└── prices
    ├── price
    ├── price
    └── price
```

The correct model may be:

```text
products
-------------------
product_id
name

product_prices
-------------------
product_id
currency
price
```

### Grain declaration

```text
products       = one row per product
product_prices = one row per product-price observation
```

This avoids repeating parent data:

```text
BAD: product_id/name copied into every price row
GOOD: child table carries product_id as a relationship key
```

### Accidental multiplication

If a product has 3 prices and 4 regions:

```text
3 prices × 4 regions = 12 combinations
```

Exploding both arrays into one table can create 12 rows even if the intended grains were 3 and 4 separately.

> Define the grain of every output table before exploding nested structures.

This is the same conceptual rule from Topic 06, applied to enterprise XML.

---

## 22. Streaming XML at Scale

A 2 GB XML feed should not imply:

```python
xml_text = Path("feed.xml").read_text()
```

or:

```python
root = etree.parse("feed.xml").getroot()
```

followed by retaining the entire document indefinitely.

For very large documents, the architecture should process one logical record at a time.

```text
2 GB XML
   ↓
stream bytes
   ↓
parse events
   ↓
complete <product>
   ↓
extract product + prices
   ↓
emit rows
   ↓
clear processed node
   ↓
continue
```

---

## 23. `iterparse` and Bounded Memory

Python's `ElementTree.iterparse()` incrementally parses sections and yields events such as `start` and `end`. It still performs blocking reads, so “streaming” here means incremental parsing rather than asynchronous network streaming.

### Educational parent/child streaming parser

```python
from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Iterator
from typing import Any


def local_name(tag: str) -> str:
    """Return an XML local name from '{uri}name' or 'name'."""
    return tag.rsplit("}", 1)[-1]


def stream_products(path: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    products: list[dict[str, Any]] = []
    prices: list[dict[str, Any]] = []

    for event, elem in ET.iterparse(path, events=("end",)):
        if local_name(elem.tag) != "product":
            continue

        product_id = elem.get("id")
        if not product_id:
            raise ValueError("product without required id")

        product_row = {
            "product_id": product_id,
            "name": None,
        }

        for child in elem:
            child_name = local_name(child.tag)
            if child_name == "name":
                product_row["name"] = child.text.strip() if child.text else None
            elif child_name == "prices":
                for price_elem in child:
                    if local_name(price_elem.tag) != "price":
                        continue
                    prices.append(
                        {
                            "product_id": product_id,
                            "currency": price_elem.get("currency"),
                            "price": price_elem.text.strip()
                            if price_elem.text
                            else None,
                        }
                    )

        products.append(product_row)

        # Drop children and text already processed so the tree can release
        # memory as parsing advances.
        elem.clear()

    return products, prices
```

### Why `clear()` matters

Without clearing processed elements, references can accumulate and the parser can effectively retain a large fraction of the document tree.

A common production pattern is more careful:

```python
for event, elem in etree.iterparse(
    path,
    events=("end",),
    tag="{urn:example}product",
):
    process(elem)
    elem.clear()

    # For lxml, remove already-processed preceding siblings when safe for
    # your document structure to prevent the parent from retaining them.
```

`lxml.etree.iterparse` supports event selection and tag filtering and documents options such as `no_network` and entity-resolution behavior.

### Bounded-memory output

Do not recreate the same problem downstream by collecting millions of extracted rows in one Python list.

Instead, use a bounded batch:

```text
parse 50,000 records
   ↓
validate
   ↓
write a batch to Parquet
   ↓
discard batch
   ↓
continue
```

The exact batch size is a benchmark parameter, not a magic constant.

---

## 24. XML Error Handling

There are at least four failure classes:

```text
File-level syntax failure
       │
       ├── malformed XML
       ├── truncated file
       └── encoding problem

Record-level failure
       │
       ├── missing required field
       ├── invalid value
       └── unexpected child

Schema failure
       │
       └── violates XSD contract

Business failure
       │
       └── structurally valid but invalid for the business
```

### Malformed XML

If the XML is structurally malformed, you may not be able to safely continue from an arbitrary location. A file-level failure should normally quarantine the source file and preserve the parser error.

### Record-level failure

If the document remains structurally valid and a single business record is wrong, you may be able to quarantine just that logical record and continue.

### Progress tracking

For large feeds, record:

- source file identity;
- parser version;
- number of records seen;
- number emitted;
- number quarantined;
- last durable checkpoint if the design supports restart from checkpoints;
- failure summary.

Do not claim that `iterparse` automatically provides restartable record checkpoints. That is an application-level design decision.

---

## 25. XML Security

Untrusted XML is a security boundary.

The critical risks include:

- **XXE (XML External Entity)** — malicious document declarations can cause an XML processor to resolve an external resource unexpectedly;
- **entity-expansion attacks** — recursively expanding entities can consume disproportionate CPU or memory;
- resource exhaustion / denial-of-service behavior;
- unexpected network or local-resource access through unsafe parser configuration.

The conceptual lesson is:

```text
Untrusted XML
     ↓
Unsafe parser defaults
     ↓
Potentially dangerous resolution/expansion
```

Do not turn security teaching into an exploit recipe. Focus on defensive architecture.

---

## 26. XXE and Entity Expansion

### XXE concept

A document can contain an external entity declaration. If the parser resolves it, the parser may attempt to retrieve an external resource.

The danger is not “XML syntax”; the danger is **parser behavior applied to untrusted input**.

### Entity expansion concept

An attacker can create entities that expand repeatedly. A tiny document can therefore cause extremely large in-memory expansions.

A well-known form of entity-expansion abuse is the **"billion laughs" attack**, where nested entity references can expand a small XML document into an extremely large amount of data.

```xml
<!DOCTYPE lolz [
  <!ENTITY a "ha"><!ENTITY b "&a;&a;&a;&a;&a;&a;">
]><lolz>&b;</lolz>
```

This small example shows one entity expanding another. Each extra level of nesting multiplies the expansion, which can consume disproportionate CPU and memory. That is the "billion laughs" class of attack. `defusedxml` rejects DTD and entity-expansion behavior like this instead of letting the unsafe expansion proceed.

For this chapter, remember:

> The parser must be configured so untrusted XML cannot unexpectedly resolve external entities or perform dangerous expansion.

---

## 27. `defusedxml`

`defusedxml` provides hardened wrappers around Python's XML APIs for common unsafe XML behaviors. Its implementation exposes defensive controls around DTDs, entities, and external references.

### Safe basic parsing pattern

```python
from defusedxml import ElementTree as DefusedET


def parse_untrusted_xml(path: str):
    """Parse untrusted XML with a defensive parser."""
    return DefusedET.parse(path)
```

For an in-memory string:

```python
from defusedxml import ElementTree as DefusedET

xml_bytes = b"<root><item>123</item></root>"
root = DefusedET.fromstring(xml_bytes)
print(root.findtext("item"))
```

### What `defusedxml` does not solve

It does not automatically solve:

- business validation;
- incorrect namespaces;
- incorrect record grain;
- bad numeric values;
- missing business keys;
- incorrect XSD conformance policy;
- duplicate records;
- downstream data leaks caused by your own logging/quarantine design.

Security and correctness are separate layers.

### Safe XML architecture

```text
Untrusted source
      ↓
Size / type checks
      ↓
Defensive XML parser
      ↓
Optional XSD validation
      ↓
Business validation
      ↓
Quarantine / accept
```

---

## 28. XSD Validation with lxml

An XML document can be:

1. **syntactically valid XML** — it is well formed;
2. **schema valid** — it conforms to the expected XSD;
3. **business valid** — it satisfies business rules.

These are different tests.

### Embedded XSD example

The exercise must remain self-contained, so keep the XSD in memory:

```python
from lxml import etree

xsd_text = """
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="urn:example:products"
           xmlns="urn:example:products"
           elementFormDefault="qualified">
  <xs:element name="feed">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="product" maxOccurs="unbounded">
          <xs:complexType>
            <xs:sequence>
              <xs:element name="name" type="xs:string"/>
            </xs:sequence>
            <xs:attribute name="id" type="xs:string" use="required"/>
          </xs:complexType>
        </xs:element>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>
"""

schema_doc = etree.XML(xsd_text.encode("utf-8"))
schema = etree.XMLSchema(schema_doc)

xml_text = """
<feed xmlns="urn:example:products">
  <product id="P100">
    <name>Keyboard</name>
  </product>
</feed>
"""

xml_doc = etree.fromstring(xml_text.encode("utf-8"))

if not schema.validate(xml_doc):
    print(schema.error_log)
    raise ValueError("XML failed XSD validation")
```

`lxml.etree.XMLSchema` creates a schema validator and provides validation/error-log behavior.

### When to validate

For high-value feeds, validate as early as practical:

```text
parse safely
   ↓
structural validity
   ↓
XSD validation (when applicable)
   ↓
business rules
   ↓
reconciliation
   ↓
load
```

Do not confuse XSD with business rules. An XSD can say an element is a decimal; it may not know whether the amount is allowed for a particular account.

---

# Fixed-Width and Mainframe Data

## 29. Fixed-Width Files Fundamentals

A fixed-width record assigns meaning to **positions**, not delimiters.

Example:

```text
Positions:  1        11       21       31
            |--------|--------|--------|
Record:     Asha     00001234 00123450  +
```

In machine terms, positions are commonly zero-based slices:

```text
human positions 1–10  → Python [0:10]
human positions 11–18 → Python [10:18]
```

That difference is a major source of off-by-one errors.

### Layout diagram

```text
012345678901234567890123456789
|---------|--------|----------|
name      account  amount
```

You need a source layout specification to know where one field ends and the next begins.

### Padding and alignment

Text fields may be left-aligned:

```text
"ABC       "
```

Numbers may be right-aligned:

```text
"      123"
```

A parser should strip padding only when the contract says padding is not significant.

---

## 30. Fixed-Width Parsing with pandas

`pandas.read_fwf()` reads fixed-width formatted lines.

### `widths`

```python
import pandas as pd
from io import StringIO

text = """000001Asha     0000123400012500
000002Ravi     0000789000009000
"""

# widths: record_id=6, customer=10, account=8, amount=8

df = pd.read_fwf(
    StringIO(text),
    widths=[6, 10, 8, 8],
    names=["record_id", "customer", "account", "amount_raw"],
)

print(df)
```

### `colspecs`

`colspecs` gives explicit start/end offsets:

```python
import pandas as pd
from io import StringIO

text = """000001Asha     0000123400012500
000002Ravi     0000789000009000
"""

spec = [
    (0, 6),    # record_id
    (6, 16),   # customer
    (16, 24),  # account
    (24, 32),  # amount
]

df = pd.read_fwf(
    StringIO(text),
    colspecs=spec,
    names=["record_id", "customer", "account", "amount_raw"],
)

print(df)
```

Use `colspecs` when you want the positions to be visible in the parser code. For production layout-driven parsers, a separate specification is usually even safer.

---

## 31. Fixed-Width Parsing with Polars

Polars does not require a dedicated fixed-width reader for many cases. When lines are already in a DataFrame/Series, direct string slicing can be explicit and efficient.

Example:

```python
import polars as pl

lines = pl.DataFrame(
    {
        "raw": [
            "000001Asha     0000123400012500",
            "000002Ravi     0000789000009000",
        ]
    }
)

parsed = lines.select(
    pl.col("raw").str.slice(0, 6).alias("record_id"),
    pl.col("raw").str.slice(6, 10).str.strip_chars().alias("customer"),
    pl.col("raw").str.slice(16, 8).alias("account"),
    pl.col("raw").str.slice(24, 8).alias("amount_raw"),
)

print(parsed)
```

Convert types explicitly after slicing:

```python
parsed = parsed.with_columns(
    pl.col("record_id").cast(pl.Int64),
    pl.col("account").cast(pl.String),
    pl.col("amount_raw").cast(pl.Int64),
)
```

### When direct slicing is useful

Use it when:

- the layout is fixed and known;
- you want expression-level transformation;
- the input is already represented as a string column;
- you want to integrate parsing with a larger Polars transformation pipeline.

For many heterogeneous record-type files, however, a small explicit dispatcher can be easier to audit than one giant expression.

---

## 32. Padding, Alignment, and Signed Fields

A field such as:

```text
"    1234"
```

may be a right-aligned integer.

A field such as:

```text
"ABC     "
```

may be a left-aligned code.

A signed amount may appear as:

```text
00012345+
00012345-
```

or the sign may occupy a separate field.

Therefore, parsing should distinguish:

```text
raw representation
        ↓
strip / interpret padding
        ↓
interpret sign
        ↓
convert type
```

Do not `strip()` every field automatically. Leading/trailing spaces may be significant in some fixed-width contracts.

---

## 33. Implied Decimals

A mainframe field may encode:

```text
0001234
```

with an implied scale of 2.

The business value is:

```text
12.34
```

Conceptually:

```text
raw integer = 1234
scale       = 2
value       = 1234 / 100 = 12.34
```

### Safe conversion

```python
from decimal import Decimal


def parse_implied_decimal(raw: str, scale: int) -> Decimal:
    clean = raw.strip()
    if not clean:
        return Decimal("0")

    if not clean.isdigit():
        raise ValueError(f"Invalid implied-decimal field: {raw!r}")

    return Decimal(clean).scaleb(-scale)

print(parse_implied_decimal("0001234", 2))  # 12.34
```

This function should be driven by a **layout specification**, not by magic assumptions buried in business code.

---

## 34. Record-Type Codes

A single fixed-width file can contain multiple layouts.

Example:

```text
H...
D...
D...
D...
T...
```

A one-layout `read_fwf()` call is therefore insufficient.

The parser should first inspect the record type:

```text
line
 ↓
line[0]
 ↓
┌──────┬──────┬──────┐
 H      D      T
 ↓      ↓      ↓
header detail trailer
layout  layout  layout
```

---

## 35. Header / Detail / Trailer Files

A typical feed is:

```text
H = file/header control information
D = business detail records
T = file/trailer control information
```

The header might contain:

- source system;
- business date;
- batch ID;
- expected record count.

The trailer might contain:

- record count;
- amount total;
- checksum/control total.

The ingestion job should keep these control records out of the analytical detail table while still using them for validation.

---

## 36. Layout Specifications as Code

This is one of the most important production concepts.

Avoid scattering this everywhere:

```python
value = line[37:49]
amount = line[49:61]
code = line[61:66]
```

Six months later, nobody knows what 37, 49, 61, or 66 mean.

Instead use a layout model:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class FieldSpec:
    name: str
    start: int
    end: int
    data_type: str
    scale: int | None = None
    required: bool = True
    record_type: str = "D"


DETAIL_LAYOUT = [
    FieldSpec("account_id", 1, 11, "string"),
    FieldSpec("amount", 11, 19, "decimal", scale=2),
    FieldSpec("status", 19, 20, "string"),
]
```

### Why this is safer

A specification can contain:

- field name;
- start/end position;
- width;
- data type;
- decimal scale;
- sign rules;
- nullable/required status;
- record type;
- version;
- effective date.

That allows the parser to become generic.

---

## 37. Versioned Layout Specifications

Source contracts change.

Suppose version 1 says:

```text
amount: 11–19
```

and version 2 inserts a field:

```text
amount: 15–23
```

Hard-coded slices can silently parse the wrong bytes.

A versioned specification might look conceptually like:

```text
source: BANK_A
record_type: D
layout_version: 2026-01
valid_from: 2026-01-01
fields: ...

source: BANK_A
record_type: D
layout_version: 2026-07
valid_from: 2026-07-01
fields: ...
```

### Embedded YAML-style specification

The following is an **example inside this Markdown file**. Do not create a separate YAML file.

```yaml
source: BANK_A
layout_version: "2026-07"
record_types:
  D:
    fields:
      - name: account_id
        start: 1
        end: 10
        type: string
        required: true
      - name: amount
        start: 10
        end: 19
        type: decimal
        scale: 2
        required: true
      - name: sign
        start: 19
        end: 20
        type: sign
        required: true
```

### Embedded CSV-style alternative

```text
record_type,name,start,end,type,scale,required
D,account_id,1,10,string,,true
D,amount,10,19,decimal,2,true
D,sign,19,20,sign,,true
```

Both are representations of the same concept: **metadata describing a parser contract**.

### Loading a specification

For an embedded Python dictionary, no external dependency is needed:

```python
LAYOUT = {
    "D": [
        {"name": "account_id", "start": 1, "end": 10, "type": "string"},
        {"name": "amount", "start": 10, "end": 19, "type": "decimal", "scale": 2},
        {"name": "sign", "start": 19, "end": 20, "type": "sign"},
    ]
}
```

In a real platform, the external specification is often stored and versioned separately from the parser implementation so sender changes can be reviewed without rewriting the entire parser.

---

## 38. Record-Type Dispatch

A production-style architecture is:

```text
read raw line
      ↓
validate minimum length
      ↓
detect record type
      ↓
select versioned layout
      ↓
parse fields
      ↓
convert types
      ↓
validate record
      ↓
emit row OR quarantine
```

### Complete educational dispatcher

```python
from __future__ import annotations

from decimal import Decimal
from typing import Any


def parse_field(raw: str, spec: dict[str, Any]) -> Any:
    value = raw.strip()
    field_type = spec["type"]

    if value == "" and not spec.get("required", True):
        return None

    if field_type == "string":
        return value

    if field_type == "integer":
        return int(value)

    if field_type == "decimal":
        scale = int(spec.get("scale", 0))
        return Decimal(value).scaleb(-scale)

    if field_type == "sign":
        if value not in {"+", "-"}:
            raise ValueError(f"Invalid sign: {value!r}")
        return value

    raise ValueError(f"Unsupported field type: {field_type}")


def parse_line(line: str, layout_by_type: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    if not line:
        raise ValueError("empty line")

    record_type = line[0]
    layout = layout_by_type.get(record_type)
    if layout is None:
        raise ValueError(f"Unknown record type: {record_type!r}")

    row: dict[str, Any] = {"record_type": record_type}

    for spec in layout:
        start = int(spec["start"])
        end = int(spec["end"])

        if end > len(line):
            raise ValueError(
                f"Line too short for field {spec['name']}: need {end}, got {len(line)}"
            )

        row[spec["name"]] = parse_field(line[start:end], spec)

    return row
```

### Bad record vs bad file

Treat these differently.

```text
bad record
   ↓
quarantine record
   ↓
continue if the file remains trustworthy
```

versus:

```text
bad file structure / missing trailer / broken encoding
   ↓
quarantine entire source file
   ↓
do not publish partial data
```

The correct boundary depends on the source contract and whether completeness can still be proven.

---

# Mainframe Data

## 39. Mainframe Data Fundamentals

Mainframes remain important because large organizations often have long-lived systems for banking, insurance, government, airlines, retail, and other transaction-heavy workloads.

Common data-engineering concerns are:

- COBOL copybooks;
- EBCDIC encoded text;
- binary numerics;
- packed decimal (`COMP-3`);
- record-oriented files;
- header/detail/trailer control structures.

Your goal is **working ingestion knowledge**, not a complete COBOL course.

---

## 40. COBOL Copybooks

A COBOL copybook is effectively a reusable data-layout definition.

Conceptually:

```text
COBOL Copybook
      ↓
Field names
positions
lengths
types
scales
sign rules
      ↓
Parsing specification
      ↓
Typed analytical columns
```

A copybook may describe fields such as:

```text
ACCOUNT-ID      PIC X(10)
AMOUNT          PIC S9(7)V99 COMP-3
STATUS          PIC X(1)
```

You do not need to become a COBOL programmer to recognize that this means:

- `ACCOUNT-ID` is text;
- `AMOUNT` is signed numeric with an implied decimal scale of 2 and packed-decimal storage;
- `STATUS` is one character.

The engineering task is to translate that contract accurately into a parser specification.

---

## 41. EBCDIC

EBCDIC is a family of character encodings historically used by IBM mainframe systems. It is not the same byte encoding as ASCII or UTF-8.

Python provides several EBCDIC-related codec aliases; `cp037` is one example documented by the Python standard-library codec registry.

### Conceptual flow

```text
mainframe bytes
      ↓
EBCDIC decode (e.g. cp037)
      ↓
Unicode text
      ↓
normal parsing
```

### Simple decoding example

```python
raw = bytes.fromhex("c8c5d3d3d6")
text = raw.decode("cp037")

print(text)  # HELLO
```

The code point mapping is encoding-specific. Never guess an encoding from one file's visual appearance.

### Safe operational pattern

Store:

- original binary file;
- declared source encoding;
- actual decoding used;
- parser/layout version;
- validation outcome.

That makes a future encoding correction replayable.

---

## 42. Packed Decimal / `COMP-3`

Packed decimal stores decimal digits compactly in binary nibbles.

A byte has two nibbles:

```text
1 byte
┌────────┬────────┐
│ 4 bits │ 4 bits │
│ nibble │ nibble │
└────────┴────────┘
```

A common conceptual pattern is:

```text
[ digit ][ digit ] [ digit ][ digit ] [ digit ][ sign ]
```

The final low nibble is typically a sign nibble. Exact sign conventions can vary by environment; common positive markers include `C` and `F`, and common negative markers include `D` and `B`.

### Example

```text
12 34 5C
```

can represent the unscaled digits:

```text
12345
```

with `C` meaning positive in a common convention.

With scale 2:

```text
12345 / 100 = 123.45
```

### Educational decoder

```python
from __future__ import annotations

from decimal import Decimal


POSITIVE_SIGNS = {0xA, 0xC, 0xE, 0xF}
NEGATIVE_SIGNS = {0xB, 0xD}


def decode_comp3(raw: bytes, scale: int = 0) -> Decimal:
    """Educational COMP-3 decoder for common sign-nibble conventions."""
    if not raw:
        raise ValueError("COMP-3 field cannot be empty")

    nibbles: list[int] = []
    for byte in raw:
        nibbles.append((byte >> 4) & 0x0F)
        nibbles.append(byte & 0x0F)

    sign_nibble = nibbles.pop()

    if sign_nibble not in POSITIVE_SIGNS | NEGATIVE_SIGNS:
        raise ValueError(f"Unsupported sign nibble: 0x{sign_nibble:X}")

    if any(n > 9 for n in nibbles):
        raise ValueError("Invalid digit nibble in COMP-3 field")

    digits = "".join(str(n) for n in nibbles)
    unscaled = Decimal(digits or "0")
    value = unscaled.scaleb(-scale)

    if sign_nibble in NEGATIVE_SIGNS:
        value = -value

    return value


raw = bytes.fromhex("12345C")
print(decode_comp3(raw, scale=2))
# Expected when run: 123.45
```

### Why generic text parsing fails

These bytes are not ordinary characters. Treating them as UTF-8 or fixed-width text can produce meaningless output.

Also note the distinction:

```text
Source storage representation
          ≠
Target analytical representation
```

The lake should usually store a proper typed decimal such as Arrow/Parquet decimal, not the original packed bytes as the analytical value.

### Production warning

The decoder above is intentionally educational. Production mainframe ingestion should use battle-tested, source-compatible libraries and test against a representative set of signed, zero, maximum, negative, and boundary values.

---

## 43. Binary Mainframe Fields

A mainframe record may mix:

```text
text | packed decimal | binary integer | text
```

That means “decode whole file as `cp037`” can be wrong.

The layout specification must identify which byte ranges are:

- character encoded;
- packed decimal;
- binary numeric;
- control/status bytes.

Endianness matters for binary integers, while packed-decimal interpretation follows the source's data representation rather than ordinary integer byte order.

---

# Legacy-to-Lake Architecture

## 44. Legacy-to-Lake Architecture

A robust architecture is:

```text
                    SOURCE
                      │
          ┌───────────┼─────────────┐
          ↓           ↓             ↓
       Excel         XML       Fixed-width
          │           │             │
          └───────────┼─────────────┘
                      ↓
               BRONZE PRESERVE
                      ↓
                Safe Parsing
                      ↓
               Schema / Type Rules
                      ↓
               Business Validation
                      ↓
                Reconciliation
                 ┌────┴────┐
                 ↓         ↓
              ACCEPT    QUARANTINE
                 ↓         │
           Typed Silver    │
                 ↓         │
              Parquet  ◄───┘ (for replay)
                 ↓
       Partition + Compression
                 ↓
            Downstream BI/ML
```

### Bronze

Keep the original source unchanged.

Bronze should preserve the evidence required to answer:

> “What exactly did the sender send us?”

### Silver

Silver turns source representations into typed analytical records.

Typical output:

- Parquet;
- explicit types;
- useful partitioning;
- appropriate compression;
- sensible file sizing.

### Lineage metadata

Record, where appropriate:

- source identifier/path/object key;
- source file hash or stable identity;
- source arrival timestamp;
- ingestion run ID;
- parser version;
- layout version;
- source-system name;
- parsing timestamp;
- validation result.

Do not put sensitive raw values into logs by default.

---

## 45. Bronze Preservation

Bronze is not an excuse to keep everything forever without policy.

It is a controlled evidence layer.

A good pattern is:

```text
immutable source
      ↓
content identity
      ↓
bronze retention policy
      ↓
replay / audit / backfill
```

Why preserve raw source?

- parser bugs can be corrected without asking the sender to resend;
- schema/layout changes can be reprocessed;
- disputed reconciliation results can be investigated;
- lineage remains auditable;
- historical backfills become possible.

Never overwrite bronze merely because you found a parsing bug.

---

## 46. Silver Parquet Conversion

Once the source is understood and validated:

```text
raw legacy representation
        ↓
normalized types
        ↓
Arrow table
        ↓
Parquet
```

Example with PyArrow:

```python
from datetime import date
from decimal import Decimal

import pyarrow as pa
import pyarrow.parquet as pq

rows = [
    {
        "account_id": "00001234",
        "business_date": date(2026, 9, 28),
        "amount": Decimal("123.45"),
    },
    {
        "account_id": "00007890",
        "business_date": date(2026, 9, 28),
        "amount": Decimal("900.00"),
    },
]

table = pa.Table.from_pylist(
    rows,
    schema=pa.schema(
        [
            pa.field("account_id", pa.string(), nullable=False),
            pa.field("business_date", pa.date32(), nullable=False),
            pa.field("amount", pa.decimal128(18, 2), nullable=False),
        ]
    ),
)

pq.write_table(
    table,
    "silver_accounts.parquet",
    compression="zstd",
)
```

PyArrow's Parquet writer supports Zstandard and other codecs; it writes Arrow tables to Parquet with explicit compression settings.

### Reusing Topics 01–09

- row vs columnar → Parquet as analytical storage;
- Parquet internals → row groups/statistics/layout awareness;
- PyArrow → typed file creation;
- Avro/row formats → understanding source ingestion representations;
- nested data → XML parent/child modeling;
- compression → Zstandard choice where appropriate;
- partitioning → output directory layout;
- small files → batching and target file discipline.

This is the point where the earlier topics become one engineering system.

---

## 47. Quarantine Design

Every unparseable record should carry enough context to explain and replay the failure.

Recommended fields:

| Field | Purpose |
|---|---|
| `source_id` | Which source file/feed? |
| `record_number` | Which record? |
| `raw_record` or secure reference | What failed? |
| `error_reason` | Why was it rejected? |
| `layout_version` | Which parser contract was used? |
| `parser_version` | Which code version? |
| `ingestion_run_id` | Which execution? |
| `timestamp` | When was it processed? |

### Privacy/security

Raw failed records may contain personal or financial information.

Therefore quarantine itself must be protected with:

- appropriate access controls;
- encryption;
- retention policy;
- masking/redaction where operationally sufficient;
- audit logging.

“Quarantine” does not mean “dump sensitive data into a public log file”.

---

## 48. Sender Reconciliation

Reconciliation is the bridge between “we parsed something” and “we processed the file completely.”

Typical controls:

```text
Header
 ├── expected detail count
 └── batch identity

Details
 ├── parsed count
 └── parsed amount sum

Trailer
 ├── reported detail count
 └── reported amount sum
```

### Reconciliation flow

```text
Source controls
      ↓
Parse detail records
      ↓
Compute count / amount
      ↓
Compare
      ↓
┌─────┴─────┐
↓           ↓
MATCH      MISMATCH
↓           ↓
accept    fail/quarantine
```

---

## 49. Control Totals and Trailer Records

### Complete H/D/T example

```python
from __future__ import annotations

from decimal import Decimal


def parse_fixed_width_feed(lines: list[str]) -> dict[str, object]:
    if not lines:
        raise ValueError("Empty file")

    header = lines[0]
    trailer = lines[-1]

    if header[0] != "H":
        raise ValueError("Missing H header")
    if trailer[0] != "T":
        raise ValueError("Missing T trailer")

    expected_count = int(header[1:9])
    expected_amount = Decimal(trailer[1:15]).scaleb(-2)
    reported_count = int(trailer[15:23])

    details: list[dict[str, object]] = []
    for record_number, line in enumerate(lines[1:-1], start=2):
        if line[0] != "D":
            raise ValueError(f"Unexpected record type at line {record_number}")

        account_id = line[1:11].strip()
        amount_raw = line[11:19]
        sign = line[19:20]

        amount = Decimal(amount_raw).scaleb(-2)
        if sign == "-":
            amount = -amount
        elif sign != "+":
            raise ValueError(f"Bad sign at line {record_number}")

        details.append(
            {
                "account_id": account_id,
                "amount": amount,
            }
        )

    actual_count = len(details)
    actual_amount = sum((d["amount"] for d in details), Decimal("0"))

    if actual_count != expected_count or actual_count != reported_count:
        raise ValueError(
            f"Count mismatch: actual={actual_count}, "
            f"header={expected_count}, trailer={reported_count}"
        )

    if actual_amount != expected_amount:
        raise ValueError(
            f"Amount mismatch: actual={actual_amount}, "
            f"trailer={expected_amount}"
        )

    return {
        "details": details,
        "count": actual_count,
        "amount": actual_amount,
    }
```

### Rounding and precision

For financial amounts:

- parse to `Decimal`;
- define scale explicitly;
- avoid float equality for reconciliation;
- document rounding rules.

---

## 50. Idempotency and Replay

A legacy ingestion job should be safe to retry.

A useful identity model is:

```text
source_file_identity
        +
layout_version
        +
parser_version
        ↓
processing identity
```

The exact uniqueness key depends on the source system.

The key property is:

> Reprocessing the same source should not silently create duplicate analytical rows.

### Idempotent pattern

```text
Bronze source exists
      ↓
Check source identity
      ↓
Already successfully processed?
  ┌──────────┴──────────┐
  ↓                     ↓
 yes                    no
 skip / verify       parse + validate
                            ↓
                         publish
```

### Replay

A corrected parser should be able to read the original bronze source again.

That is why immutable source preservation and layout/version metadata matter.

---

## 51. Layout Evolution and Change Management

Source changes are normal.

Examples:

- new Excel column;
- header moves by one row;
- workbook sheet renamed;
- XML namespace changes;
- XML element moves;
- fixed-width field width changes;
- new record type added;
- decimal scale changes;
- encoding changes;
- trailer format changes.

### Production response

```text
Detect change
   ↓
Quarantine or controlled fail
   ↓
Identify new layout
   ↓
Version specification
   ↓
Test representative samples
   ↓
Controlled rollout
   ↓
Replay/backfill
```

### Backward compatibility

Never assume the newest parser should reinterpret every historical file using the newest layout.

Instead:

```text
source date / file metadata
        ↓
select effective layout version
        ↓
parse according to that version
```

Keep historical layout versions as long as replay requirements demand.

---

## 52. Production Observability

Track at least:

### Source metrics

- files discovered;
- files successfully accepted;
- files rejected;
- file bytes;
- source arrival delay.

### Parsing metrics

- records seen;
- records emitted;
- records quarantined;
- malformed records;
- type-conversion failures;
- unknown record types.

### Reconciliation metrics

- expected count;
- actual count;
- expected amount;
- actual amount;
- mismatch count.

### Output metrics

- rows written;
- Parquet file count;
- output bytes;
- partition distribution;
- parser/layout version.

### Operational metrics

- duration;
- memory pressure;
- retry count;
- replay count;
- quarantine backlog.

Example dashboard concept:

| Run | Source Files | Rows | Quarantined | Count Match | Amount Match | Output MB | Status |
|---|---:|---:|---:|---|---|---:|---|
| 2026-09-28-01 | … | … | … | YES/NO | YES/NO | … | … |

Never fabricate the values. Populate them from the actual run.

---

# Comprehensive Hands-On Lab

## 53. Comprehensive Hands-On Lab — `legacy_ingestion.py`

> **Important:** Do not physically create `legacy_ingestion.py`. The complete educational implementation belongs inside this Markdown file, matching the project file-safety rule.

The lab combines the entire topic.

---

### Part 1 — Excel

Create an educational workbook **in memory** using `openpyxl`; no `.xlsx` file needs to be added to the repository.

Required workbook characteristics:

- multiple sheets;
- two-row header;
- merged cells;
- a serial-date-like numeric value;
- totals row.

Example construction:

```python
from datetime import datetime
from io import BytesIO

from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws.title = "Sales"

ws.merge_cells("A1:D1")
ws["A1"] = "ACME RETAIL — SEPTEMBER SALES"
ws["A2"] = "Store"
ws["B2"] = "Date"
ws["C2"] = "Account"
ws["D2"] = "Amount"

ws.append(["001", datetime(2026, 9, 28), "00001234", 125.50])
ws.append(["002", datetime(2026, 9, 28), "00007890", 300.00])
ws.append(["TOTAL", None, None, 425.50])

summary = wb.create_sheet("Summary")
summary["A1"] = "Prepared by Finance"

buffer = BytesIO()
wb.save(buffer)
buffer.seek(0)

print("Workbook created in memory:", len(buffer.getvalue()), "bytes")
```

Then inspect rather than trusting the visible report:

```python
import pandas as pd

inspection = pd.read_excel(
    buffer,
    sheet_name="Sales",
    header=None,
)

print(inspection.to_string(index=False, header=False))
```

Tasks:

1. identify the true header rows;
2. normalize the headers;
3. preserve `account` as a string;
4. identify the totals row;
5. convert the amount column to numeric/decimal;
6. validate the computed detail total;
7. verify that the second worksheet is not accidentally treated as sales.

---

### Part 2 — XML

Use this small document as the shape of a much larger feed:

```python
xml_text = """
<feed xmlns="urn:example:products">
  <product id="P100">
    <name>Keyboard</name>
    <prices>
      <price currency="INR">1499.00</price>
      <price currency="USD">18.00</price>
    </prices>
  </product>
  <product id="P200">
    <name>Mouse</name>
    <prices>
      <price currency="INR">799.00</price>
    </prices>
  </product>
</feed>
"""
```

The target tables are:

```text
products
--------
product_id
name

product_prices
--------------
product_id
currency
price
```

Implement a streaming parser using `iterparse` and clear processed nodes.

Then repeat the parsing against a much larger conceptual 2 GB feed. The point is to demonstrate that the architecture remains bounded-memory; do **not** generate a 2 GB test artifact just to satisfy the exercise.

Add the defensive parser check:

```python
from defusedxml import ElementTree as DefusedET

root = DefusedET.fromstring(xml_text.encode("utf-8"))
print(root.tag)
```

Then document which inputs are trusted and which are treated as untrusted.

---

### Part 3 — Fixed-Width

Build an educational H/D/T feed as an in-memory list:

```python
lines = [
    "H00000003000020260928",
    "D000001234500012550+",
    "D000007890000030000+",
    "D000005555500007500+",
    "T0000000004255000000003",
]
```

Before parsing, define the exact contract used by the exercise. Then:

1. dispatch on `H`, `D`, `T`;
2. parse detail fields;
3. convert implied decimal values;
4. validate signs;
5. calculate detail count and amount;
6. compare with the trailer;
7. quarantine bad detail records;
8. reject an unknown record type.

Do not assume the sample positions are self-evident. The learning objective is to write down the layout before writing slices.

---

### Part 4 — Mainframe Stretch Exercise

#### EBCDIC

```python
ebcdic_bytes = bytes.fromhex("c8c5d3d3d6")
print(ebcdic_bytes.decode("cp037"))
```

#### COMP-3

```python
raw = bytes.fromhex("12345C")
print(decode_comp3(raw, scale=2))
```

Explain each step in plain language and then identify which fields in a hypothetical copybook would need this decoder.

---

### Part 5 — Lake Output

Turn accepted rows into an Arrow Table and write Parquet using deliberate physical choices:

```python
import pyarrow as pa
import pyarrow.parquet as pq

accepted = pa.table(
    {
        "account_id": ["00001234", "00007890"],
        "business_date": ["2026-09-28", "2026-09-28"],
        "amount": [125.50, 300.00],
    }
)

pq.write_table(
    accepted,
    "silver/example.parquet",
    compression="zstd",
)
```

For a partitioned dataset, use `pyarrow.dataset.write_dataset()` rather than inventing a custom file writer. Current PyArrow exposes `partitioning`, `max_rows_per_file`, row-group settings, and `existing_data_behavior`; these are important knobs for production layout.

Example:

```python
import pyarrow.dataset as ds

# Add partition columns before writing.
table = pa.table(
    {
        "business_date": ["2026-09-28", "2026-09-28"],
        "account_id": ["00001234", "00007890"],
        "amount": [125.50, 300.00],
    }
)

ds.write_dataset(
    table,
    base_dir="silver/accounts",
    format="parquet",
    partitioning=["business_date"],
    partitioning_flavor="hive",
    max_rows_per_file=100_000,
    existing_data_behavior="error",
)
```

Remember: `max_rows_per_file` controls row count, not a guaranteed byte size. File size still depends on schema, encoding, and compression.

---

### Part 6 — Quarantine

Represent rejected rows with metadata:

```python
quarantine_row = {
    "source_id": "bank_2026_09_28.dat",
    "record_number": 1842,
    "error_reason": "Invalid signed amount",
    "layout_version": "2026-07",
    "parser_version": "legacy-ingestion-3.4.1",
    "ingestion_run_id": "run-20260928-001",
    # Prefer a secure raw-record reference when raw content is sensitive.
    "raw_record_ref": "secure://quarantine/run-20260928-001/1842",
}
```

Ask:

- Does the raw content contain PII?
- Who can access quarantine?
- How long is it retained?
- Can the source record be replayed after a parser fix?

---

# Testing Strategy

## 54. Testing Strategy

Build tests around failure modes, not just happy-path parsing.

### Excel tests

- valid workbook;
- malformed report structure;
- wrong header row;
- incorrect date interpretation;
- leading-zero preservation;
- unexpected sheet structure;
- hidden-sheet policy;
- totals-row exclusion;
- totals reconciliation.

### XML tests

- valid XML;
- malformed XML;
- namespace mismatch;
- XPath returning no rows;
- large streaming input;
- memory remains bounded by design;
- defensive parser rejects unsafe behavior;
- XSD validation failure;
- business-rule failure.

### Fixed-width tests

- valid record;
- short line;
- extra-long line;
- invalid numeric field;
- invalid implied decimal;
- unknown record type;
- bad sign;
- wrong layout version;
- trailer count mismatch;
- trailer amount mismatch.

### Mainframe tests

- EBCDIC decoding;
- packed decimal positive;
- packed decimal negative;
- zero;
- scale 0;
- maximum/minimum representative values;
- binary-field parsing;
- mixed text/binary record.

### Idempotent reprocessing test

```text
Run 1
  ↓
output accepted

Run 2 with the same bronze input
  ↓
verify no duplicate analytical rows
  ↓
verify same logical result
```

Do not define “idempotent” as “the code returned exit status 0 twice”. The data state must remain correct.

---

# Debugging Guide

## 55. Debugging Guide

Use:

> **symptom → likely cause → inspect → measure → repair → lesson**

### Excel: dates shifted

**Likely causes**

- wrong 1900/1904 interpretation;
- accidental integer parsing;
- timezone conversion applied to a date-only field.

**Inspect**

- workbook metadata;
- source cell types;
- known reference dates.

**Repair**

- define the source date system explicitly;
- add regression tests.

### Excel: IDs lost zeros

**Likely cause**

A numeric dtype was inferred for an identifier.

**Repair**

Read as string or normalize to string before any numeric conversion.

### Excel: duplicate headers

**Likely cause**

Multi-row report headers were interpreted as detail records.

**Repair**

Inspect with `header=None`, then define the real header structure.

### Excel: totals included as data

**Likely cause**

The parser consumed the entire used range.

**Repair**

Detect and separate the totals/control region before typing detail rows.

### XML: no rows extracted

**Likely cause**

Namespace mismatch.

**Inspect**

```python
print(root.tag)
```

Then inspect the namespace URI rather than changing XPath randomly.

### XML: XPath returns nothing

Use:

```python
print(root.xpath("//*[local-name()='product']"))
```

as a **diagnostic probe** only. Do not blindly replace a contractually namespace-aware XPath with `local-name()` in production; it can match elements from multiple namespaces.

### XML: memory grows continuously

**Likely causes**

- retaining parsed nodes;
- accumulating all output rows in memory;
- keeping parent references unnecessarily.

**Repair**

- process completed records;
- `clear()` processed nodes;
- write bounded batches downstream.

### XML: malformed document

Determine whether the source is incomplete or structurally invalid. A malformed whole document may require file-level quarantine rather than record-level recovery.

### XML: security rejection

Treat it as a security event/data-quality event. Preserve enough metadata to identify the source without logging sensitive payloads.

### Fixed-width: columns shifted

**Likely causes**

- off-by-one slice;
- source layout version changed;
- wrong encoding altered byte positions.

**Repair**

Inspect raw bytes/characters and compare against the versioned layout.

### Fixed-width: decimal scale wrong

**Likely cause**

`12345` interpreted as 12345 instead of 123.45.

**Repair**

Read the source contract for scale and test representative values.

### Fixed-width: trailer totals do not match

Possible causes:

- skipped detail record;
- duplicate record;
- parsing failure;
- wrong numeric scale;
- negative sign mishandled;
- file truncated.

### Mainframe: unreadable text

Likely encoding mismatch. Test `cp037` or another source-declared EBCDIC codec only when the source contract indicates it.

### Mainframe: binary treated as text

The layout must identify byte ranges by representation type. A mixed record cannot be decoded with one text codec end-to-end.

---

# Performance and Memory

## 56. Performance and Memory Considerations

Different source formats fail in different ways.

| Format | Typical pressure |
|---|---|
| Excel | Workbook parsing, large object model, human-oriented structure |
| XML | Whole-document memory growth if not streamed |
| Fixed-width | Usually straightforward once layout is known |
| EBCDIC/binary mainframe | Correctness complexity more than file-size complexity |

### The key metrics

Measure:

- source bytes read;
- parse CPU time;
- peak RAM where observable;
- records processed;
- records quarantined;
- output bytes;
- output file count;
- downstream query behavior.

Do not invent benchmark numbers.

### Excel performance

Excel is usually a **source interchange format**, not the analytical storage format. Convert it to a typed columnar format as early as practical after validation.

### XML performance

For large feeds:

```text
read incrementally
   ↓
parse one logical record
   ↓
validate
   ↓
write bounded batch
   ↓
clear
```

### Fixed-width performance

Fixed-width parsing can be CPU-friendly because field boundaries are known. The challenge is usually correctness and versioning rather than discovering delimiters.

### Output considerations

A legacy parser that writes one Parquet file per tiny batch simply moves the problem downstream.

Combine this topic with Topics 07–09:

```text
Parser
  ↓
buffer / batch
  ↓
typed rows
  ↓
reasonable row groups
  ↓
sensible target file size
  ↓
partition only where useful
  ↓
Zstandard (if measured and appropriate)
```

---

# Production Design

## 57. Common Production Failure Modes

1. Trusting Excel's displayed values instead of stored values.
2. Losing leading zeros.
3. Treating totals rows as detail rows.
4. Assuming hidden rows/sheets are irrelevant.
5. Misinterpreting serial dates.
6. Loading a giant XML document fully into memory.
7. Ignoring namespaces.
8. Parsing untrusted XML with unsafe defaults.
9. Hard-coding fixed-width slices everywhere.
10. Ignoring implied decimals.
11. Misreading signs.
12. Parsing all record types with one layout.
13. Skipping control-total checks.
14. Discarding malformed data instead of quarantining it.
15. Overwriting bronze source data.
16. Failing to version the layout specification.
17. Creating duplicate output on retries.
18. Logging sensitive raw records carelessly.
19. Publishing Parquet before validation finishes.
20. Building a parser that cannot replay historical inputs.

The lesson behind nearly all of these failures is:

> **The source contract is part of the data, and the parser must make that contract explicit.**

---

## 58. Practical Design Scenarios

### Scenario 1 — 500 stores send Excel reports daily

Design questions:

1. How will source files be identified?
2. How will sheet/layout drift be detected?
3. How will totals be reconciled?
4. Where will raw files be retained?
5. How will duplicate deliveries be detected?
6. How will the output be partitioned?
7. How will small-file growth be controlled?

A strong design includes:

```text
500 files
  ↓
bronze object store
  ↓
source identity + schema inspection
  ↓
parallel parsing
  ↓
reconciliation
  ↓
bounded batches
  ↓
typed Parquet
```

### Scenario 2 — 2 GB XML product feed

Requirements:

- no full-memory tree;
- namespace awareness;
- parent + child tables;
- defensive parsing if untrusted;
- progress metrics;
- replayability.

### Scenario 3 — Untrusted supplier XML

Add:

- size limits;
- hardened XML parsing;
- controlled network behavior;
- optional XSD validation;
- quarantine;
- secure error handling.

### Scenario 4 — Fixed-width bank statement

You need:

- source layout version;
- account identifiers preserved as strings;
- decimal scale;
- signs;
- H/D/T reconciliation;
- business validation;
- exact monetary arithmetic;
- secure quarantine.

### Scenario 5 — Mainframe EBCDIC + `COMP-3`

Architecture:

```text
binary file
  ↓
layout selection
  ↓
field-by-field decoding
 ┌──────┼────────────┐
 ↓      ↓            ↓
EBCDIC COMP-3    binary integer
 ↓      ↓            ↓
Unicode Decimal     integer
 └──────┼────────────┘
        ↓
validated typed row
        ↓
Parquet
```

### Scenario 6 — Sender changes layout without notice

The safest behavior is generally:

```text
unexpected structure
       ↓
fail/quarantine
       ↓
alert owner
       ↓
identify version
       ↓
test
       ↓
controlled rollout
       ↓
replay bronze
```

Do not “make the parser flexible” by guessing. Silent guessing is often worse than a visible failure.

---

# Interview and Architecture Questions

## 59. Interview Questions

### Basic — 10+

1. Why are Excel files difficult ingestion sources?
2. What is the difference between `.xls` and `.xlsx` conceptually?
3. What does `sheet_name` do in `read_excel()`?
4. What does `header=None` mean?
5. Why would you use `skiprows`?
6. Why is an account number often a string rather than an integer?
7. What is XML?
8. What is an XML namespace?
9. What is a fixed-width file?
10. What is a trailer record?
11. Why can a totals row not simply be treated as ordinary data?

### Intermediate — 10+

1. How would you inspect a workbook before trusting its headers?
2. What is the difference between `openpyxl` and `calamine` from a reader-selection perspective?
3. Why can an Excel serial date be dangerous?
4. Why can `read_excel()` inference be wrong for identifiers?
5. When would `pandas.read_xml` be enough?
6. When would you choose `lxml` instead?
7. Why do namespaces often cause XPath bugs?
8. Why does repeated XML child data often belong in a separate table?
9. What does `iterparse()` buy you?
10. Why is `element.clear()` important?
11. Why is `colspecs` useful in fixed-width parsing?
12. What is an implied decimal?

### Hard — 10+

1. How would you distinguish a malformed XML file from a bad XML record?
2. Explain XXE at a defensive architecture level.
3. Why does XSD validation not equal business validation?
4. Why can `max_rows`-style batching still produce memory growth in a parser?
5. How would you parse a file containing H/D/T records?
6. Why should fixed-width layouts be externalized?
7. How would you handle multiple layout versions?
8. What makes `COMP-3` fundamentally different from text digits?
9. Why can a mixed EBCDIC + binary file not be decoded with one codec?
10. How would you design record-level quarantine?
11. How would you reconcile trailer counts and monetary totals?

### Advanced / Production — 10+

1. Design a replayable bronze-to-silver pipeline for legacy feeds.
2. How would you make source processing idempotent?
3. What metadata belongs on every output row or batch for lineage?
4. How would you safely migrate from layout version 1 to version 2?
5. How would you support historical replay with old layout contracts?
6. How would you protect sensitive quarantine data?
7. How would you distinguish parser failure from source-quality failure?
8. How would you prevent small Parquet files generated by per-file/per-record processing?
9. How would you benchmark pandas vs Polars for a specific Excel workload?
10. How would you design XML processing for a 2 GB document?
11. How would you handle a supplier's namespace change?
12. How would you operate a mainframe ingestion pipeline under partial failures?

### Concise answer key themes

Strong answers usually mention:

- source inspection;
- explicit grain;
- explicit schema;
- source preservation;
- defensive parsing;
- validation + reconciliation;
- quarantine;
- versioned layout specifications;
- idempotency;
- replay;
- lineage;
- typed Parquet;
- partition/compression/file-size discipline;
- observability;
- security.

---

## 60. Architecture / System-Design Questions

### 1. Design ingestion for daily Excel reports from 500 stores

Discuss:

- file identity;
- workbook inspection;
- sheet selection;
- schema normalization;
- totals reconciliation;
- parallelism;
- bronze retention;
- idempotency;
- silver Parquet;
- partitioning/file sizing;
- monitoring.

### 2. Design a 2 GB XML product feed pipeline

Discuss:

- streaming `iterparse`;
- bounded batches;
- namespaces;
- parent/child grains;
- security;
- XSD;
- quarantine;
- checkpoint/replay strategy;
- output layout.

### 3. Design secure XML ingestion for untrusted suppliers

Discuss:

- input size/type limits;
- hardened parser;
- network controls;
- XXE/entity-expansion defense;
- schema validation;
- quarantine;
- sensitive-data handling;
- auditability.

### 4. Design a fixed-width bank statement system

Discuss:

- versioned layout specification;
- account ID strings;
- signs;
- decimal scale;
- H/D/T records;
- exact monetary arithmetic;
- reconciliation;
- secure quarantine;
- replay.

### 5. Design a mainframe EBCDIC + COMP-3 pipeline

Discuss:

- copybook ingestion;
- field-level representation types;
- `cp037` or source-declared encoding;
- packed-decimal decoding;
- test vectors;
- typed target schema;
- lineage;
- source preservation.

### 6. Design a bronze-to-silver architecture

A strong answer should show:

```text
source
 ↓
bronze immutable evidence
 ↓
parse
 ↓
validate
 ↓
reconcile
 ↓
quarantine / accept
 ↓
silver typed Parquet
```

### 7. Design quarantine and replay

Discuss:

- record identity;
- source identity;
- error category;
- secure raw-reference strategy;
- replay tooling;
- corrected-parser runs;
- deduplication.

### 8. Design layout versioning

Discuss:

- effective dates;
- explicit version IDs;
- sender/source identity;
- backward compatibility;
- tests per version;
- rollout controls;
- replay.

### 9. Design control-total reconciliation

Discuss:

- expected count;
- actual count;
- expected amount;
- actual amount;
- rounding/scale;
- mismatch handling;
- alerting;
- audit trail.

### 10. Design a system resilient to sender format changes

The strongest design treats a source change as a controlled contract event rather than an invitation to silently infer a new schema.

---

# Review and Production Checklist

## 61. Review Checklist

### Source Understanding

- [ ] Format identified.
- [ ] Logical record identified.
- [ ] Target grain defined.
- [ ] Source date/encoding rules documented.
- [ ] Hidden/merged/report-control regions understood.

### Parsing

- [ ] Parser selected intentionally.
- [ ] Types explicit.
- [ ] Special encodings handled correctly.
- [ ] Multiple record types dispatched correctly.
- [ ] Layout specification versioned.

### Validation

- [ ] Structural validation performed.
- [ ] Type validation performed.
- [ ] Business validation performed.
- [ ] Control totals reconciled.
- [ ] Mismatch policy documented.

### Security

- [ ] Untrusted XML treated as a security boundary.
- [ ] Defensive XML parser used where appropriate.
- [ ] XSD is not mistaken for a security control by itself.
- [ ] Quarantine data is access-controlled.
- [ ] Logs do not leak sensitive payloads.

### Storage

- [ ] Bronze preserved.
- [ ] Silver is typed.
- [ ] Parquet chosen deliberately.
- [ ] Compression chosen deliberately.
- [ ] Partitioning matches query patterns.
- [ ] File size is controlled.

### Operations

- [ ] Idempotent.
- [ ] Replayable.
- [ ] Observable.
- [ ] Auditable.
- [ ] Layout versions supported.
- [ ] Retry behavior defined.
- [ ] Backfill strategy defined.
- [ ] Operational owner defined.

---

# Final Mental Model

## 62. Final Mental Model

> **Legacy ingestion is not “just file parsing.”**

It is:

```text
Understand the source
        +
Understand the grain
        +
Define the target schema
        +
Parse safely
        +
Validate aggressively
        +
Reconcile with the sender
        +
Quarantine failures
        +
Preserve the original
        +
Convert to typed analytical storage
        +
Use good physical layout
        +
Make the pipeline replayable and auditable
```

A Senior Data Engineer thinks about three layers at the same time:

```text
Logical correctness
       +
Physical data layout
       +
Operational safety
       =
Production-grade ingestion
```

---

# Learning Checkpoint

You have completed the chapter when you can demonstrate all of the following.

### Practical checkpoint

- [ ] Convert Excel serial dates correctly and handle the 1900/1904 distinction deliberately.
- [ ] Handle a merged header region without treating it as data.
- [ ] Preserve leading-zero identifiers.
- [ ] Separate totals rows from detail rows.
- [ ] Reconcile a computed amount/count with source controls.
- [ ] Stream-parse a large XML document with bounded-memory design.
- [ ] Explain XXE and entity-expansion attacks defensively.
- [ ] Use `defusedxml` for untrusted XML where appropriate.
- [ ] Handle XML namespaces.
- [ ] Use XPath for realistic extraction tasks.
- [ ] Map repeated XML children to a child table.
- [ ] Parse fixed-width records using explicit positions.
- [ ] Handle implied decimals and signed fields.
- [ ] Dispatch H/D/T records using different layouts.
- [ ] Represent layouts as versioned specifications.
- [ ] Decode a small EBCDIC example using a source-appropriate codec such as `cp037`.
- [ ] Explain and decode a representative `COMP-3` value conceptually.
- [ ] Design a bronze → parse → validate → quarantine → silver pipeline.
- [ ] Make the ingestion replayable and idempotent.
- [ ] Publish typed Parquet with sensible compression, partitioning, and file sizing.
- [ ] Explain why source representation and target analytical representation are different concerns.

### Explain aloud

Without looking at the chapter, explain:

1. Why an Excel sheet is not automatically a table.
2. Why XML requires a grain decision before flattening.
3. Why `iterparse()` helps with large XML.
4. Why `defusedxml` belongs at the security boundary.
5. Why fixed-width parsers need explicit layout contracts.
6. Why `COMP-3` cannot be treated as ordinary text.
7. Why trailer controls are data-quality gates.
8. Why bronze preservation enables replay.
9. Why typed Parquet is the destination rather than Excel/XML/fixed-width.
10. Why physical layout still matters after parsing is correct.

---

# File-Layout Learning Loop for This Topic

Use the module's measure-first loop:

```text
Read
→ Predict
→ Inspect Source
→ Define Schema + Grain
→ Parse
→ Validate
→ Reconcile
→ Write Output
→ Inspect Output
→ Measure
→ Change One Thing
→ Measure Again
→ Write Down the Rule
→ Explain It Aloud
```

Before implementation, predict:

- record count;
- logical grain;
- data types;
- number of output rows;
- likely output partitions/files;
- likely memory pressure;
- likely failure points;
- reconciliation behavior.

Then measure the real result.

---

# Final Review: What a Production-Ready Engineer Should Remember

1. **Excel's visual appearance is not its data model.**
2. **A serial date is meaningful only in the context of its workbook date system.**
3. **Identifiers that look numeric often need string semantics.**
4. **Formulas and displayed/cached values are different concepts.**
5. **Merged cells, hidden regions, totals, titles, and notes must be treated as source-structure problems.**
6. **XML is hierarchical; choose table grain before flattening it.**
7. **Namespaces qualify element names through namespace URIs, not merely prefixes.**
8. **Large XML feeds should be designed for bounded-memory processing.**
9. **Untrusted XML must be parsed defensively.**
10. **XSD validation, business validation, and security are separate concerns.**
11. **Fixed-width data is simple only after the layout contract is understood.**
12. **Implied decimals and sign conventions belong in the layout specification.**
13. **H/D/T control records are often reconciliation assets, not analytical rows.**
14. **COBOL copybooks can be treated as source-layout contracts.**
15. **EBCDIC decoding must use the correct source codec; `cp037` is one documented example, not a universal mainframe encoding.**
16. **`COMP-3` is a packed representation and requires field-level decoding.**
17. **Preserve the raw source so parser improvements can be replayed.**
18. **Quarantine bad records without silently discarding evidence.**
19. **Make layout versions, parser versions, and source identity observable.**
20. **The target is typed analytical storage with deliberate physical layout.**
21. **A successful parser process is not enough; correctness must be reconciled and tested.**
22. **Legacy ingestion is a contract-management, data-quality, security, and storage-design problem.**

---

## Source/Version Notes for the Code in This Chapter

The examples in this chapter target modern Python and current library APIs. Version-sensitive behavior should be rechecked against the installed versions in the project before standardization.

Relevant current documentation used to verify examples includes:

- pandas `read_excel()` and `ExcelFile()` for sheet selection, headers, `skiprows`, `usecols`, and Excel engines;
- Polars `read_excel()` for sheet selection, schema overrides, and Excel engines;
- PyArrow Parquet and Dataset APIs for typed Parquet writes, compression, partitioning, and `max_rows_per_file`;
- Python `xml.etree.ElementTree.iterparse()`;
- lxml XPath, `iterparse()`, and `XMLSchema`;
- Python codec support for `cp037`;
- `defusedxml` defensive XML parsing.

These references verify API shape and security/encoding concepts. They do not replace testing against the exact versions and source files used by your production environment.

---

## File-Safety Boundary

All educational examples, implementations, tests, and exercises in this chapter are intentionally contained inside this Markdown document.

No separate `legacy_ingestion.py`, parser file, dataset, workbook, XML file, fixed-width file, test file, benchmark file, configuration file, or ADR is required to understand or complete the chapter.
