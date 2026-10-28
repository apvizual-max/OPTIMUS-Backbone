# Runs — mavis-skill-google-keep-sites

Append-only. Every entry is one run of this skill, with its measured numbers.
A correction is a NEW entry that references the old one; no entry is ever
rewritten or removed.

| when | status | task | outcome |
|---|---|---|---|
| 2026-10-28T00:38:46.068Z | success | created the member + its verifier; measured both refusals live | verifier exit 0: auth/keep and auth/sites absent from FULL_SCOPES, both tools still present, doctor EXPECTED_REFUSED=[keep,sites], live probe reports STATUS=REFUSED for both (403 PERMISSION_DENIED / 404) |
| 2026-10-28T01:16:16.593Z | success | re-measured the two refused services | VERDICT=PASS; keep -> 403 scope inexistent, sites -> 404 API retired; both absent from FULL_SCOPES; both reported as REFUSED, never as OK |
