// Google_Access - MCP server (Streamable HTTP), zero dependencies.
//
// WHY IT EXISTS
// -------------
// Popy: "AVEM NEVOEI DE AUTENTIFICARE PERMANENTA! ... sa poti te loghezi o
// data si tii inte mereu". The re-consent loop on this machine was never a
// Google problem: it was that every Google MCP server kept its OWN credential
// store, and a dead grant in one store looked exactly like "sign in again".
//
// So this container owns ONE credential (a refresh token in a mounted volume)
// and mints short-lived access tokens from it, forever, without consent.
// The refresh token is the only durable secret; it is never in the image.
//
// It is a MODULAR surface: one MCP endpoint, many tools, one credential.
//
// The scope of the current grant is what Google granted at consent time:
// drive, gmail.modify, calendar, documents, spreadsheets, presentations,
// forms. Tools that need a scope outside that set (photos, tasks, script,
// chat, youtube, books) DO NOT silently fail: they report the missing scope
// and point at google_scope_upgrade, which prints the one consent URL that
// widens everything in a single click.
//
// Two scopes were REMOVED from the widening set on measured grounds:
//   - https://www.googleapis.com/auth/sites -> the Google Sites API was
//     retired; the scope is no longer in Google's scope registry, so asking
//     for it fails the WHOLE consent request with invalid_scope.
//   - https://www.googleapis.com/auth/keep  -> Google publishes no grantable
//     user OAuth scope for the Keep API (workspace-admin only), so it is
//     rejected as invalid for the same reason.
// One invalid scope invalidates all 28 others. Verified against the
// authoritative discovery documents and against the live consent screen.
//
// ASCII ONLY. Runs on node:22-slim.

import http from "node:http";
import fs from "node:fs";
import path from "node:path";

const DATA_DIR = process.env.GA_DATA_DIR || "/data";
const CRED_FILE = path.join(DATA_DIR, "credentials.json");
const REAUTH_FLAG = path.join(DATA_DIR, "REAUTH_REQUIRED");
// Measured defect 2026-10-27: the fallback literal was 8765, a port already
// owned on this host by a foreign process (python, service "hc-backend").
// The image sets GA_PORT explicitly, so this literal was a second source of
// truth about the same thing; it now matches the Dockerfile default.
const PORT = Number(process.env.GA_PORT || 8766);
const HOST = process.env.GA_HOST || "127.0.0.1";

const OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token";
const EXTENDLM_MCP_URL = process.env.GA_EXTENDLM_URL || "https://mcp.extendlm.com/mcp";

// ---------------------------------------------------------------------------
// ExtendLM access token: minted, refreshed, and persisted in the volume.
//
// The access token from the authorization code expires in about three hours.
// Without a refresh path, the whole NotebookLM capability dies silently at
// that moment - the tool would start answering 401. The refresh token lives
// in the same volume file, so renewal is code, not a human action.
// ---------------------------------------------------------------------------
const EXTENDLM_REFRESH_SKEW_MS = 120000; // renew two minutes before expiry

function extendlmConfigPath() {
  return path.join(DATA_DIR, "extendlm.json");
}

function readExtendlmConfig() {
  try {
    return JSON.parse(fs.readFileSync(extendlmConfigPath(), "utf8"));
  } catch {
    return null;
  }
}

async function refreshExtendlmToken(cfg) {
  if (!cfg || !cfg.refresh_token || !cfg.token_endpoint || !cfg.client_id) {
    throw new Error(
      "EXTENDLM_NO_REFRESH: " + extendlmConfigPath() + " has no refresh_token/token_endpoint/client_id."
    );
  }
  const res = await fetch(cfg.token_endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      Accept: "application/json",
    },
    body: new URLSearchParams({
      grant_type: "refresh_token",
      refresh_token: cfg.refresh_token,
      client_id: cfg.client_id,
    }).toString(),
  });
  const text = await res.text();
  if (!res.ok) {
    throw new Error("EXTENDLM_REFRESH_HTTP_" + res.status + ": " + text.slice(0, 200));
  }
  const j = JSON.parse(text);
  const now = Date.now();
  const next = {
    ...cfg,
    token: j.access_token,
    access_token: j.access_token,
    // The server may rotate the refresh token; keep the new one when it sent one.
    refresh_token: j.refresh_token || cfg.refresh_token,
    token_type: j.token_type || cfg.token_type || "Bearer",
    scope: j.scope || cfg.scope,
    expires_at: j.expires_in ? now + Number(j.expires_in) * 1000 : null,
    refreshed_at: new Date(now).toISOString(),
  };
  const tmp = extendlmConfigPath() + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify(next, null, 2), "utf8");
  fs.renameSync(tmp, extendlmConfigPath());
  return next;
}

async function extendlmAccessToken(force) {
  const cfg = readExtendlmConfig();
  if (!cfg || !cfg.token) {
    throw new Error(
      "NO_EXTENDLM_TOKEN: put {\"token\":\"...\"} in " + extendlmConfigPath() + " on the host. Run extendlm-provision.mjs and authorize in the browser."
    );
  }
  const expiresAt = cfg.expires_at ? Number(cfg.expires_at) : 0;
  const expired = !expiresAt || Date.now() >= expiresAt;
  const stale = expired || Date.now() >= expiresAt - EXTENDLM_REFRESH_SKEW_MS;
  // The ExtendLM refresh token is ROTATED by the server: a new refresh token
  // invalidates the old one. Two instances refreshing from the same copy
  // would fight, and the loser would break the winner. So the instance that
  // owns the token refreshes; every other instance only consumes a snapshot
  // (GA_EXTENDLM_NO_REFRESH=1 - that is the Cloud).
  const noRefresh = process.env.GA_EXTENDLM_NO_REFRESH === "1";
  if (force || stale) {
    if (noRefresh) {
      if (expired) {
        throw new Error(
          "EXTENDLM_TOKEN_EXPIRED_NO_REFRESH: this instance must not rotate the shared refresh token (GA_EXTENDLM_NO_REFRESH=1). The owner instance has to publish a fresh snapshot."
        );
      }
      return cfg.token;
    }
    if (cfg.refresh_token && cfg.token_endpoint && cfg.client_id) {
      try {
        return (await refreshExtendlmToken(cfg)).token;
      } catch (e) {
        // A token that is still valid does not need a renewal to work.
        if (force || expired) throw e;
      }
    } else if (force) {
      throw new Error(
        "EXTENDLM_NO_REFRESH: " + extendlmConfigPath() + " has no refresh_token - re-authorize with extendlm-provision.mjs."
      );
    }
  }
  return cfg.token;
}

// ---------------------------------------------------------------------------
// API hosts - ONE source of truth, measured from the discovery documents.
//
// Measured defect 2026-10-27: a single "https://www.googleapis.com" base made
// 8 of 14 services answer 404. Each API has its own host:
//   drive/calendar/books -> www.googleapis.com
//   gmail -> gmail.googleapis.com      tasks -> tasks.googleapis.com
//   docs -> docs.googleapis.com        sheets -> sheets.googleapis.com
//   slides -> slides.googleapis.com    forms -> forms.googleapis.com
//   photoslibrary -> photoslibrary.googleapis.com
//   script -> script.googleapis.com    chat -> chat.googleapis.com
//   youtube -> youtube.googleapis.com  people -> people.googleapis.com
//   keep -> keep.googleapis.com        sites -> sites.googleapis.com
const API_BASE = {
  drive: "https://www.googleapis.com",
  gmail: "https://gmail.googleapis.com",
  calendar: "https://www.googleapis.com",
  docs: "https://docs.googleapis.com",
  sheets: "https://sheets.googleapis.com",
  slides: "https://slides.googleapis.com",
  forms: "https://forms.googleapis.com",
  photoslibrary: "https://photoslibrary.googleapis.com",
  photospicker: "https://photospicker.googleapis.com",
  books: "https://www.googleapis.com",
  tasks: "https://tasks.googleapis.com",
  keep: "https://keep.googleapis.com",
  sites: "https://sites.googleapis.com",
  script: "https://script.googleapis.com",
  chat: "https://chat.googleapis.com",
  youtube: "https://youtube.googleapis.com",
  people: "https://people.googleapis.com",
};


// The full set Popy asked for: everything Google that is not Google Cloud.
// Used ONLY when generating a widening consent URL - never to widen silently.
const FULL_SCOPES = [
  "openid",
  "https://www.googleapis.com/auth/userinfo.email",
  "https://www.googleapis.com/auth/userinfo.profile",
  "https://www.googleapis.com/auth/drive",
  "https://www.googleapis.com/auth/drive.readonly",
  "https://www.googleapis.com/auth/drive.appdata",
  "https://www.googleapis.com/auth/gmail.readonly",
  "https://www.googleapis.com/auth/gmail.modify",
  "https://www.googleapis.com/auth/gmail.compose",
  "https://www.googleapis.com/auth/gmail.send",
  "https://www.googleapis.com/auth/gmail.settings.basic",
  "https://www.googleapis.com/auth/calendar",
  "https://www.googleapis.com/auth/calendar.events",
  "https://www.googleapis.com/auth/documents",
  "https://www.googleapis.com/auth/spreadsheets",
  "https://www.googleapis.com/auth/presentations",
  "https://www.googleapis.com/auth/forms.body",
  "https://www.googleapis.com/auth/forms.responses.readonly",
  "https://www.googleapis.com/auth/photoslibrary.readonly",
  "https://www.googleapis.com/auth/photoslibrary.appendonly",
  "https://www.googleapis.com/auth/photoslibrary",
  "https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata",
  "https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata",
  // The Photo Picker API is the documented path to library photos after the
  // 2025-03-31 scope removal: the user picks, the API hands the picks over.
  "https://www.googleapis.com/auth/photospicker.mediaitems.readonly",
  "https://www.googleapis.com/auth/books",
  "https://www.googleapis.com/auth/tasks",
  "https://www.googleapis.com/auth/script.projects",
  "https://www.googleapis.com/auth/chat.messages",
  "https://www.googleapis.com/auth/chat.spaces.readonly",
  "https://www.googleapis.com/auth/youtube.upload",
  "https://www.googleapis.com/auth/youtube.readonly",
  "https://www.googleapis.com/auth/contacts",
  "https://mail.google.com/",
];

// ---------------------------------------------------------------------------
// credential + access token
// ---------------------------------------------------------------------------

function readCreds() {
  try {
    return JSON.parse(fs.readFileSync(CRED_FILE, "utf8"));
  } catch {
    return null;
  }
}

function writeReauthFlag(reason) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(
    REAUTH_FLAG,
    JSON.stringify({ reason, at: new Date().toISOString() }, null, 2),
    "utf8"
  );
}

function clearReauthFlag() {
  try {
    fs.unlinkSync(REAUTH_FLAG);
  } catch {
    /* not there: fine */
  }
}

let tokenCache = { access: null, expiresAt: 0, scope: "", cred: "" };

// MEASURED 2026-10-27: after a widening consent the credential file is
// replaced, but the cached access token still belonged to the OLD grant. The
// container then answered 403 "insufficient authentication scopes" while the
// very same scope was granted and present in the file. The cache therefore
// carries a fingerprint of the credential it was minted from.
function credentialFingerprint(creds) {
  if (!creds) return "";
  return (
    String(creds.refresh_token || "").length +
    ":" +
    String(creds.refresh_token || "").slice(-12) +
    ":" +
    String(creds.provisioned_at || "")
  );
}

async function mintAccessToken() {
  const creds = readCreds();
  if (!creds || !creds.refresh_token) {
    throw new Error("NO_CREDENTIAL: " + CRED_FILE + " is missing. Run provision-grant.cjs on the host.");
  }
  const body = new URLSearchParams({
    client_id: creds.client_id,
    client_secret: creds.client_secret,
    refresh_token: creds.refresh_token,
    grant_type: "refresh_token",
  });
  const res = await fetch(OAUTH_TOKEN_URL, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });
  let json = {};
  try {
    json = await res.json();
  } catch {
    /* not json */
  }
  if (res.status !== 200 || !json.access_token) {
    const reason = "token endpoint http " + res.status + " " + (json.error || "") + " " + (json.error_description || "");
    if (/invalid_grant|unauthorized_client/i.test(reason)) {
      writeReauthFlag(reason.trim());
    }
    throw new Error("REAUTH_REQUIRED: " + reason.trim());
  }
  tokenCache = {
    access: json.access_token,
    expiresAt: Date.now() + Number(json.expires_in || 3600) * 1000,
    scope: json.scope || "",
    cred: credentialFingerprint(creds),
  };
  clearReauthFlag();
  return tokenCache.access;
}

async function accessToken() {
  const creds = readCreds();
  const fp = credentialFingerprint(creds);
  if (
    tokenCache.access &&
    Date.now() < tokenCache.expiresAt - 60000 &&
    tokenCache.cred === fp
  ) {
    return tokenCache.access;
  }
  return mintAccessToken();
}

async function gfetch(pathOrUrl, { method = "GET", body = null, headers = {}, raw = false } = {}) {
  const token = await accessToken();
  const url = pathOrUrl.startsWith("http") ? pathOrUrl : "https://www.googleapis.com" + pathOrUrl;
  const h = Object.assign(
    { Authorization: "Bearer " + token },
    headers
  );
  if (body !== null && !h["Content-Type"]) h["Content-Type"] = "application/json";
  const res = await fetch(url, { method, headers: h, body: body === null ? undefined : body });
  const text = await res.text();
  if (!res.ok) {
    let detail = text;
    try {
      const j = JSON.parse(text);
      detail = JSON.stringify(j.error || j);
    } catch {
      /* keep raw */
    }
    const err = new Error("GOOGLE_HTTP_" + res.status + ": " + String(detail).slice(0, 600));
    err.status = res.status;
    err.detail = detail;
    throw err;
  }
  if (raw) return { status: res.status, text };
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

// ---------------------------------------------------------------------------
// tools
// ---------------------------------------------------------------------------

function scopeOf(tool) {
  const needs = {
    gdrive_list: ["https://www.googleapis.com/auth/drive"],
    gdrive_read: ["https://www.googleapis.com/auth/drive"],
    gdrive_write: ["https://www.googleapis.com/auth/drive"],
    gdrive_delete: ["https://www.googleapis.com/auth/drive"],
    gmail_list: ["https://www.googleapis.com/auth/gmail.modify"],
    gmail_read: ["https://www.googleapis.com/auth/gmail.modify"],
    gmail_send: ["https://www.googleapis.com/auth/gmail.send"],
    gmail_draft: ["https://www.googleapis.com/auth/gmail.compose"],
    gmail_label: ["https://www.googleapis.com/auth/gmail.modify"],
    gdocs_get: ["https://www.googleapis.com/auth/documents"],
    gdocs_create: ["https://www.googleapis.com/auth/documents"],
    gdocs_update: ["https://www.googleapis.com/auth/documents"],
    gsheets_read: ["https://www.googleapis.com/auth/spreadsheets"],
    gsheets_write: ["https://www.googleapis.com/auth/spreadsheets"],
    gcalendar_list: ["https://www.googleapis.com/auth/calendar"],
    gcalendar_create: ["https://www.googleapis.com/auth/calendar.events"],
    gphotos_list: ["https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata"],
    gphotos_albums: ["https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata"],
    gphotos_create_album: ["https://www.googleapis.com/auth/photoslibrary.appendonly"],
    gphotos_upload: ["https://www.googleapis.com/auth/photoslibrary.appendonly"],
    gphotos_edit_item: ["https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata"],
    gphotos_picker_start: ["https://www.googleapis.com/auth/photospicker.mediaitems.readonly"],
    gphotos_picker_result: ["https://www.googleapis.com/auth/photospicker.mediaitems.readonly"],
    gbooks_search: [],
    gkeep_list: [],
    gtasks_list: ["https://www.googleapis.com/auth/tasks"],
    gsites_list: [],
    gscript_list: ["https://www.googleapis.com/auth/drive"],
    gchat_spaces: ["https://www.googleapis.com/auth/chat.spaces.readonly"],
    gcontacts_list: ["https://www.googleapis.com/auth/contacts"],
    youtube_my_videos: ["https://www.googleapis.com/auth/youtube.readonly"],
    youtube_upload: ["https://www.googleapis.com/auth/youtube.upload"],
  };
  return needs[tool] || [];
}

function currentScopes() {
  const creds = readCreds();
  return (creds && creds.scope) || tokenCache.scope || "";
}

function missingScope(tool) {
  const have = currentScopes().split(/\s+/).filter(Boolean);
  const need = scopeOf(tool);
  if (!need.length) return null;
  // a broader scope covers the narrower one
  const ok = need.every((s) => have.includes(s) || have.some((h) => s.startsWith(h)));
  return ok ? null : need.join(" ");
}

const TOOLS = [
  {
    name: "google_auth_status",
    description:
      "State of the permanent Google credential in this container: LIVE grant, granted scopes, whether a re-consent is required, and the local data paths. Call this first when Google calls fail.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "google_scope_upgrade",
    description:
      "Prints the ONE consent URL that widens the credential to every grantable Google API scope (photos, tasks, script, chat, youtube, books, contacts, full mail). One click in a browser, permanent afterwards. Use the client whose secret is in the mounted secrets volume.",
    inputSchema: {
      type: "object",
      properties: {
        client: { type: "string", description: "Which mounted client to use: 'live' (default) or 'secrets'." },
        redirect_uri: { type: "string", description: "Optional redirect URI; defaults to urn:ietf:wg:oauth:2.0:oob." },
      },
      additionalProperties: false,
    },
  },
  {
    name: "gdrive_list",
    description: "List files/folders in Drive. Supports a Drive q query and a parent folder id.",
    inputSchema: {
      type: "object",
      properties: {
        q: { type: "string", description: "Drive query, e.g. \"mimeType='application/vnd.google-apps.folder'\"." },
        folder_id: { type: "string", description: "Parent folder id; 'root' means My Drive." },
        page_size: { type: "number", description: "1..1000, default 50." },
      },
      additionalProperties: false,
    },
  },
  {
    name: "gdrive_read",
    description: "Read a Drive file. Google-native docs are exported as text; other files are downloaded (text-ish content only).",
    inputSchema: {
      type: "object",
      properties: { file_id: { type: "string" }, mime_type: { type: "string" } },
      required: ["file_id"],
      additionalProperties: false,
    },
  },
  {
    name: "gdrive_write",
    description: "Create a file in Drive (optionally as a Google Doc/Sheet) with text content.",
    inputSchema: {
      type: "object",
      properties: {
        name: { type: "string" },
        content: { type: "string" },
        mime_type: { type: "string", description: "Defaults to text/plain." },
        folder_id: { type: "string" },
      },
      required: ["name"],
      additionalProperties: false,
    },
  },
  {
    name: "gmail_list",
    description: "List Gmail messages. Supports a Gmail search query (q).",
    inputSchema: {
      type: "object",
      properties: {
        q: { type: "string" },
        max_results: { type: "number", description: "1..100, default 25." },
      },
      additionalProperties: false,
    },
  },
  {
    name: "gmail_read",
    description: "Read one Gmail message by id.",
    inputSchema: {
      type: "object",
      properties: { message_id: { type: "string" } },
      required: ["message_id"],
      additionalProperties: false,
    },
  },
  {
    name: "gmail_send",
    description: "Send an email from the account.",
    inputSchema: {
      type: "object",
      properties: {
        to: { type: "string" },
        subject: { type: "string" },
        body: { type: "string" },
        cc: { type: "string" },
      },
      required: ["to", "subject", "body"],
      additionalProperties: false,
    },
  },
  {
    name: "gmail_draft",
    description: "Create a Gmail draft (not sent).",
    inputSchema: {
      type: "object",
      properties: {
        to: { type: "string" },
        subject: { type: "string" },
        body: { type: "string" },
      },
      required: ["to", "subject", "body"],
      additionalProperties: false,
    },
  },
  {
    name: "gdocs_get",
    description: "Read a Google Doc as plain text.",
    inputSchema: {
      type: "object",
      properties: { document_id: { type: "string" } },
      required: ["document_id"],
      additionalProperties: false,
    },
  },
  {
    name: "gdocs_create",
    description: "Create a Google Doc with text content.",
    inputSchema: {
      type: "object",
      properties: { title: { type: "string" }, body: { type: "string" } },
      required: ["title"],
      additionalProperties: false,
    },
  },
  {
    name: "gdocs_update",
    description: "Append text to a Google Doc (insertText at the end of the body).",
    inputSchema: {
      type: "object",
      properties: { document_id: { type: "string" }, text: { type: "string" } },
      required: ["document_id", "text"],
      additionalProperties: false,
    },
  },
  {
    name: "gsheets_read",
    description: "Read a range from a Google Sheet.",
    inputSchema: {
      type: "object",
      properties: {
        spreadsheet_id: { type: "string" },
        range: { type: "string", description: "e.g. A1:D50" },
      },
      required: ["spreadsheet_id"],
      additionalProperties: false,
    },
  },
  {
    name: "gsheets_write",
    description: "Write values into a range of a Google Sheet.",
    inputSchema: {
      type: "object",
      properties: {
        spreadsheet_id: { type: "string" },
        range: { type: "string" },
        values: { type: "array", items: { type: "array", items: { type: "string" } } },
      },
      required: ["spreadsheet_id", "range", "values"],
      additionalProperties: false,
    },
  },
  {
    name: "gcalendar_list",
    description: "List calendar events.",
    inputSchema: {
      type: "object",
      properties: {
        max_results: { type: "number" },
        time_min: { type: "string" },
        time_max: { type: "string" },
      },
      additionalProperties: false,
    },
  },
  {
    name: "gcalendar_create",
    description: "Create a calendar event.",
    inputSchema: {
      type: "object",
      properties: {
        summary: { type: "string" },
        start: { type: "string", description: "ISO 8601." },
        end: { type: "string", description: "ISO 8601." },
        description: { type: "string" },
      },
      required: ["summary", "start", "end"],
      additionalProperties: false,
    },
  },
  {
    name: "gphotos_list",
    description:
      "List media items this app created in the user's Google Photos library. " +
      "Since 2025-03-31 Google only grants library-wide read to app-created content " +
      "(photoslibrary.readonly.appcreateddata).",
    inputSchema: {
      type: "object",
      properties: { page_size: { type: "number" } },
      additionalProperties: false,
    },
  },
  {
    name: "gphotos_albums",
    description: "List albums this app created in the user's Google Photos library.",
    inputSchema: {
      type: "object",
      properties: { page_size: { type: "number" } },
      additionalProperties: false,
    },
  },
  {
    name: "gphotos_create_album",
    description: "Create an album in the user's real Google Photos library (photoslibrary.appendonly).",
    inputSchema: {
      type: "object",
      properties: {
        title: { type: "string" },
        description: { type: "string" },
      },
      required: ["title"],
      additionalProperties: false,
    },
  },
  {
    name: "gphotos_upload",
    description:
      "Upload bytes into the user's Google Photos library (photoslibrary.appendonly). " +
      "Takes base64 content, uploads it raw, then creates the media item.",
    inputSchema: {
      type: "object",
      properties: {
        filename: { type: "string" },
        mime_type: { type: "string" },
        content_base64: { type: "string" },
        description: { type: "string" },
        album_id: { type: "string" },
      },
      required: ["content_base64"],
      additionalProperties: false,
    },
  },
  {
    name: "gphotos_edit_item",
    description: "Edit an app-created media item (description) in the user's library.",
    inputSchema: {
      type: "object",
      properties: {
        media_item_id: { type: "string" },
        description: { type: "string" },
      },
      required: ["media_item_id"],
      additionalProperties: false,
    },
  },
  {
    name: "gphotos_picker_start",
    description:
      "Open the Google Photos Picker so the user can pick photos and videos from their real library " +
      "(photospicker.mediaitems.readonly). Returns a picker_uri to open in the signed-in browser. " +
      "This is the supported path to library media after Google removed library-wide read on 2025-03-31.",
    inputSchema: {
      type: "object",
      properties: { max_item_count: { type: "number" } },
      required: [],
      additionalProperties: false,
    },
  },
  {
    name: "gphotos_picker_result",
    description:
      "Read the media items the user picked in a picker session (gphotos_picker_start). " +
      "Returns the picked items with their ids, filenames and base urls. The session is deleted " +
      "automatically when the last page has been read.",
    inputSchema: {
      type: "object",
      properties: {
        session_id: { type: "string" },
        page_token: { type: "string" },
      },
      required: ["session_id"],
      additionalProperties: false,
    },
  },
  {
    name: "gbooks_search",
    description: "Search Google Books (public API, no special scope).",
    inputSchema: {
      type: "object",
      properties: { q: { type: "string" }, max_results: { type: "number" } },
      required: ["q"],
      additionalProperties: false,
    },
  },
  {
    name: "gkeep_list",
    description: "List Google Keep notes (needs the keep scope).",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "gtasks_list",
    description: "List Google Tasks (needs the tasks scope).",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "gsites_list",
    description: "List Google Sites (needs the sites scope).",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "gscript_list",
    description: "List Apps Script projects (needs the script.projects scope).",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "gchat_spaces",
    description: "List Google Chat spaces (needs the chat.messages scope).",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "youtube_my_videos",
    description: "List the channel's own YouTube videos (needs the youtube.readonly scope).",
    inputSchema: {
      type: "object",
      properties: { max_results: { type: "number" } },
      additionalProperties: false,
    },
  },
  {
    name: "gcontacts_list",
    description: "List Google Contacts through the People API (needs the contacts scope).",
    inputSchema: {
      type: "object",
      properties: { max_results: { type: "number" } },
      additionalProperties: false,
    },
  },
  {
    name: "notebooklm_ask",
    description:
      "Ask a question to a Gemini Notebook (NotebookLM) notebook through the ExtendLM MCP server (https://mcp.extendlm.com/mcp). Needs an ExtendLM token in /data/extendlm.json and the ExtendLM browser extension connected to your Google account. Without notebook_id the first visible notebook is used and its title is returned with the answer.",
    inputSchema: {
      type: "object",
      properties: {
        question: { type: "string", description: "The question to ask the notebook." },
        notebook_id: { type: "string", description: "Optional notebook id. Defaults to the first notebook visible to the account." },
      },
      required: ["question"],
      additionalProperties: false,
    },
  },
];

// ---------------------------------------------------------------------------
// tool implementations
// ---------------------------------------------------------------------------

function b64url(buf) {
  return Buffer.from(buf).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function rawEmail({ to, subject, body, cc }) {
  const lines = [];
  lines.push("To: " + to);
  if (cc) lines.push("Cc: " + cc);
  lines.push("Subject: " + subject);
  lines.push("MIME-Version: 1.0");
  lines.push('Content-Type: text/plain; charset="UTF-8"');
  lines.push("");
  lines.push(body || "");
  return lines.join("\n");
}

const IMPL = {
  async google_auth_status() {
    const creds = readCreds();
    const flag = fs.existsSync(REAUTH_FLAG) ? JSON.parse(fs.readFileSync(REAUTH_FLAG, "utf8")) : null;
    let live = false;
    let probe = "not probed";
    try {
      await accessToken();
      live = true;
      probe = "token minted";
    } catch (e) {
      probe = e.message;
    }
    return {
      credential_present: !!creds,
      client_id: creds ? creds.client_id : null,
      grant_live: live,
      reauth_required: !!flag || !live,
      reauth_reason: flag ? flag.reason : null,
      probe,
      granted_scopes: currentScopes().split(/\s+/).filter(Boolean),
      data_dir: DATA_DIR,
      credential_file: CRED_FILE,
      note: "The refresh token lives in the mounted volume, not in the image. Access tokens are minted from it automatically.",
    };
  },

  async google_scope_upgrade(args) {
    const client = (args && args.client) || "live";
    const creds = readCreds();
    if (!creds) throw new Error("NO_CREDENTIAL");
    const redirect = (args && args.redirect_uri) || "urn:ietf:wg:oauth:2.0:oob";

    // Two clients are available on this machine:
    //  - 'live'   : the client the current (permanent) grant belongs to
    //  - 'secrets': the client whose secret sits in the mounted secrets volume
    // The widening consent is made with 'secrets' so the resulting token is
    // not tied to a client whose secret lives only in one store.
    let clientId = creds.client_id;
    let secretFile = null;
    if (client === "secrets") {
      const dir = process.env.GA_SECRETS_DIR || "/secrets";
      let files = [];
      try {
        files = fs.readdirSync(dir);
      } catch {
        throw new Error("NO_SECRETS_DIR: " + dir + " is not mounted.");
      }
      for (const f of files) {
        if (!/client_secret.*\.json$/i.test(f)) continue;
        try {
          const j = JSON.parse(fs.readFileSync(path.join(dir, f), "utf8"));
          const sec = j.web || j.installed || {};
          if (sec.client_id) {
            clientId = sec.client_id;
            secretFile = f;
            break;
          }
        } catch {
          /* not json */
        }
      }
      if (!secretFile) throw new Error("NO_CLIENT_IN_SECRETS: no client_secret json under " + dir);
    }

    const params = new URLSearchParams({
      client_id: clientId,
      redirect_uri: redirect,
      response_type: "code",
      access_type: "offline",
      prompt: "consent",
      include_granted_scopes: "true",
      scope: FULL_SCOPES.join(" "),
    });
    return {
      consent_url: "https://accounts.google.com/o/oauth2/v2/auth?" + params.toString(),
      client_used: client,
      client_id_used: clientId,
      secret_file: secretFile,
      scopes_requested: FULL_SCOPES.length,
      instruction:
        "Open this URL once in the signed-in browser, press Allow, and copy the code back. Then run on the host: node provision-grant.cjs --from-code <code> --client <client>. After that the grant is permanent and no consent is needed again.",
    };
  },

  async gdrive_list(args) {
    const page = Math.min(Number(args.page_size || 50), 1000);
    let q = args.q || "";
    if (args.folder_id && !/trashed/.test(q)) {
      const f = args.folder_id === "root" ? "root" : args.folder_id;
      q = q ? q + " and '" + f + "' in parents" : "'" + f + "' in parents";
    }
    const url =
      "/drive/v3/files?pageSize=" +
      page +
      "&fields=files(id,name,mimeType,size,modifiedTime,parents,webViewLink,trashed)" +
      (q ? "&q=" + encodeURIComponent(q) : "");
    const r = await gfetch(url);
    return { count: (r.files || []).length, files: r.files || [] };
  },

  async gdrive_read(args) {
    const meta = await gfetch(API_BASE.drive + "/drive/v3/files/" + args.file_id + "?fields=id,name,mimeType,size");
    const m = meta.mimeType || "";
    if (m === "application/vnd.google-apps.document") {
      const t = await gfetch(API_BASE.drive + "/drive/v3/files/" + args.file_id + "/export?mimeType=text/plain", { raw: true });
      return { id: meta.id, name: meta.name, mime_type: m, text: t.text };
    }
    if (m === "application/vnd.google-apps.spreadsheet") {
      const t = await gfetch(API_BASE.drive + "/drive/v3/files/" + args.file_id + "/export?mimeType=text/csv", { raw: true });
      return { id: meta.id, name: meta.name, mime_type: m, text: t.text };
    }
    const t = await gfetch(API_BASE.drive + "/drive/v3/files/" + args.file_id + "?alt=media", { raw: true });
    return { id: meta.id, name: meta.name, mime_type: m, text: t.text.slice(0, 200000) };
  },

  async gdrive_write(args) {
    const mime = args.mime_type || "text/plain";
    const body = args.content || "";
    const meta = { name: args.name, mimeType: mime };
    if (args.folder_id) meta.parents = [args.folder_id];
    if (mime === "application/vnd.google-apps.document") {
      const doc = await gfetch(API_BASE.drive + "/drive/v3/files", { method: "POST", body: JSON.stringify(meta) });
      if (body) {
        await gfetch(API_BASE.docs + "/v1/documents/" + doc.id + ":batchUpdate", {
          method: "POST",
          body: JSON.stringify({
            requests: [{ insertText: { location: { index: 1 }, text: body } }],
          }),
        });
      }
      return { id: doc.id, name: doc.name, webViewLink: doc.webViewLink };
    }
    const boundary = "ga_boundary_" + Date.now();
    const encoded = b64url(Buffer.from(body, "utf8"));
    const payload =
      "--" + boundary + "\r\nContent-Type: " + mime + "\r\n\r\n" + body + "\r\n--" + boundary + "--";
    const created = await gfetch(API_BASE.drive + "/upload/drive/v3/files?uploadType=multipart", {
      method: "POST",
      headers: { "Content-Type": "multipart/related; boundary=" + boundary },
      body: payload,
    }).catch(async () => {
      // multipart/related needs the JSON part first
      const json = b64url(Buffer.from(JSON.stringify(meta), "utf8"));
      const p2 =
        "--" + boundary + "\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n" + json +
        "\r\n--" + boundary + "\r\nContent-Type: " + mime + "\r\n\r\n" + body + "\r\n--" + boundary + "--";
      return gfetch(API_BASE.drive + "/upload/drive/v3/files?uploadType=multipart", {
        method: "POST",
        headers: { "Content-Type": "multipart/related; boundary=" + boundary },
        body: p2,
      });
    });
    void encoded;
    return { id: created.id, name: created.name, webViewLink: created.webViewLink };
  },

  async gmail_list(args) {
    const max = Math.min(Number(args.max_results || 25), 100);
    const url = "/gmail/v1/users/me/messages?maxResults=" + max + (args.q ? "&q=" + encodeURIComponent(args.q) : "");
    const r = await gfetch(url);
    const messages = r.messages || [];
    const brief = [];
    for (const m of messages.slice(0, max)) {
      const d = await gfetch(API_BASE.gmail + "/gmail/v1/users/me/messages/" + m.id + "?format=metadata&metadataHeaders=Subject&metadataHeaders=From&metadataHeaders=Date");
      const h = d.payload ? d.payload.headers || [] : [];
      const get = (n) => (h.find((x) => x.name.toLowerCase() === n) || {}).value || "";
      brief.push({ id: m.id, threadId: m.threadId, subject: get("subject"), from: get("from"), date: get("date") });
    }
    return { count: brief.length, messages: brief };
  },

  async gmail_read(args) {
    const r = await gfetch(API_BASE.gmail + "/gmail/v1/users/me/messages/" + args.message_id + "?format=full");
    const h = r.payload ? r.payload.headers || [] : [];
    const get = (n) => (h.find((x) => x.name.toLowerCase() === n) || {}).value || "";
    let body = "";
    const walk = (p) => {
      if (!p) return;
      if (p.mimeType === "text/plain" && p.body && p.body.data) body = Buffer.from(p.body.data, "base64").toString("utf8");
      (p.parts || []).forEach(walk);
    };
    walk(r.payload);
    return { id: r.id, subject: get("subject"), from: get("from"), to: get("to"), date: get("date"), body };
  },

  async gmail_send(args) {
    const raw = rawEmail(args);
    const r = await gfetch(API_BASE.gmail + "/gmail/v1/users/me/messages/send", {
      method: "POST",
      body: JSON.stringify({ raw: b64url(Buffer.from(raw, "utf8")) }),
    });
    return { sent: true, id: r.id, threadId: r.threadId };
  },

  async gmail_draft(args) {
    const raw = rawEmail(args);
    const r = await gfetch(API_BASE.gmail + "/gmail/v1/users/me/drafts", {
      method: "POST",
      body: JSON.stringify({ message: { raw: b64url(Buffer.from(raw, "utf8")) } }),
    });
    return { draft_id: r.id };
  },

  async gdocs_get(args) {
    const d = await gfetch(API_BASE.docs + "/v1/documents/" + args.document_id);
    const read = (p) => (p.textRun ? p.textRun.content : "");
    let text = "";
    const walk = (el) => {
      if (!el) return;
      if (el.paragraph) text += read(el.paragraph.elements ? el.paragraph.elements[0] : {}) + "\n";
      (el.paragraphs || []).forEach(walk);
      (el.content || []).forEach(walk);
      (el.table || {}).rows &&
        el.table.rows.forEach((row) => {
          row.cells.forEach((c) => (c.content || []).forEach(walk));
        });
    };
    walk(d.body);
    return { title: d.title, document_id: d.documentId, text };
  },

  async gdocs_create(args) {
    const d = await gfetch(API_BASE.docs + "/v1/documents", {
      method: "POST",
      body: JSON.stringify({ title: args.title }),
    });
    if (args.body) {
      await gfetch(API_BASE.docs + "/v1/documents/" + d.documentId + ":batchUpdate", {
        method: "POST",
        body: JSON.stringify({
          requests: [{ insertText: { location: { index: 1 }, text: args.body } }],
        }),
      });
    }
    return { document_id: d.documentId, title: d.title };
  },

  async gdocs_update(args) {
    const r = await gfetch(API_BASE.docs + "/v1/documents/" + args.document_id + ":batchUpdate", {
      method: "POST",
      body: JSON.stringify({
        requests: [{ insertText: { location: { index: 1 }, text: args.text } }],
      }),
    });
    return { document_id: args.document_id, replies: (r.replies || []).length };
  },

  async gsheets_read(args) {
    const range = args.range || "A1:Z100";
    const r = await gfetch(
      API_BASE.sheets + "/v4/spreadsheets/" + args.spreadsheet_id + "/values/" + encodeURIComponent(range)
    );
    return { spreadsheet_id: args.spreadsheet_id, range, values: r.values || [] };
  },

  async gsheets_write(args) {
    const r = await gfetch(
      API_BASE.sheets + "/v4/spreadsheets/" + args.spreadsheet_id + "/values/" + encodeURIComponent(args.range) + "?valueInputOption=RAW",
      { method: "PUT", body: JSON.stringify({ range: args.range, values: args.values }) }
    );
    return { spreadsheet_id: args.spreadsheet_id, updated: r.updatedCells, range: r.updatedRange };
  },

  async gcalendar_list(args) {
    const p = new URLSearchParams({ maxResults: String(Math.min(Number(args.max_results || 25), 250)) });
    if (args.time_min) p.set("timeMin", args.time_min);
    if (args.time_max) p.set("timeMax", args.time_max);
    const r = await gfetch(API_BASE.calendar + "/calendar/v3/calendars/primary/events?" + p.toString());
    return { count: (r.items || []).length, events: (r.items || []).map((e) => ({ id: e.id, summary: e.summary, start: e.start, end: e.end, location: e.location })) };
  },

  async gcalendar_create(args) {
    const r = await gfetch(API_BASE.calendar + "/calendar/v3/calendars/primary/events", {
      method: "POST",
      body: JSON.stringify({
        summary: args.summary,
        description: args.description || "",
        start: { dateTime: args.start },
        end: { dateTime: args.end },
      }),
    });
    return { event_id: r.id, htmlLink: r.htmlLink };
  },

  // Google removed library-wide read on 2025-03-31: the old scopes now reach
  // only content this app created. The tool reports that truth instead of
  // pretending the whole library is reachable.
  async gphotos_list(args) {
    const r = await gfetch(
      API_BASE.photoslibrary + "/v1/mediaItems?pageSize=" + Math.min(Number(args.page_size || 25), 100)
    );
    return {
      count: (r.mediaItems || []).length,
      scope_note: "app-created media items only (Google removed library-wide read on 2025-03-31)",
      photos: (r.mediaItems || []).map((p) => ({ id: p.id, created: p.mediaMetadata && p.mediaMetadata.dateTaken })),
    };
  },

  async gphotos_albums(args) {
    const r = await gfetch(
      API_BASE.photoslibrary + "/v1/albums?pageSize=" + Math.min(Number(args.page_size || 25), 100)
    );
    return {
      count: (r.albums || []).length,
      scope_note: "app-created albums only (Google removed library-wide read on 2025-03-31)",
      albums: (r.albums || []).map((a) => ({ id: a.id, title: a.title, productUrl: a.productUrl })),
    };
  },

  async gphotos_create_album(args) {
    const r = await gfetch(API_BASE.photoslibrary + "/v1/albums", {
      method: "POST",
      body: JSON.stringify({ album: { title: args.title, description: args.description || "" } }),
    });
    return { album_id: r.id, title: r.title, productUrl: r.productUrl };
  },

  async gphotos_upload(args) {
    // Two steps, both under photoslibrary.appendonly: upload the raw bytes,
    // then create the media item with the token that upload returns.
    const bytes = Buffer.from(String(args.content_base64 || ""), "base64");
    if (!bytes.length) throw new Error("EMPTY_CONTENT (content_base64 decoded to 0 bytes)");
    const mimeType = args.mime_type || "image/jpeg";
    const up = await gfetch(API_BASE.photoslibrary + "/v1/uploads?uploadType=media", {
      method: "POST",
      headers: { "Content-Type": mimeType },
      body: bytes,
    });
    const token = up && up.uploadToken;
    if (!token) throw new Error("NO_UPLOAD_TOKEN (the uploads endpoint did not return one)");
    const created = await gfetch(API_BASE.photoslibrary + "/v1/mediaItems:batchCreate", {
      method: "POST",
      body: JSON.stringify({
        mediaItems: [
          {
            description: args.description || "",
            simpleMediaDetails: { filename: args.filename || "upload.jpg", mimeType: mimeType },
            uploadTokens: [token],
          },
        ],
        albumId: args.album_id || undefined,
      }),
    });
    const results = (created && created.newMediaItemResults) || [];
    const first = results[0] || {};
    return {
      uploaded_bytes: bytes.length,
      status: first.status || null,
      media_item_id: first.mediaItem && first.mediaItem.id,
      productUrl: first.mediaItem && first.mediaItem.productUrl,
    };
  },

  async gphotos_edit_item(args) {
    const r = await gfetch(API_BASE.photoslibrary + "/v1/mediaItems/" + encodeURIComponent(args.media_item_id), {
      method: "PATCH",
      body: JSON.stringify({ description: args.description || "" }),
    });
    return { id: r.id, description: r.description };
  },

  async gphotos_picker_start(args) {
    // MEASURED: photospicker.googleapis.com is already enabled in the project,
    // and the current API takes NO pollingUri - sessions.create returns a
    // pickerUri the user opens in the browser signed into their own account.
    const max = Math.min(Number(args.max_item_count || 2000), 2000);
    const r = await gfetch(API_BASE.photospicker + "/v1/sessions", {
      method: "POST",
      body: JSON.stringify({ pickingConfig: { maxItemCount: String(max) } }),
    });
    return {
      session_id: r.id,
      picker_uri: r.pickerUri,
      media_items_set: Boolean(r.mediaItemsSet),
      expire_time: r.expireTime,
      polling: r.pollingConfig || null,
      instruction:
        "Open picker_uri in the browser signed in to the Google account that owns the photos, select the items, confirm. Then call gphotos_picker_result with this session_id.",
    };
  },

  async gphotos_picker_result(args) {
    const id = String(args.session_id || "");
    if (!id) {
      throw new Error("SESSION_ID_REQUIRED: gphotos_picker_result needs the session id from gphotos_picker_start.");
    }
    const s = await gfetch(API_BASE.photospicker + "/v1/sessions/" + encodeURIComponent(id));
    if (!s.mediaItemsSet) {
      return {
        session_id: id,
        media_items_set: false,
        count: 0,
        items: [],
        instruction: "The user has not finished picking yet. Poll again in a few seconds.",
      };
    }
    const q =
      "?sessionId=" +
      encodeURIComponent(id) +
      "&pageSize=100" +
      (args.page_token ? "&pageToken=" + encodeURIComponent(args.page_token) : "");
    const r = await gfetch(API_BASE.photospicker + "/v1/mediaItems" + q);
    const items = r.mediaItems || [];
    const nextPageToken = r.nextPageToken || null;
    // The API asks clients to delete sessions so they do not pile up.
    let sessionDeleted = false;
    if (!nextPageToken) {
      try {
        await gfetch(API_BASE.photospicker + "/v1/sessions/" + encodeURIComponent(id), {
          method: "DELETE",
        });
        sessionDeleted = true;
      } catch {
        /* cleanup is best effort */
      }
    }
    return {
      session_id: id,
      media_items_set: true,
      count: items.length,
      next_page_token: nextPageToken,
      session_deleted: sessionDeleted,
      items: items.map((it) => ({
        id: it.id,
        type: it.type,
        create_time: it.createTime,
        mime_type: it.mediaFile && it.mediaFile.mimeType,
        filename: it.mediaFile && it.mediaFile.filename,
        base_url: it.mediaFile && it.mediaFile.baseUrl,
      })),
      note: "base_url is valid for 60 minutes and needs the same bearer token to fetch the bytes.",
    };
  },

  async gbooks_search(args) {
    const r = await gfetch(
      API_BASE.books + "/books/v1/volumes?q=" + encodeURIComponent(args.q) + "&maxResults=" + Math.min(Number(args.max_results || 10), 40)
    );
    return {
      count: (r.items || []).length,
      items: (r.items || []).map((i) => ({
        title: i.volumeInfo && i.volumeInfo.title,
        authors: i.volumeInfo && i.volumeInfo.authors,
        publishedDate: i.volumeInfo && i.volumeInfo.publishedDate,
        link: i.volumeInfo && i.volumeInfo.infoLink,
      })),
    };
  },

  async gkeep_list() {
    const r = await gfetch(API_BASE.keep + "/v1/notes?pageSize=50");
    return { count: (r.notes || []).length, notes: (r.notes || []).map((n) => ({ name: n.name, title: n.title })) };
  },

  async gtasks_list() {
    const r = await gfetch(API_BASE.tasks + "/tasks/v1/users/@me/lists");
    return { lists: (r.items || []).map((l) => ({ id: l.id, title: l.title })) };
  },

  async gsites_list() {
    const r = await gfetch(API_BASE.sites + "/v1/sites");
    return { sites: (r.site || r.sites || []).map((s) => ({ name: s.name, url: s.url })) };
  },

  async gscript_list() {
    const r = await gfetch(
      API_BASE.drive +
        "/drive/v3/files?q=" +
        encodeURIComponent("mimeType='application/vnd.google-apps.script' and trashed=false") +
        "&pageSize=25&fields=files(id,name,modifiedTime)"
    );
    return {
      source: "drive file list (the Apps Script API publishes no projects.list method)",
      count: (r.files || []).length,
      projects: (r.files || []).map((p) => ({ script_id: p.id, title: p.name })),
    };
  },

  async gchat_spaces() {
    const r = await gfetch(API_BASE.chat + "/v1/spaces");
    return { spaces: (r.spaces || []).map((s) => ({ name: s.name, displayName: s.displayName })) };
  },

  async youtube_my_videos(args) {
    const r = await gfetch(
      API_BASE.youtube + "/youtube/v3/channels?part=contentDetails,id,snippet&mine=true"
    );
    return { channel: r.items && r.items[0] ? r.items[0].snippet.title : null, channel_id: r.items && r.items[0] ? r.items[0].id : null };
  },

  async gcontacts_list(args) {
    const p = new URLSearchParams({
      personFields: "names,emailAddresses",
      pageSize: String(Math.min(Number(args.max_results || 25), 100)),
    });
    const r = await gfetch(API_BASE.people + "/v1/people/me/connections?" + p.toString());
    return {
      count: (r.connections || []).length,
      contacts: (r.connections || []).map((c) => ({
        name: c.names && c.names[0] ? c.names[0].displayName : null,
        email: c.emailAddresses && c.emailAddresses[0] ? c.emailAddresses[0].value : null,
      })),
    };
  },

  async notebooklm_ask(args) {
    const question = String((args && args.question) || "").trim();
    if (!question) throw new Error("QUESTION_REQUIRED: notebooklm_ask needs a question.");

    // MEASURED: the ExtendLM MCP is stateless - initialize answers 400 and no
    // mcp-session-id is issued, but tools/list and tools/call answer 200 with
    // the bearer token alone. Every call therefore carries the token.
    const rpc = async (method, params, token) => {
      const res = await fetch(EXTENDLM_MCP_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json, text/event-stream",
          Authorization: "Bearer " + token,
        },
        body: JSON.stringify({ jsonrpc: "2.0", id: Date.now() % 100000, method, params }),
      });
      const body = await res.text();
      if (!res.ok) {
        throw new Error("EXTENDLM_HTTP_" + res.status + ": " + body.slice(0, 300));
      }
      const frames = [];
      const trimmed = body.trim();
      if (trimmed.startsWith("{")) {
        frames.push(JSON.parse(trimmed));
      } else {
        for (const line of trimmed.split(/\r?\n/)) {
          if (!line.startsWith("data:")) continue;
          const raw = line.slice(5).trim();
          if (!raw) continue;
          try {
            frames.push(JSON.parse(raw));
          } catch {
            /* not a JSON frame */
          }
        }
      }
      const err = frames.find((f) => f && f.error);
      if (err) throw new Error("EXTENDLM_RPC_ERROR: " + JSON.stringify(err.error).slice(0, 300));
      const result = frames.map((f) => (f && f.result) || {}).find((r) => Object.keys(r).length);
      return result || {};
    };

    const callTool = async (name, argumentsObj, token) => {
      const res = await rpc("tools/call", { name, arguments: argumentsObj }, token);
      const text = Array.isArray(res.content)
        ? res.content.map((c) => (c && (c.text || c.data)) || "").join("\n").trim()
        : "";
      let parsed = {};
      try {
        parsed = JSON.parse(text || "{}");
      } catch {
        parsed = { raw: text };
      }
      return { text, parsed, isError: Boolean(res.isError) };
    };

    const execute = async (token) => {
      // 1. MEASURED shape: { connections: [{ extension_connection, users: [{ auth_user_id, is_selected }] }] }
      let extensionConnection = args.extension_connection;
      let authUserId = args.auth_user_id;
      if (!extensionConnection || !authUserId) {
        const users = await callTool("list_notebook_users", {}, token);
        const conn = (users.parsed.connections || [])[0];
        if (!conn || !conn.extension_connection) {
          throw new Error(
            "EXTENDLM_NO_CONNECTION: the ExtendLM extension is not connected to a Gemini Notebook account. Open the ExtendLM extension in Chrome and connect it."
          );
        }
        extensionConnection = extensionConnection || conn.extension_connection;
        const selected =
          (conn.users || []).find((u) => u.is_selected) || (conn.users || [])[0];
        authUserId = authUserId || (selected && selected.auth_user_id) || "0";
      }

      // 2. MEASURED shape: { items: [{ id, title, source_count, ... }] }
      let notebookId = args.notebook_id;
      let notebookTitle = null;
      if (!notebookId) {
        const listed = await callTool(
          "list_notebooks",
          { extension_connection: extensionConnection, auth_user_id: authUserId, limit: 25 },
          token
        );
        const items = listed.parsed.items || listed.parsed.notebooks || [];
        if (!items.length) {
          throw new Error("EXTENDLM_NO_NOTEBOOKS: no notebook is visible for this account.");
        }
        notebookId = items[0].id;
        notebookTitle = items[0].title || null;
      }

      // 3. The actual question.
      const asked = await callTool(
        "ask_notebook",
        {
          extension_connection: extensionConnection,
          auth_user_id: authUserId,
          notebook_id: notebookId,
          question,
        },
        token
      );
      return {
        notebook_id: notebookId,
        notebook_title: notebookTitle,
        auth_user_id: authUserId,
        answer: asked.parsed && asked.parsed.answer ? asked.parsed.answer : asked.text,
        answer_chars: asked.text ? asked.text.length : 0,
        is_error: asked.isError,
      };
    };

    // The access token expires on its own. A 401 means the token died, not
    // that the grant died: renew it and try once more, silently.
    try {
      return await execute(await extendlmAccessToken(false));
    } catch (e) {
      if (String(e && e.message).includes("EXTENDLM_HTTP_401")) {
        return await execute(await extendlmAccessToken(true));
      }
      throw e;
    }
  },
};

// ---------------------------------------------------------------------------
// MCP plumbing (Streamable HTTP, JSON-RPC 2.0)
// ---------------------------------------------------------------------------

const PROTOCOL_VERSION = "2024-11-05";

function rpcResult(id, result) {
  return { jsonrpc: "2.0", id, result };
}
function rpcError(id, code, message) {
  return { jsonrpc: "2.0", id, error: { code, message } };
}

async function handleToolCall(name, args) {
  const impl = IMPL[name];
  if (!impl) throw new Error("UNKNOWN_TOOL: " + name);
  const miss = missingScope(name);
  if (miss) {
    throw new Error(
      "MISSING_SCOPE: " + name + " needs " + miss + ". The current grant covers " +
        currentScopes() + ". Call google_scope_upgrade for the one consent URL that widens it (one click, permanent)."
    );
  }
  return impl(args || {});
}

async function handleRpc(msg) {
  const { id, method, params } = msg;
  switch (method) {
    case "initialize":
      return rpcResult(id, {
        protocolVersion: PROTOCOL_VERSION,
        capabilities: { tools: { listChanged: false } },
        serverInfo: { name: "Google_Access", version: "1.0.0" },
        instructions:
          "Permanent Google access for any AI on this machine. Call google_auth_status first if a Google call fails; it reports whether a re-consent is required and the granted scopes.",
      });
    case "notifications/initialized":
      return null;
    case "ping":
      return rpcResult(id, {});
    case "tools/list":
      return rpcResult(id, { tools: TOOLS });
    case "tools/call": {
      try {
        const out = await handleToolCall(params.name, params.arguments || {});
        return rpcResult(id, {
          content: [{ type: "text", text: JSON.stringify(out, null, 2) }],
          isError: false,
        });
      } catch (e) {
        return rpcResult(id, {
          content: [{ type: "text", text: "ERROR: " + (e && e.message ? e.message : String(e)) }],
          isError: true,
        });
      }
    }
    case "resources/list":
      return rpcResult(id, { resources: [] });
    case "prompts/list":
      return rpcResult(id, { prompts: [] });
    default:
      if (id === undefined) return null;
      return rpcError(id, -32601, "METHOD_NOT_FOUND: " + method);
  }
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://" + (req.headers.host || HOST));
  if (req.method === "GET" && (url.pathname === "/health" || url.pathname === "/")) {
    let grant = "absent";
    try {
      await accessToken();
      grant = "live";
    } catch (e) {
      grant = "reauth_required";
    }
    const body = JSON.stringify({
      service: "Google_Access",
      grant,
      reauth_required: fs.existsSync(REAUTH_FLAG),
      tools: TOOLS.length,
      data_dir: DATA_DIR,
      time: new Date().toISOString(),
    });
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(body);
    return;
  }
  if (req.method !== "POST") {
    res.writeHead(405, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "method not allowed" }));
    return;
  }
  let raw = "";
  req.on("data", (c) => (raw += c));
  req.on("end", async () => {
    let msg;
    try {
      msg = JSON.parse(raw);
    } catch {
      res.writeHead(400, { "Content-Type": "application/json" });
      res.end(JSON.stringify(rpcError(null, -32700, "parse error")));
      return;
    }
    const out = await handleRpc(msg);
    const wantsSse = String(req.headers.accept || "").includes("text/event-stream");
    if (out === null) {
      res.writeHead(202, { "Content-Type": "application/json" });
      res.end("");
      return;
    }
    const payload = JSON.stringify(out);
    if (wantsSse) {
      res.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache" });
      res.end("event: message\ndata: " + payload + "\n\n");
    } else {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(payload);
    }
  });
});

server.listen(PORT, HOST, () => {
  console.log("Google_Access MCP listening on http://" + HOST + ":" + PORT + "/mcp");
  console.log("DATA_DIR=" + DATA_DIR + " CREDENTIALS=" + (fs.existsSync(CRED_FILE) ? "present" : "MISSING"));
  console.log("TOOLS=" + TOOLS.length);
});
