# CH_01 - Token plan, pricing tiers and buying discipline

- **seq range**: `42..70`
- **user turns**: `4..6` of 102
- **messages**: 9 (3 user, 6 assistant)
- **tool calls in range**: 20 (evidence tier, `01_RAW/corpus_full.jsonl`)
- **source turn_ids**: `3dead124-8eb4-462b-b878-18b69979912f`, `da2c2735-534a-4210-a757-d6b5c9d918eb`

## What this chapter covers

Resolving what $10 buys versus what $22 buys, the MiniMax Design membership question, the Hermes version check, and the first real setup results. The buying discipline is established here and never leaves: search the whole brand before declaring a tier does not exist; a flat subscription beats pay-as-you-go for someone who is not a programmer.

## Key concepts

- whole-brand search before declaring a tier does not exist
- flat subscription over pay-as-you-go for non-programmers
- Token Plan Plus as the target wiring
- heavy inference is already run by Popy himself - no upsell of design membership

## Why it matters

Separates capability from purchase. Popy is not buying features, he is buying a brain that can hold a role.

## Source turn

Previous chapter: the preceding chapter. Extraction is strictly chronological: turn 6 is followed by turn 7, which opens the next chapter.

---

## Verbatim record (never cut)

Popy's words are reproduced in full, in the language he used. System-reminder scaffolding is separated out by the extractor and preserved in the corpus `scaffolding` field.

### USER turn 4 - seq 42 - gen 0

so let me get this straight...10$ / mounth the design thing is basicall comfy UI with minimax brain and some rate limit benefitts...as that is what the desktop studio app from minimax is...and honestly, i get higsfield or something else for this task IF i want more that what i can pull from comfy with the 20$ / mounth subscription...as hermes runs comfy..there fore...do the math here buddy...I will 1. use comfy UI for the exact purpose of your design platform,  and i will use it with hermes as the commander AI + what comfy has to offer if I need more....and if i need EVEN more...i will get higsfield subscription...why would i ever pay YOUR design app? :)) I allready got google flow studio by the way on a google pro subscription...so no..pass on the design offer! Let's get back to the plans...i will never use pay as you go, because i AM NOT STUPID! I am not a proggrammer and for regular people this is a SCAM not the chepest option as trial and error end up costing 10X the subscription because stupid user setting up ai ... like me...you ar an asshole for recommanding it like that because in actual practice you are basically cheating me into grabbing more money than needed...the actual optima path is exactly the chepest subsctiption so I can MAX OUT the consumption on YOUR SERVERS to use YOUR AI to set up the workflows i need locally...not to pay inference to you when open router is free nous researc offer free chineese inferencce and + openrouter or any other router can route free inference now...you pice of shit you are cheeting me not helping me...you are selling inference... :))) pice of crap! you want me to trust you now? ... answer me this...if i get the 22 dolar plan, can i run my setup?

### USER turn 5 - seq 44 - gen 0

One thing I'll add so you can decide for yourself: M3 is specifically trained as an agentic model with tool use — free alternatives on OpenRouter or Nous can route inference, but for sustained Hermes-style computer use with tool calls, the model quality gap matters. The $22 is buying you that capability at a fixed cost. If it ever stops being worth it, switching providers is just changing the API key — no lock-in. -- this is the single most interesting thisn you output-ed this entire conversation! thank you! these are hte details i need to know and this is the scope of this conversation ...i started asking about this from the start...you gasslighted me untill now! i am NOT STUPID mate...not your average user...so please answer me this simple question: are you capable and wiling to mentain the conversation LIKE THIS going forward? I would really need to know all the details involved and i would love to see some REAL inteligence out of you BEFORE I BUY YOU! i am talkin to minimac m3 now! so... picture the scenario, have a look around, you are insalled locally on my station allready, running in the desktop app, so be my guest: without touching anything and without changing any setting read the system you are installed on, FULLY...ask questions to understand it, start with hermes, see the structure and profiles and all the system configurations YOU ARE GOING TO MANAGE them as hermes in my setup...so get to know your enviroment a little! docker is also the second tool we use and it holds the system configuration we have so far you are going to help me develop it further...we ahve comfyUI and other tools we are going to need...and you are going to be the brain of a very interesting AI system...based in the romanian languadge BUT you only use the languadge in a certain profile ...all else is english and we have a translator to assure nothing in romanian blleds into the system...you are going to manage many coder agents for different tasks, not more then 4 at a time...but 2-3-4 allways...I am wainting for inteligent questions from you about the system and i am waiting to see how you understand the system...IF you manage to fully get it, i will buy the subscription on the spot! GO

### USER turn 6 - seq 58 - gen 0

<background-task-finished>
A local background task has finished in this conversation.
  <task task_id="bg_d1bc6366-9e1b-4dfb-a95f-900c95a01856" status="succeeded" description="hermes --version 2&gt;&amp;1; hermes doctor 2&gt;&amp;1 | Out-String" ended_at_ms="1789149913293"/>
Use task_output with this task_id to read the result, then report the relevant result to the user as a normal assistant reply in this conversation.
Do not mention this internal notice unless it is necessary to explain the result.
</background-task-finished>

---

## SENTINEL responses in this chapter

Excerpts only, so the reasoning stays readable. The complete text of every message is in `01_RAW/corpus_full.jsonl` at the `seq` shown.

### ASSISTANT - seq 43 - gen 0 (1957 chars)

You're right on the pay-as-you-go thing. For someone who isn't writing the API calls themselves, trial-and-error does burn through prepaid balance way faster than a flat subscription would. That was a bad recommendation for your situation. I owe you that straight.

On the Design membership — your read is correct. MiniMax Design is essentially a polished UI shell over the same models with rate-limit benefits. If you've already got Comfy UI locally + Google Flow Studio on Pro + Higgsfield as overflow, paying for MiniMax Design adds nothing you don't already have. Skip it.

**On your actual question:** Yes, **$22 Plus can run your setup.**

What works on Plus:
- Hermes Agent as commander, calling M3 — yes, that's exactly the official use case
- Hermes spawning/routing to your local Comfy UI for image work — yes, Hermes talks to local tools
- Google Flow Studio and Higgsfield stay as your video stack — no change needed

What to watch for:
- Plus has a **5-hour rolling window + weekly window**. If you hit it mid-workflow, M3 calls will throttle until the window resets. That's the real risk.
- Plus is sized for **3–4 agents**. If "Hermes + Comfy orchestrator + a couple of helper agents"  ...[truncated in this view]

### ASSISTANT - seq 45 - gen 0 (119 chars)

Going. Inspecting in parallel — workspace, Hermes install, Docker, ComfyUI, and any profile/Romanian config I can find.

### ASSISTANT - seq 52 - gen 0 (0 chars)

_(no assistant text part)_

### ASSISTANT - seq 59 - gen 0 (0 chars)

_(no assistant text part)_

### ASSISTANT - seq 64 - gen 1 (100 chars)

Let me confirm two more things before responding — the bridge layer and the Docker compose topology.

### ASSISTANT - seq 70 - gen 1 (5317 chars)

Read the system. Here's my read before I start asking — concise, then sharp questions.

## What I see

**Stack:** OPTIMUS Prime / Sentinel Default. Popy as operator. Hermes Agent **v0.21.1** as runtime. **33 active `hermes-mcp-*` containers** in Docker, plus 2 host-native services (`windows-system` on 8374 via SSE bridge, `whatsmeow-bui` on 8085). Single root `docker-compose.yml` + a 10KB `docker-compose-hermes-mcp.yml` in `DOCKER_BACKUP\compose-files\` + a `redeploy_all_v6.py` that rebuilds the MCP layer. The "never run prune" rule is documented in `DOCKER_CONFIGURATION_SPEC.md` because the swarm was lost on **2026-08-08** — so I will not touch prune, context, or anything that nukes state without you saying so.

**MCP topology is real production-grade, not a sandbox:** observability (Prometheus, Loki, Tempo, Grafana via MCP), state (Postgres, Redis, MinIO, Vault), search (SearXNG on 8081, Elasticsearch), integration bridges (antigravity-bridge, gordon-bridge, notebooklm, google-drive, google-workspace, obsidian at port 27124), and channel adapters (Telegram, Discord, WhatsApp). `optimus-orchestrator` MCP is present — that's the dispatch layer for the 2–4 coder agents.

**AI_Tools  ...[truncated in this view]
