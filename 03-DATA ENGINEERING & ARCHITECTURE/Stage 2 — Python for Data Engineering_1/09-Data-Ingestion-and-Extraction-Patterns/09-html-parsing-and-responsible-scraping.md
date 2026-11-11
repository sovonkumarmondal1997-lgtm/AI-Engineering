# HTML Parsing and Responsible Scraping

> **Core principle:** Scraping is not “download HTML and use CSS selectors.” It is an ingestion problem with source-policy, correctness, reliability, change-management, and operational constraints.

This chapter teaches how to extract structured data from HTML when an appropriate authorized API, feed, export, or other structured interface is unavailable or unsuitable.

The objective is not to teach techniques for bypassing access controls. The objective is to build extraction systems that are **responsible, correct, reproducible, observable, maintainable, resumable, and polite to the source**.

---

# 1. Learning Objectives

By the end of this module, you should be able to:

- Explain what HTML is and how it is represented as a document tree.
- Distinguish downloading HTML from parsing HTML.
- Distinguish parsing from data extraction and data validation.
- Inspect a page before writing an extractor.
- Use BeautifulSoup for practical HTML parsing.
- Use `lxml` and XPath when appropriate.
- Write maintainable CSS selectors.
- Extract text, attributes, links, tables, and repeated records.
- Normalize text and URLs.
- Handle missing fields safely.
- Recognize malformed HTML and unexpected page structures.
- Detect JavaScript-generated content.
- Extract and validate JSON-LD and other embedded metadata.
- Decide when an API or feed should be preferred over HTML.
- Understand robots.txt and source policies.
- Identify an automated client appropriately.
- Use bounded request rates, timeouts, retries, caching, and conditional requests.
- Define explicit crawl boundaries.
- Deduplicate URLs and extracted records.
- Make an extractor safe to rerun.
- Decide when raw HTML should be retained.
- Define a source/extraction contract.
- Detect schema drift and selector drift.
- Validate extraction quality instead of trusting HTTP 200.
- Instrument extraction with logs and metrics.
- Classify failures and respond appropriately.
- Build a local/mock responsible HTML extractor.
- Design tests for parser correctness and source changes.
- Reason about performance and bounded concurrency.
- Compare API extraction with HTML extraction without assuming a universal winner.
- Defend an extraction design in an architecture review.
- Know when to stop using HTML extraction and seek a different source.

---

# 2. Prerequisites

This topic assumes familiarity with earlier Module 2.9 topics:

- HTTP fundamentals.
- `httpx` / `requests`.
- Sessions and connections.
- Explicit timeouts.
- Authentication concepts.
- Pagination.
- Rate limits and HTTP 429.
- Retries and backoff.
- JSON / JSONL.
- Logging.
- Idempotency.
- Safe file writes.
- Data-pipeline fundamentals.

These topics are **not re-taught in full**. Instead, they are connected to HTML extraction.

The mental model is:

```text
HTTP knowledge
    +
HTML parsing
    +
validation
    +
rate limiting
    +
observability
    +
responsible source access
    =
production HTML extraction
```

---

# 3. Why HTML Extraction Is a Data Engineering Problem

A short scraping script can look like:

```text
download page
    ↓
find elements
    ↓
print values
```

A production ingestion system must answer much harder questions:

```text
Is this source legitimate for automated access?
Is there an official API?
What exactly does one page represent?
How do we know extraction is complete?
What happens when the page changes?
What happens when the source returns a login page?
How do we avoid unnecessary source load?
How do we retry safely?
How do we prevent duplicate records?
How do we reproduce yesterday's result?
How do we detect silent corruption?
How do we recover from partial progress?
```

Compare two mindsets:

```text
Web-development mindset:
"How do I display this page?"

Data-engineering mindset:
"How do I reliably extract the correct records from this
source over time, under source and operational constraints?"
```

HTML extraction therefore has the same production concerns as other ingestion systems:

- completeness,
- correctness,
- freshness,
- idempotency,
- resumability,
- observability,
- reproducibility,
- failure handling,
- source protection.

---

# 4. The Source-Selection Hierarchy

Before scraping HTML, investigate whether a structured interface already exists.

Use this decision hierarchy:

```text
Official API
    ↓
Official feed / export / download
    ↓
Partner or authorized interface
    ↓
HTML extraction when permitted and appropriate
```

Why is HTML often a weaker data interface?

- HTML is presentation-oriented.
- Page structure can change.
- Selectors can break.
- Content may be incomplete.
- JavaScript may generate data after the initial response.
- Pagination can change.
- Semantic meaning may be ambiguous.
- Source policies may restrict automated access.
- A browser page may contain data that is not intended as a stable machine interface.

If an appropriate authorized API exists, it is often preferable because it exposes structured data directly.

That is a **decision based on requirements**, not a universal rule.

---

# 5. HTML Fundamentals

## 5.1 What is HTML?

HTML stands for **HyperText Markup Language**.

It describes the structure of a document using elements.

Example:

```html
<!doctype html>
<html>
  <head>
    <title>Example Catalog</title>
  </head>

  <body>
    <main>
      <h1>Products</h1>

      <article class="product" data-product-id="101">
        <h2>Mechanical Keyboard</h2>
        <span class="price">$79.99</span>
      </article>
    </main>
  </body>
</html>
```

An element generally has:

```text
opening tag
    +
attributes
    +
content
    +
closing tag
```

For example:

```html
<article class="product">
    ...
</article>
```

The tag is:

```text
article
```

The attribute is:

```text
class="product"
```

---

## 5.2 Common HTML elements

| Element | Typical meaning |
|---|---|
| `<html>` | Document root |
| `<head>` | Metadata |
| `<body>` | Visible document content |
| `<div>` | Generic container |
| `<span>` | Generic inline container |
| `<p>` | Paragraph |
| `<a>` | Link |
| `<table>` | Table |
| `<tr>` | Table row |
| `<th>` | Table header cell |
| `<td>` | Table data cell |
| `<ul>` | Unordered list |
| `<li>` | List item |
| `<article>` | Self-contained content |
| `<section>` | Logical section |
| `<h1>`–`<h6>` | Headings |

Do not assume that a tag's name alone defines the business meaning of the data. Extraction logic should use the actual source structure.

---

# 6. The DOM Mental Model

When an HTML document is parsed, it can be represented as a tree.

For:

```html
<main>
  <article class="product">
    <h2>Keyboard</h2>
    <span class="price">$79.99</span>
  </article>
</main>
```

Think:

```text
main
└── article.product
    ├── h2
    │   └── "Keyboard"
    └── span.price
        └── "$79.99"
```

This tree is commonly called the **DOM**, or Document Object Model.

Relationships include:

```text
parent
child
sibling
ancestor
descendant
```

These relationships are important because selectors and XPath navigate this structure.

---

# 7. HTML Source vs DOM vs Rendered Page

These are not the same thing.

```text
HTTP response
      ↓
HTML source
      ↓
HTML parser
      ↓
DOM representation
```

A browser may then execute JavaScript:

```text
Initial HTML
      ↓
JavaScript execution
      ↓
additional API calls
      ↓
DOM changes
      ↓
rendered page
```

An HTTP client such as `httpx` or `requests` normally receives the HTTP response. It does **not** automatically execute arbitrary browser JavaScript.

Therefore:

```text
What you see in a browser
        ≠
necessarily what an HTTP client downloads
```

This distinction is one of the most common sources of beginner confusion.

---

# 8. HTML Parsing vs Web Scraping

These concepts must remain separate.

## HTML parsing

Turning HTML text into a structured tree that can be queried.

## Data extraction

Selecting elements and converting their contents into structured records.

## Scraping

Automated retrieval and extraction of information from web pages.

## Responsible ingestion

Operating that extraction with:

- appropriate authorization,
- source-policy awareness,
- conservative traffic,
- validation,
- reproducibility,
- observability,
- safe failure behavior.

Therefore:

```text
Downloading HTML
        ≠
Parsing HTML
        ≠
Extracting fields
        ≠
Validating records
        ≠
Operating a production ingestion pipeline
```

---

# 9. Inspect the Page Before Writing Code

A production engineer should inspect the source before choosing selectors.

Useful inspection methods include:

- browser developer tools,
- page source,
- element inspection,
- HTML hierarchy inspection,
- network inspection for understanding page behavior,
- canonical URL inspection,
- embedded metadata inspection.

Look for:

- stable semantic elements,
- IDs,
- classes,
- `data-*` attributes,
- repeated records,
- tables,
- links,
- pagination,
- embedded structured metadata.

## 9.1 Avoid blindly copying browser-generated selectors

A browser may generate:

```css
div:nth-child(4) > div:nth-child(2) > span:nth-child(1)
```

This may work today but depend on accidental layout.

Prefer meaningful selectors such as:

```css
article.product
article[data-product-id]
article.product h2
article.product .price
```

Selectors are effectively part of your extractor's implicit schema.

---

# 10. CSS Selectors

A CSS selector is a pattern used to identify elements in an HTML document.

## 10.1 Tag selector

```css
article
```

Matches:

```html
<article>...</article>
```

## 10.2 Class selector

```css
.product
```

Matches:

```html
<article class="product">
```

## 10.3 ID selector

```css
#main
```

Matches:

```html
<div id="main">
```

IDs should be used when they are stable and semantically meaningful.

## 10.4 Attribute selector

```css
article[data-product-id]
```

Matches articles that have the attribute.

A specific value can be selected:

```css
article[data-product-id="101"]
```

## 10.5 Descendant selector

```css
article.product h2
```

Finds an `h2` somewhere inside a product article.

## 10.6 Child selector

```css
main > article
```

Requires the article to be a direct child.

## 10.7 Combined selector

```css
article.product[data-product-id] h2
```

The best selector is not necessarily the shortest one. It should balance:

```text
precision
+
stability
+
readability
+
maintainability
```

---

# 11. BeautifulSoup

BeautifulSoup is a Python library for parsing and navigating HTML.

Install it with:

```bash
python -m pip install beautifulsoup4
```

Basic usage:

```python
from bs4 import BeautifulSoup

html = """
<article class="product">
    <h2>Keyboard</h2>
    <span class="price">$49.99</span>
</article>
"""

soup = BeautifulSoup(html, "html.parser")

title_element = soup.select_one("article.product h2")
price_element = soup.select_one("article.product .price")

print(title_element.get_text(strip=True))
print(price_element.get_text(strip=True))
```

---

# 12. BeautifulSoup Core Operations

## `find()`

Find one matching element:

```python
element = soup.find("article")
```

## `find_all()`

Find multiple elements:

```python
articles = soup.find_all("article")
```

## `select()`

Use CSS selectors:

```python
articles = soup.select("article.product")
```

## `select_one()`

Return the first match:

```python
article = soup.select_one("article.product")
```

## `get_text()`

Extract descendant text:

```python
text = article.get_text(" ", strip=True)
```

## `get()`

Read an attribute safely:

```python
href = article.get("href")
```

## `.attrs`

Inspect all attributes:

```python
attributes = article.attrs
```

---

# 13. Safe BeautifulSoup Extraction

This is an anti-pattern:

```python
# Anti-pattern
price = soup.select_one(".price").get_text(strip=True)
```

If `.price` is missing:

```text
AttributeError
```

A safer version:

```python
price_element = soup.select_one(".price")

price = (
    price_element.get_text(" ", strip=True)
    if price_element is not None
    else None
)
```

For required fields, do not silently accept `None`.

Instead:

```python
if price_element is None:
    raise ValueError("required field 'price' was not found")
```

The correct behavior depends on whether the field is:

```text
required
or
optional
```

---

# 14. lxml

`lxml` is a mature Python library for processing XML and HTML.

Install:

```bash
python -m pip install lxml
```

Basic HTML parsing:

```python
from lxml import html

document = html.fromstring(
    """
    <article class="product">
        <h2>Keyboard</h2>
        <span class="price">$49.99</span>
    </article>
    """
)

title = document.xpath(
    "string(//article[@class='product']/h2)"
).strip()

price = document.xpath(
    "string(//article[@class='product']/span[@class='price'])"
).strip()

print(title)
print(price)
```

`lxml` is particularly useful when XPath expressions are a natural fit.

---

# 15. CSS Selectors vs XPath

| Concern | CSS Selectors | XPath |
|---|---|---|
| Readability | Often concise | Can become verbose |
| Browser familiarity | High | Moderate |
| Attribute matching | Strong | Strong |
| Descendant traversal | Strong | Strong |
| Complex relationships | More limited | Very expressive |
| Text-oriented queries | Possible but limited | Strong |
| Parent/ancestor navigation | Limited | Strong |
| Maintainability | Often good for simple structure | Depends on expression |
| Best use | Semantic element selection | Complex tree relationships |

There is no universal winner.

Choose based on:

- source structure,
- complexity,
- team familiarity,
- readability,
- maintainability,
- testability.

---

# 16. Extracting Text Correctly

This:

```python
element.text
```

does not always capture all meaningful descendant text.

Consider:

```html
<p>
    Price:
    <strong>$79.99</strong>
    today
</p>
```

A more useful approach is:

```python
text = element.get_text(" ", strip=True)
```

which produces a normalized representation such as:

```text
Price: $79.99 today
```

A reusable normalization function:

```python
def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = " ".join(value.split())

    return normalized or None
```

Why normalize explicitly?

Because HTML text may contain:

- newlines,
- indentation,
- repeated whitespace,
- non-obvious formatting,
- nested elements,
- empty text nodes.

Normalization should be deterministic and testable.

---

# 17. Extracting Attributes and URLs

Common attributes include:

```python
href = element.get("href")
src = element.get("src")
product_id = element.get("data-product-id")
```

Relative URLs are common:

```text
/products/123
```

while your output may require:

```text
https://example.com/products/123
```

Use `urljoin`:

```python
from urllib.parse import urljoin

base_url = "https://example.com/catalog/"
relative_url = "/products/123"

absolute_url = urljoin(base_url, relative_url)

print(absolute_url)
```

Result:

```text
https://example.com/products/123
```

Do not manually concatenate URLs:

```python
# Anti-pattern
absolute_url = base_url + relative_url
```

That approach fails for many valid URL forms.

---

# 18. URL Normalization

A crawler can encounter multiple representations of a logically equivalent resource:

```text
https://example.com/products/123
https://example.com/products/123?utm_source=email
https://example.com/products/123/
```

Whether these are equivalent depends on the source.

Potential normalization operations include:

- resolving relative URLs,
- lowercasing the host,
- removing known tracking parameters,
- normalizing trailing slashes when source semantics permit,
- sorting query parameters only when safe.

Do **not** aggressively normalize URLs without understanding source semantics.

A query parameter may change the resource:

```text
?page=2
?language=fr
?currency=USD
```

Therefore:

> URL normalization is a source-specific correctness decision, not a string-cleaning exercise.

---

# 19. Extracting Tables

HTML tables use elements such as:

```html
<table>
  <tr>
    <th>Product</th>
    <th>Price</th>
  </tr>
  <tr>
    <td>Keyboard</td>
    <td>$79.99</td>
  </tr>
</table>
```

A simple parser:

```python
from bs4 import BeautifulSoup

html = """
<table>
  <tr>
    <th>Product</th>
    <th>Price</th>
  </tr>
  <tr>
    <td>Keyboard</td>
    <td>$79.99</td>
  </tr>
  <tr>
    <td>Mouse</td>
    <td>$39.99</td>
  </tr>
</table>
"""

soup = BeautifulSoup(html, "html.parser")

rows = soup.select("table tr")

records = []

for row in rows[1:]:
    cells = row.select("td")

    if len(cells) != 2:
        continue

    records.append(
        {
            "product": cells[0].get_text(" ", strip=True),
            "price": cells[1].get_text(" ", strip=True),
        }
    )

print(records)
```

Production table extraction must consider:

- missing cells,
- inconsistent columns,
- nested elements,
- empty rows,
- malformed tables,
- multiple tables,
- repeated headers.

Do not assume every table is rectangular and clean.

---

# 20. Repeated Records

A very common extraction structure is:

```html
<article class="product">
    ...
</article>

<article class="product">
    ...
</article>
```

Extract each record:

```python
records = []

for article in soup.select("article.product"):
    record = {
        "product_id": article.get("data-product-id"),
        "name": (
            article.select_one("h2").get_text(" ", strip=True)
            if article.select_one("h2")
            else None
        ),
        "price": (
            article.select_one(".price").get_text(" ", strip=True)
            if article.select_one(".price")
            else None
        ),
    }

    records.append(record)
```

A production record might look like:

```python
{
    "product_id": "101",
    "name": "Mechanical Keyboard",
    "price": "$79.99",
    "url": "https://example.com/products/101",
}
```

Prefer a stable identifier when the source provides one.

---

# 21. Missing and Optional Fields

Not every field has the same semantic importance.

Example:

```text
product_id → required
name       → required
price      → optional
image_url  → optional
description → optional
```

Treating every missing field as a fatal error is often too strict.

Treating every missing field as acceptable is dangerous.

Use explicit classification.

```python
product_id_element = article.select_one("[data-product-id]")
name_element = article.select_one("h2")
price_element = article.select_one(".price")

if product_id_element is None:
    raise ValueError("missing required product identifier")

if name_element is None:
    raise ValueError("missing required product name")

record = {
    "product_id": product_id_element.get("data-product-id"),
    "name": name_element.get_text(" ", strip=True),
    "price": (
        price_element.get_text(" ", strip=True)
        if price_element is not None
        else None
    ),
}
```

Distinguish:

```text
missing
empty
invalid
not applicable
unknown
```

These states can have different downstream meanings.

---

# 22. HTML Parsing Failure Modes

Common failures include:

- malformed HTML,
- changed CSS classes,
- missing elements,
- duplicate elements,
- unexpected nesting,
- page redesign,
- localization differences,
- pagination changes,
- content embedded somewhere unexpected,
- JavaScript-generated content,
- bot/challenge pages,
- login pages,
- HTTP 200 responses containing unexpected content.

The most important lesson:

```text
HTTP 200
    ≠
correct extraction
```

A server can return:

```http
HTTP/1.1 200 OK
Content-Type: text/html
```

while the body contains:

```text
Login required
```

or:

```text
Access verification
```

or:

```text
An error occurred
```

Therefore validate the content itself.

---

# 23. JavaScript-Generated Content

There are two broad patterns.

## Server-rendered

```text
Browser
   |
   | GET
   v
Server
   |
   | HTML containing data
   v
Browser
```

## Client-rendered

```text
Browser
   |
   | GET
   v
Server
   |
   | HTML application shell
   v
Browser
   |
   | JavaScript executes
   |
   +---- API request
   |
   +---- DOM update
```

An HTTP client may receive only:

```html
<div id="app"></div>
<script src="/app.js"></script>
```

while the browser eventually displays thousands of records.

## Diagnose this situation

Look for:

- expected content missing from the downloaded HTML,
- application-shell markup,
- script tags,
- embedded JSON,
- network requests made by the page.

If the page uses an underlying official or authorized API, prefer that structured interface when permitted.

Browser automation is a conceptual alternative for some legitimate workflows, but it has substantially higher operational cost and should not be used to bypass access controls.

---

# 24. Structured Metadata and Embedded Data

Pages may contain structured information in:

- JSON-LD,
- metadata tags,
- canonical links,
- Open Graph tags,
- embedded script data.

Example:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Example Product",
  "sku": "ABC-123"
}
</script>
```

Parse it carefully:

```python
import json

from bs4 import BeautifulSoup

html = """
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Example Product",
  "sku": "ABC-123"
}
</script>
"""

soup = BeautifulSoup(html, "html.parser")

script = soup.select_one(
    'script[type="application/ld+json"]'
)

if script is not None:
    metadata = json.loads(script.string or "{}")
    print(metadata["name"])
```

Embedded metadata can sometimes be more stable than presentation markup.

But:

> Embedded metadata still requires validation and should not automatically be treated as authoritative.

A page can contain stale, incomplete, duplicated, or inconsistent metadata.

---

# 25. Responsible Scraping

## 25.1 Technical capability does not imply permission

Before automating access, ask:

```text
Is there an official API?
Is there an official export?
Is there an official feed?
Is automated access permitted?
What does robots.txt indicate?
What do the site's terms/policies say?
Is authentication required?
Is the data public?
Is there a contractual restriction?
Is personal/sensitive information involved?
Is the request volume reasonable?
```

Laws, terms, policies, and permissions vary by website and jurisdiction.

This chapter does not provide legal advice.

When uncertain, consult the source documentation, applicable terms, and appropriate legal/compliance guidance.

---

# 26. robots.txt

A site may publish crawler guidance at:

```text
/robots.txt
```

A conceptual example:

```text
User-agent: ExampleDataExtractor
Disallow: /private/
Disallow: /account/
Allow: /public/

Sitemap: https://example.com/sitemap.xml
```

Relevant concepts include:

- `User-agent`
- `Allow`
- `Disallow`
- `Sitemap`
- `Crawl-delay` when encountered.

robots.txt is primarily a crawler-access signaling mechanism. It is **not itself a complete statement of legal permission**.

A responsible crawler should inspect it before automated collection and follow applicable source policies.

Do not treat a disallowed path as a puzzle to solve.

---

# 27. User-Agent and Client Identification

An automated client should identify itself appropriately.

Example:

```python
headers = {
    "User-Agent": (
        "ExampleDataExtractor/1.0 "
        "(+https://example.com/contact)"
    )
}
```

Good client identification supports:

- transparency,
- operational contact,
- source-owner troubleshooting,
- distinguishing legitimate automation.

Do not pretend to be a different browser for the purpose of bypassing restrictions.

---

# 28. Polite Request Behavior

Responsible crawling combines:

```text
explicit timeout
+
bounded concurrency
+
rate limiting
+
backoff
+
jitter
+
caching
+
conditional requests
+
limited crawl scope
+
unnecessary-request avoidance
```

A useful mental model is:

```text
Responsible scraping
=
low unnecessary load
+
respect for source policies
+
safe retry behavior
+
controlled request rate
+
observability
```

A crawler should stop or escalate when access is denied rather than trying to defeat the denial.

---

# 29. Caching

Caching is particularly valuable for HTML extraction because the same page can otherwise be downloaded repeatedly during:

- development,
- debugging,
- parser changes,
- retries,
- reruns,
- tests.

Caching can reduce:

```text
network traffic
source load
latency
quota consumption
```

A simple conceptual cache:

```python
cache: dict[str, bytes] = {}

def get_cached(url: str) -> bytes | None:
    return cache.get(url)

def put_cached(url: str, content: bytes) -> None:
    cache[url] = content
```

This is intentionally simplistic.

A real cache needs to consider:

- expiration,
- storage limits,
- cache keys,
- content validation,
- invalidation,
- concurrency,
- persistence,
- privacy,
- retention.

## HTTP cache validation

HTTP mechanisms such as:

```text
ETag
If-None-Match
Last-Modified
If-Modified-Since
```

can allow a client to determine whether a resource changed without repeatedly downloading the full body.

Use them when supported and appropriate.

---

# 30. Crawl Boundaries

A crawler must have explicit boundaries.

Useful controls include:

```text
allowed domains
allowed paths
maximum pages
maximum depth
pagination limits
URL normalization
visited URL set
query-parameter policy
crawl state
```

Without boundaries, a crawler can accidentally:

- follow enormous numbers of pages,
- revisit the same URLs,
- follow tracking links,
- enter loops,
- traverse unrelated parts of a site,
- overload the source.

Example configuration concept:

```text
allowed_domain = example.com
allowed_prefix = /catalog/
max_pages = 100
max_depth = 3
```

The boundary is a safety mechanism, not merely an optimization.

---

# 31. URL Deduplication

A visited set is a simple first control:

```python
visited_urls: set[str] = set()

if url in visited_urls:
    return

visited_urls.add(url)
```

In a real crawler, the normalized URL should generally be the key:

```text
raw URL
   ↓
normalize
   ↓
canonical crawl key
   ↓
visited set
```

Be careful with canonicalization because two URLs that look similar can represent different resources.

---

# 32. Deduplication and Idempotency

Suppose a pipeline is rerun.

You do not want:

```text
same URL
+
same extraction run
+
same record
=
duplicate business record
```

Useful mechanisms include:

- URL deduplication,
- content hashes,
- stable source identifiers,
- extraction run IDs,
- deterministic transformations.

Example content hash:

```python
import hashlib


def content_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
```

A content hash can help identify identical source bodies.

It should **not automatically be treated as a business key**.

For example, a product may legitimately change price while keeping the same business identity.

---

# 33. Raw HTML vs Parsed Data

A production pipeline can look like:

```text
Source HTML
    ↓
Raw landing
    ↓
Parsed records
    ↓
Validated records
```

Raw HTML can be valuable for:

- debugging,
- reproducibility,
- parser upgrades,
- auditability,
- reprocessing historical data.

But raw retention has costs:

- storage,
- privacy,
- retention requirements,
- licensing/copyright considerations,
- potentially sensitive information.

A useful rule is:

> Retain enough source evidence to support correctness and recovery, but define retention deliberately.

Raw source storage itself must comply with applicable policies and requirements.

---

# 34. Extraction Contracts

An HTML source should have a documented extraction contract.

Illustrative example:

```yaml
source:
  name: example_catalog
  base_url: https://example.com

access:
  method: html
  policy_checked: true

extraction:
  item_selector: "article.product"
  fields:
    id: "[data-product-id]"
    name: "h2"
    price: ".price"

pagination:
  strategy: next-link

limits:
  max_pages: 100
```

The exact YAML structure is not important.

The important idea is that the extractor has explicit assumptions:

```text
source
access policy
selectors
required fields
pagination
limits
```

Those assumptions can then be reviewed, tested, and monitored.

---

# 35. Schema Drift and Page Changes

HTML sources change.

For example:

```html
<span class="price">
```

might become:

```html
<span class="current-price">
```

Or:

```html
<article class="product">
```

might become:

```html
<div class="product-card">
```

A weak extractor may simply produce:

```text
0 records
```

and report success.

That is dangerous.

A robust extractor detects anomalies through:

- selector hit counts,
- expected record-count ranges,
- required-field presence,
- null-rate changes,
- completeness checks,
- page fingerprints,
- content-type checks,
- known page markers.

---

# 36. Data Validation After Extraction

Validation should happen at multiple layers.

## HTTP validation

Check:

- status code,
- content type,
- response size,
- expected redirects where relevant.

## HTML validation

Check:

- expected page title,
- expected root element,
- expected selector count,
- known page markers.

## Record validation

Check:

- required ID,
- required name,
- valid URL,
- numeric values,
- allowed value ranges.

## Pipeline validation

Check:

- record count,
- duplicate rate,
- null rate,
- freshness,
- source coverage.

Example:

```python
def validate_record(record: dict[str, object]) -> None:
    product_id = record.get("product_id")
    name = record.get("name")

    if not product_id:
        raise ValueError("missing product_id")

    if not name:
        raise ValueError("missing product name")
```

The key principle:

> Extraction should fail loudly when the data violates known correctness assumptions.

---

# 37. Observability

Measure both the HTTP layer and the extraction layer.

Useful metrics:

```text
pages_requested
pages_successful
pages_failed
http_errors
parse_errors
records_extracted
records_rejected
duplicate_records
retry_count
request_latency
bytes_downloaded
cache_hits
selector_miss_count
```

Useful structured log fields:

```text
run_id
source
url
status_code
duration_ms
records_extracted
error_type
```

A job that says:

```text
SUCCESS
```

does not prove that extraction was correct.

A better success definition includes evidence such as:

```text
expected page range
expected record range
required selectors present
acceptable null rates
no unexpected schema drift
```

---

# 38. Error Classification

| Failure | Example | Typical action |
|---|---|---|
| DNS/network | Connection failure | Bounded retry |
| Timeout | Request timeout | Bounded retry |
| 429 | Rate limited | Respect `Retry-After` |
| 403 | Access denied | Stop/escalate; do not bypass |
| 404 | Missing page | Record/skip according to contract |
| 5xx | Server error | Bounded retry |
| Parse failure | Unexpected HTML | Alert/investigate |
| Selector miss | Page changed | Alert/investigate |
| Empty result | Unexpected content | Validate/escalate |
| Login page | Authentication/session issue | Stop and investigate |
| Challenge page | Access control | Stop; do not bypass |

The exact action depends on the source contract.

---

# 39. What Not to Do

Do not:

- bypass robots.txt,
- evade CAPTCHAs,
- rotate IPs to circumvent restrictions,
- spoof identities to defeat controls,
- bypass authentication,
- defeat technical access controls,
- use aggressive concurrency,
- use unlimited retries,
- crawl without boundaries,
- ignore terms or source policies,
- download huge amounts of unnecessary data,
- repeatedly request unchanged pages,
- silently accept zero records,
- rely on brittle generated selectors,
- treat HTTP 200 as proof of extraction success,
- store sensitive data without justification,
- use scraping to circumvent access restrictions.

The correct response to access denial is:

```text
stop
+
investigate
+
use an authorized alternative
+
contact the source owner when appropriate
```

---

# 40. Hands-On Project — Responsible HTML Extractor

This project uses a local HTML document rather than a live external site.

## 40.1 Source HTML

```html
<html>
  <body>
    <main>
      <article class="product" data-product-id="101">
        <h2>Mechanical Keyboard</h2>
        <span class="price">$79.99</span>
        <a href="/products/101">View</a>
      </article>

      <article class="product" data-product-id="102">
        <h2>Wireless Mouse</h2>
        <span class="price">$39.99</span>
        <a href="/products/102">View</a>
      </article>
    </main>
  </body>
</html>
```

The project should produce:

```python
[
    {
        "product_id": "101",
        "name": "Mechanical Keyboard",
        "price": "$79.99",
        "url": "https://example.com/products/101",
    },
    {
        "product_id": "102",
        "name": "Wireless Mouse",
        "price": "$39.99",
        "url": "https://example.com/products/102",
    },
]
```

---

## 40.2 Step 1 — Parse

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "html.parser")
```

---

## 40.3 Step 2 — Select records

```python
articles = soup.select("article.product")

if not articles:
    raise ValueError("no product records found")
```

This check is important.

A selector that returns zero records may mean:

- legitimate empty source,
- page changed,
- wrong URL,
- login page,
- challenge page,
- selector drift.

Do not automatically treat zero as success.

---

## 40.4 Step 3 — Extract fields

```python
from urllib.parse import urljoin


base_url = "https://example.com"

records = []

for article in articles:
    product_id = article.get("data-product-id")

    name_element = article.select_one("h2")
    price_element = article.select_one(".price")
    link_element = article.select_one("a[href]")

    if not product_id:
        raise ValueError("missing product identifier")

    if name_element is None:
        raise ValueError(
            f"missing product name for {product_id}"
        )

    if link_element is None:
        raise ValueError(
            f"missing product link for {product_id}"
        )

    record = {
        "product_id": product_id,
        "name": name_element.get_text(" ", strip=True),
        "price": (
            price_element.get_text(" ", strip=True)
            if price_element is not None
            else None
        ),
        "url": urljoin(
            base_url,
            link_element.get("href", ""),
        ),
    }

    records.append(record)
```

---

# 41. Add Normalization

A stronger implementation makes normalization explicit.

```python
def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = " ".join(value.split())

    return normalized or None
```

Then:

```python
name = normalize_text(
    name_element.get_text(" ", strip=True)
)
```

The same normalization function can be unit-tested independently.

---

# 42. Add Deduplication

Suppose the same product appears twice.

```python
seen_ids: set[str] = set()
deduplicated_records = []

for record in records:
    product_id = record["product_id"]

    if product_id in seen_ids:
        continue

    seen_ids.add(product_id)
    deduplicated_records.append(record)
```

This assumes `product_id` is a stable source identifier.

Do not deduplicate solely on product name if names are not guaranteed to be unique.

---

# 43. Add Content Hashing

For raw HTML:

```python
import hashlib


def content_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
```

You might record:

```text
source_url
retrieved_at
content_hash
parser_version
extraction_run_id
```

This can help with:

- duplicate source bodies,
- reproducibility,
- audit trails,
- reprocessing.

---

# 44. Add Extraction Metrics

For a small local project:

```python
metrics = {
    "pages_requested": 1,
    "pages_successful": 1,
    "records_extracted": len(records),
    "records_rejected": 0,
    "selector_miss_count": 0,
}
```

Production systems would emit these through their observability infrastructure.

---

# 45. Add a Source Contract

Document:

```text
Source:
    example_catalog

Allowed domain:
    example.com

Allowed path:
    /products/

Record selector:
    article.product

Required fields:
    data-product-id
    h2
    a[href]

Optional fields:
    .price

Maximum pages:
    100

Expected record range:
    1–1000
```

This turns assumptions into explicit engineering artifacts.

---

# 46. Hands-On Exercise — Broken HTML

Modify the local HTML so that it contains:

1. A missing price.
2. A changed product class.
3. A missing product ID.
4. Nested formatting inside the name.
5. An empty article.
6. A duplicate product.

Example:

```html
<article class="product" data-product-id="101">
  <h2>
    Mechanical
    <strong>Keyboard</strong>
  </h2>
</article>

<article class="product">
  <h2>Broken Product</h2>
</article>

<article class="product" data-product-id="101">
  <h2>Mechanical Keyboard</h2>
</article>
```

### Your task

Make the extractor:

- preserve valid records,
- reject invalid records,
- report missing required fields,
- tolerate optional missing fields,
- normalize nested text,
- deduplicate duplicate identifiers.

### Expected reasoning

Do not simply catch every exception and continue.

Distinguish:

```text
expected optional absence
vs
unexpected required-field failure
```

---

# 47. Hands-On Exercise — Selector Drift

Version 1:

```html
<article class="product">
```

Version 2:

```html
<div class="product-card">
```

Suppose your selector is:

```css
article.product
```

and suddenly:

```python
len(soup.select("article.product"))
```

returns:

```text
0
```

### Questions

1. Is zero records necessarily a legitimate result?
2. What other page types could produce zero?
3. How would you distinguish selector drift from an empty catalog?
4. Should you simply broaden the selector to:

```css
.product
```

?

### Answer

Not automatically.

A broader selector may increase false positives.

The correct production response is:

```text
zero selector hits
    ↓
validate page identity
    ↓
inspect representative HTML
    ↓
compare expected structure
    ↓
alert if source changed
    ↓
update extractor intentionally
```

Selector flexibility should not come at the cost of silent incorrect extraction.

---

# 48. Hands-On Exercise — Responsible Crawler Design

Design a local/mock crawler with:

```text
allowed domain
allowed path
maximum pages
maximum depth
request delay
retry budget
cache
visited URL set
content validation
structured logging
```

Conceptual pseudocode:

```text
queue seed URL

while queue not empty:
    url = pop()

    if outside allowed scope:
        continue

    if already visited:
        continue

    if page limit reached:
        stop

    wait for rate limiter

    fetch with timeout

    validate HTTP response

    validate page identity

    cache raw response if appropriate

    parse HTML

    extract records

    validate records

    enqueue allowed links

    record metrics
```

The important design property is boundedness.

---

# 49. Production Architecture

A production HTML ingestion system can look like:

```text
Scheduler
    ↓
Source Contract
    ↓
Policy / robots Check
    ↓
URL Queue
    ↓
Crawl Boundary
    ↓
Rate Limiter
    ↓
HTTP Client
    ↓
Response Validation
    ↓
Raw Landing
    ↓
HTML Parser
    ↓
Extractor
    ↓
Record Validation
    ↓
Deduplication
    ↓
Bronze Dataset
    ↓
Observability
    ↓
Alerting
```

## Scheduler

Determines when extraction should run.

## Source Contract

Defines:

- source,
- policy assumptions,
- selectors,
- limits,
- expected outputs.

## Policy / robots check

Prevents the crawler from blindly accessing disallowed paths.

## URL queue

Tracks work.

## Crawl boundary

Prevents accidental expansion into unrelated resources.

## Rate limiter

Controls source load.

## HTTP client

Handles:

- timeout,
- connection reuse,
- headers,
- retries.

## Response validation

Confirms:

```text
status
content type
expected page identity
```

## Raw landing

Preserves source evidence when retention is appropriate.

## Parser

Converts HTML into a queryable tree.

## Extractor

Maps page structure into records.

## Record validation

Protects downstream systems from malformed data.

## Deduplication

Prevents repeated logical records.

## Observability

Measures system behavior.

## Alerting

Detects:

- source failures,
- schema drift,
- abnormal record counts,
- repeated parse failures.

---

# 50. Reprocessing and Reproducibility

Consider:

```text
raw HTML
+
parser version
+
extraction logic
```

This combination can allow historical reprocessing without repeatedly hitting the source.

For example:

```text
Day 1
HTML downloaded
    ↓
Parser v1
    ↓
Records

Day 20
Parser v2 fixes price parsing
    ↓
Read retained raw HTML
    ↓
Parser v2
    ↓
Reprocessed records
```

Track:

- parser version,
- extraction-code version,
- source snapshot,
- extraction run ID,
- retrieval timestamp.

Raw retention must still respect:

- storage cost,
- privacy,
- retention policy,
- licensing,
- source restrictions.

---

# 51. Testing HTML Extractors

## 51.1 Unit tests

Test:

- selector extraction,
- text normalization,
- URL normalization,
- missing fields,
- malformed HTML.

Example test scenario:

```text
Input:
<h2>  Keyboard   </h2>

Expected:
Keyboard
```

## 51.2 Contract tests

Verify:

```text
expected selectors exist
required fields exist
record count is plausible
```

## 51.3 Regression tests

Keep representative HTML examples as fixtures in a normal software project.

Because this curriculum artifact has a strict single-file requirement, this module does not create external test files. The examples remain embedded here for learning.

A regression fixture should represent a known source version.

---

# 52. Testing Strategy for Page Changes

A robust process is:

```text
Source changes
    ↓
Extractor detects anomaly
    ↓
Pipeline refuses to silently publish bad data
    ↓
Alert
    ↓
Engineer investigates
    ↓
Extractor updated
    ↓
Historical raw data reprocessed
```

Why?

Because:

```text
controlled failure
>
silent corruption
```

A pipeline that stops with a clear alert is often safer than a pipeline that continues producing plausible-looking but incorrect records.

---

# 53. Performance Considerations

Important variables include:

- network latency,
- HTML payload size,
- parser CPU,
- selector complexity,
- number of pages,
- concurrency,
- source rate limits,
- caching,
- repeated parsing,
- memory usage.

For many web extraction workloads:

```text
network behavior
+
source constraints
```

dominate parser CPU cost.

But parser CPU can matter when:

- pages are very large,
- HTML is complex,
- parsing volume is very high,
- repeated transformations are expensive.

Measure before optimizing.

---

# 54. Bounded Concurrency

Consider:

```text
1 worker
5 workers
50 workers
500 workers
```

More workers do not automatically mean faster ingestion.

At some point:

```text
more workers
    ↓
more concurrent requests
    ↓
rate limit reached
    ↓
429s
    ↓
retries
    ↓
more traffic
```

Other bottlenecks include:

- CPU,
- memory,
- connection pools,
- source limits,
- downstream storage.

The production goal is **bounded concurrency aligned with source capacity**, not maximum parallelism.

---

# 55. HTML Extraction vs API Extraction

| Dimension | API | HTML Extraction |
|---|---|---|
| Schema stability | Often explicit | Often implicit |
| Parsing complexity | Usually lower | Usually higher |
| Source contract | Usually documented | May be presentation-driven |
| Performance | Often efficient | Depends on page size/parsing |
| Pagination | Usually explicit | May be link-based or inconsistent |
| Authentication | Provider-defined | Provider-defined |
| Change frequency | API contract may be deliberate | Page redesigns can break selectors |
| Maintainability | Often simpler | Requires selector maintenance |
| Operational risk | Depends on provider | Often higher schema-drift risk |
| Structured data | Native | Must be inferred/extracted |
| Policy considerations | Usually documented | Must be assessed carefully |

This table does not establish a universal winner.

A suitable decision depends on:

```text
source availability
authorization
data requirements
freshness
volume
cost
stability
engineering effort
operational risk
```

If an appropriate authorized API exists, it is often the preferred structured ingestion interface.

---

# 56. Real-World Data Engineering Scenario

Suppose a company needs daily product metadata from an external public catalog.

Three options exist.

## Option A — Official API

Potential characteristics:

```text
structured data
documented schema
explicit pagination
documented quotas
```

Potential trade-offs:

```text
authentication
quota cost
subscription requirements
```

## Option B — Official feed/export

Potential characteristics:

```text
large batches
fewer requests
stable delivery artifact
```

Potential trade-offs:

```text
freshness may be lower
files may require additional processing
```

## Option C — HTML extraction

Potential characteristics:

```text
direct access to public presentation
no structured API dependency
```

Potential trade-offs:

```text
selector maintenance
page redesign risk
policy review
rate limiting
parser complexity
possible JavaScript rendering
```

### Architecture decision

Do not ask:

> Which method is always best?

Ask:

```text
Which interface satisfies the required correctness,
freshness, authorization, cost, operational reliability,
and source-impact constraints?
```

That is the Data Engineering decision.

---

# 57. Complete End-to-End Example

A production-oriented product extraction workflow:

```text
External product catalog
        ↓
Check API availability
        ↓
Check source policy
        ↓
Inspect robots.txt
        ↓
Define allowed pages
        ↓
Identify client
        ↓
Fetch with httpx
        ↓
Explicit timeout
        ↓
Rate limit
        ↓
Cache / conditional request
        ↓
Validate response
        ↓
Persist raw evidence where appropriate
        ↓
Parse with BeautifulSoup
        ↓
Extract product records
        ↓
Normalize text/URLs
        ↓
Validate required fields
        ↓
Deduplicate
        ↓
Detect schema changes
        ↓
Track metrics
        ↓
Persist structured records
        ↓
Alert on anomalies
```

The important point is that BeautifulSoup is only one component.

---

# 58. Advanced Architecture Questions

## 1. What if an API is unavailable but public HTML contains the required data?

First establish whether HTML access is permitted and whether another authorized interface exists.

If HTML is appropriate:

```text
define scope
+
policy checks
+
bounded retrieval
+
validation
+
raw evidence
+
robust extraction
+
monitoring
```

Do not treat the absence of an API as permission to bypass restrictions.

## 2. How would you detect a silent page redesign?

Monitor:

- selector hit counts,
- record counts,
- required-field presence,
- null rates,
- page fingerprints,
- expected markers.

Alert on statistically or contractually significant changes.

## 3. How would you prevent zero-record extraction from being treated as success?

Define explicit expectations:

```text
zero records
+
source normally non-empty
=
anomaly
```

Validate page identity and extraction counts before publishing.

## 4. How would you make a crawler resumable?

Persist:

- visited URL state,
- crawl frontier,
- successful URLs,
- failed URLs,
- extraction run ID,
- source snapshots where appropriate.

A restart should continue from known state rather than rediscovering the entire crawl.

## 5. How would you control source load?

Use:

```text
rate limit
+
bounded concurrency
+
caching
+
conditional requests
+
crawl boundaries
+
request minimization
```

## 6. How would you design crawl boundaries?

Explicitly define:

```text
allowed domains
allowed paths
maximum pages
maximum depth
pagination limits
query-parameter policy
```

## 7. How would you handle millions of URLs?

First determine whether HTML extraction is appropriate at that scale.

Then consider:

- source limits,
- distributed scheduling,
- shared rate limiting,
- durable crawl state,
- partitioned work,
- deduplication,
- storage,
- observability.

Do not assume “more workers” is the solution.

## 8. When should raw HTML be retained?

When reproducibility, auditability, debugging, or reprocessing justifies the storage and policy cost.

## 9. How would you reprocess historical pages after fixing a parser?

Use retained raw HTML snapshots:

```text
raw snapshot
+
new parser
=
new records
```

This avoids unnecessary re-downloads.

## 10. How would you distinguish source outage from parser failure?

Compare:

```text
HTTP status
content type
response body markers
selector hit counts
historical record counts
```

An HTTP 200 with zero selectors is a different failure from a 503.

## 11. How would you detect a 200 login or challenge page?

Validate:

- title,
- expected root selectors,
- known page markers,
- authentication indicators,
- expected content counts.

Never assume status code alone proves semantic success.

## 12. How would you handle localization?

Treat locale as part of the source contract.

Potential differences include:

- language,
- decimal separators,
- date formats,
- currency,
- page structure.

Do not mix localized pages without explicit normalization rules.

## 13. How would you design observability?

Capture:

```text
request metrics
parse metrics
record metrics
source metrics
schema-change indicators
error classifications
```

## 14. When would you stop using HTML extraction?

Examples:

- an official API becomes available,
- source policy changes,
- page structure becomes too unstable,
- extraction quality becomes unacceptable,
- operational cost becomes excessive,
- source volume exceeds safe limits,
- required data can no longer be reliably recovered.

## 15. How would you review the design from compliance, reliability, and cost perspectives?

Ask three groups of questions:

```text
Compliance:
Are we authorized?
Are policies respected?
Are retention practices appropriate?

Reliability:
Can we detect failures?
Can we resume?
Can we reprocess?
Can we detect schema drift?

Cost:
How many requests?
How much bandwidth?
How much storage?
How much engineering maintenance?
```

---

# 59. Debugging Scenarios

## Scenario 1 — HTTP 200 but zero records

### Symptom

```text
status = 200
records = 0
```

### Likely causes

- selector drift,
- login page,
- challenge page,
- JavaScript-generated content,
- legitimate empty source.

### Investigation

Inspect:

```text
response content type
page title
expected selectors
raw HTML
known page markers
```

### Corrective action

Determine which condition occurred before changing selectors.

### Prevention

Add zero-record and page-identity validation.

---

## Scenario 2 — Record count suddenly drops by 95%

### Symptom

```text
Yesterday: 10,000 records
Today:      500 records
```

### Likely causes

- source redesign,
- pagination failure,
- selector drift,
- localization change,
- source outage,
- legitimate business change.

### Investigation

Compare:

```text
raw HTML
page counts
selector hits
HTTP responses
pagination links
```

### Corrective action

Fix the actual failure rather than widening selectors blindly.

### Prevention

Record-count anomaly monitoring.

---

## Scenario 3 — CSS selector returns `None`

### Symptom

```python
soup.select_one(".price")
```

returns `None`.

### Likely causes

- missing optional field,
- changed selector,
- malformed page,
- wrong page.

### Investigation

Inspect the specific record and page source.

### Corrective action

Classify the field as required or optional and update the extractor if the source contract changed.

### Prevention

Selector contract tests.

---

## Scenario 4 — Site changes HTML structure

### Symptom

All extraction counts change after a redesign.

### Investigation

Compare source snapshots before and after the change.

### Corrective action

Update selectors intentionally and add regression coverage.

### Prevention

Schema-drift monitoring.

---

## Scenario 5 — Crawler receives 429

### Symptom

```http
429 Too Many Requests
```

### Investigation

Inspect:

```text
Retry-After
rate-limit headers
request rate
concurrency
```

### Corrective action

Respect provider guidance and reduce traffic.

### Prevention

Proactive rate limiting.

---

## Scenario 6 — Crawler receives 403

### Symptom

```http
403 Forbidden
```

### Correct response

Do not attempt to bypass the restriction.

Investigate:

- authorization,
- source policy,
- documented access mechanism.

Escalate or use an authorized alternative.

---

## Scenario 7 — HTML is replaced by a login page

### Symptom

```text
HTTP 200
```

but extraction finds:

```text
<form id="login">
```

### Correct response

Classify as semantic/content failure, not success.

Investigate authentication/session behavior through authorized mechanisms.

---

## Scenario 8 — Page is JavaScript-rendered

### Symptom

Expected product data is absent from downloaded HTML.

### Investigation

Inspect:

- HTML shell,
- scripts,
- browser network behavior,
- documented API endpoints.

### Correct action

Prefer an authorized structured interface if available.

Do not use browser automation to bypass access controls.

---

## Scenario 9 — Duplicate URLs produce duplicate records

### Cause

URL normalization or visited-state failure.

### Corrective action

Normalize URLs carefully and track visited crawl keys.

### Prevention

Test canonicalization and deduplication.

---

## Scenario 10 — Same page downloaded thousands of times

### Likely causes

- missing cache,
- duplicate URLs,
- retry loop,
- broken crawl state,
- repeated jobs.

### Corrective action

Measure request frequency and trace URL generation.

### Prevention

Caching, URL deduplication, and durable crawl state.

---

# 60. Common Beginner Mistakes

## Assuming every page is static HTML

Some content is generated after JavaScript executes.

## Using brittle selectors

Layout-dependent selectors break easily.

## Ignoring missing elements

Production pages are not guaranteed to be complete.

## Ignoring relative URLs

Relative links must be resolved correctly.

## Ignoring rate limits

The source is a shared system, not an unlimited endpoint.

## Making too many requests

Unnecessary traffic increases source load and operational risk.

## Not caching

Repeated development requests can needlessly hit the source.

## Ignoring robots.txt

A responsible crawler checks crawler guidance.

## Bypassing restrictions

Access denial is a boundary, not a challenge.

## Assuming 200 means success

HTTP success is not extraction success.

## Silently accepting zero records

Zero may indicate source or parser failure.

## No schema-drift detection

A broken selector can silently corrupt output.

## No logging

Failures become difficult to diagnose.

## No metrics

Quality degradation becomes invisible.

## No retry budget

Jobs can hang indefinitely.

## No deduplication

Reruns can create duplicate data.

## No source contract

Assumptions remain undocumented and untestable.

## No validation

Bad records flow downstream.

## Storing unnecessary raw data

Storage and privacy costs can become unnecessary.

## Treating scraping as a one-off script

Production ingestion requires operational design.

---

# 61. Benchmarking and Performance Experiment

Compare conceptual strategies:

```text
1. One worker
2. Small bounded concurrency
3. Larger bounded concurrency
4. Cached repeated extraction
5. Uncached repeated extraction
```

Measure:

```text
runtime
pages/sec
requests
bytes downloaded
cache hits
429s
CPU time
memory
```

The goal is not:

```text
maximum workers
```

The goal is:

```text
required useful throughput
+
acceptable source load
+
stable extraction quality
```

A useful observation is often:

```text
1 worker
    ↓
network-bound

10 workers
    ↓
better utilization

100 workers
    ↓
source rate limit

500 workers
    ↓
429s + retries + wasted traffic
```

The exact behavior depends on the source and environment.

---

# 62. Production Data Engineering Example

Suppose:

```text
Source:
SaaS product catalog

Pages:
50,000

Average page:
500 KB

Required freshness:
daily

Source policy:
bounded automated access

Extraction:
product metadata
```

Approximate raw transfer volume:

```text
50,000 × 500 KB
= 25,000,000 KB
≈ 25 GB
```

This simple calculation immediately exposes important questions:

```text
Is daily HTML retrieval necessary?
Is there an official export?
Can conditional requests reduce transfer?
Can caching eliminate unchanged downloads?
Can the crawl scope be reduced?
What rate does the source permit?
How much raw HTML should be retained?
```

Data Engineering starts with the workload and requirements, not with a parser library.

---

# 63. Production Checklist

## Source

```text
[ ] Official API checked
[ ] Official feed/export checked
[ ] Permission/policies reviewed
[ ] robots.txt inspected
[ ] Crawl scope defined
```

## HTTP

```text
[ ] Explicit timeout
[ ] Appropriate User-Agent
[ ] Bounded retries
[ ] Retry-After respected
[ ] Rate limiter configured
[ ] Caching considered
[ ] Conditional requests considered
```

## Parsing

```text
[ ] Selectors documented
[ ] Missing fields handled
[ ] URL normalization implemented
[ ] Text normalization implemented
[ ] Malformed HTML considered
[ ] JavaScript-generated content diagnosed
```

## Correctness

```text
[ ] Required fields validated
[ ] Record counts monitored
[ ] Duplicates detected
[ ] Schema drift detected
[ ] Zero-record failures detected
[ ] Page identity validated
```

## Reliability

```text
[ ] Idempotent reruns
[ ] Resumable workflow
[ ] Raw evidence strategy defined
[ ] Parser version tracked
[ ] Extraction-code version tracked
```

## Observability

```text
[ ] Structured logs
[ ] Request metrics
[ ] Parse metrics
[ ] Extraction metrics
[ ] Failure alerts
[ ] Source-change alerts
```

---

# 64. Interview Questions

## Basic

### 1. What is HTML parsing?

HTML parsing converts HTML text into a structured representation that can be navigated and queried.

### 2. What is the DOM?

The Document Object Model represents an HTML document as a tree of elements, attributes, and text nodes.

### 3. What is BeautifulSoup?

A Python library for parsing and navigating HTML and XML-like documents.

### 4. What is a CSS selector?

A pattern used to identify elements in a document.

### 5. What is XPath?

A query language for navigating XML/HTML document trees, particularly useful for complex relationships.

---

## Intermediate

### 6. CSS selectors vs XPath?

CSS selectors are often concise and familiar. XPath can express complex tree relationships and text-oriented queries more directly. The choice depends on structure and maintainability.

### 7. How do you handle missing elements?

Classify fields as required or optional, check elements before dereferencing them, and validate required fields explicitly.

### 8. How do you normalize extracted text?

Use explicit deterministic rules such as whitespace normalization and test the normalization separately.

### 9. How do you extract links?

Read `href`, resolve relative URLs using `urljoin`, and validate the resulting URL against crawl boundaries.

### 10. How do you detect selector drift?

Monitor selector hit counts, record counts, required-field presence, null rates, and representative source structure.

---

## Advanced

### 11. How would you build a production HTML extractor?

Start with source selection and policy checks, then define boundaries, fetch politely, validate responses, preserve raw evidence where appropriate, parse, extract, normalize, validate, deduplicate, observe, and make reruns/reprocessing safe.

### 12. How would you respect source rate limits?

Use proactive throttling, bounded concurrency, caching, provider-directed retry delays, bounded retries, and shared quota coordination where necessary.

### 13. How would you detect silent data corruption?

Define extraction contracts and monitor:

```text
record counts
selector hits
required-field presence
null rates
duplicates
page identity
```

### 14. How would you design resumability?

Persist crawl state and extraction progress so completed work is not unnecessarily repeated.

### 15. How would you handle page redesigns?

Detect the change, stop or quarantine affected output, investigate, update extraction logic, test against historical raw HTML, and reprocess where appropriate.

### 16. How would you monitor extraction quality?

Monitor both infrastructure metrics and data-quality metrics.

---

## Senior / Architecture

### 17. When should you refuse to scrape?

When access is not authorized, source policies prohibit the activity, an authorized interface is available and should be used, the source cannot be accessed responsibly, or the operational risk is unacceptable.

### 18. How do you decide between API and HTML extraction?

Evaluate:

```text
authorization
correctness
freshness
volume
stability
cost
engineering effort
operational risk
```

### 19. How do you design responsible crawling at scale?

Use explicit scope, centralized policy, bounded concurrency, shared rate limiting, durable crawl state, deduplication, caching, validation, observability, and clear stop conditions.

### 20. How do you handle millions of URLs without overwhelming the source?

Partition work while enforcing a shared source-level traffic budget. More workers should not imply more aggregate traffic than the source permits.

### 21. How do you design replay/reprocessing?

Retain appropriate raw source snapshots and track parser/extractor versions so historical data can be processed again without unnecessary source requests.

### 22. How do you balance reliability, cost, freshness, and source impact?

Treat them as explicit design dimensions:

```text
freshness requirement
        +
required completeness
        +
source constraints
        +
operational budget
        +
data retention requirements
```

The architecture should be driven by the workload.

---

# 65. Final Knowledge Check

## Conceptual

1. What is the difference between HTML source and a rendered browser page?
2. Why is HTML extraction an ingestion problem?
3. Why should an API be investigated before scraping?
4. What does a CSS selector do?
5. Why can a generated browser selector be fragile?
6. What is the difference between parsing and extraction?
7. Why is HTTP 200 insufficient to prove extraction success?
8. What is robots.txt?
9. Why should a crawler identify itself?
10. Why is rate limiting part of responsible scraping?

## Code-reading

Given:

```python
element = soup.select_one(".price")
price = element.get_text(strip=True)
```

What happens if the element is absent?

Expected answer:

```text
element becomes None
then get_text() raises AttributeError
```

Given:

```python
absolute_url = urljoin(
    "https://example.com/catalog/",
    "/products/101",
)
```

What is the result?

```text
https://example.com/products/101
```

## Debugging

A pipeline reports:

```text
HTTP success = 100%
records = 0
```

What should you investigate?

Expected areas:

```text
page identity
selector hits
login/challenge page
JavaScript rendering
source redesign
empty source
```

## Architecture

A source has:

```text
official API
daily export
HTML pages
```

What should you compare?

```text
correctness
freshness
cost
stability
authorization
engineering effort
operational risk
```

Do not answer by naming a universal winner.

---

# 66. Final Production Mental Model

The entire module can be reduced to:

```text
Prefer structured interfaces
        ↓
Verify permission and source policy
        ↓
Inspect robots.txt
        ↓
Define crawl boundaries
        ↓
Identify the client
        ↓
Fetch politely
        ↓
Validate HTTP response
        ↓
Validate page identity
        ↓
Cache / conditionally request when appropriate
        ↓
Parse robustly
        ↓
Extract structured records
        ↓
Normalize values and URLs
        ↓
Validate data
        ↓
Detect source changes
        ↓
Deduplicate
        ↓
Persist appropriate raw evidence
        ↓
Observe
        ↓
Retry only when appropriate
        ↓
Make reruns safe
        ↓
Reprocess from retained evidence when possible
        ↓
Stop when the source contract no longer supports
reliable, authorized extraction
```

The senior-level lesson is:

> **Do not measure the quality of an HTML extractor by whether it can retrieve a page. Measure it by whether it can repeatedly produce correct, complete, explainable data without violating source constraints or silently corrupting downstream systems.**

---

# 67. Final Architecture-Review Framework

Before approving an HTML extraction design, ask:

```text
1. What is the source?
2. Is an official structured interface available?
3. Are we authorized to automate access?
4. What does robots.txt indicate?
5. What do applicable source policies say?
6. What is the expected volume?
7. What freshness is required?
8. What is the source's request policy?
9. What are the crawl boundaries?
10. What happens when HTML changes?
11. How do we detect bad extraction?
12. How do we prevent excessive source load?
13. How do we make the workflow resumable?
14. How do we reprocess historical data?
15. How do we observe failures?
16. How do we validate correctness?
17. What is the operational cost?
18. How much raw data should be retained?
19. How do we handle sensitive information?
20. When would we replace HTML extraction with another interface?
```

If the design cannot answer these questions, it is not yet a production-ready ingestion design.

---

# 68. Final Checkpoint

Before moving forward, verify that you can explain and demonstrate:

```text
[ ] HTML fundamentals
[ ] DOM
[ ] HTML source vs rendered page
[ ] Parsing
[ ] BeautifulSoup
[ ] lxml
[ ] CSS selectors
[ ] XPath
[ ] Text extraction
[ ] Attribute extraction
[ ] URL normalization
[ ] Table extraction
[ ] Repeated-record extraction
[ ] Missing-field handling
[ ] Malformed HTML
[ ] JavaScript-generated content
[ ] JSON-LD / embedded metadata
[ ] API-first thinking
[ ] Responsible scraping
[ ] robots.txt
[ ] User-Agent identification
[ ] Polite request behavior
[ ] Rate limiting
[ ] Caching
[ ] Conditional requests
[ ] Crawl boundaries
[ ] URL deduplication
[ ] Record deduplication
[ ] Idempotency
[ ] Raw HTML retention trade-offs
[ ] Extraction contracts
[ ] Schema drift
[ ] Data validation
[ ] Observability
[ ] Error classification
[ ] Production architecture
[ ] Reproducibility
[ ] Testing
[ ] Performance
[ ] Bounded concurrency
[ ] API vs HTML trade-offs
[ ] Hands-on responsible extractor
[ ] Broken HTML debugging
[ ] Selector-drift debugging
[ ] Responsible crawler design
[ ] Production failure diagnosis
[ ] Architecture review
[ ] Interview preparation
[ ] Production checklist
```

If you can check these boxes and explain **why** each exists—not merely reproduce the code—you have moved from “I know how to scrape HTML” toward:

> **I can design and operate a responsible HTML-based ingestion component.**
