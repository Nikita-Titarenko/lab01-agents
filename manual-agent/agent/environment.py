"""Caching strategies environment with verified facts.

Sources used for fact verification and the detailed descriptions below:
- Microsoft Learn, "Cache-Aside pattern"
- Microsoft Learn, "Caching guidance for application design"
- Microsoft Learn, "No Caching antipattern"
- AWS Prescriptive Guidance, "Database Caching Strategies Using Redis"
- Martin Kleppmann, "Designing Data-Intensive Applications" (caching and consistency chapters)

Sources used for implementation/library mappings below:
- Spring Framework Reference and Spring Data Redis Reference
- Caffeine Wiki
- Ehcache 3 documentation
- Apache Ignite documentation
- NCache documentation
- Hazelcast documentation
- Microsoft Learn, ASP.NET Core caching guidance
- Django, SQLAlchemy, redis-py, cachetools, aiocache, dogpile.cache documentation
- Celery, RQ, APScheduler documentation

The descriptions are intentionally conservative: they reflect documented design patterns and trade-offs
commonly described in the sources above rather than unverified vendor-specific claims.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

NOT_FOUND = "NOT_FOUND"


@dataclass(frozen=True)
class CachingStrategy:
    identifier: str
    title: str
    description: str
    read_path: str
    write_path: str
    strengths: str
    implementations: dict[str, dict[str, str]]
    tradeoffs: dict[str, str]
    sources: list[str]
    implementation_sources: dict[str, list[str]]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


STRATEGIES: dict[str, CachingStrategy] = {
    "cache_aside": CachingStrategy(
        identifier="cache_aside",
        title="Cache-Aside",
        description=(
            "Cache-Aside is a lazy-loading pattern in which the application checks the cache first and, on a miss, "
            "reads the value from the primary data store and then writes it into the cache. This is the core model "
            "described by Microsoft Learn in the Cache-Aside pattern and is often used as a baseline for read-heavy "
            "systems where the cache is filled only when data is actually needed."
        ),
        read_path="On a cache miss, the application reads the value from the database or object store and then populates the cache for future requests.",
        write_path="Writes go to the primary store first; the application or cache invalidation logic must then decide whether to refresh or evict the cached entry.",
        strengths="This pattern is simple to adopt, works well for skewed read-heavy workloads, and avoids caching data that is never accessed.",
        implementations={
            "java": {
                "Spring Cache + Caffeine": "Use @Cacheable/@CacheEvict with CaffeineCacheManager for in-process lazy loading.",
                "Spring Cache + Redis": "Use RedisCacheManager for distributed cache-aside with explicit key eviction on writes.",
            },
            "c#": {
                "IMemoryCache (.NET)": "Application-first cache-aside in process memory with manual miss handling and eviction.",
                "IDistributedCache (.NET) + Redis": "Distributed cache-aside for multi-instance services with explicit invalidation after writes.",
            },
            "python": {
                "cachetools": "Decorator-based or explicit in-memory cache-aside for read-heavy paths.",
                "redis-py": "Manual get/set cache-aside with Redis and application-managed TTL/invalidation.",
            },
        },
        tradeoffs={
            "staleness_risk": "The cache can serve stale data if the data store changes and the application does not invalidate or refresh the entry promptly.",
            "consistency_cost": "Cache invalidation and refresh logic move into the application layer, which increases the burden of read-after-write consistency.",
            "cache_miss_penalty": "Cold-cache and miss-heavy workloads incur an initial database read before the next requests benefit from the cache.",
            "write_complexity": "The application must coordinate write paths, invalidation, and cache warming or eviction decisions.",
        },
        sources=[
            "Microsoft Learn, 'Cache-Aside pattern'",
            "Microsoft Learn, 'Caching guidance for application design'",
            "AWS Prescriptive Guidance, 'Database Caching Strategies Using Redis'",
        ],
        implementation_sources={
            "java": [
                "Spring Framework Reference, 'Cache Abstraction'",
                "Caffeine Wiki",
                "Spring Data Redis Reference",
            ],
            "c#": [
                "Microsoft Learn, 'In-memory caching in ASP.NET Core'",
                "Microsoft Learn, 'Distributed caching in ASP.NET Core'",
                "StackExchange.Redis documentation",
            ],
            "python": [
                "cachetools documentation",
                "redis-py documentation",
            ],
        },
    ),
    "read_through": CachingStrategy(
        identifier="read_through",
        title="Read-Through",
        description=(
            "Read-Through delegates cache misses to the cache layer itself: the application asks the cache for a key, and "
            "if the key is absent the cache fetches the value from the backing store and stores it. The design is commonly "
            "discussed in caching architecture guidance because it centralizes data-loading logic and reduces application-side "
            "cache management code."
        ),
        read_path="The cache performs the load from the backing store and stores the value before returning it to the caller.",
        write_path="Writes are usually still persisted in the primary store, while the cache may be updated or refreshed as part of the surrounding architecture.",
        strengths="The application code stays simpler because loading logic is centralized in the cache layer and read operations can remain consistent in one place.",
        implementations={
            "java": {
                "Ehcache 3 CacheLoaderWriter": "Read-through via CacheLoaderWriter to load values on misses from the backing store.",
                "Apache Ignite Read-Through": "Configure CacheStore with read-through semantics in Ignite caches.",
            },
            "c#": {
                "FusionCache": "Read-through style factory delegates with fail-safe and stampede protection.",
                "CacheManager.Core": "Read-through with layered caches and custom handle providers.",
            },
            "python": {
                "dogpile.cache": "Region.get_or_create provides read-through-like miss loading.",
                "aiocache": "Read-through behavior with decorators and async backend loaders.",
            },
        },
        tradeoffs={
            "dependency_on_cache_logic": "The cache component must understand how to load and manage missing entries, which increases cache-layer complexity.",
            "invalidation_dependency": "If the backing store changes outside the cache path, the cache still needs a valid invalidation or refresh strategy.",
            "single_point_of_logic": "The cache becomes a critical part of the read path, so cache bugs or failures can affect a large portion of read traffic.",
            "write_path_tension": "This pattern does not automatically solve the write side; the design still needs a coherent strategy for mutation and consistency.",
        },
        sources=[
            "Microsoft Learn, 'Caching guidance for application design'",
            "AWS Prescriptive Guidance, 'Database Caching Strategies Using Redis'",
            "Martin Kleppmann, 'Designing Data-Intensive Applications' (caching and consistency chapters)",
        ],
        implementation_sources={
            "java": [
                "Ehcache 3 documentation, 'CacheLoaderWriter'",
                "Apache Ignite documentation, 'Read-Through and Write-Through'",
            ],
            "c#": [
                "FusionCache documentation",
                "CacheManager.Core documentation",
            ],
            "python": [
                "dogpile.cache documentation",
                "aiocache documentation",
            ],
        },
    ),
    "write_through": CachingStrategy(
        identifier="write_through",
        title="Write-Through",
        description=(
            "Write-Through writes data to the cache and the primary store in the same operation so the cached value remains "
            "fresh after a successful write. This makes the cache a write-aligned read source and is often used when the "
            "system prioritizes read freshness over lower write latency."
        ),
        read_path="After a write succeeds, subsequent reads can hit the updated cache entry without requiring an immediate read-through from the database.",
        write_path="The write request is sent to the cache layer, which synchronously persists the change to the backing store before acknowledging the operation.",
        strengths="This pattern keeps cached values aligned with committed data and reduces the chance that a client reads a stale value after a write.",
        implementations={
            "java": {
                "Ehcache 3 CacheLoaderWriter": "Write-through by synchronously writing through CacheLoaderWriter to the system of record.",
                "Apache Ignite Write-Through": "CacheStore-backed write-through with transactional options.",
            },
            "c#": {
                "NCache Write-Through Provider": "Provider model for synchronous cache-to-database writes.",
                "Hazelcast .NET Client + MapStore": "Write-through with MapStore semantics configured on Hazelcast cluster side.",
            },
            "python": {
                "dogpile.cache + SQLAlchemy hook": "Application-enforced synchronous write-through orchestration.",
                "Django cache framework + custom repository layer": "Persist then update cache in one write transaction path.",
            },
        },
        tradeoffs={
            "consistency_cost": "Each write must be committed to both the cache and the primary store, which increases the cost of maintaining strong read-after-write consistency.",
            "write_latency": "Each write incurs the cost of persisting to both cache and primary storage, which increases the latency of the critical write path.",
            "reduced_write_throughput": "The synchronous write to the primary store can reduce throughput under heavy write workloads.",
            "cache_write_overhead": "Every mutation must be applied to the cache, which adds operational cost and can amplify write pressure on cache nodes.",
            "complexity_under_failures": "If the cache or backing store fails in the middle of the write, the system needs careful failure-handling and retry logic.",
        },
        sources=[
            "Microsoft Learn, 'Caching guidance for application design'",
            "AWS Prescriptive Guidance, 'Database Caching Strategies Using Redis'",
            "Martin Kleppmann, 'Designing Data-Intensive Applications' (caching and consistency chapters)",
        ],
        implementation_sources={
            "java": [
                "Ehcache 3 documentation, 'Write-Through Caching'",
                "Apache Ignite documentation, 'Read-Through and Write-Through'",
            ],
            "c#": [
                "NCache documentation, 'Write-through Caching'",
                "Hazelcast documentation, 'MapStore/MapLoader'",
            ],
            "python": [
                "dogpile.cache documentation",
                "Django documentation, 'Caching framework'",
            ],
        },
    ),
    "write_behind": CachingStrategy(
        identifier="write_behind",
        title="Write-Behind",
        description=(
            "Write-Behind accepts writes in the cache first and delays propagation to the primary store. This pattern is "
            "used to absorb bursts, reduce perceived latency, and improve write throughput when a small amount of eventual "
            "consistency is acceptable."
        ),
        read_path="Recent values can be read from cache immediately, even before the database reflects the most recent change.",
        write_path="The cache acknowledges the write and later flushes or batches the update to the backing store asynchronously.",
        strengths="This pattern reduces perceived write latency and can smooth spikes by batching writes to the primary store.",
        implementations={
            "java": {
                "Hazelcast MapStore write-behind": "Configure write-delay-seconds and batching for async persistence.",
                "Apache Ignite write-behind store": "Enable write-behind buffering and flush settings in CacheStore.",
            },
            "c#": {
                "NCache write-behind": "Asynchronous write-behind queue with retries and batch commits.",
                "Redis + background worker": "Custom queue worker persists buffered writes to the source of truth.",
            },
            "python": {
                "Celery + Redis": "Accept writes quickly, then persist asynchronously via Celery tasks.",
                "RQ + redis-py": "Queue write operations and flush to DB out-of-band.",
            },
        },
        tradeoffs={
            "data_loss_risk": "If the cache fails before persistence, updates may be lost unless a durable queue or backup mechanism is in place.",
            "eventual_consistency": "Readers may see recent data in the cache but not yet in the primary store, which requires application-level tolerance for stale reads.",
            "operational_complexity": "The system must track pending writes, retries, and recovery after crashes or partial persistence.",
            "monitoring_overhead": "The team must monitor write lag and queue health to avoid stale or dropped updates.",
        },
        sources=[
            "AWS Prescriptive Guidance, 'Database Caching Strategies Using Redis'",
            "Microsoft Learn, 'Caching guidance for application design'",
            "Martin Kleppmann, 'Designing Data-Intensive Applications' (eventual consistency chapters)",
        ],
        implementation_sources={
            "java": [
                "Hazelcast documentation, 'MapStore and Write-Behind'",
                "Apache Ignite documentation, 'Write-Behind Caching'",
            ],
            "c#": [
                "NCache documentation, 'Write-behind Cache'",
                "StackExchange.Redis documentation",
            ],
            "python": [
                "Celery documentation",
                "RQ documentation",
                "redis-py documentation",
            ],
        },
    ),
    "write_around": CachingStrategy(
        identifier="write_around",
        title="Write-Around",
        description=(
            "Write-Around bypasses the cache on write and stores the new value directly in the primary store. This pattern "
            "is useful when write-heavy workloads create lots of one-off values that are unlikely to be read again soon, "
            "because it avoids cache pollution and eviction churn."
        ),
        read_path="When a later read happens, the cache misses and the application loads the value from the primary store, which may cause the cache to fill only for genuinely hot data.",
        write_path="The write is sent directly to the primary store without populating the cache, reducing cache churn for infrequently accessed keys.",
        strengths="This pattern prevents cache pollution from values that are written once and never read again, and it is often attractive for write-heavy or bursty workloads.",
        implementations={
            "java": {
                "Spring Data JPA + Spring Cache": "Bypass cache on writes and rely on cache-aside load during subsequent reads.",
                "Redisson + repository layer": "Write directly to DB, populate Redis only from read path.",
            },
            "c#": {
                "EF Core + IDistributedCache": "Persist writes directly through EF Core and fill cache only in query handlers.",
                "Dapper + Redis": "Command path bypasses cache; query path caches hot records.",
            },
            "python": {
                "SQLAlchemy + redis-py": "Write directly to DB and load cache lazily on first read.",
                "Django ORM + Django cache": "Avoid cache writes in save path and cache only in selected read views.",
            },
        },
        tradeoffs={
            "cold_reads": "The first read after a write is often slower because the cache does not contain the new value yet.",
            "cache_miss_frequency": "Hot keys may still miss repeatedly if the system does not proactively warm the cache after the next read.",
            "write_side_inefficiency": "The pattern avoids cache write overhead but also loses some of the latency benefits on read-after-write access patterns.",
            "limited_reuse": "It is less suitable when many writes are followed by immediate reads of the same data.",
        },
        sources=[
            "Microsoft Learn, 'Caching guidance for application design'",
            "AWS Prescriptive Guidance, 'Database Caching Strategies Using Redis'",
            "Microsoft Learn, 'No Caching antipattern'",
        ],
        implementation_sources={
            "java": [
                "Spring Cache documentation",
                "Spring Data JPA documentation",
                "Redisson documentation",
            ],
            "c#": [
                "Microsoft Learn, 'Distributed caching in ASP.NET Core'",
                "Entity Framework Core documentation",
                "Dapper documentation",
            ],
            "python": [
                "SQLAlchemy documentation",
                "Django documentation, 'Caching framework'",
                "redis-py documentation",
            ],
        },
    ),
    "refresh_ahead": CachingStrategy(
        identifier="refresh_ahead",
        title="Refresh-Ahead",
        description=(
            "Refresh-Ahead proactively refreshes cached entries before expiration, based on expected future access or a "
            "predictive refresh policy. This is useful for hot keys where the cost of a miss is high and the system can "
            "afford to precompute or fetch replacements before the entry expires."
        ),
        read_path="The cache refreshes hot keys before expiry so that future reads continue to observe low-latency cache hits.",
        write_path="Refresh behavior is usually combined with an underlying write strategy, and the refresh is triggered by expiry or access heuristics rather than only by explicit writes.",
        strengths="This pattern reduces latency spikes for frequently accessed keys and helps keep hot entries warm without waiting for a miss to trigger a fetch.",
        implementations={
            "java": {
                "Caffeine refreshAfterWrite": "Automatic asynchronous refresh of hot keys using refreshAfterWrite policy.",
                "Spring @Scheduled + Redis": "Periodic prefetch jobs refresh frequently requested Redis keys.",
            },
            "c#": {
                "FusionCache soft/hard timeout": "Background refresh with fail-safe serving and eager refresh options.",
                "IHostedService + IDistributedCache": "Scheduled workers refresh critical keys before TTL expiration.",
            },
            "python": {
                "aiocache + APScheduler": "Schedule proactive refresh coroutines for hot cache keys.",
                "Celery beat + Redis": "Periodic tasks refresh key sets ahead of expiration.",
            },
        },
        tradeoffs={
            "predictive_waste": "The system may refresh data that is never requested again, which increases unnecessary compute and network work.",
            "heuristic_complexity": "The refresh policy depends on workload understanding, access forecasting, and TTL tuning.",
            "operational_cost": "The system must dedicate capacity to background refreshes, which raises operational cost for large or highly dynamic datasets.",
            "stale_window_risk": "If the prediction is wrong, the cache may still experience misses or serve data that is refreshed too late.",
            "resource_overhead": "The system must dedicate capacity to background refreshes, which raises operational cost for large or highly dynamic datasets.",
        },
        sources=[
            "Microsoft Learn, 'Caching guidance for application design'",
            "AWS Prescriptive Guidance, 'Database Caching Strategies Using Redis'",
            "Martin Kleppmann, 'Designing Data-Intensive Applications' (caching and expiration design)",
        ],
        implementation_sources={
            "java": [
                "Caffeine Wiki, 'refreshAfterWrite'",
                "Spring Framework documentation, '@Scheduled'",
                "Spring Data Redis Reference",
            ],
            "c#": [
                "FusionCache documentation",
                "Microsoft Learn, 'Background tasks with hosted services in ASP.NET Core'",
                "Microsoft Learn, 'Distributed caching in ASP.NET Core'",
            ],
            "python": [
                "aiocache documentation",
                "APScheduler documentation",
                "Celery documentation",
            ],
        },
    ),
}

ALIASES = {
    "cache aside": "cache_aside",
    "cache-aside": "cache_aside",
    "cacheaside": "cache_aside",
    "read through": "read_through",
    "read-through": "read_through",
    "writethrough": "write_through",
    "write through": "write_through",
    "write-through": "write_through",
    "writebehind": "write_behind",
    "write behind": "write_behind",
    "write-behind": "write_behind",
    "writearound": "write_around",
    "write around": "write_around",
    "write-around": "write_around",
    "refresh ahead": "refresh_ahead",
    "refresh-ahead": "refresh_ahead",
    "refreshahead": "refresh_ahead",
}

LANGUAGE_ALIASES = {
    "java": "java",
    "c#": "c#",
    "csharp": "c#",
    "cs": "c#",
    "python": "python",
    "py": "python",
}


def normalize_strategy_name(name: str) -> str:
    normalized = " ".join(name.strip().lower().replace("_", " ").split())
    return ALIASES.get(normalized, normalized.replace(" ", "_"))


def normalize_language_name(name: str) -> str:
    normalized = " ".join(name.strip().lower().split())
    return LANGUAGE_ALIASES.get(normalized, normalized)


def _general_method(strategy_name: str) -> dict[str, object] | str:
    """Return the full verified record for one caching strategy."""

    normalized_name = normalize_strategy_name(strategy_name)
    strategy = STRATEGIES.get(normalized_name)
    if strategy is None:
        return NOT_FOUND
    return strategy.to_dict()


def lookup_caching_strategy(strategy_name: str) -> dict[str, object] | str:
    """Return the public strategy record without implementation catalogs."""

    result = _general_method(strategy_name)
    if result == NOT_FOUND:
        return NOT_FOUND

    return {
        "identifier": result["identifier"],
        "title": result["title"],
        "description": result["description"],
        "read_path": result["read_path"],
        "write_path": result["write_path"],
        "strengths": result["strengths"],
        "tradeoffs": result["tradeoffs"],
        "sources": result["sources"],
    }


def get_implementations(strategy_name: str, language: str) -> dict[str, object] | str:
    """Return language-specific implementations and their sources for a strategy."""

    result = _general_method(strategy_name)
    if result == NOT_FOUND:
        return NOT_FOUND

    normalized_language = normalize_language_name(language)
    strategy_implementations = result["implementations"]
    if normalized_language not in strategy_implementations:
        return NOT_FOUND

    return {
        "identifier": result["identifier"],
        "title": result["title"],
        "language": normalized_language,
        "implementations": strategy_implementations[normalized_language],
        "implementation_sources": result["implementation_sources"][normalized_language],
        "sources": result["sources"],
    }


def summarize_environment() -> str:
    names = ", ".join(strategy.title for strategy in STRATEGIES.values())
    return f"Available caching strategies: {names}."