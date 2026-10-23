
## 2023-10-25 - Avoid `dataclasses.asdict` for deep serialization in Python
**Learning:** `dataclasses.asdict()` uses a recursive deep copy approach. When working with objects that hold complex, deeply nested properties (e.g., dictionary of dictionaries), this recursive deep copy is noticeably slow.
**Action:** For classes like `Check` with deep structure, construct the serialized dictionary manually rather than calling `asdict()`. Also, when aggregating multiple states (like count ok, warn, fail), consolidate the logic into a single iteration block rather than multiple list comprehensions.
