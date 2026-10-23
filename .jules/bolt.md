## 2024-05-24 - [Avoid `dataclasses.asdict` in deep structures]
**Learning:** `dataclasses.asdict` performs a recursive deep copy, which is unexpectedly slow for objects with deep or complex nested dictionaries (like `evidence` dicts in bridge responses), causing API delays.
**Action:** Replace `asdict(self)` with manual dictionary construction in `to_dict()` methods for performance-critical endpoints like `/doctor`.

## 2024-05-24 - [Reduce iterations in properties]
**Learning:** Computing stats (ok_count, warn_count, worst) using multiple list comprehensions or generators in properties (`self.worst` + sum comprehensions) iterates the same list multiple times, which is inefficient on large lists of checks.
**Action:** Calculate all aggregation metrics in a single pass over the data array during serialization.
