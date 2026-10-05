# AgentTube (Lumen) — Adoption Plan / Getting It Running

Verified by execution on 2026-09-27/28 · master tip `0d7eaf96` · scratch clone `/Users/santosh/.hermes/cache/scratch/ytaa`

---

## What I actually ran (evidence)

| Step | Command | Result |
|---|---|---|
| Boot the server | `node index.js` (PORT=3457 in scratch) | ✅ Started clean |
| Port binding observed | `lsof -nP -iTCP:3457 -sTCP:LISTEN` | ⚠️ **`TCP *:3457` — binds ALL interfaces**, not loopback (confirms unmerged PR #40 matters) |
| Health | `GET /health` | ✅ 200 — `{"status":"setup_required","initialized":true}` |
| Dashboard | `GET /` | ✅ 200 |
| Dashboard data | `GET /api/dashboard` | ✅ 200 |
| Readiness gate | `GET /api/readiness` | ✅ `{"status":"unverified", checks:[]}` |
| Generation without keys | `POST /generate` | ✅ **correctly refused**: "Finish setup with npm run walkthrough before generating content" |
| Full test suite | `npm test` | ✅ 46/46 passed |
| Lint | `npm run lint` | ✅ clean |

**Conclusion: it boots, serves, and gates correctly out of the box. Nothing is broken at the infrastructure level.**

---

## The two credential walls

Startup log, verbatim:

```
⚠️  Missing credentials for: youtube, an AI provider (OpenAI, Gemini, OpenRouter, Kimi, MiMo, or GLM)
⚠️  API_KEY is not set; mutating API routes are unprotected
⚠️  Dashboard started in setup mode; generation and publishing are disabled
```

So there are exactly two hard requirements:

1. **An AI text provider** — one key from any of OpenAI / Gemini / OpenRouter / Kimi / MiMo / GLM
2. **Google OAuth credentials** — a YouTube Data API OAuth client (Desktop app type) tied to the target channel

Plus a soft third: **TTS**, which the code treats as **fail-closed** — no narration means the production can never be approved, scheduled, or published (`README.md:88`).

---

## ⚠️ Correction to the README: "local models via Ollama" is NOT implemented

`README.md` claims "local models via Ollama". I grepped the whole tree and **there is no Ollama provider** — `utils/ai-text-service.js` hardcodes 5 cloud `baseURL`s into the `PROVIDERS` map (lines 11–47) and there is no env override for the base URL. The only `baseUrl` overrides in the repo are for *video* providers (`MINIMAX_API_BASE`, `KLING_API_BASE_URL`, `DASHSCOPE_*`).

**But the codebase is trivially local-capable.** I patched in a 7-line `ollama` preset and it worked first try:

```js
// utils/ai-text-service.js — add to PROVIDERS
ollama: {
  name: 'Ollama (local)',
  baseURL: process.env.OLLAMA_BASE_URL || 'http://localhost:11434/v1',
  defaultModel: 'ornith:lite',
  models: ['ornith:lite', 'qwen3.6:latest', 'qwen3:4b'],
  envKey: 'OLLAMA_API_KEY',
},
```

Proof of real output (your Ollama, `ornith:lite`, **$0**):

```
[AITextService] [INFO] Ollama (local) initialized (model: ornith:lite)
--- GENERATED ---
"Your data never leaves your machine — and that's the only reason local AI actually beats the cloud."
```

Your local fleet (7 models, already running on :11434): `qwen3.6:latest`, `qwen3:4b`, `gemma4:31b-mlx-64k`, `gemma4:31b-mlx`, `ornith:lite`, `deepseek-coder-v2:latest`, `nomic-embed-text:latest`.

### And the whole video pipeline can be local too

I proved the fail-closed narration → MP4 path end-to-end with **no cloud at all**:
macOS `say` (TTS) → system `ffmpeg` → real MP4:

```
narration.aiff  238,258 bytes
proof.mp4        61,806 bytes
codec_name=h264 / codec_type=video
codec_name=aac  / codec_type=audio
duration=5.309796
signature: 0000 0020 6674 7970 6973 6f6d   -> ftypisom  ✅ real MP4
```

So: **text via Ollama, TTS via `say`, assembly via ffmpeg = a fully local, $0 AgentTube.** None of it needs a cloud key. It just needs ~2 small patches (an `ollama` provider preset, and a `say`-based TTS provider).

---

## Recommended path — two tiers

### Tier A — De-risk locally first ($0, no Google account)

Do this before spending anything. It proves the pipeline on your machine with the real code.

1. Clone somewhere permanent (not the scratch dir):
   ```bash
   git clone https://github.com/darkzOGx/youtube-automation-agent.git ~/Desktop/projects/agenttube
   cd ~/Desktop/projects/agenttube && npm install && npm rebuild sqlite3
   node node_modules/ffmpeg-static/install.js   # or set FFMPEG_PATH=/opt/homebrew/bin/ffmpeg
   ```
2. Apply the Ollama provider patch above; set `OLLAMA_API_KEY=ollama`, `OLLAMA_BASE_URL=http://localhost:11434/v1`
3. Apply a `say`-based TTS provider (or use it as an offline stopgap) so narration isn't fail-closed
4. `npm test` → must be 46/46 before you change anything
5. Run `npm run walkthrough` — skip YouTube OAuth for now, configure only the text provider
6. Generate one video through the dashboard, inspect the MP4 on disk

**Exit criterion:** a real, non-simulated MP4 with audible narration, produced with zero cloud spend.

### Tier B — Add YouTube publishing (real channel, real stakes)

Only after Tier A works:

1. Google Cloud Console → new project → enable **YouTube Data API v3**
2. OAuth consent screen → External; add yourself as a test user
3. Credentials → Create → **OAuth client ID** → type **Desktop app**
   - Redirect URI must be **`http://127.0.0.1`** (the code normalizes legacy hardcoded callbacks, but Desktop-app client type is required)
4. Save the client to `config/credentials.json` (schema: `config/credentials.example.json`), or run `npm run credentials:setup`
5. Configure the channel block: `channelName`, `channelDescription`, `defaultCategory`, `defaultPrivacy`, `targetAudience`, `postingFrequency`, `preferredPostTime`
6. `DEFAULT_PRIVACY_STATUS=private` — keep it private until you trust the output
7. Run the **Production readiness** gate in the dashboard → **Run verified check** (it makes small live text+TTS requests, verifies channel access, builds and decodes a temp MP4, validates metadata — and never uploads)
8. Do **not** tick the paid image/video probe boxes on the first pass

**Note:** your repo already has a Google Cloud project pattern in use for other work — reuse that project rather than creating a new one if the OAuth consent branding is already set up. Don't enable the paid image/video probes until readiness is green without them.

### Hardening — do these before it ever touches a real channel

| Action | Why |
|---|---|
| `API_KEY=<long random>` in `.env` | Without it, **all 46 mutating routes are open** — the middleware no-ops when unset (`index.js:215-227`) |
| Bind to loopback | Confirmed live: it listens on `*:3457`. Patch `app.listen(PORT, '127.0.0.1', ...)` (that's PR #40, still unmerged) |
| Keep `DEFAULT_PRIVACY_STATUS=private` | First N videos should never auto-publish |
| Set `ENGAGEMENT_DAILY_REPLY_CAP` low | If you ever enable comment replies |
| Never enable `ANONYMOUS_TELEMETRY_ENABLED` | Off by default; leave it off unless you stand up your own collector |

---

## Two bugs that will bite this specific setup — fix before you trust output

### 🔴 #56 — silent template fallback (hits you immediately with a reasoning model)

`utils/ai-text-service.js:110-166` passes an explicit `temperature` and only retries on the **`max_tokens` spelling** 400 — there is **no retry for a temperature rejection**. Any reasoning-family model that only accepts `temperature=1` → 400 → `agents/script-writer-agent.js:176` logs a `warn` and `return null` → the caller silently falls back to hardcoded template text containing literals like:

```
[Detailed explanation with visuals]     (script-writer-agent.js:508)
Example 1: [Specific case study]        (script-writer-agent.js:522)
```

Your green capability check stays green while the script is garbage. **Your local `ornith:lite` / `qwen3.6` are reasoning models — this will hit you unless you either omit `temperature` or apply PR #58.**

### 🔴 #57 — narration truncated mid-sentence (silent)

`generateSlideshowVideo()` sizes the video track from a 150-wpm word-count estimate that **skips array-shaped `content` sections**; `addAudioToVideo()` then muxes with ffmpeg `-shortest`, silently dropping the audio tail. Reported measured case: **42.5s video vs 143.5s narration**. This is the default `VIDEO_PROVIDER=slideshow` path — i.e. exactly the path you'd use for free. Three competing fix PRs exist (#59, #61, #60). **Apply #59 or #61 before producing anything you care about.**

---

## Strategic read for Sai Ameya

You already run offer-first YouTube marketing (`youtube-offer-flywheel-marketing`) — where success is qualified conversations, leads, and clients, **not views or subscribers**. That changes how to use this tool:

- AgentTube optimizes for **publish cadence** (research → script → produce → publish → learn). Its feedback loop tunes CTR/retention/format. That's a *vanity-metric* loop.
- For your model it's better used as a **production engine, not a strategy engine**: feed it your offer-derived topics and let it do the scripting, narration, assembly, and upload mechanics. Drive the strategy from your own offer-first plan.
- The genuinely valuable parts for you: **durable SQLite evidence per stage**, **resume-from-checkpoint**, and **approval gates at every mutation**. Those map onto videoGen's Prometheus stage renderer far better than the YouTube publishing loop does.
- Blunt answer on the token situation: **don't point this at a channel that matters** until you've separated the tool from the token promotion. Run it in Tier A locally, on a throwaway channel, and keep the README's `agenttube.fun` context in mind — the code is honest, the project's front page is a memecoin funnel.

---

## Exact ordering

```
Tier A (free, today)          Tier B (paid/real, after A works)
─────────────────────         ────────────────────────────────────
clone + npm install      →    Google Cloud project + YouTube Data API v3
npm rebuild sqlite3      →    OAuth Desktop client, redirect http://127.0.0.1
ffmpeg-static install    →    config/credentials.json
npm test  == 46/46       →    channel block (name, audience, cadence, privacy=private)
patch: ollama provider   →    API_KEY=<random>  +  bind 127.0.0.1
patch: say TTS           →    walkthrough → configure → readiness gate
apply PR #58 (temp bug)  →    generate 1 video, keep private
apply PR #59 or #61      →    inspect the real MP4 yourself
generate + inspect MP4   →    only then consider enabling the schedule
```
