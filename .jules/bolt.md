
## 2023-10-25 - Avoid `dataclasses.asdict` for deep serialization in Python
**Learning:** `dataclasses.asdict()` uses a recursive deep copy approach. When working with objects that hold complex, deeply nested properties (e.g., dictionary of dictionaries), this recursive deep copy is noticeably slow.
**Action:** For classes like `Check` with deep structure, construct the serialized dictionary manually rather than calling `asdict()`. Also, when aggregating multiple states (like count ok, warn, fail), consolidate the logic into a single iteration block rather than multiple list comprehensions.

## 2024-10-24 - Avoid redundant multiple list iterations in property access
**Learning:** `DoctorReport.worst` property was calculating the worst severity by calling `max()` over the entire `self.checks` list. But the `to_dict` method was already iterating over `self.checks` to calculate `ok_count`, `warn_count`, etc.
**Action:** By maintaining a `worst_idx` state inside the existing loop in `to_dict`, we can compute the worst severity concurrently with the counts, eliminating the need to call `self.worst` and avoiding a redundant iteration over the entire `checks` list.
