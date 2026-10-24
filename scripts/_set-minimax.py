import json, os, shutil

import sys

HOME = os.path.expanduser("~")
KEY = os.environ.get("MINIMAX_API_KEY")
if not KEY:
    print("Error: MINIMAX_API_KEY environment variable is not set.", file=sys.stderr)
    sys.exit(1)

MM = "MiniMax-M2.7-highspeed"
MMV1 = "https://api.minimax.io/v1"
OLL = "http://127.0.0.1:11434/v1"

q = os.path.join(HOME, ".qwen", "settings.json")
bak = q + ".bak-ollama"

# Start from the KNOWN-GOOD original. The previous attempt set
# security.auth.selectedType = "minimax", and Qwen's resolveModelConfig looks
# that up in a fixed set of recognised auth types; an unknown name resolves to
# undefined and it dies with
#   TypeError: Cannot read properties of undefined (reading 'model')
# MiniMax's surface is OpenAI-compatible, so the correct move is to keep the
# recognised type and change only the endpoint, key and model.
shutil.copyfile(bak, q)
with open(q, "r", encoding="utf-8") as f:
    d = json.load(f)

d["modelProviders"] = {
    # key stays "openai": that is the type Qwen understands, and MiniMax
    # serves the OpenAI shape. Only the target underneath it changes.
    "openai": [
        {
            "baseUrl": MMV1,
            "envKey": "MINIMAX_API_KEY",
            "id": MM,
            "name": MM + " (MiniMax)",
        },
        {
            "baseUrl": OLL,
            "envKey": "OLLAMA_API_KEY",
            "id": "qwen2.5-coder:1.5b",
            "name": "qwen2.5-coder:1.5b (Ollama, local, free)",
        },
    ]
}
d["model"] = {"baseUrl": MMV1, "name": MM}
d.setdefault("env", {})["MINIMAX_API_KEY"] = KEY
d.setdefault("security", {})["auth"] = {
    "apiKey": KEY,
    "baseUrl": MMV1,
    "selectedType": "openai",  # <- recognised type, MiniMax underneath
}
with open(q, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
    f.write("\n")

print("restored from  :", bak)
print("model          :", d["model"]["name"])
print("baseUrl        :", d["model"]["baseUrl"])
print("selectedType   :", d["security"]["auth"]["selectedType"])
print("provider list  :", ", ".join(p["id"] for p in d["modelProviders"]["openai"]))
