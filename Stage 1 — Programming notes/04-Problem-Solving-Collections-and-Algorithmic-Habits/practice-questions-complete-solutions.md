# Module 04 — Practice Questions: Complete Solutions and Line-by-Line Explanations

**Roadmap position:** Stage 1 → Module 04 — Problem-Solving, Collections, and Algorithmic Habits  
**Source:** `practice-questions.md` (35 questions)  
**Scope:** Only the seven Module 04 chapters: search/count/filter/map/aggregate; grouping/deduplication/sorting; Big-O; lists/dictionaries/sets/stacks/queues; comprehensions; recursion; parsing and regular expressions.

## Learning-level assessment

Your project tree places this practice set after the seven Module 04 lessons. The preceding modules teach Python values and collections, conditionals, loops, functions, scope, and errors. Module 04 then adds collection-processing patterns, grouping, sorting, complexity analysis, data-structure selection, comprehensions, recursion, parsing, CSV/JSON basics, and regular expressions.

**Current level:** beginner progressing toward intermediate. You can now use functions, loops, dictionaries, sets, tuples, comprehensions, generators, `Counter`, `defaultdict`, `deque`, recursion, and basic regex. Later modules cover file handling, testing frameworks, packages, OOP, and advanced production Python. This solution set does not depend on those later topics. Standard-library modules explicitly covered by the parsing lesson (`re`, `csv`, `io`, `collections`, `functools`) are used where the question calls for them.

---

# BASIC — Questions 1–5

## 1. First match, count, and total above a threshold

```python
def summarize_large(amounts, threshold):
    first_large = next((a for a in amounts if a > threshold), None)
    count_large = sum(a > threshold for a in amounts)
    total_large = sum(a for a in amounts if a > threshold)
    return first_large, count_large, total_large
```

- `def` defines a function receiving the amounts and threshold.
- `next(generator, None)` finds the first amount above the threshold; `None` is returned if no match exists.
- `sum(condition for ...)` counts matches because `True` and `False` contribute `1` and `0`.
- The final `sum` adds only qualifying amounts.
- Return the three results as a tuple.

**Example:** `[50, 120, 30, 200, 80]`, threshold `100` → `(120, 2, 320)`.  
**Complexity:** O(n) time, O(1) auxiliary space; three linear scans, no intermediate list.  
**Edges:** empty/no matches → `(None, 0, 0)`; equality is excluded because the comparison is `>`.

## 2. Group transactions by customer

```python
from collections import defaultdict

def total_by_customer(transactions):
    totals = defaultdict(int)
    for transaction in transactions:
        totals[transaction["customer"]] += transaction["amount"]
    return dict(totals)
```

- Import `defaultdict`.
- `defaultdict(int)` supplies `0` for a new customer key.
- Loop through every transaction.
- Add its amount to that customer's running total.
- Convert to an ordinary dictionary for the return value.

**Example:** A:100, B:50, A:30 → `{"A": 130, "B": 50}`.  
**Complexity:** O(n) average time, O(k) space for k customers.  
**Edges:** empty input → `{}`; negative amounts correctly represent refunds.

## 3. Trace recursive countdown sum

```python
def count_down_sum(n):
    if n == 0:
        return 0
    return n + count_down_sum(n - 1)
```

- Define the function with current number `n`.
- Base case: when `n` reaches zero, return zero and stop recursing.
- Otherwise, return the current `n` plus the result for `n - 1`.

For `count_down_sum(4)`: calls descend `4 → 3 → 2 → 1 → 0`; returns unwind `0 → 1 → 3 → 6 → 10`.  
**Complexity:** O(n) time and O(n) call-stack space.  
**Edges:** zero returns zero; negative input never reaches this base case, so this version assumes non-negative input.

## 4. Filter and lowercase words with a comprehension

```python
words = ["Python", "AI", "Data", "Engineering"]
result = [word.lower() for word in words if len(word) > 4]
```

- `word.lower()` is the value placed in the output.
- `for word in words` visits each original word.
- `if len(word) > 4` retains only words longer than four characters.

**Output:** `["python", "engineering"]`.  
**Complexity:** O(n) time, O(k) output space.  
**Edges:** empty input or no qualifying words → `[]`; `"Data"` is excluded because its length is exactly four.

## 5. Parse a delimited person line

```python
def parse_person_line(line):
    name, age, country = line.split(",")
    return {
        "name": name.strip(),
        "age": int(age.strip()),
        "country": country.strip(),
    }
```

- Split on the fixed comma delimiter into three strings.
- Unpack those strings into named variables.
- `strip()` removes surrounding whitespace from name and country.
- Strip age and convert it from text to an integer.
- Return a dictionary with meaningful field names.

**Example:** `"  John , 25 , India  "` → `{"name": "John", "age": 25, "country": "India"}`.  
**Complexity:** O(m) time for line length m; fixed-size output.  
**Edges:** wrong field count or nonnumeric age raises `ValueError`; this basic solution assumes valid input.

---

# MODERATE — Questions 6–15

## 6. Filter, map, and aggregate with a generator

```python
def total_completed_amount(transactions):
    return sum(
        transaction["amount"]
        for transaction in transactions
        if transaction["status"] == "completed"
    )
```

- Define the function.
- `sum()` consumes the generator and maintains the running total.
- Extract each transaction's amount.
- Visit the transactions one at a time.
- Keep only records whose status is exactly `"completed"`.

**Complexity:** O(n) time, O(1) auxiliary space.  
**Edges:** empty input or no completed records → `0`; negative refunds are included if completed.

## 7. Group customers, then rank by total

```python
from collections import defaultdict

def rank_customers(transactions):
    totals = defaultdict(int)
    for transaction in transactions:
        totals[transaction["customer"]] += transaction["amount"]
    return sorted(totals.items(), key=lambda item: item[1], reverse=True)
```

- Create zero-initialized totals.
- Visit every transaction and add its amount to its customer's total.
- `items()` produces `(customer, total)` pairs.
- `key=lambda item: item[1]` sorts by the second element, the total.
- `reverse=True` ranks highest first.

**Complexity:** O(n + k log k) time, O(k) space.  
**Edges:** empty input → `[]`; equal totals retain stable input/dictionary order.

## 8. Deduplicate events by a composite key, keeping the first

```python
def deduplicate_events(events):
    seen = set()
    result = []
    for event in events:
        key = (event["user_id"], event["day"], event["action"])
        if key not in seen:
            seen.add(key)
            result.append(event)
    return result
```

- `seen` tracks combinations already encountered.
- `result` stores surviving original records in arrival order.
- Build a tuple from the three identity fields; tuples of hashable values can be set members.
- If the tuple has not been seen, add it to the set and append the event.
- Return the first occurrence of every combination.

**Complexity:** O(n) average time, O(n) space.  
**Edges:** empty → `[]`; same user/day but different action remains distinct. All tuple components must be hashable.

## 9. Choose a structure for processed order IDs

```python
def is_new_order(order_id, processed_ids):
    if order_id in processed_ids:
        return False
    processed_ids.add(order_id)
    return True

processed_ids = set()
```

- Use a set because the required operation is membership, not retrieval of associated data.
- If the ID already exists, return `False`.
- Otherwise add it and return `True`.
- Initialize tracking with an empty set.

**Complexity:** O(1) average per ID, O(n) for n IDs; O(n) storage. A list would need O(n) membership and O(n²) overall across n checks.  
**Edges:** first ID returns `True`; repeated ID returns `False`.

## 10. Compare list comprehension and generator expression

```python
def sum_of_squares_list(numbers):
    return sum([n * n for n in numbers if n > 100])

def sum_of_squares_generator(numbers):
    return sum(n * n for n in numbers if n > 100)
```

- Both functions visit the numbers.
- `n * n` is the transformed value.
- `if n > 100` filters the input.
- Square brackets build a complete temporary list before summing.
- Parentheses/generator syntax produces values on demand as `sum()` consumes them.

**Complexity:** both O(n) time; list version O(k) extra space, generator version O(1) auxiliary space. Prefer the generator when the intermediate collection is not reused.  
**Edges:** empty/no qualifying numbers → `0`.

## 11. Analyze a nested loop with a constant inner bound

```python
def print_windows(items):
    for i in range(len(items)):
        for j in range(5):
            print(items[i], j)
```

- The outer loop runs n times.
- The inner loop always runs exactly five times, independent of n.
- Total prints are `5n`, so dropping the constant factor gives O(n), not O(n²).
- Nothing is accumulated in memory.

**Complexity:** O(n) time, O(1) auxiliary space.  
**Edges:** empty list prints nothing; one item prints five lines.

## 12. Recursively sum a nested list

```python
def deep_sum(items):
    total = 0
    for item in items:
        if isinstance(item, list):
            total += deep_sum(item)
        else:
            total += item
    return total
```

- Start the current list's subtotal at zero.
- Visit every element.
- If the element is a list, recursively sum that smaller list and add its returned subtotal.
- Otherwise add the numeric leaf directly.
- Return the subtotal after all elements are processed.

**Example:** `[1, [2, 3], [4, [5, 6]], 7]` → `28`.  
**Complexity:** O(m) time for m total elements; O(d) stack space for maximum nesting depth.  
**Edges:** empty list and empty nested lists contribute zero. Assumes leaves are numbers.

## 13. Validate a product code with `fullmatch`

```python
import re

def is_valid_product_code(code):
    return re.fullmatch(r"[A-Z]{2}-\d{4}", code) is not None
```

- Import regex support.
- `[A-Z]{2}` requires exactly two uppercase ASCII letters.
- `-` matches a literal hyphen.
- `\d{4}` requires four digits.
- `fullmatch()` requires the entire string to conform.
- A Match object means `True`; `None` means `False`.

**Example:** `"AB-1234"` → `True`; `"AB-1234extra"` → `False`.  
**Complexity:** O(m) time, O(1) auxiliary space.  
**Edges:** lowercase, wrong digit count, extra characters, and empty strings fail.

## 14. Extract fields from a log line

```python
import re

LOG_PATTERN = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) "
    r"(?P<time>\d{2}:\d{2}:\d{2}) "
    r"(?P<level>\w+): (?P<message>.+)"
)

def parse_log_line(line):
    match = LOG_PATTERN.search(line)
    return match.groupdict() if match else None
```

- Compile the reusable pattern once.
- `(?P<date>...)` captures the date under a name.
- The next named group captures the time.
- The level group captures word characters.
- The message group captures the remaining non-empty text.
- Search for the pattern; if a match exists, return its named captures as a dictionary; otherwise return `None`.

**Complexity:** O(m) time for line length m; fixed number of fields.  
**Edges:** malformed input returns `None`; the message may contain additional colons. Trailing spaces remain in the message unless stripped.

## 15. Parse quoted CSV correctly

```python
import csv
import io

def parse_csv_rows(raw_csv):
    reader = csv.reader(io.StringIO(raw_csv))
    return list(reader)
```

- Import the CSV parser and `StringIO`.
- `StringIO` makes the raw string behave like a file.
- `csv.reader` parses rows while respecting quoted fields and embedded commas.
- `list()` consumes the reader and returns all rows.

**Complexity:** O(c) time and O(c) result space for c input characters.  
**Edges:** empty input returns `[]`; varying row widths are accepted unless separately validated. Do not use `.split(",")` for genuine CSV.

---

# HARD — Questions 16–25

## 16. Deduplicate, filter, group, aggregate, and sort

```python
from collections import defaultdict

def deduplicate_by_id(transactions):
    by_id = {}
    for transaction in transactions:
        by_id[transaction["id"]] = transaction
    return list(by_id.values())

def spending_report(transactions):
    deduplicated = deduplicate_by_id(transactions)
    completed = [t for t in deduplicated if t["status"] == "completed"]
    totals = defaultdict(int)
    for transaction in completed:
        totals[transaction["customer"]] += transaction["amount"]
    return sorted(totals.items(), key=lambda item: item[1], reverse=True)
```

- Build a dictionary indexed by transaction ID.
- Assignment overwrites an earlier record with the same ID: last occurrence wins.
- Convert dictionary values to the deduplicated list.
- Filter the final versions to completed status.
- Create customer totals initialized to zero.
- Add each completed amount to the correct customer.
- Sort customer/total pairs by total descending.

**Complexity:** O(n + k log k) time, O(n) space for intermediate records.  
**Edges:** a last correction marked failed is excluded; no completed records → `[]`.

## 17. Count ERROR lines per service

```python
import re
from collections import Counter

LOG_PATTERN = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) "
    r"(?P<service>\w+) (?P<level>\w+): (?P<message>.+)"
)

def error_counts_by_service(log_text):
    parsed = []
    for line in log_text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = LOG_PATTERN.fullmatch(line)
        if match:
            parsed.append(match.groupdict())
    errors = [record for record in parsed if record["level"] == "ERROR"]
    return dict(Counter(record["service"] for record in errors))
```

- Import regex and `Counter`.
- Compile named groups for date, time, service, level, and message.
- Create a list of parsed records.
- Split raw text into lines; strip whitespace and skip blanks.
- `fullmatch()` rejects lines with extra or missing structure.
- Convert valid matches to dictionaries.
- Filter to exact `"ERROR"` severity.
- Count service names and return a plain dictionary.

**Complexity:** O(C) time for C total characters; O(n) intermediate space.  
**Edges:** malformed/blank lines are skipped; no errors or empty input → `{}`.

## 18. Clean and validate monetary strings

```python
import re

AMOUNT_PATTERN = re.compile(r"[+-]?(?:\d+(?:\.\d+)?|\.\d+)")
GROUPED_PATTERN = re.compile(r"[+-]?\d{1,3}(?:,\d{3})+(?:\.\d+)?")

def clean_amounts(raw_values):
    cleaned = []
    for value in raw_values:
        normalized = value.strip().lstrip("$€£").strip()
        if "," in normalized:
            if not GROUPED_PATTERN.fullmatch(normalized):
                continue
            normalized = normalized.replace(",", "")
        if not AMOUNT_PATTERN.fullmatch(normalized):
            continue
        cleaned.append(float(normalized))
    return cleaned
```

- Compile a general numeric grammar and a valid thousands-grouping grammar.
- Create the output list.
- Visit each raw string.
- Remove outer whitespace, a leading known currency symbol, and any following whitespace.
- If commas exist, first require correct thousands grouping; otherwise skip the value.
- Remove commas only after that validation.
- Require the remaining string to fully match a numeric format.
- Convert valid numeric text to `float` and append it.
- Return valid values only.

**Complexity:** O(n·m) time for n values of average length m; O(n) output space.  
**Edges:** `$1,200.50` → `1200.5`; `€500` → `500.0`; invalid text, `1.2.3`, `1,2` are skipped; negative values remain negative. For real financial calculations, `Decimal` is generally safer than binary floating point.

## 19. Recursively total numeric leaves in nested dictionaries

```python
def total_sales(data):
    total = 0
    for value in data.values():
        if isinstance(value, dict):
            total += total_sales(value)
        else:
            total += value
    return total
```

- Start subtotal at zero.
- Iterate over dictionary values.
- Recurse when a value is another dictionary.
- Otherwise add the numeric leaf.
- Return the combined total.

**Example:** nested sample in the question → `430`.  
**Complexity:** O(v) time for v values; O(d) stack space for depth d.  
**Edges:** empty dictionary contributes zero; negative values are included. Assumes all leaves are numeric.

## 20. Group unique customer IDs by country

```python
from collections import defaultdict

def unique_customers_by_country(customers):
    result = defaultdict(set)
    for customer in customers:
        result[customer["country"]].add(customer["customer_id"])
    return dict(result)
```

- Each new country receives an empty set automatically.
- Visit every customer record.
- Add its ID to that country's set; duplicates collapse automatically.
- Return an ordinary dictionary.

**Complexity:** O(n) average time, O(u) space for distinct country/ID pairs.  
**Edges:** empty input → `{}`; same ID in two countries appears in both sets.

## 21. Parse a nested delimited transaction

```python
def parse_transaction_line(line):
    transaction_id, customer, items_raw, status = line.split("|")
    items = {}
    if items_raw:
        for item in items_raw.split(","):
            name, separator, quantity = item.partition(":")
            items[name] = int(quantity)
    return {
        "id": transaction_id,
        "customer": customer,
        "items": items,
        "status": status,
    }
```

- Split the outer record on `|` into four fields.
- Initialize an empty item dictionary.
- Skip the item loop when the item field is empty.
- Split each item on commas.
- Partition each item at its first colon into name, separator, and quantity.
- Convert quantity to integer and store it under the item name.
- Return the structured transaction dictionary.

**Example:** `"T1|John|apple:2,banana:3|completed"` → expected nested dictionary.  
**Complexity:** O(m) time for line length m; O(k) space for k items.  
**Edges:** empty item field → `{}`; malformed quantity raises `ValueError`; extra `|` breaks this simple format.

## 22. Extract and validate contact strings

```python
import re

CONTACT_PATTERN = re.compile(
    r"(?P<name>[\w\s]+) <(?P<email>[\w.+-]+@[\w-]+\.[\w.-]+)>"
)

def extract_valid_contacts(raw_contacts):
    results = []
    for entry in raw_contacts:
        match = CONTACT_PATTERN.fullmatch(entry.strip())
        if match:
            results.append((match.group("name").strip(), match.group("email")))
    return results
```

- Compile one pattern with named groups for name and email.
- Create the results list.
- Visit each contact and trim outer whitespace.
- `fullmatch()` requires the entire entry to follow `Name <email>`.
- If it matches, extract the name and email by group name.
- Strip name whitespace, append a tuple, then return all valid tuples.

**Complexity:** O(n·m) time for n entries averaging m characters; O(n) output space.  
**Edges:** missing brackets or invalid email shape is skipped; this is a basic format check, not complete email-standard validation.

## 23. Calculate tree depth recursively

```python
def tree_depth(node):
    if not node["children"]:
        return 1
    return 1 + max(tree_depth(child) for child in node["children"])
```

- Inspect the current node's children.
- No children means this leaf node has depth one: the base case.
- Otherwise recursively calculate each child's depth.
- `max()` chooses the deepest child path.
- Add one for the current node.

**Complexity:** O(n) time because every node is visited once; O(h) call-stack space for tree height h.  
**Edges:** single node → `1`; chain of n nodes → depth n; wide tree with leaf children → depth 2.

## 24. Optimize duplicate detection

```python
def has_duplicate_optimized(transaction_ids):
    seen = set()
    for transaction_id in transaction_ids:
        if transaction_id in seen:
            return True
        seen.add(transaction_id)
    return False
```

- Start an empty set.
- Visit each ID.
- If it is already present, a duplicate exists; return immediately.
- Otherwise add it and continue.
- If the loop ends, no duplicate was found.

**Why the original is slow:** list membership scans an expanding list, producing O(n²) worst-case time.  
**Complexity:** optimized O(n) average time, O(n) space.  
**Edges:** empty/no duplicates → `False`; first repeated ID → `True`.

## 25. Build duplicate rejection plus FIFO processing

```python
from collections import deque

seen_ids = set()
pending_queue = deque()

def receive_transaction(transaction):
    transaction_id = transaction["id"]
    if transaction_id in seen_ids:
        return False
    seen_ids.add(transaction_id)
    pending_queue.append(transaction)
    return True

def process_next():
    if not pending_queue:
        return None
    return pending_queue.popleft()
```

- Import `deque`.
- Set handles fast duplicate membership; deque holds pending transactions in arrival order.
- Initialize both structures.
- Read incoming transaction ID.
- Reject it if already seen.
- Otherwise record the ID, append the transaction to the queue, and accept it.
- When processing, return `None` for an empty queue.
- Otherwise remove and return the oldest transaction with `popleft()`.

**Complexity:** receive O(1) average; process O(1); O(n) storage.  
**Edges:** duplicate rejected; empty queue returns `None`. IDs remain in `seen_ids` after processing, so a later resubmission is still rejected by design.

---

# ADVANCED — Questions 26–35

## 26. Parse, deduplicate, filter, group, and report transaction logs

```python
import re
from collections import defaultdict

LINE_PATTERN = re.compile(
    r"TXN:(?P<id>\S+) CUST:(?P<customer>\S+) "
    r"AMT:(?P<amount>\d+) STATUS:(?P<status>\S+)"
)

def parse_lines(raw_text):
    parsed, unparseable = [], []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = LINE_PATTERN.fullmatch(line)
        if match:
            record = match.groupdict()
            record["amount"] = int(record["amount"])
            parsed.append(record)
        else:
            unparseable.append(line)
    return parsed, unparseable

def deduplicate_first(records):
    seen, result = set(), []
    for record in records:
        if record["id"] not in seen:
            seen.add(record["id"])
            result.append(record)
    return result

def build_customer_report(raw_text):
    parsed, unparseable = parse_lines(raw_text)
    deduplicated = deduplicate_first(parsed)
    completed = [r for r in deduplicated if r["status"] == "completed"]
    totals = defaultdict(int)
    for record in completed:
        totals[record["customer"]] += record["amount"]
    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    return {
        "totals_by_customer": ranked,
        "unparseable_count": len(unparseable),
    }
```

- Compile a strict named-group pattern for transaction ID, customer, amount, and status.
- `parse_lines` creates valid and invalid buckets.
- Split into lines, trim, skip blanks, and require a full-line match.
- Convert the extracted amount to integer before aggregation.
- Preserve malformed nonblank lines separately.
- `deduplicate_first` uses a set to keep only the first record for each ID.
- Parse the raw input, deduplicate, then filter to completed records.
- `defaultdict(int)` accumulates customer totals.
- Sort totals highest-first and return them with the invalid-line count.

**Complexity:** O(C + n + k log k) time (C characters, n lines, k customers); O(n) space.  
**Edges:** nonnumeric amount fails regex and is unparseable; duplicate ID keeps first status; empty input returns empty totals and zero invalid count.

## 27. Analyze deduplication plus sorting complexity

```python
def unique_sorted_ids(customer_ids):
    seen = set()
    unique_ids = []
    for customer_id in customer_ids:
        if customer_id not in seen:
            seen.add(customer_id)
            unique_ids.append(customer_id)
    return sorted(set(unique_ids))
```

- `seen` provides average O(1) membership.
- `unique_ids` preserves the first-seen order while collecting unique IDs.
- The loop processes n raw records: O(n) average.
- `set(unique_ids)` repeats deduplication over k unique IDs: O(k), redundant but still work.
- `sorted(...)` sorts k IDs: O(k log k).

**Overall:** O(n + k + k log k) = O(n + k log k), where k ≤ n.  
**Space:** O(k). When duplicates are common, sorting only k unique IDs matters; saying only O(n log n) hides that distinction.

## 28. Decide whether `lru_cache` fits nested dictionary/list depth

```python
def max_depth(data):
    if isinstance(data, dict) and data:
        return 1 + max(max_depth(value) for value in data.values())
    if isinstance(data, list) and data:
        return 1 + max(max_depth(value) for value in data)
    return 1
```

- If the value is a non-empty dictionary, recursively inspect its values and add one.
- If it is a non-empty list, recursively inspect its elements and add one.
- Empty containers or scalar leaves return depth one.

**Memoization decision:** applying `@lru_cache` directly is invalid because dictionaries and lists are unhashable. It would raise `TypeError`. Repeated shared sub-objects may cause repeated work, but caching needs a usable key. A manually designed identity cache could use `id(data)`, but mutation can make cached results stale and requires careful lifetime/cycle handling; it is not a simple drop-in decorator.

**Complexity:** without caching O(v) visits across the structure; stack O(d).  
**Edges:** empty dict/list returns 1; no repeated substructure means caching adds overhead without benefit.

## 29. Choose structures for session membership, lookup, FIFO expiry, and audit order

```python
from collections import deque

active_session_ids = set()
sessions_by_id = {}
creation_order = deque()

def create_session(session_id, data):
    active_session_ids.add(session_id)
    sessions_by_id[session_id] = data
    creation_order.append(session_id)

def is_active(session_id):
    return session_id in active_session_ids

def get_session(session_id):
    return sessions_by_id.get(session_id)

def expire_oldest():
    if not creation_order:
        return None
    session_id = creation_order.popleft()
    active_session_ids.discard(session_id)
    sessions_by_id.pop(session_id, None)
    return session_id

def audit_report():
    return [sessions_by_id[sid] for sid in creation_order if sid in sessions_by_id]
```

- Set supports fast active-membership checks.
- Dictionary maps ID to session data.
- Deque preserves creation order and supports O(1) oldest removal.
- Creating a session inserts ID/data/order into all three structures.
- Membership checks use the set.
- Lookup uses `.get()` to safely return `None` when absent.
- Expiry safely handles an empty deque, removes the oldest ID, then removes it from set and dictionary.
- Audit iterates IDs in creation order and returns data still present.

**Complexity:** create/check/get/expire O(1) average; audit O(m); O(m) storage.  
**Assumption:** IDs are unique and not reused.  
**Edges:** empty expiry → `None`; expired lookup → `None`.

## 30. Replace repeated customer scans with a dictionary index

```python
def enrich_orders_optimized(orders, customers):
    customers_by_id = {}
    for customer in customers:
        customers_by_id.setdefault(customer["id"], customer["name"])
    return [
        {**order, "customer_name": customers_by_id.get(order["customer_id"])}
        for order in orders
    ]
```

- Create an ID-to-name dictionary.
- Visit each customer once.
- `setdefault` stores the first name for an ID and does not overwrite it later, matching the original loop's `break` behavior.
- For every order, unpack its existing fields into a new dictionary and add `customer_name`.
- `.get()` returns `None` for an unknown customer ID.

**Complexity:** O(n + m) average time for n customers and m orders; O(n + m) output/index space. The naive nested scan costs O(m·n).  
**Edges:** missing customer → name `None`; duplicate customer IDs preserve the first; empty orders → `[]`.

## 31. Fix the hidden quadratic email membership check

```python
def unique_valid_emails_fixed(records):
    seen = set()
    valid_emails = []
    for record in records:
        email = record.get("email")
        if email and email not in seen:
            seen.add(email)
            valid_emails.append(email)
    return valid_emails
```

- Set tracks membership efficiently; list preserves output order.
- Read email safely with `.get()`.
- Skip missing/empty email values.
- If not already seen, add it to the set and append it to the result.
- Return first-seen unique emails.

**Bottleneck in original:** `email not in valid_emails` scans a growing list, causing O(n²) worst-case time.  
**Complexity:** fixed version O(n) average time, O(u) space for u unique emails.  
**Edges:** missing/empty values skipped; duplicate email retained once; order preserved.

## 32. Memoize recursive Fibonacci

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci_fast(n):
    if n <= 1:
        return n
    return fibonacci_fast(n - 1) + fibonacci_fast(n - 2)
```

- Import `lru_cache`.
- Decorator caches results by function argument.
- Base cases return 0 or 1 directly.
- Otherwise calculate the two preceding Fibonacci values.
- Repeated requests for an already computed integer return from cache instead of repeating recursion.

**Why naive version is slow:** the same subproblems are recomputed in many branches, giving O(2ⁿ) time.  
**Memoized complexity:** O(n) time, O(n) cache plus call-stack space.  
**Edges:** large n still has recursion depth O(n), so the recursion limit remains relevant. Integer arguments are hashable, making them valid cache keys.

## 33. Fix recursive leaf counting

```python
def count_leaves_fixed(items):
    total = 0
    for item in items:
        if isinstance(item, list):
            total += count_leaves_fixed(item)
        else:
            total += 1
    return total
```

- Start the count at zero.
- Visit every item.
- For a nested list, recursively count its leaves and **add the returned count**.
- For a non-list value, add one leaf.
- Return the total.

**Bug:** the original called `count_leaves(item)` but discarded its return value.  
**Complexity:** O(m) time for all elements; O(d) stack space.  
**Edges:** flat `[1, 2, 3]` → 3; `[[1, 2], [3, [4, 5]]]` → 5; empty nested lists add zero.

## 34. Refactor an unreadable nested comprehension

```python
def is_processable(item):
    return (
        item["status"] == "active"
        and item["value"] is not None
        and item["value"] > 0
    )

all_items = [item for group in raw_groups for item in group["items"]]
result = [process(item) for item in all_items if is_processable(item)]
```

- The helper function names the business rule: active, non-None, positive value.
- The first comprehension flattens items from all groups into one list.
- The second comprehension visits the flattened items.
- It filters using the named helper.
- It calls `process()` only for qualifying items.

**Why clearer:** nested iteration and three conditions are separated into named steps.  
**Complexity:** O(m) time if `process` is O(1); O(m) extra space for `all_items`. The original fused comprehension avoids that intermediate list.  
**Edges:** empty group contributes nothing; value zero is excluded; missing `"value"` still raises `KeyError` as in the original.

## 35. Build an end-to-end log processing pipeline

```python
import re
from collections import defaultdict, Counter

LOG_PATTERN = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) "
    r"(?P<level>\w+): (?P<message>.+)"
)
TRANSACTION_PATTERN = re.compile(r"TXN\d+")

def parse_lines(raw_text):
    parsed, unparseable = [], []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = LOG_PATTERN.fullmatch(line)
        if match:
            parsed.append(match.groupdict())
        else:
            unparseable.append(line)
    return parsed, unparseable

def deduplicate_by_transaction(records):
    seen, result = set(), []
    for record in records:
        match = TRANSACTION_PATTERN.search(record["message"])
        key = match.group() if match else None
        if key is None or key not in seen:
            if key is not None:
                seen.add(key)
            result.append(record)
    return result

def build_full_report(raw_text):
    parsed, unparseable = parse_lines(raw_text)
    deduplicated = deduplicate_by_transaction(parsed)
    severity_counts = Counter(record["level"] for record in deduplicated)

    errors_by_transaction = defaultdict(list)
    for record in deduplicated:
        if record["level"] == "ERROR":
            match = TRANSACTION_PATTERN.search(record["message"])
            key = match.group() if match else "none"
            errors_by_transaction[key].append(record)

    return {
        "total_lines": len(raw_text.splitlines()),
        "parsed_count": len(parsed),
        "unparseable_count": len(unparseable),
        "deduplicated_count": len(deduplicated),
        "severity_counts": dict(severity_counts),
        "errors_by_transaction": dict(errors_by_transaction),
    }
```

**Line-by-line design**

1. Import regex, `defaultdict`, and `Counter`.
2. Compile the main log format with named date/time/level/message groups.
3. Compile a second pattern for transaction references such as `TXN123`.
4. `parse_lines` creates valid and invalid buckets.
5. Split the input into lines, trim each, and skip blanks.
6. Require the whole nonblank line to match the log pattern.
7. Convert a successful match to a dictionary; preserve failed lines separately.
8. `deduplicate_by_transaction` creates a set and result list.
9. Search each message for its first transaction reference.
10. Keep every record without a reference; for referenced records, keep only the first occurrence.
11. `build_full_report` parses, deduplicates, and counts severity levels.
12. Loop through deduplicated records and retain exact `ERROR` severity records in groups by transaction ID.
13. Use `"none"` for an error without a transaction reference.
14. Return total input lines, parsed count, invalid count, deduplicated count, severity counts, and error groups.

**Complexity:** O(C) time under the assumption that these simple regex patterns scan linearly, where C is total input characters; O(n) record space for n lines. Set/dictionary operations are O(1) average-case.  
**Important counting convention:** `total_lines` includes blank lines; `parsed_count` and `unparseable_count` exclude blank lines. Therefore total lines may exceed parsed + unparseable.  
**Edges:** malformed lines are preserved; no-reference records are not deduplicated against each other; duplicate referenced records keep the first; grouping keeps every deduplicated ERROR record for a transaction; empty text returns zero counts and empty dictionaries.

---

# Final revision checklist

- [ ] Search, count, filter, map, aggregate, and generator expressions.
- [ ] Grouping with dictionaries/`defaultdict`, counting with `Counter`, and sorting with a key.
- [ ] First-write-wins versus last-write-wins deduplication.
- [ ] Composite tuple keys and set membership.
- [ ] O(1), O(n), O(n²), O(n log n), and O(2ⁿ) reasoning.
- [ ] Lists versus dictionaries versus sets versus stacks/queues/deques.
- [ ] List comprehensions versus generators and memory trade-offs.
- [ ] Recursive base cases, recursive calls, unwinding, and call-stack depth.
- [ ] Parsing with `split`, `partition`, `strip`, `csv`, and regex.
- [ ] Regex `fullmatch`, named groups, quantifiers, and compiled patterns.
- [ ] Pipeline design: parse → validate → deduplicate → filter → group → aggregate → sort → report.
- [ ] Edge cases: empty input, malformed rows, duplicates, missing keys, invalid types, and deeply nested input.

**Engineering rule:** choose data structures based on the operations the workload performs; use the simplest parser that correctly understands the input format; and analyze the cost of the operation inside a loop, not merely the number of loops visible in the code.
