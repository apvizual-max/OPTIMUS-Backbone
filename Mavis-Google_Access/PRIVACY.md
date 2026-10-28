# Privacy Policy - Sentinel Hermes Google Access

**Effective date:** 27 October 2026
**Applies to:** the "Sentinel Hermes Google Access" OAuth application (Google Cloud project `gen-lang-client-0284509562`, OAuth client `Sentinel Hermes CLI`), used by the local MCP container `Google_Access`.

## What this application accesses

The application accesses your Google account **only for the account that
authorises it** (`apvizual@gmail.com`). It holds a single OAuth grant with the
scopes listed on the Google consent screen, which cover: Drive, Gmail, Calendar,
Google Docs, Sheets, Slides, Forms, Tasks, Apps Script, Photos, Books, YouTube,
Contacts and your basic profile information.

## What it does with the data

- The data is read and written **only by instructions you or your own local
  tools give it**. The container holds no copy of your data: it queries the
  Google API live and returns the result to whoever asked.
- The credential (a refresh token) is stored **locally on your own machine**, in
  a file that is never published and never placed inside a container image.
- Nothing is sold, shared or sent to any third party. The application talks
  directly to Google APIs and to ExtendLM.
- Access can be revoked at any time at
  <https://myaccount.google.com/permissions> - revoking it immediately stops
  the container from accessing your account.

## Retention

No copies are retained by the application itself. Local diagnostic files
(`data/last-probe.txt`, `data/last-service-probe.txt`) contain counters,
status codes and service names - not message bodies, not document contents.

## Contact

Questions: `apvizual@gmail.com`
