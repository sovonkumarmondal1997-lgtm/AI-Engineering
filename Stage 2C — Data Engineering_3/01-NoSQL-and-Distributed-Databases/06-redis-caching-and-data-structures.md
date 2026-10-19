# Redis: Caching and Data Structures

**Roadmap location:** `Stage 2C — Data Engineering_3/01-NoSQL-and-Distributed-Databases/06-redis-caching-and-data-structures.md`  
**Level:** Beginner → Intermediate → Advanced  
**Primary purpose:** Learn to select Redis data structures and build reliable low-latency serving patterns without confusing speed with durability or correctness.

> **Version note.** Examples use broadly supported Redis commands and `redis-py` (`redis` package). Check the exact Redis server and client versions you deploy. Redis Open Source, Redis Stack, and managed Redis-compatible services do not necessarily expose identical modules, commands, defaults, or operational controls. Commands that inspect or change server configuration may be restricted on managed services.

## 1. Learning objectives

By the end, you should be able to:

- Explain why Redis is fast and where latency can still arise.
- Choose strings, hashes, lists, sets, sorted sets, Streams, bitmaps, HyperLogLog, or a Bloom filter based on access patterns and guarantees.
- Estimate command complexity and recognize operations that become expensive as a key grows.
- Design TTLs, cache invalidation, cache-aside, stampede protection, and cache failure behavior.
- Use atomic commands, Lua scripts, `MULTI`/`EXEC`, and pipelining appropriately.
- Implement practical rate limiting, sessions, deduplication, leaderboards, and queue-like workflows.
- Explain persistence, eviction, memory overhead, replication, Sentinel, and Cluster trade-offs.
- Use Python connection pools and explicit serialization safely.
- Run the required experiments, collect real measurements, and document observations without inventing benchmark results.

## 2. Prerequisites and roadmap position

This topic follows NoSQL families and consistency concepts, MongoDB document modelling, Cassandra partitioning, and DynamoDB access-pattern modelling. Those topics establish that a data store must be selected for its access patterns and failure model, not just its API.

Expected prior skills:

- Python functions, exceptions, packages, JSON, and environment variables.
- Basic SQL and the difference between operational workloads and analytical aggregation.
- HTTP/service latency, caching, idempotency, and basic concurrency concepts.
- Docker Compose and command-line use.

Redis is a specialised store used alongside a primary database, not a replacement for PostgreSQL, DuckDB, Kafka, or an analytical lakehouse by default. Later NoSQL-to-lakehouse ingestion work should treat Redis as an operational source with explicit retention and extraction constraints.

## 3. Terminology

| Term | Meaning |
|---|---|
| Key | A binary-safe identifier used to locate a value, often namespaced, e.g. `report:daily:2026-10-19`. |
| Value / data structure | The string or structured Redis value stored at a key. |
| TTL | Time to live; remaining lifetime before an expiring key is removed logically. |
| Cache hit / miss | A requested value exists and is usable / is absent or unusable. |
| Eviction | Redis removes keys to satisfy a configured memory policy. |
| Atomic command | One command executes indivisibly relative to other commands on the same Redis server. |
| Pipeline | Multiple commands sent together to reduce network round trips; it is not inherently a transaction. |
| Persistence | Mechanism to recover data after process/server restart, with a specific loss window. |
| Primary / replica | A node that accepts writes for its data and one that replicates it. |
| Hash slot | One of 16,384 logical slots used by Redis Cluster to assign keys to shards. |

## 4. What Redis is and why it is fast

Redis is an in-memory data-structure server accessed through a request/response protocol. It supports atomic operations over a key's value, expiration, replication, optional persistence, and horizontal partitioning through Cluster.

Common reasons for low latency:

1. Data structures are usually served from memory rather than random disk reads.
2. Commands operate on purpose-built structures, such as hash tables, linked lists, and skip lists.
3. A command normally avoids a full query planner and complex joins.
4. The client/server protocol is compact, and pipelining can amortize network round trips.

These are not a promise that every operation is O(1) or every workload is fast. A huge `LRANGE`, a large set intersection, a Lua script that runs too long, a big key, CPU saturation, network distance, TLS, persistence I/O, replication lag, or a hot shard can all produce latency. Redis command execution has historically been largely single-threaded for command processing, while networking and some background/I/O work may use additional threads depending on version and configuration. Do not infer that Redis uses only one thread for every subsystem, nor assume CPU-heavy commands can scale linearly across cores.

### 4.1 Command execution model

A command is executed without another ordinary command interleaving into its execution on that server. This makes commands such as `INCR`, `ZADD`, and `HINCRBY` useful building blocks for concurrency-safe updates. It does **not** make a sequence of independent commands atomic. Use a transaction, a Lua script, or a purpose-built atomic command when a read-modify-write sequence must not race.

### 4.2 Key namespacing

Use predictable prefixes to identify ownership and purpose:

```text
session:{user_id}
profile:{user_id}
cache:orders-summary:{customer_id}:{date}
rate:{user_id}:{route}
leaderboard:season-2026
```

Avoid sensitive information in keys if it could appear in logs or monitoring. Choose separators consistently. In Cluster, braces such as `{customer-42}` form a hash tag: the substring inside braces influences the hash slot. Hash tags can enable multi-key operations on related keys but can also concentrate traffic on one slot; use them deliberately.

## 5. Core data structures and command complexity

Big-O describes how work scales with the data structure, not end-to-end latency. Redis documentation gives command-specific complexity; check the version-specific command reference before relying on a bound. The following are common cases.

### 5.1 Strings

Strings store bytes and can represent text, serialized JSON, counters, flags, or opaque payloads.

```redis
SET cache:product:42 '{"id":42,"name":"Keyboard"}' EX 300
GET cache:product:42
TTL cache:product:42
INCR metrics:requests
SET session:abc token NX EX 60
```

- `GET`, `SET`: O(1) with respect to key count; payload copying and allocation still depend on value size.
- `INCR`: O(1) for the integer value.
- `EXPIRE`: O(1) for one key.
- `SET ... NX EX`: atomic conditional creation with expiry; useful for short-lived claims, but not by itself a complete distributed lock protocol.

Use strings when the application retrieves or replaces a whole value, or needs atomic numeric updates. Large serialized blobs may cause unnecessary bandwidth, copying, and cache invalidation if only one field changes.

### 5.2 Hashes

Hashes store field/value pairs under one key, useful for compact records where individual fields change independently.

```redis
HSET user:42 name "Asha" plan "pro" login_count 3
HGET user:42 plan
HGETALL user:42
HINCRBY user:42 login_count 1
```

- `HSET`, `HGET`, `HINCRBY`: O(1) average for one field.
- `HMGET`: O(N) in the number of requested fields.
- `HGETALL`: O(N) in the number of fields; avoid for unbounded hashes.

A hash is not a relational row with schema enforcement. The application owns validation, field types, and migration strategy. Hashes may be memory-efficient for small records, but exact encoding and memory cost depend on Redis version, field/value sizes, and configuration.

### 5.3 Lists

Lists are ordered sequences suited to bounded work queues, recent items, and simple producer/consumer patterns.

```redis
LPUSH jobs:email job-102
RPUSH jobs:email job-103
LPOP jobs:email
LRANGE jobs:email 0 9
```

- `LPUSH`, `RPUSH`, `LPOP`, `RPOP`: O(1) at the ends.
- `LRANGE key start stop`: O(S+N), where S is the distance to the start and N is the returned elements; retrieving a large range costs time and bandwidth.
- `LINDEX`: O(N) for traversing to an index in the general case.

Lists do not automatically provide the durable replay, consumer groups, or operational semantics of Kafka. Blocking list commands can be useful for simple queues, but reliability requirements may call for Streams or a dedicated message broker.

### 5.4 Sets

Sets hold unique members and support membership and set algebra.

```redis
SADD campaign:2026:visitors user-1 user-2 user-1
SISMEMBER campaign:2026:visitors user-2
SCARD campaign:2026:visitors
SINTER cohort:paid cohort:active
```

- `SADD`, `SREM`, `SISMEMBER`, `SCARD`: O(1) average per member.
- `SMEMBERS`: O(N), returning every member.
- `SINTER`: depends on the sizes of the input sets and the chosen implementation path; large set algebra can be expensive.

Sets are exact for membership and cardinality but store every member. They are suitable for exact deduplication at moderate scale when memory is acceptable. For approximate unique counts, consider HyperLogLog.

### 5.5 Sorted sets

Sorted sets map unique members to numeric scores. Redis orders members by score and breaks equal-score ties lexicographically.

```redis
ZADD leaderboard:season-2026 1200 player-7 980 player-3
ZINCRBY leaderboard:season-2026 25 player-7
ZREVRANGE leaderboard:season-2026 0 9 WITHSCORES
ZRANK leaderboard:season-2026 player-3
```

- `ZADD`, `ZREM`, `ZINCRBY`, rank lookups: typically O(log N) per member.
- `ZRANGE`/`ZREVRANGE`: O(log N + M), where M is the number of returned members.
- Range-by-score complexity is typically O(log N + M).

Sorted sets work well for leaderboards, scheduling windows, and sliding-window rate limiting. Keep the cardinality bounded where possible; a score's meaning and tie-break rules must be defined by the application.

### 5.6 Streams

Streams are append-oriented logs with IDs, field/value entries, consumer groups, pending-entry tracking, and acknowledgement. They are useful for Redis-native event workflows, but retention and durability depend on trimming and persistence/replication configuration.

```redis
XADD events:orders * order_id 1001 event_type created
XRANGE events:orders - + COUNT 10
# Start at 0 to consume entries that already exist in this example.
XGROUP CREATE events:orders order-workers 0 MKSTREAM
XREADGROUP GROUP order-workers worker-1 COUNT 10 BLOCK 5000 STREAMS events:orders >
# Replace <entry-id-from-read> with the actual ID returned by XREADGROUP.
XACK events:orders order-workers <entry-id-from-read>
```

The group start ID matters: `$` starts after the stream's current last entry, so a group created with `$` after the `XADD` above would not deliver that earlier entry. Use `$` when the intended policy is to consume only entries added after group creation; use `0` (or an explicit ID) to process retained history. A consumer must acknowledge only after processing has succeeded. Failed/unacknowledged entries remain pending and require a recovery strategy such as `XPENDING` and `XCLAIM`; `XAUTOCLAIM` is available from Redis 6.2. Streams are not automatically an unlimited durable event log.

### 5.7 Other useful structures

| Structure | Example | Use and trade-off |
|---|---|---|
| Bitmap | `SETBIT daily-active:2026-10-19 123 1`; `BITCOUNT daily-active:2026-10-19` | Compact flags indexed by integer offset; offset range and semantics must be controlled. |
| HyperLogLog | `PFADD visitors:campaign-7 user-1 user-2`; `PFCOUNT visitors:campaign-7` | Approximate cardinality with small, bounded memory; cannot enumerate members and has a small standard error (about 0.81% under typical conditions). |
| Bloom filter | `BF.ADD seen-events event-123`; `BF.EXISTS seen-events event-123` | Probabilistic membership: false positives possible, false negatives are not expected under normal operation. Requires RedisBloom/module or a compatible managed offering; not a core command on every Redis deployment. |
| Geospatial commands | `GEOADD stores 77.6 12.9 store-1`; `GEOSEARCH stores FROMLONLAT 77.6 12.9 BYRADIUS 5 km` | Geographic lookup built on sorted-set-like storage; not a full GIS engine. |

### 5.8 Complexity quick reference

| Command family | Common complexity | Watch out for |
|---|---|---|
| `GET`, `SET`, `INCR`, `EXPIRE` | O(1) per key/value operation | Value size, key expiry bursts, hot keys. |
| `HGET`, `HSET`, `HINCRBY` | O(1) average per field | Unbounded `HGETALL`. |
| `LPUSH`, `RPOP` | O(1) at list ends | Large `LRANGE`, queue growth. |
| `SADD`, `SISMEMBER` | O(1) average per member | `SMEMBERS`, large intersections. |
| `ZADD`, `ZRANK` | O(log N) per member | Large range responses and unbounded cardinality. |
| `SCAN` | O(1) per call, O(N) for a full iteration | It is incremental, may return duplicates, and is not a consistent snapshot. |
| `KEYS pattern` | O(N) over the keyspace | Avoid in production on a busy large instance. |
| Lua script | Depends on script work | Runs atomically but blocks other command execution while running; keep short. |

## 6. Expiration, TTL, and lifecycle

Set expiration when creating a cache entry so an error between writing the value and setting TTL cannot leave an accidental permanent key:

```redis
SET cache:report:daily:2026-10-19 '{"total":81}' EX 120
EXPIRE cache:report:daily:2026-10-19 120
TTL cache:report:daily:2026-10-19
PTTL cache:report:daily:2026-10-19
PERSIST cache:report:daily:2026-10-19
```

`TTL` returns seconds; `PTTL` returns milliseconds. `-2` means the key does not exist; `-1` means the key exists but has no expiry. Expiration is not a real-time scheduler: Redis removes expired keys lazily on access and through active expiration work. Do not build precise business deadlines around the assumption that a key disappears at an exact millisecond.

### 6.1 TTL jitter

If many cache entries are written simultaneously with the same TTL, they may expire together and create a burst of database traffic. Add random jitter, e.g. a base 300 seconds plus 0–60 seconds, to spread expiry. Jitter reduces synchronized expiration; it does not guarantee only one loader runs on a miss.

### 6.2 Cache lifecycle

- **Hit:** return the cached value; update metrics.
- **Miss:** read the source of truth, populate cache with a bounded TTL, then return the value.
- **Source update:** invalidate or refresh affected keys according to a documented policy.
- **Expiration:** key becomes logically unavailable; a later request may reload it.
- **Eviction:** under a memory policy, Redis may remove a key before TTL. Application code must treat both as cache misses.
- **Redis outage:** decide whether to fail open to the database, fail closed, or degrade the feature; protect the source from a sudden full miss storm.

## 7. Caching patterns

### 7.1 Cache-aside (lazy loading)

The application checks Redis first. On a miss, it queries PostgreSQL/DuckDB or another source, then stores the result.

```text
request -> Redis GET
            | hit -> return
            | miss -> source query -> Redis SET with TTL -> return
```

Advantages: simple, caches only requested data, source remains authoritative. Costs: first miss is slow, invalidation must be designed, concurrent misses can stampede.

### 7.2 Read-through

A cache abstraction owns the miss loader. Application code requests a value from the abstraction rather than explicitly performing the source lookup. This is a library/application pattern; Redis itself does not automatically query PostgreSQL when a key is absent.

### 7.3 Write-through

Writes go through a layer that updates the source and cache as part of the same logical operation. It can improve read freshness, but Redis and the database do not become one atomic transaction just because both are updated. Define failure recovery and ordering.

### 7.4 Write-behind (write-back)

The application writes to the cache first and asynchronously persists later. It can reduce write latency, but risks data loss and replay complexity if Redis or the consumer fails before durable persistence. Use only with explicit durability, backlog, retry, idempotency, and reconciliation requirements—not casually for critical records.

### 7.5 Pattern comparison

| Pattern | Read latency | Freshness | Write complexity | Failure considerations |
|---|---|---|---|---|
| Cache-aside | Very low on hit; source latency on miss | TTL/invalidation dependent | Moderate | Miss storms and stale values. |
| Read-through | Similar hit/miss behavior | Loader policy dependent | Centralized cache layer | Loader outages and cache abstraction behavior. |
| Write-through | Low on later reads | Can be fresh if source/cache sequencing is correct | Higher | Partial failure across two systems. |
| Write-behind | Low write acknowledgement latency | Eventual | Highest operational complexity | Acknowledged-but-not-durable writes, retries, backlog and replay. |

### 7.6 Invalidation strategies

1. **TTL only:** simple, bounded staleness, but stale until expiry.
2. **Explicit delete:** after successful source update, delete the affected cache key. A race can still repopulate stale data if a concurrent miss read the old source value.
3. **Versioned keys:** include a source version in cache key or payload. Old entries expire naturally; resolving current version must itself be reliable.
4. **Event-driven invalidation:** consume CDC/outbox events and invalidate or refresh keys. Events can be delayed, duplicated, or reordered, so handlers should be idempotent and monitor lag.
5. **Write-through refresh:** update source and cache through a single application service, with explicit partial-failure handling.

Do not claim perfect consistency between Redis and a separate database without a shared transaction protocol. State the acceptable stale window and the recovery process.

## 8. Cache stampedes and protection

A stampede occurs when many requests miss or expire together and all issue the same expensive source query.

Mitigations can be combined:

- TTL jitter.
- Request coalescing/single-flight inside one process.
- A short distributed lock around refresh, with a bounded wait and fallback policy.
- Stale-while-revalidate: serve a still-acceptable stale value while one worker refreshes it.
- Pre-warming for known high-traffic keys.
- Database concurrency limits and circuit breakers so Redis failure does not overload the source.

A basic lock acquisition:

```redis
SET lock:aggregate:daily random-token NX PX 10000
```

The token must be unique to the owner. Release only if the stored token still matches; never blindly `DEL` a lock key, because a lease may expire and another worker may acquire it. In Redis versions that support it, a short Lua compare-and-delete script is commonly used:

```lua
if redis.call('GET', KEYS[1]) == ARGV[1] then
  return redis.call('DEL', KEYS[1])
end
return 0
```

Locks have caveats: client pauses, lease expiry during long work, failover and replication timing, clock/network uncertainty, and work continuing after lease loss. A lock is not a substitute for a fencing token or database-side concurrency control when correctness is critical. Keep the critical section bounded and make refresh work idempotent.

## 9. Atomic operations, scripts, transactions, and pipelining

### 9.1 Purpose-built atomic commands

```redis
INCR metrics:api:requests
HINCRBY user:42 login_count 1
SET lock:job:42 token NX PX 10000
```

Each command is atomic on its Redis server. `SETNX lock:job:42 token` is the older standalone conditional-set command, but it can leave a key without expiry if a later `EXPIRE` fails. Prefer `SET lock:job:42 token NX EX 10` or `SET ... NX PX 10000` when expiry must be attached atomically. Neither form alone solves lease expiry, failover, or fencing requirements for correctness-critical distributed locks.

### 9.2 `MULTI` / `EXEC`

```redis
MULTI
INCR account:42:attempts
EXPIRE account:42:attempts 3600
EXEC
```

Redis queues commands between `MULTI` and `EXEC`, then executes the queued sequence without other commands interleaving. This is not a relational rollback transaction: a runtime error in one command does not automatically roll back earlier or later commands in the transaction. Use `WATCH` for optimistic concurrency when a transaction depends on a prior read; if a watched key changes, `EXEC` aborts and the client must retry.

### 9.3 Lua scripts

Lua scripts run atomically relative to other commands on the server and are useful when the logic must read, check, and update Redis state without a race. They block command processing while running, so keep scripts short and bounded. In Cluster, all keys touched by a script must be supplied as keys and generally need to be in the same hash slot.

### 9.4 Pipelining

Pipelining sends several independent commands before waiting for responses, reducing network round trips:

```python
pipe = client.pipeline(transaction=False)
for key in keys:
    pipe.get(key)
values = pipe.execute()
```

A pipeline is not automatically atomic. `transaction=True` (the usual `redis-py` default) typically wraps commands in `MULTI`/`EXEC`; set the mode explicitly to communicate intent. Pipelining very large batches increases memory use and response latency; use bounded batches.

## 10. Common application patterns

### 10.1 Sliding-window rate limiter with a sorted set

For each user/route, store request IDs as members and timestamps as scores. Remove entries older than the window, count remaining requests, then add the current request if under limit. The read-check-write sequence must be atomic; implement it in a Lua script. The script below uses server time from `TIME`, removes expired entries, checks count, inserts a unique request ID, and sets a key TTL.

```lua
-- KEYS[1] = rate-limit key
-- ARGV[1] = window length in milliseconds
-- ARGV[2] = maximum requests
-- ARGV[3] = unique request ID
local now_parts = redis.call('TIME')
local now = (tonumber(now_parts[1]) * 1000) + math.floor(tonumber(now_parts[2]) / 1000)
local window = tonumber(ARGV[1])
local limit = tonumber(ARGV[2])
if not window or not limit or window <= 0 or limit <= 0 or not ARGV[3] or ARGV[3] == '' then
  return redis.error_reply('window, limit, and request ID must be valid')
end
local cutoff = now - window
redis.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', cutoff)
-- An accepted request retried with the same ID remains accepted and is not counted twice.
if redis.call('ZSCORE', KEYS[1], ARGV[3]) then
  return {1, redis.call('ZCARD', KEYS[1])}
end
local count = redis.call('ZCARD', KEYS[1])
if count >= limit then
  return {0, count}
end
redis.call('ZADD', KEYS[1], now, ARGV[3])
redis.call('PEXPIRE', KEYS[1], window)
return {1, count + 1}
```

Complexity includes the removed members: `ZREMRANGEBYSCORE` costs O(log N + M), where M is the number removed; `ZSCORE` and `ZCARD` are O(1), and `ZADD` is O(log N). The whole script runs atomically but can block other commands while removing a large backlog, so keep the window state bounded and monitor script latency. Generate a globally unique member per logical request (for example UUID). A retry with the same ID is idempotently allowed if that accepted ID is still in the active window; rejected attempts are not stored, so a later retry may be allowed when capacity opens. If you need to replay the exact previous rejection too, store a bounded decision record separately. In Cluster, a single rate-limit key is simple; do not split one user's window across arbitrary slots unless the algorithm accounts for it.

### 10.2 Leaderboard

Use a sorted set where member is player ID and score is points:

```redis
ZINCRBY leaderboard:season-2026 10 player-7
ZREVRANGE leaderboard:season-2026 0 9 WITHSCORES
ZREVRANK leaderboard:season-2026 player-7
```

Decide tie handling, score reset/season rollover, and whether rank must be exact. A single global leaderboard key may become hot at very high update rates; partitioning by region/season or maintaining local leaderboards plus a merge layer may be needed.

### 10.3 Sessions

Store a session as a string or hash and apply TTL:

```redis
HSET session:opaque-token user_id 42 role analyst
EXPIRE session:opaque-token 1800
```

For session creation, set the fields and expiry in a safe sequence (e.g. `MULTI`/`EXEC`, or a Lua script) so a partial failure cannot create a permanent session. Do not place secrets or personally identifying details in key names. Consider cookie security, revocation, rotation, and Redis outage behavior.

### 10.4 Deduplication

For a bounded time window, use `SADD` and check its integer return value (1 means new member, 0 means already present):

```redis
SADD seen:events:2026-10-19 event-abc
EXPIRE seen:events:2026-10-19 172800
```

The `SADD` is atomic; however, the separate `EXPIRE` can race/fail and leave the key without TTL. A Lua script or a transaction can add the member and establish/refresh expiry together. Partition dedup keys by time or business domain to avoid unbounded sets. If a false positive is acceptable and scale is large, evaluate a Bloom filter.

### 10.5 Counters

`INCR` is atomic, but a counter is only as durable as the Redis configuration and replication/failover behavior. If the counter represents a financial balance or legally significant event count, use a transactional system of record and treat Redis as a derived view.

## 11. Redis Streams, Pub/Sub, lists, and Kafka

| Capability | Redis Pub/Sub | Redis Lists | Redis Streams | Kafka |
|---|---|---|---|---|
| Delivery model | Live broadcast to currently subscribed clients | Queue-like push/pop | Append log with IDs and consumer groups | Partitioned durable log with consumer groups |
| Replay | No built-in replay for disconnected subscribers | Not a general replay log | Yes, while entries are retained | Yes, subject to retention and offsets |
| Consumer tracking | No durable acknowledgement | Simple queue operations; reliable patterns require extra care | Pending entries and `XACK` | Offsets and group coordination |
| Ordering | Publish order on a connection/server context; not a durable global history | List order | Stream ID order within a stream | Order within a partition |
| Retention | No message retention | Items remain until popped/removed | Explicit trimming/retention strategy; persistence-dependent | Configured retention policy |
| Best fit | Ephemeral notifications | Simple bounded queues | Redis-native event/work queues | High-volume event streaming and durable pipelines |

Pub/Sub messages published while a subscriber is disconnected are lost. Streams support replay, but they are still constrained by trimming, server resources, persistence and replication configuration. Kafka is generally the stronger choice for large, long-retained, multi-consumer event pipelines and lakehouse ingestion. Redis Streams may fit lower-complexity event workflows where Redis is already operationally central.

Consumer groups do not make side effects exactly-once. If a consumer writes to a database and crashes before `XACK`, the entry can be delivered again. Make handlers idempotent with event IDs, deduplication, upserts, or an outbox/inbox pattern. Track pending-entry age and recovery.

## 12. Python integration with `redis-py`

Install:

```bash
python -m pip install 'redis>=5,<7'
```

Use environment variables rather than hardcoding credentials. `decode_responses=True` decodes byte responses as text; it is convenient for string-only data but may be unsuitable for binary payloads.

```python
from __future__ import annotations

import json
import os
from typing import Any

import redis
from redis.exceptions import RedisError

pool = redis.ConnectionPool.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True,
    max_connections=50,
    socket_connect_timeout=2,
    socket_timeout=2,
    health_check_interval=30,
)
client = redis.Redis(connection_pool=pool)


def cache_set_json(key: str, value: dict[str, Any], ttl_seconds: int) -> None:
    if ttl_seconds <= 0:
        raise ValueError("ttl_seconds must be positive")
    payload = json.dumps(value, separators=(",", ":"), sort_keys=True)
    client.set(key, payload, ex=ttl_seconds)


def cache_get_json(key: str) -> dict[str, Any] | None:
    raw = client.get(key)
    if raw is None:
        return None
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("Cached payload is not a JSON object")
    return value


def safe_get(key: str) -> str | None:
    try:
        return client.get(key)
    except RedisError:
        # Production policy: emit metrics/logs and decide whether to bypass cache.
        # Do not silently swallow errors in a way that hides a persistent outage.
        raise


if __name__ == "__main__":
    client.ping()
    cache_set_json("cache:demo:42", {"id": 42, "name": "Asha"}, 60)
    print(cache_get_json("cache:demo:42"))
```

### 12.1 Resource and serialization choices

Redis stores bytes. Common choices:

- **JSON:** readable and interoperable; relatively verbose and requires encode/decode.
- **MessagePack/CBOR:** compact binary serialization; requires shared schema/versioning discipline.
- **Pickle:** Python-specific and unsafe to deserialize if data can be attacker-controlled; avoid for untrusted/shared cache content.
- **Hash fields:** useful for field-level updates; may be less convenient for versioned nested structures.

Set maximum connections, connect/read timeouts, TLS/authentication as required, and explicit retry budgets. Avoid retrying non-idempotent application actions blindly: a timeout can mean the server executed the command but the response was lost. Redis client libraries provide connection pooling and often retry options, but retry behavior varies by client version and configuration. Verify it and define command idempotency before enabling broad retries.

### 12.2 Batch reads and pipelines

```python
keys = [f"cache:product:{product_id}" for product_id in range(1, 101)]
pipe = client.pipeline(transaction=False)
for key in keys:
    pipe.get(key)
values = pipe.execute()
```

Use a bounded batch size and measure both request latency and response size. In Redis Cluster, a pipeline may be routed to multiple nodes by the client, and cross-slot multi-key commands remain restricted. A pipeline does not remove those constraints.

### 12.3 Local testing versus managed Redis

A local Docker Redis is useful for command practice, tests, and reproducible experiments. It does not reproduce managed-service failover, network latency, IAM integration, TLS defaults, maintenance behavior, backups, scaling, or billing. Use local tests to verify logic and use a controlled staging service to validate operational assumptions. Never run destructive memory, failover, or configuration experiments on a production cache.

## 13. Persistence and durability

Redis can be configured for durable use cases, but persistence is not a complete durability guarantee. The actual recovery point depends on persistence mode, fsync policy, replication acknowledgements, failover behavior, disk health, and backup/restore procedures.

### 13.1 RDB snapshots

RDB writes point-in-time snapshots at configured intervals or on explicit save operations. It can provide compact backups and faster recovery in many workloads, but changes after the latest completed snapshot can be lost if the process or host fails. Snapshotting may create CPU, memory, disk I/O, and copy-on-write memory pressure.

### 13.2 AOF (Append Only File)

AOF records write operations for replay. With `appendfsync always`, each write is synchronized more frequently at a latency cost; `everysec` usually offers a practical compromise with a potential loss window around the last second under certain failures; `no` leaves fsync timing largely to the OS. Exact behavior depends on Redis version and configuration. AOF rewrite compacts the log and has resource implications.

### 13.3 RDB versus AOF

| Property | RDB | AOF |
|---|---|---|
| Recovery | Load a snapshot | Replay logged write operations (may be slower for large logs) |
| Potential lost writes | Since last snapshot | Depends on fsync policy and failure mode |
| File shape | Snapshot | Append log, periodically rewritten |
| Operational considerations | Snapshot CPU/memory/I/O | Log growth, rewrite, fsync latency |

Some deployments enable both. Inspect active settings with permitted configuration/`INFO` commands, and test restore procedures. Replication is not a substitute for backups: accidental deletes can replicate. Backups should be isolated, monitored, and restore-tested.

## 14. Memory, eviction, big keys, and fragmentation

Redis has finite memory. Account for payloads, data-structure metadata, allocator overhead, replication buffers, client buffers, persistence copy-on-write overhead, and operating-system memory—not just the raw value bytes.

Useful inspection commands:

```redis
INFO memory
INFO stats
INFO keyspace
MEMORY USAGE cache:product:42
OBJECT ENCODING cache:product:42
SLOWLOG GET 10
LATENCY LATEST
SCAN 0 MATCH cache:* COUNT 100
```

Command availability and operational permissions vary by service. `SCAN` is safer than `KEYS` for incremental discovery, but it can return duplicates and is not a snapshot. Use `MEMORY USAGE` on representative keys rather than sampling only tiny values.

### 14.1 Eviction policies

Eviction is triggered when Redis reaches the configured `maxmemory` threshold for data subject to the selected policy.

| Policy | Behavior | Typical consideration |
|---|---|---|
| `noeviction` | Rejects writes that need additional memory | Useful when silent key removal is unacceptable; clients must handle write errors. |
| `allkeys-lru` | Evicts least-recently-used approximations among all keys | General-purpose cache when any cached key may be discarded. |
| `allkeys-lfu` | Evicts least-frequently-used approximations among all keys | Can favor frequently accessed items; depends on access distribution. |
| `volatile-lru` | LRU approximation among keys with TTL | Persistent keys are protected; if no eligible key exists, writes may fail. |
| `volatile-ttl` | Prefers keys with the shortest remaining TTL among keys with expiration | Useful when expiring cache keys are expected to be disposable; not the same as LRU. |
| `volatile-lfu` | LFU approximation among expiring keys | Expiring-key subset only. |
| `allkeys-random` / `volatile-random` | Random eviction across all keys / expiring keys | Rarely ideal for skewed cache access patterns. |

`allkeys-lru` uses an approximation rather than tracking exact global LRU for every access. `volatile-ttl` does not mean “remove every expired key first”; expiration and eviction are distinct processes. Under `volatile-*`, keys without TTL are not candidates for eviction.

### 14.2 Big keys and hot keys

A **big key** consumes substantial memory or causes expensive reads/deletes because it contains a huge string, hash, set, list, or sorted set. A **hot key** receives disproportionate traffic. They are different problems, though one key can be both.

- Avoid retrieving huge collections in one command.
- Use incremental scans/iteration where supported and bounded page sizes.
- Delete large collections carefully; `UNLINK` may free memory asynchronously for supported values, while `DEL` can block for large values depending on data type and version.
- Break data into bounded keys if access patterns allow it.
- Use `redis-cli --bigkeys` against an approved non-production or carefully controlled environment; it samples/scans and can still create load.

Fragmentation occurs when allocator/OS memory exceeds the memory occupied by logical values. Check `used_memory`, `used_memory_rss`, and fragmentation-related fields in `INFO memory`. High RSS does not necessarily mean the dataset itself grew by the same amount. Defragmentation availability and behavior depend on build, version, and service; do not turn it on blindly without monitoring.

## 15. Replication, Sentinel, and Cluster

### 15.1 Replication

Redis replication copies primary data to replicas asynchronously in common configurations. A successful write acknowledgement from a primary does not necessarily mean every replica has persisted the write. Replication improves read scaling and failover options, but lag and acknowledged-write loss during failover remain possible depending on timing and configuration.

### 15.2 Sentinel

Sentinel monitors non-clustered Redis primary/replica deployments, discovers topology, and coordinates failover. It does not shard the dataset. Clients must support Sentinel discovery and reconnect after a primary change. Use multiple Sentinel processes in failure domains as documented by the deployment; a single Sentinel process is not a robust quorum.

### 15.3 Redis Cluster

Cluster partitions the keyspace across primary nodes using **16,384 hash slots**. A key maps to a slot, and slots are assigned to primaries. Replicas can be used for failover and optionally reads, subject to client behavior and consistency expectations.

```text
key -> CRC16/hash-tag calculation -> slot 0..16383 -> owning primary
```

Hash tags force related keys into the same slot:

```text
cart:{customer-42}:items
cart:{customer-42}:metadata
```

This enables certain multi-key commands and scripts across these keys because they share a slot. But a broad hash tag can create a hot slot. Most multi-key operations in Cluster require all keys to share a slot; do not assume an arbitrary transaction or script can atomically span different shards.

### 15.4 Resharding and failover

Resharding moves hash slots between primaries; a client may receive `MOVED` or `ASK` redirections during topology changes and must use a Cluster-aware client. Failover promotes a replica when a primary is considered unavailable, but replication is asynchronous and some recent writes may be lost. Test client reconnects, retry behavior, and idempotency. Avoid assuming failover is instantaneous or invisible.

### 15.5 Capacity planning

Estimate:

- Expected key count and average/p95/p99 value size, plus metadata overhead.
- Peak requests/sec and command mix; cost of large ranges and scripts.
- Hit ratio and source database capacity under both normal miss rate and full-cache-loss conditions.
- Memory overhead for replication, clients, persistence fork/copy-on-write, and headroom.
- Data growth, TTL distribution, eviction behavior, replication lag, and recovery time.
- Availability targets and acceptable data loss/staleness.

Use load tests with representative cardinality, skew, value sizes, concurrency, and network topology. Report p50/p95/p99 latency, throughput, error rate, hit ratio, evictions, memory, and source-query load. Do not extrapolate a benchmark from a tiny local dataset to production without qualification.

## 16. Probabilistic structures and ML serving awareness

### 16.1 HyperLogLog versus set

- Set: exact unique count, can enumerate members, memory grows with cardinality.
- HyperLogLog: approximate unique count, cannot enumerate members, memory is bounded and small, with a standard error around 0.81% for typical Redis HyperLogLog behavior.

Use a set when exact membership is needed and the cardinality is manageable. Use HyperLogLog for aggregate unique-visitor estimates where approximation is acceptable. Do not use HyperLogLog to answer “was this exact user seen?”

### 16.2 Bloom filters

Bloom filters save memory for approximate membership. A positive means “possibly present”; a negative means “definitely absent” under normal operation. False positives grow with insertion count and configuration. The RedisBloom module or compatible service is required; validate support before using `BF.*` commands. A Bloom filter can avoid expensive downstream lookups but must not be the sole authority for irreversible business decisions if false positives are unacceptable.

### 16.3 Bitmaps

Bitmaps efficiently represent Boolean state indexed by integer position, e.g. daily active user flags if user IDs are dense and bounded. Sparse, huge IDs can waste space because memory scales with the highest offset, not simply the number of set bits. Consider ID mapping and time partitioning.

### 16.4 ML feature-serving cache and vector awareness

Redis can cache precomputed online features, feature bundles, model metadata, inference results, and rate-limit/serving state. Design keys around entity ID, feature version, and freshness requirements. Avoid silently mixing feature versions or leaking one tenant's features to another. Monitor hit ratio, feature staleness, serialization cost, and tail latency.

Vector search is not implied by core Redis strings/hashes. Vector capabilities depend on Redis version, modules (for example Redis Stack/Redis Query Engine), or the managed provider. Treat it as a separate capability to validate for dimensions, index type, filtering, memory, latency, and availability. Redis as a feature cache does not replace offline feature computation, lineage, or training/serving consistency controls.

## 17. Hands-on lab — `experiments/06_redis/`

Create this directory in the repository:

```text
experiments/06_redis/
├── README.md
├── docker-compose.yml
├── requirements.txt
├── src/
│   ├── cache_aside.py
│   ├── rate_limiter.py
│   ├── leaderboard.py
│   ├── visitor_count.py
│   └── stampede_demo.py
├── scripts/
│   ├── 01-core-types.redis
│   ├── 02-fill-memory.sh
│   └── measure_cache.py
└── results/
    └── README.md   # record measured outputs; do not commit secrets
```

This is the lab layout to create; the lesson does not create those additional files for you.

### 17.1 Setup requirements

- Docker and Docker Compose.
- Python 3.11+ recommended for the lab, with `redis` (`redis-py`) and the database driver appropriate to the chosen source (DuckDB Python package or PostgreSQL driver such as `psycopg`).
- A local Redis instance isolated from production. For the memory/eviction exercise, use a dedicated disposable container.
- A reproducible dataset and fixed query parameters. Record Redis version, source database version, hardware, container limits, concurrency, and run duration.

Minimal `docker-compose.yml` for local command practice:

```yaml
services:
  redis:
    image: redis:7.4
    ports:
      - "6379:6379"
    command: ["redis-server", "--appendonly", "yes"]
    volumes:
      - redis_data:/data
volumes:
  redis_data:
```

This Compose file is a learning baseline, not production hardening. Pin an exact patch/digest for reproducible team use. Do not expose Redis publicly. For destructive eviction testing, use a separate container/configuration with a strict memory limit and no valuable data.

Run:

```bash
mkdir -p experiments/06_redis/{src,scripts,results}
cd experiments/06_redis
docker compose up -d
docker compose exec redis redis-cli PING
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
python -m pip install redis duckdb
```

For PostgreSQL instead of DuckDB, install the relevant driver and configure credentials through environment variables. Never commit secrets.

### Exercise 1 — Practise every core data type

Run and annotate the following in `redis-cli`:

```redis
SET demo:string hello EX 60
GET demo:string
HSET demo:hash name "Asha" level 3
HGET demo:hash name
HGETALL demo:hash
LPUSH demo:list a b c
LRANGE demo:list 0 -1
SADD demo:set a b a
SISMEMBER demo:set b
SCARD demo:set
ZADD demo:zset 20 alice 15 bob
ZREVRANGE demo:zset 0 -1 WITHSCORES
TTL demo:string
SCAN 0 MATCH demo:* COUNT 100
```

Record for each command: purpose, expected return type, stated time complexity, whether it mutates state, whether it is atomic, and any size-dependent cost. Clean up only lab keys with `UNLINK` or `DEL`.

**Expected observation:** Redis returns values immediately for this small local dataset; this is not a performance benchmark. The purpose is to connect each data type to its command semantics and complexity.

**Evaluation:** Explain why `HGETALL` and large `LRANGE` calls can be risky even when the data structure itself is in memory.

### Exercise 2 — Sketch cache-aside for a slow aggregate

Choose one repeatable query such as daily order revenue from PostgreSQL or DuckDB. Write down:

- Query SQL and representative result shape.
- Cache key, serialization format, and TTL (include a reason for the duration).
- Cache hit/miss flow and error policy if Redis is unavailable.
- Invalidation rule after new orders or corrections.
- Maximum acceptable staleness and how it will be measured.

**Evaluation:** Another engineer should be able to infer correctness and stale-data behavior from the design without asking you what the TTL means.

### Exercise 3 — Put Redis in front of a slow aggregate; measure hit ratio and latency

Implement `cache_aside.py` with a function that performs `GET`, executes the aggregate on miss, serializes the result, and writes it with `SET ... EX`. Warm the key, then run a fixed workload containing repeated and unique parameters.

Collect measurements without inventing results:

- `requests_total`, `cache_hits`, `cache_misses`, source-query count.
- Hit ratio = `cache_hits / requests_total` (report undefined if no requests).
- Per-request elapsed time using `time.perf_counter_ns()`; report p50/p95/p99 separately for hits, misses, and total requests.
- Source query latency, Redis errors, and stale-data test outcomes.

Run at least three trials after a documented warm-up. Use the same input distribution and concurrency for baseline (no cache) and cached cases. Save raw measurements and environment metadata in `results/README.md` or a CSV generated by your own script.

**Expected observation:** repeated keys should produce cache hits after the first successful population. Actual latency and hit ratio depend on query, hardware, data, concurrency, and cache-key cardinality; do not assume or fabricate a numerical speedup.

**Evaluation:** Explain how TTL and invalidation affect correctness, and why the average latency alone can hide a poor p99.

### Exercise 4 — Implement and test a sliding-window rate limiter

Use the Lua script from Section 10.1. Call it with a namespaced key such as `rate:{user-42}:orders`, a 60,000 ms window, a configured maximum, and a unique UUID request ID.

Test cases:

1. Fewer than the configured limit: accepted requests return allowed.
2. At the limit: the next new request is rejected.
3. After old timestamps fall outside the window: new requests become eligible.
4. Same request ID submitted twice: document and test your idempotency behavior; the provided simple script should be extended if retries must not count twice.
5. Concurrent requests: verify the limit is not exceeded by racing read-check-write clients.

**Evaluation:** Describe the sorted-set operations' complexity and how key expiry bounds idle state. Explain what changes if you use multiple Redis Cluster shards or multiple independent application regions.

### Exercise 5 — Leaderboard and unique visitor counter

Use a sorted set for leaderboard scores. Test score increment, rank, top 10, tie behavior, and season reset.

For visitors, compare:

```redis
SADD visitors:day:2026-10-19 user-100
SCARD visitors:day:2026-10-19
PFADD visitors_hll:day:2026-10-19 user-100
PFCOUNT visitors_hll:day:2026-10-19
```

Run the same generated IDs through both structures at multiple cardinalities (for example 1k, 10k, and 100k), resetting each structure between trials. Capture `MEMORY USAGE visitors:day:...` and `MEMORY USAGE visitors_hll:day:...` after each insertion batch on the same Redis build and configuration. Record the exact cardinality from the generated input and compare it with `PFCOUNT`; repeat with multiple ID-length distributions if relevant. Avoid comparing the whole-server `INFO memory` delta unless the instance is isolated and background overhead is controlled. A set is exact and enumerable; HyperLogLog is approximate and non-enumerable. Do not compare memory from a tiny sample as if it predicts all cardinalities precisely.

**Evaluation:** State which structure fits a financial or compliance count versus a high-volume analytics estimate.

### Exercise 6 — Reproduce and mitigate a cache stampede

Create a slow loader that sleeps or executes a deliberately expensive aggregate on cache miss. Start many concurrent clients against one expired/missing key. Count simultaneous source queries.

Run two explicitly separated experiments so the mitigation matches the failure mode:

**A. One hot key expires:** compare (1) no protection, (2) per-process single-flight, (3) a short tokenized Redis lock plus bounded wait, and (4) optional stale-while-revalidate. TTL jitter alone does not serialize callers racing on the same key after that key expires.

**B. Many keys expire together:** populate a representative set of keys with identical TTLs, then repeat with randomized TTL jitter. Compare source-query bursts and expiry distribution. This is where jitter can spread synchronized expiry across different keys.

For the lock case, use `SET lock-key token NX PX lease-ms` and compare-and-delete release; never blind-delete. Keep the loader bounded, and demonstrate the behavior when it exceeds the lease. Record source-query count, p95/p99 latency, lock timeouts, errors, and stale responses.

**Expected observation:** single-flight/lock protection should reduce concurrent duplicate work for the tested hot key; jitter can spread expiry across a population of keys but is not a single-key mutual-exclusion mechanism. No mitigation is a universal guarantee.

**Evaluation:** Explain lock lease expiry, owner tokens, retry/fallback, and why a database-side idempotency mechanism may still be required.

### Exercise 7 — Fill memory under `allkeys-lru` and observe evictions

Use a dedicated disposable container. Set a small `maxmemory` and `allkeys-lru` policy through the container's server command/configuration, not a shared service. Confirm settings with `CONFIG GET` if permitted.

Example for an isolated container launched specifically for this lab:

```bash
docker run --rm --name redis-eviction-lab -p 6380:6379 redis:7.4 \
  redis-server --maxmemory 64mb --maxmemory-policy allkeys-lru --save "" --appendonly no
```

Connect to port 6380 and write many keys with controlled value sizes, e.g. generated strings via a Python loop. Sample `INFO memory`, `INFO stats` (`evicted_keys`), and `DBSIZE` periodically. Access a subset repeatedly to create a skewed access pattern, then test whether frequently used keys survive more often than cold keys. LRU is approximate; do not expect a perfectly deterministic victim order. This container intentionally disables persistence and must contain no important data.

**Evaluation:** Explain what the `evicted_keys` counter indicates, how TTL differs from eviction, and why a cache client must treat an evicted key as a miss.

## 18. Operational checklist

Before production rollout, answer:

- What is the source of truth, and what happens when Redis is unavailable?
- Which keys have TTLs? Which keys are intentionally persistent?
- Is memory bounded? What eviction policy applies? What happens when writes cannot be admitted?
- Are key cardinality, payload size, big-key risk, and hot-key skew measured?
- Are Redis errors, hit ratio, p95/p99 latency, evictions, memory, rejected connections, replication lag, and source load monitored?
- Are retries bounded and commands idempotent where retries may repeat work?
- Are credentials, network exposure, TLS, ACLs, and tenant isolation configured?
- Is persistence/backup enabled according to the recovery-point objective, and has restore been tested?
- Has failover and client reconnection been tested in staging?
- Are scripts bounded and all Cluster multi-key operations slot-compatible?
- Is the event/queue retention strategy explicit? Can consumers recover from pending or duplicate work?

## 19. Common mistakes

- Treating Redis as automatically fast regardless of command complexity, payload size, or hot keys.
- Using `KEYS *` in production instead of an incremental strategy such as `SCAN` or a maintained index.
- Omitting TTLs on cache keys and allowing unbounded growth.
- Assuming expiration and eviction are the same mechanism.
- Updating the database and cache without a failure/reconciliation strategy.
- Assuming two separate Redis commands are atomic as a sequence.
- Treating pipelining as a transaction.
- Running a long Lua script that blocks other command execution.
- Implementing a lock with blind `DEL`, no owner token, or an unbounded lease.
- Assuming Redis replication or AOF means no writes can ever be lost.
- Treating Pub/Sub as durable messaging or Streams as an unlimited Kafka replacement.
- Ignoring duplicate delivery and idempotency in queue/event consumers.
- Using a single hot leaderboard or counter key without measuring write contention.
- Using HyperLogLog where exact membership or exact enumeration is required.
- Using Bloom filter membership as a definitive answer when false positives are unacceptable.
- Assuming all Redis-compatible services support the same modules and commands.

## 20. Practice questions

1. Why is `GET` generally fast, and what can make it slow in practice?
2. When would you use a hash rather than a JSON string?
3. Compare list, Stream, and Kafka for a work queue with replay requirements.
4. Why is `HGETALL` risky on an unbounded hash?
5. What is the difference between TTL expiration and eviction?
6. Why does cache-aside require an invalidation strategy?
7. What is a cache stampede, and which mitigation would you use for a high-value aggregate?
8. Compare `SET NX EX`, `MULTI`/`EXEC`, Lua, and pipelining.
9. Why is `SETNX` without expiration dangerous for a lock?
10. How can a Redis Stream consumer process a message twice, and how do you make the side effect idempotent?
11. Compare RDB and AOF in terms of recovery point and operational cost.
12. What does `allkeys-lru` do when Redis reaches `maxmemory`?
13. How are Redis Sentinel and Redis Cluster different?
14. Why do multi-key operations need attention in Cluster?
15. When is HyperLogLog preferable to a set, and what capability is lost?
16. What should you measure before claiming Redis improved application latency?

## 21. Checkpoints

- [ ] Choose the appropriate Redis data structure for a stated access pattern.
- [ ] Explain command complexity and identify dangerous unbounded operations.
- [ ] Set and inspect TTLs and namespace keys consistently.
- [ ] Implement cache-aside with hit/miss metrics and a stated invalidation policy.
- [ ] Protect an expensive cache fill from a stampede without unsafe lock release.
- [ ] Explain atomic commands, scripts, transactions, and pipelining accurately.
- [ ] Implement a sorted-set sliding-window rate limiter and leaderboard.
- [ ] Compare Streams, Pub/Sub, lists, and Kafka for retention and consumer recovery.
- [ ] Explain RDB versus AOF and the actual durability limitations.
- [ ] Diagnose memory growth, big keys, eviction, and hot-key skew.
- [ ] Explain replication, Sentinel, Cluster hash slots, and cross-slot restrictions.
- [ ] Compare exact sets with HyperLogLog and understand Bloom-filter false positives.

## 22. Final self-assessment

Score each statement from 0 to 2: **0** = cannot explain or implement; **1** = can explain with notes; **2** = can implement, test, and justify trade-offs.

| Skill | Score (0–2) |
|---|---:|
| Data structures and complexity | |
| TTL and key lifecycle | |
| Cache-aside, invalidation, stampede protection | |
| Atomicity, scripts, transactions, pipelining | |
| Rate limiter, leaderboard, sessions, deduplication | |
| Python client, pools, serialization, retries | |
| Streams, Pub/Sub, queue reliability | |
| Persistence and recovery-point reasoning | |
| Eviction, memory, big keys, fragmentation | |
| Replication, Sentinel, Cluster, hash slots | |
| Probabilistic structures and ML serving cache | |
| Reproducible measurement and operational readiness | |

**Interpretation:** 20–24 indicates strong practical readiness for this topic; 14–19 means revisit the lowest-scoring sections and repeat the labs; below 14 means repeat the core data structures and cache-aside exercises before advancing. The score is a learning checkpoint, not a certification.

## 23. Technical references and version notes

Use the documentation matching the Redis server and client actually deployed. These official references support the command semantics and operational behavior discussed here:

- [Redis command reference](https://redis.io/docs/latest/commands/) — syntax and command-specific complexity; check the `Since` field before using newer commands.
- [Redis sorted sets](https://redis.io/docs/latest/develop/data-types/sorted-sets/) — sorted-set operations and range complexity.
- [Redis Streams](https://redis.io/docs/latest/develop/data-types/streams/) — consumer groups, pending entries, acknowledgement, and recovery.
- [`XAUTOCLAIM`](https://redis.io/docs/latest/commands/xautoclaim/) — available since Redis Open Source 6.2.0.
- [Redis Cluster specification](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/) — hash slots, routing, and multi-key constraints.
- [Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) — RDB/AOF behavior and configuration.
- [Redis eviction](https://redis.io/docs/latest/develop/reference/eviction/) — `maxmemory` and eviction policy behavior.
- [redis-py documentation](https://redis.readthedocs.io/en/stable/) — Python API, pools, pipelines, and version-specific behavior.

The lesson's Docker examples use Redis 7.4 as a practice baseline, not as a claim that every Redis-compatible managed service has identical features or defaults. Redis 6.2+ is required for `XAUTOCLAIM`; Redis modules such as Bloom filters and vector/search capabilities must be installed or explicitly supported by the target service. Confirm version, ACL permissions, module availability, Cluster behavior, and managed-service restrictions before adopting a command operationally.

## 24. Lab completion record

Record actual values only after running the experiments:

| Experiment | Environment/version | Dataset/workload | Measured results | Interpretation / next change |
|---|---|---|---|---|
| Core data types | | | | |
| Cache-aside aggregate | | | | |
| Sliding-window limiter | | | | |
| Leaderboard and visitors | | | | |
| Stampede protection | | | | |
| `allkeys-lru` eviction | | | | |

Do not paste secrets, credentials, production keys, or sensitive payloads into the report. State limitations and unexpected behavior honestly. The key engineering outcome is not a fabricated speedup; it is a defensible design with measured trade-offs, a failure model, and a repeatable test procedure.
