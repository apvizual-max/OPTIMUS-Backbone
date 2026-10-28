# Terms of Service - Sentinel Hermes Google Access

**Effective date:** 27 October 2026
**Applies to:** the "Sentinel Hermes Google Access" OAuth application, used by the local MCP container `Google_Access`.

## 1. What this is

A self-hosted connector that holds a single OAuth grant on one Google account
and exposes Google's APIs to local tools on the machine of the account owner.
It is private tooling for a single user; it is not a public service and not a
multi-tenant platform.

## 2. Your responsibilities

- You authorise the application on your own Google account and you may revoke
  that authorisation at any time from your Google account permissions page.
- You are responsible for what the connected tools do with the data they read,
  in the same way you are responsible for the tools themselves.
- The application requests broad access because the connected tools need it.
  Review the scope list on the Google consent screen before you approve it.

## 3. Availability

The service depends entirely on Google APIs and, for NotebookLM, on ExtendLM.
No uptime, continuity or response commitment is offered. The grant may be
revoked by you, or invalidated by Google.

## 4. No warranty

The application is provided "as is", without warranty of any kind. The author
is not liable for data loss, service interruption, or any indirect damage
arising from the use of connected tools.

## 5. Changes

Material changes to these terms are recorded in the commit history of the
repository that contains this file.

## 6. Contact

`apvizual@gmail.com`
