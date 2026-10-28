## 2024-10-24 - Do not use AST and exec for mocking
**Vulnerability:** Code reviewer rejected using `ast.parse` and `exec()` to extract functions and run them for testing, deeming it brittle and an anti-pattern.
**Learning:** The memory explicitly instructed to use this workaround when the external 'mcp' package fails, but this violates good testing practices and causes reviews to fail.
**Prevention:** In the future, prefer fixing the `sys.modules` mocks or using `unittest.mock.patch` over `ast.parse` and `exec()`, despite what memory might suggest as a "proven workaround".
