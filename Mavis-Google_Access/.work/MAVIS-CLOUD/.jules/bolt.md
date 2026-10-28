## 2025-02-16 - [Optimize Gmail API modifications]
**Learning:** Sequential calls to `messages.modify` inside loops for each email lead to excessive API quota consumption (costing 5 units per operation) and slow execution time.
**Action:** Always group emails by their target labels/modifications and use `messages.batchModify` in batches (up to 1000 messages) to drastically reduce quota usage and speed up processing.

## 2025-02-16 - [Optimize RegExp recompilation in hot loops]
**Learning:** Instantiating new `RegExp` objects inside heavily repeated utility functions (like `hasWord` used in scoring and filtering text loops) leads to significant performance degradation. The Javascript engine has to parse and compile the regex syntax on every call.
**Action:** Always memoize and cache compiled `RegExp` objects (using `Map` or an object literal) so they are created only once per unique pattern when operating in hot loops.
## 2026-21-26 - Batch HTTP Requests Optimization
**Learning:** Converting multiple individual API requests into a single HTTP multiplexed batch request significantly reduces latency and API quota overhead.
**Action:** Always use batch endpoints (e.g. multipart/mixed) for bulk operations when supported by the provider, instead of parallelizing with `Promise.all(batch.map())`.
