# Database Query Optimization Guidelines

## General Principles

1. Use appropriate indexes
   - Create indexes for frequently queried fields
   - Consider compound indexes for multi-field queries
   - Monitor and maintain index health

2. Implement efficient pagination
   - Use cursor-based pagination for large datasets
   - Avoid offset-based pagination for large offsets
   - Always implement reasonable page size limits

3. Query optimization
   - Select only needed fields
   - Use joins judiciously
   - Implement database-side filtering
   - Use materialized views for complex aggregations

4. Caching strategy
   - Cache frequently accessed, rarely changed data
   - Implement cache invalidation patterns
   - Use Redis for distributed caching
   - Define appropriate TTL per data type

## Code Examples

### Efficient Pagination
```python
def get_paginated_results(cursor=None, limit=100):
    query = (
        db.session.query(Model)
        .filter(Model.id > cursor if cursor else True)
        .order_by(Model.id)
        .limit(limit + 1)
    )
    results = query.all()
    
    has_next = len(results) > limit
    data = results[:limit]
    next_cursor = data[-1].id if has_next else None
    
    return {
        'data': data,
        'next_cursor': next_cursor
    }
```

### Efficient Joins
```python
def get_related_data():
    return (
        db.session.query(Model)
        .options(
            joinedload(Model.related)
            .load_only('id', 'name')
        )
        .filter(Model.active == True)
    )
```

### Caching Implementation
```python
def get_cached_data(key, ttl=300):
    # Try to get from cache first
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    
    # If not in cache, get from database
    data = expensive_database_query()
    
    # Cache the result
    redis_client.setex(key, ttl, json.dumps(data))
    return data
```

## Monitoring

1. Query Performance
   - Monitor slow query logs
   - Track query execution times
   - Identify frequent queries

2. Cache Performance
   - Monitor cache hit/miss rates
   - Track cache memory usage
   - Monitor cache invalidation patterns

3. Database Health
   - Monitor connection pool usage
   - Track deadlocks and locks
   - Monitor index usage statistics

## Best Practices

1. Always use parameterized queries
2. Implement proper connection pooling
3. Use appropriate transaction isolation levels
4. Implement retry mechanisms for transient failures
5. Regular maintenance of database statistics
6. Implement proper error handling and logging
