## 2024-05-24 - Database Aggregation Queries
**Learning:** Multiple scalar aggregations (`count()`, `sum()`, `avg()`) on the same table can easily become a hidden bottleneck, acting similarly to an N+1 query issue since each invokes a separate database roundtrip. In ORMs like SQLAlchemy, it's a common anti-pattern to call these separately.
**Action:** When computing multiple statistics for a single entity type, always combine them into a single `.with_entities(func.count(), func.sum(), func.avg())` query to reduce database network I/O.
