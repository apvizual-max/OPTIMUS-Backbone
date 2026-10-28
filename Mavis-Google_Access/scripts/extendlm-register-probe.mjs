// extendlm-register-probe.mjs - find which client metadata ExtendLM accepts.
//
// Measured: POST /rest/v1/mcp/oauth/register with a full RFC 7591 body was
// refused with 400 invalid_client_metadata. This tries the plausible shapes
// and prints which one is accepted, so the provisioner sends metadata the
// server actually takes - instead of guessing again.
const AS = "https://api.extendlm.com";
const meta = await (await fetch(AS + "/.well-known/oauth-authorization-server")).json();
console.log("METADATA_KEYS=" + Object.keys(meta).join(","));
console.log("SCOPES_SUPPORTED=" + (meta.scopes_supported || []).join(" "));
console.log("REGISTRATION_REQUIRED=" + (meta.registration_endpoint || "-"));

const base = {
  client_name: "Google_Access",
  redirect_uris: ["http://127.0.0.1:8799/callback"],
  grant_types: ["authorization_code", "refresh_token"],
  response_types: ["code"],
  token_endpoint_auth_method: "none",
};

const variants = [
  ["minimal", { ...base }],
  ["minimal+scope", { ...base, scope: "mcp" }],
  ["minimal+client_uri", { ...base, client_uri: "https://mcp.extendlm.com/" }],
  ["minimal+logo", { ...base, logo_uri: "https://mcp.extendlm.com/logo.png" }],
  ["client_name_only", { client_name: "Google_Access", redirect_uris: ["http://127.0.0.1:8799/callback"] }],
  ["no_refresh", { ...base, grant_types: ["authorization_code"] }],
  ["code_only_response", { ...base, response_types: ["code"], grant_types: ["authorization_code", "refresh_token"], token_endpoint_auth_method: "none", scope: "notebooks.read" }],
  ["localhost_redirect", { ...base, redirect_uris: ["http://localhost:8799/callback"] }],
  ["with_all_metadata", { ...base, client_uri: "https://mcp.extendlm.com/", logo_uri: "https://mcp.extendlm.com/logo.png", policy_uri: "https://mcp.extendlm.com/policy", tos_uri: "https://mcp.extendlm.com/tos", contacts: ["apvizual@gmail.com"] }],
];

for (const [name, body] of variants) {
  try {
    const r = await fetch(meta.registration_endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body),
    });
    const t = await r.text();
    let detail = t.slice(0, 220).replace(/\s+/g, " ");
    if (r.ok) {
      let j = {};
      try {
        j = JSON.parse(t);
      } catch {
        /* keep raw */
      }
      detail = "client_id=" + String(j.client_id || "").slice(0, 40) + " keys=" + Object.keys(j).join("+");
    }
    console.log("VARIANT=" + name + " HTTP=" + r.status + " " + detail);
  } catch (e) {
    console.log("VARIANT=" + name + " ERROR=" + e.message);
  }
}
