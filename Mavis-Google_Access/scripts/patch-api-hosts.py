#!/usr/bin/env python3
# patch-api-hosts.py - one-time source patch for Google_Access.
#
# MEASURED DEFECT (2026-10-27): the container prefixed every relative path
# with "https://www.googleapis.com". That host only serves drive, gmail,
# calendar and books. Eight services answered 404 in the live probe:
# docs, sheets, photos, keep, sites, script, chat, youtube.
#
# The fix is a single table of API hosts (one source of truth) taken from the
# official discovery documents, not from memory.
#
# Every replacement must match exactly the expected number of times. If one
# does not, the script fails loudly and writes NOTHING.
import io
import json
import sys

PATH = r"C:\Users\apviz\.minimax\google-access\server.mjs"

with io.open(PATH, "r", encoding="utf-8-sig", newline="") as fh:
    src = fh.read()
had_bom = open(PATH, "rb").read(3) == b"\xef\xbb\xbf"

API_BASE = '''
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
  books: "https://www.googleapis.com",
  tasks: "https://tasks.googleapis.com",
  keep: "https://keep.googleapis.com",
  sites: "https://sites.googleapis.com",
  script: "https://script.googleapis.com",
  chat: "https://chat.googleapis.com",
  youtube: "https://youtube.googleapis.com",
  people: "https://people.googleapis.com",
};
'''

# (old, new, expected_count)
REPL = [
    (
        'const EXTENDLM_MCP_URL = process.env.GA_EXTENDLM_URL || "https://mcp.extendlm.com/mcp";',
        'const EXTENDLM_MCP_URL = process.env.GA_EXTENDLM_URL || "https://mcp.extendlm.com/mcp";\n' + API_BASE,
        1,
    ),
    ('gfetch("/drive/v3/', 'gfetch(API_BASE.drive + "/drive/v3/', 5),
    ('gfetch("/upload/drive/v3/', 'gfetch(API_BASE.drive + "/upload/drive/v3/', 2),
    ('gfetch("/gmail/v1/users/me/', 'gfetch(API_BASE.gmail + "/gmail/v1/users/me/', 4),
    ('gfetch("/documents/v1/documents/" + doc.id + ":batchUpdate"', 'gfetch(API_BASE.docs + "/v1/documents/" + doc.id + ":batchUpdate"', 1),
    ('gfetch("/documents/v1/documents/" + d.documentId + ":batchUpdate"', 'gfetch(API_BASE.docs + "/v1/documents/" + d.documentId + ":batchUpdate"', 1),
    ('gfetch("/documents/v1/documents/" + args.document_id + ":batchUpdate"', 'gfetch(API_BASE.docs + "/v1/documents/" + args.document_id + ":batchUpdate"', 1),
    ('gfetch("/documents/v1/documents/" + args.document_id)', 'gfetch(API_BASE.docs + "/v1/documents/" + args.document_id)', 1),
    ('gfetch("/documents/v1/documents", {', 'gfetch(API_BASE.docs + "/v1/documents", {', 1),
    ('"/sheets/v4/spreadsheets/"', 'API_BASE.sheets + "/v4/spreadsheets/"', 2),
    ('gfetch("/calendar/v3/calendars/primary/events', 'gfetch(API_BASE.calendar + "/calendar/v3/calendars/primary/events', 2),
    (
        '      "/photoslibrary/v1/photos?pageSize=" + Math.min(Number(args.page_size || 25), 100)\n',
        '      API_BASE.photoslibrary + "/v1/mediaItems?pageSize=" + Math.min(Number(args.page_size || 25), 100)\n',
        1,
    ),
    (
        'return { count: (r.photos || []).length, photos: (r.photos || []).map((p) => ({ id: p.id, created: p.mediaMetadata && p.mediaMetadata.dateTaken })) };',
        'return { count: (r.mediaItems || []).length, photos: (r.mediaItems || []).map((p) => ({ id: p.id, created: p.mediaMetadata && p.mediaMetadata.dateTaken })) };',
        1,
    ),
    ('"https://www.googleapis.com/books/v1/volumes?q="', 'API_BASE.books + "/books/v1/volumes?q="', 1),
    ('gfetch("/keep/v1/notes?pageSize=50")', 'gfetch(API_BASE.keep + "/v1/notes?pageSize=50")', 1),
    ('gfetch("/tasks/v1/users/@me/lists")', 'gfetch(API_BASE.tasks + "/tasks/v1/users/@me/lists")', 1),
    ('gfetch("/sites/v1/sites")', 'gfetch(API_BASE.sites + "/v1/sites")', 1),
    ('gfetch("/chat/v1/spaces")', 'gfetch(API_BASE.chat + "/v1/spaces")', 1),
    (
        '"https://www.googleapis.com/youtube/v3/channels/mine?part=contentDetails,id,snippet"',
        'API_BASE.youtube + "/youtube/v3/channels?part=contentDetails,id,snippet&mine=true"',
        1,
    ),
    # Apps Script: the discovery document has NO projects.list method, so the
    # list is served by Drive (projects are files with the script mime type).
    (
        '    const r = await gfetch("/script/v1/projects");\n'
        '    return { projects: (r.projects || []).map((p) => ({ script_id: p.scriptId, title: p.title })) };',
        '    const r = await gfetch(\n'
        '      API_BASE.drive +\n'
        '        "/drive/v3/files?q=" +\n'
        '        encodeURIComponent("mimeType=\'application/vnd.google-apps.script\' and trashed=false") +\n'
        '        "&pageSize=25&fields=files(id,name,modifiedTime)"\n'
        '    );\n'
        '    return {\n'
        '      source: "drive file list (the Apps Script API publishes no projects.list method)",\n'
        '      count: (r.files || []).length,\n'
        '      projects: (r.files || []).map((p) => ({ script_id: p.id, title: p.name })),\n'
        '    };',
        1,
    ),
    (
        '    gscript_list: ["https://www.googleapis.com/auth/script.projects"],',
        '    gscript_list: ["https://www.googleapis.com/auth/drive"],',
        1,
    ),
    # Contacts (People API) - the contacts scope was granted but no tool used it.
    (
        '    gchat_spaces: ["https://www.googleapis.com/auth/chat.messages"],',
        '    gchat_spaces: ["https://www.googleapis.com/auth/chat.messages"],\n'
        '    gcontacts_list: ["https://www.googleapis.com/auth/contacts"],',
        1,
    ),
    (
        '''  {
    name: "notebooklm_ask",''',
        '''  {
    name: "gcontacts_list",
    description: "List Google Contacts through the People API (needs the contacts scope).",
    inputSchema: {
      type: "object",
      properties: { max_results: { type: "number" } },
      additionalProperties: false,
    },
  },
  {
    name: "notebooklm_ask",''',
        1,
    ),
    (
        '''  async notebooklm_ask(args) {''',
        '''  async gcontacts_list(args) {
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

  async notebooklm_ask(args) {''',
        1,
    ),
]

report = []
failed = []
for old, new, want in REPL:
    found = src.count(old)
    if found != want:
        failed.append({"old": old[:70], "expected": want, "found": found})
        continue
    src = src.replace(old, new)
    report.append({"replacement": old[:70], "count": found})

if failed:
    print(json.dumps({"status": "ABORTED", "failed": failed}, indent=2))
    sys.exit(2)

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(src)
if had_bom:
    with io.open(PATH, "rb+") as fh:
        data = fh.read()
        if not data.startswith(b"\xef\xbb\xbf"):
            fh.seek(0)
            fh.write(b"\xef\xbb\xbf" + data)

print(json.dumps({"status": "PATCHED", "replacements": len(report), "bom_preserved": had_bom}, indent=2))
