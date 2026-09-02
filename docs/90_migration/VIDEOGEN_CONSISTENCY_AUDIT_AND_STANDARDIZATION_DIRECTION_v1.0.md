# videoGen Consistency Audit & Standardization Direction

**Document ID:** VIDEOGEN-CONSISTENCY-AUDIT-2026-08-10  
**Version:** 1.0  
**Status:** Evidence-based architecture recommendation — not yet a constitution  
**Purpose:** Reconstruct the project’s evolution, identify the actual sources of inconsistency, define the correct separation between constitutional, creative-compilation, production, validation, persistence, and commercial layers, and establish the minimum standard required to avoid AI-slop output.

---

## 0. Executive conclusion

The core problem in videoGen is **not primarily model quality** and it is not solved by another large prompt.

The core problem is **authority ambiguity**.

Across the archived documents, multiple layers are allowed to make or remake the same decisions:

- the screenplay writer writes dialogue;
- the dialogue writer also writes dialogue;
- one migration section says PROMETHEUS should write the actual spoken words;
- another section in the same migration document says the GENESIS Dialogue Compiler outputs the actual dialogue lines;
- the GENESIS constitution says GENESIS produces no media;
- the GENESIS agent catalog nevertheless contains image, voice, music, SFX, audio-mixing, video-composition, and subtitle production agents;
- the Psychology Specification requires clinical-looking constructs such as attachment-style classifications, trauma, defense mechanisms and cognitive biases;
- the current product direction explicitly wants non-clinical, constructive, entertainment-first relationship stories;
- the Mark & Sarah bible demands both characters in every scene and 4–5 dialogue beats per scene;
- the screenplay then creates physically ambiguous scenes and repetitive conversational structure in order to obey that rule;
- current image generation does not enforce the approved character identities;
- the current film is a sequence of largely static images with audio rather than visually performed dialogue;
- mutable shared production paths allow old assets to contaminate new films.

These are **system design contradictions**, not prompt defects.

The correct response is to create a small, explicit constitutional hierarchy and make every other artifact subordinate to it.

The recommended operating law is:

> **Constitutions define what may never drift. GENESIS decides and compiles what this production means. PROMETHEUS realizes only the frozen production specification. ORACLE independently judges the result. ATLAS remembers the approved truth and every immutable version.**

PROMETHEUS must not write dialogue, choose psychological meaning, select a different character identity, invent a new emotional state, or decide how a relationship resolves.

---

# 1. Audit scope

The uploaded archive contains **289 substantive files** after excluding macOS metadata.

### Archive date distribution

| Date | Substantive files | Interpretation |
|---|---:|---|
| 2026-07-17 | 12 | Early Movie OS / production-centric design |
| 2026-07-19 | 267 | Large GENESIS constitutional, ontology, agent, workflow and PKP expansion |
| 2026-07-20 | 1 | UI design |
| 2026-07-21 | 1 | GENESIS 2.0 migration / four-pillar consolidation attempt |
| 2026-07-25 | 2 | LLM/runtime configuration |
| 2026-08-05 | 1 | Research reference note |
| 2026-08-10 | 5 | Mark & Sarah canon + Hermes expert overview derivatives |

The canonical latest expert summary in the archive is:

`docs/expert_overview/videoGen_Expert_Project_Overview_2026-08-10.md`

The audit also inspected the attached:

`continuous_film.mp4`

Verified media properties:

- duration: approximately **459.08 seconds**
- H.264, **1920×1080**, 24 fps
- AAC stereo, 48 kHz
- aggregate mean level approximately **-18.8 dB**
- aggregate peak approximately **-1.4 dB**

The only separately mounted media artifact in this upload is the film. If the voices inside this film are intended to be the preferred Mark/Sarah voices, they should become explicit series-level voice references. If separate favorite voice samples were intended, they are not present as separate files in this upload.

---

# 2. How the project evolved

## 2.1 Stage A — Product / Movie OS thinking

The 17 July design documents contain several decisions that remain strong:

- a **Production**, not a video, is the primary object;
- different production types should share one engine;
- production grammar should vary by niche/format;
- screenplay and production timeline are different artifacts;
- one production folder should be reproducible years later;
- character and environment identities should be reusable assets;
- downstream artifacts must not modify upstream creative content.

The early architecture correctly anticipated:

- psychology;
- kids stories;
- devotional stories;
- documentaries;
- explainers;
- shorts;
- multi-part productions.

This is still the right universal-product direction.

### Valuable early law

> The screenplay answers **what happens**.  
> The timeline answers **how it is produced**.  
> The render pipeline answers **how it is generated**.

That distinction should be preserved.

---

## 2.2 Stage B — GENESIS constitutional expansion

On 19 July the project expanded into a sophisticated GENESIS specification system.

The strongest ideas were:

- knowledge precedes production;
- GENESIS produces knowledge, not media;
- canonical knowledge should be versioned;
- provenance should be preserved;
- a frozen PKP should be the production handoff;
- validation should be independent;
- characters, psychology, dialogue, audio intent, visual intent, motion intent and distribution should all become explicit specifications.

This was directionally excellent.

The problem was **scope explosion**.

The archive created:

- 10 GENESIS constitutions;
- many domain ontologies;
- 27+ agents;
- many validators;
- 19 PKP specifications;
- workflows, registries, schemas, patterns and governance files.

The distinction between constitutional law, domain semantics, pre-production planning, actual execution and validation became blurred.

---

## 2.3 Stage C — Four-pillar consolidation

The 21 July GENESIS 2.0 migration moved toward the cleaner model:

- GENESIS — creative intelligence / compiler
- PROMETHEUS — rendering
- ORACLE — validation
- ATLAS — persistence

This is the right top-level model.

However, the migration itself still contains conflicting ownership decisions.

Example:

One section says the Movie OS Dialogue Writer is a rendering-time concern and that PROMETHEUS writes the actual spoken words.

Later, **Pass 07: Dialogue Compiler** explicitly says GENESIS outputs:

- dialogue intent;
- subtext;
- emotional state;
- rhythm;
- voice direction;
- **actual dialogue lines**.

The latter is the correct direction.

**Actual screenplay dialogue must be frozen before PROMETHEUS.**

PROMETHEUS synthesizes the words. It does not author them.

---

## 2.4 Stage D — Mark & Sarah

The 10 August Mark/Sarah documents add the recurring-character requirement:

- stable identities across videos;
- dialogue-driven scenes;
- restrained emotional performance;
- relationship continuity;
- visual-reference reuse.

This is the correct series direction.

But the current character bible and screenplay are not yet suitable as final canon.

They contain rules that create formulaic output and conflict with the newer decisions made for the channel.

---

# 3. The major consistency failures

## 3.1 GENESIS says “no media,” but contains production executors

The GENESIS Master Constitution says:

> Genesis produces no media.

Yet the GENESIS agent tree includes:

- Image Generator Agent
- Voice Generator Agent
- Music Generator Agent
- Audio Mixing Agent
- Video Composer Agent
- Subtitle Agent
- SFX Generator Agent

These do not belong inside the GENESIS constitutional domain if PROMETHEUS is the production engine.

### Resolution

Demote these archived agents to historical/legacy specifications and remap their responsibilities to PROMETHEUS.

GENESIS may produce:

- visual intent;
- character visual specifications;
- dialogue text;
- performance direction;
- voice identity selection;
- music intent;
- shot design;
- motion/lip-sync requirements.

GENESIS must not produce the final:

- image;
- voice waveform;
- music file;
- lip-synced clip;
- video clip;
- mix;
- final master.

---

## 3.2 Dialogue has multiple owners

The archive currently gives dialogue authority to:

1. Screenplay Writer Agent  
   It creates Dialogue objects and actual dialogue text.

2. Dialogue Writer Agent  
   It separately writes the dialogue.

3. GENESIS Migration D3  
   It temporarily proposes that PROMETHEUS write actual spoken words.

4. GENESIS Migration Pass 07  
   It correctly places actual dialogue lines in the Dialogue Compiler.

This ambiguity alone is sufficient to create repeated dialogue, rewrites and divergence.

### New law

There is **one textual authority**:

> **The approved screenplay/dialogue artifact contains the exact words the characters will say.**

GENESIS may revise them while the production is still in creative review.

After PKP freeze:

> **PROMETHEUS may not alter one word.**

TTS is realization, not writing.

---

## 3.3 Psychology is currently too clinical for the actual product

The archived PKP-08 Psychology Specification requires constructs including:

- attachment styles;
- defense mechanisms;
- trauma;
- cognitive biases;
- emotional triggers;
- behavioral patterns.

It even requires at least one attachment style, one defense mechanism and one cognitive bias.

That is incompatible with the current niche direction.

The current product is:

> fictional, entertainment-first, constructive husband-wife relationship and emotional storytelling.

It explicitly does not want to present itself as:

- therapy;
- diagnosis;
- clinical guidance;
- scientific psychological proof.

### Resolution

Keep the useful causal model but remove mandatory clinical taxonomy.

For the Psychology niche, replace clinical labeling with a **Narrative Behavioral Mechanism**:

```text
ordinary pressure / trigger
        ↓
character interpretation
        ↓
emotion
        ↓
protective intention
        ↓
observable behavior
        ↓
partner interpretation
        ↓
relationship consequence
        ↓
recognition
        ↓
constructive response
```

Optional clinical terminology may not be required by the engine and should not be displayed as diagnosis.

---

# 4. Mark & Sarah canon needs a v2, not a patch

The current `mark_sarah_character_bible.md` is a useful prototype but should be superseded.

## 4.1 It encodes one episode mechanism as permanent character identity

Current Mark:

- guarded;
- proud;
- inwardly anxious;
- avoids vulnerability;
- fears failure;
- struggles with self-worth.

If all of those are permanent core identity, every future story will become another version of Mark withdrawing because he fears failure.

That destroys the value of the Relationship Psychology Content Ontology.

### Correct split

**Stable Character Canon**

What almost never changes:

- identity;
- family;
- age envelope;
- occupation;
- history;
- core values;
- ordinary communication tendencies;
- voice identity;
- physical reference;
- long-term relationship state.

**Episode State**

What changes per story:

- active pressure;
- current fear;
- misunderstanding;
- emotional load;
- coping behavior;
- conflict responsibility;
- current relational distance;
- current goal;
- resolution state.

Mark should not be “the psychological problem.”

Sarah should not be “the therapist.”

They are two ordinary, imperfect spouses.

---

## 4.2 Sarah is structurally cast as the wiser spouse

The current bible describes Sarah as:

- emotional counterweight;
- perceptive;
- calm;
- compassionate;
- the person who sees through Mark's silence.

The current screenplay then repeatedly makes Sarah explain Mark to Mark.

This directly conflicts with the newly approved rule that responsibility should rotate:

- sometimes Mark;
- sometimes Sarah;
- often both;
- sometimes neither;
- sometimes circumstance.

### Resolution

Mark and Sarah are **co-leads**.

Neither has permanent moral or psychological superiority.

---

## 4.3 The current dialogue rule is too mechanical

Current rule:

- both characters in every scene;
- no one-character scenes;
- 4–5 dialogue beats per scene.

This sounds consistent, but it will generate AI slop.

It forces every scene into the same shape.

It also creates obvious production contradictions.

### Example from the current screenplay

Scene 3 is “A Difficult Meeting at the Office.”

The action says Sarah is “with him in spirit,” yet Sarah speaks dialogue in the scene.

That is neither:

- physically present;
- clearly on the phone;
- memory;
- voiceover;
- intercut conversation.

It exists because the rule says Sarah must speak.

### New rule

Mark & Sarah productions should be **dialogue-dominant**, not “both physically present in every scene.”

A scene may be:

- two-person conversation;
- phone conversation;
- intercut conversation;
- individual reaction scene;
- silent domestic beat;
- work scene;
- family beat;
- transition.

But every scene must causally serve the relationship story.

---

# 5. The current screenplay shows classic AI-slop patterns

The problem is not that the screenplay is unusable. The problem is that its structure encourages machine-like repetition.

## 5.1 It reveals the answer too early

Scene 1 already has Mark say:

> he has been putting it off because he is scared.

The remaining story then repeatedly “discovers” that his silence is fear.

The story therefore has very little actual revelation left.

### Better structural law

The viewer should progressively update their understanding.

A scene should not simply restate the emotional thesis.

---

## 5.2 Sarah frequently speaks in polished therapeutic aphorisms

Examples in the archived screenplay include lines with the functional form:

- “name the pain”;
- “human is enough”;
- “stay in the truth”;
- “be seen without performing.”

The ideas are reasonable.

The problem is **human plausibility**.

Ordinary spouses under pressure rarely produce a perfectly distilled psychological insight every 30 seconds.

This is a common AI-writing signature.

### New dialogue law

A line must sound like the person speaking **in that moment**, not like the author explaining the theme.

---

## 5.3 Every scene has nearly identical rhythm

The repeated structure is approximately:

```text
Mark reveals difficulty
Sarah reframes it
Mark deepens confession
Sarah delivers insight
Mark accepts
```

This creates the illusion of progression while the mechanism remains static.

### New law

Every conversation must alter at least one of:

- knowledge;
- interpretation;
- emotional distance;
- decision;
- commitment;
- practical action;
- relationship expectation.

If nothing changes, the exchange is redundant.

---

# 6. Attached film: why it currently reads as AI-generated material rather than performed cinema

The attached film confirms the documentation problem visually.

## 6.1 Severe identity drift

Across sampled frames:

- the apparent male face changes substantially;
- the apparent female face changes substantially;
- facial structure changes;
- hair changes;
- apparent age changes;
- apparent ethnic presentation changes.

This does not satisfy “same Mark / same Sarah.”

It also conflicts with the now-defined series canon.

This is a **blocking failure**, not a minor visual-quality issue.

---

## 6.2 The opening behaves as a static image, not acted dialogue

Sampling the opening across roughly twenty seconds shows essentially the same image rather than visible conversational performance.

That means the audience hears speech while the characters are visually frozen.

For a long-form cinematic husband-wife drama, this is exactly the kind of artifact that risks being perceived as AI slop.

Ken Burns / pan-and-zoom treatment can remain useful for:

- reflective inserts;
- establishing imagery;
- memory moments;
- montage;
- non-speaking transitions.

It should not be the default realization of a visible two-person conversation.

---

## 6.3 Lip sync must become a declared shot requirement

Do not make “lip sync everything” the rule either.

That is expensive and unnecessary.

Use cinematic coverage.

### Speaker shot

If the speaker's mouth is visible and readable:

**precise or production-approved lip sync is mandatory.**

### Listener reaction shot

The listener does not need lip sync.

This is often where the psychological cinema becomes strongest.

### Over-the-shoulder

Lip sync is required when the speaking face is clearly readable.

### Wide two-shot

Lip sync may be relaxed only when mouths are too small for the audience to judge.

### Cutaway / insert

Dialogue may continue off-screen without lip sync.

### Reflective voiceover

Allowed only when the format/scene explicitly calls for voiceover.

It must not be used simply to hide failed facial animation.

---

# 7. Correct creative-to-performance chain

For Mark & Sarah, the new standard should be:

```text
Problem Family
    ↓
Sub-Series
    ↓
Primary Mechanism
    ↓
Episode Contract
    ↓
Story Arc
    ↓
Scene Causal Graph
    ↓
Screenplay
    ↓
Dialogue + Performance Intent
    ↓
Shot Plan
    ↓
Voice / Motion / Lip-Sync Plan
    ↓
Frozen PKP
    ↓
PROMETHEUS
```

Every line should carry enough intent for performance.

Example schema:

```yaml
dialogue_turn:
  line_id: SC04-MARK-03
  speaker: MARK
  text: "..."
  surface_intention: "end the conversation"
  hidden_need: "reassurance without admitting he needs it"
  response_to: SC04-SARAH-02
  emotional_state_before: guarded
  delivery:
    pace: restrained
    volume: low
    hesitation: true
  physical_action:
    looks at plate instead of Sarah
  consequence:
    Sarah realizes he is ashamed rather than angry
  next_story_effect:
    she stops pressing for an answer and asks a different question
```

This is what makes dialogue drive the next step.

The line is not merely text.

It is a causal action.

---

# 8. Scene-state continuity must be explicit

Each scene needs:

```yaml
scene_state:
  entry:
    mark_emotion:
    sarah_emotion:
    relationship_distance:
    unresolved_question:
  turning_point:
    new_information:
    changed_interpretation:
  exit:
    mark_emotion:
    sarah_emotion:
    relationship_distance:
    new_decision:
    unresolved_question:
    next_scene_cause:
```

The next scene cannot begin from an arbitrary emotional state.

Its entry state must derive from:

- the previous scene exit state; or
- a declared off-screen event.

This is the correct foundation for emotional consistency.

---

# 9. Voice identity must become series canon

Voice should not be a per-run parameter.

For a recurring series, Mark and Sarah need persistent voice identities.

Recommended ATLAS records:

```yaml
voice_identity:
  character_id: MARK
  voice_reference_id:
  provider:
  provider_voice_id:
  reference_audio:
  language: en-US
  baseline:
    pace:
    pitch:
    warmth:
    restraint:
  approved_range:
    - calm
    - concerned
    - guarded
    - frustrated
    - vulnerable
    - relieved
  prohibited_delivery:
    - announcer
    - theatrical
    - exaggerated sadness
    - motivational-speaker cadence
```

And equivalent for Sarah.

The production can change **performance**, not identity.

If the voices in `continuous_film.mp4` are the preferred voices, preserve the exact source/provider identifiers or clean reference samples before further production work.

---

# 10. The correct constitutional hierarchy

Do **not** preserve the old pattern in which everything becomes a constitution.

For the current Psychology program, use only four constitutional documents.

## 10.1 Cinema Master Constitution

Applies to every video type:

- Psychology
- Kids
- Devotional
- History
- future niches

Defines universal authority and production law.

---

## 10.2 Commercial & Distribution Constitution

Defines ethical commercial optimization and reuse across:

- YouTube
- YouTube Shorts
- Instagram
- Facebook
- Pinterest
- Threads
- future platforms

Commercial optimization may strengthen packaging and reach.

It may **never override story truth or niche ethics**.

---

## 10.3 Psychology Sub-Constitution

Initially scoped to:

> Husband-wife relationship and emotional psychology.

Defines:

- non-clinical entertainment positioning;
- constructive relationship worldview;
- allowed/excluded territory;
- one-primary-mechanism rule;
- healing/meaningful-progress resolution requirement;
- psychological explanation boundaries;
- cinematic realism principles.

---

## 10.4 Mark & Sarah Series Constitution

Defines:

- recurring universe;
- immutable identity;
- family;
- work;
- location;
- relationship history;
- voice;
- visual identity;
- continuity;
- permanent-marriage protection;
- responsibility rotation;
- dialogue-dominant style.

---

# 11. Everything else is NOT a constitution

This distinction should be enforced in the app and repository.

## Ontology

**RPCO — Relationship Psychology Content Ontology**

Answers:

> What relationship territory exists?

---

## Coverage Registry

Answers:

> What have we produced and what remains under-covered?

---

## Series Bible

Answers:

> What is canonically true about Mark & Sarah?

---

## Episode Contract

Answers:

> What exact story are we making now?

---

## Format Profile

Answers:

> Is this a long-form cinematic drama, Short, Reel, narrated derivative, etc.?

---

## Standards

Standards define measurable craft requirements, for example:

- Dialogue & Performance Standard
- Character Continuity Standard
- Visual Identity Standard
- Voice Identity Standard
- Audio Mix Standard
- Lip-Sync & Motion Standard
- Anti-AI-Slop Quality Standard
- Multi-Part Story Standard
- Platform Packaging Standard

---

## PKP

Answers:

> What exact approved production is PROMETHEUS permitted to execute?

---

## ORACLE Report

Answers:

> Did the planned and rendered work actually satisfy the required standard?

---

# 12. Critical application architecture

The application should not simply expose a pile of documents to every AI agent.

It should **resolve policy**.

## 12.1 Policy resolution

At episode creation:

```text
Cinema Master Constitution
        +
Psychology Sub-Constitution
        +
Mark & Sarah Series Constitution
        +
Applicable Commercial Rules
        +
Selected Format Profile
        +
Episode Contract
        ↓
EFFECTIVE POLICY SNAPSHOT
```

That snapshot is versioned.

GENESIS receives the snapshot.

PROMETHEUS does not need to interpret the constitutions.

It receives the frozen PKP.

ORACLE receives:

- Effective Policy Snapshot
- PKP
- Rendered Media

and checks the result against both intent and law.

ATLAS stores all versions.

---

## 12.2 Why this matters

It solves a major AI consistency problem:

**No model needs to read 289 documents to understand one episode.**

The application compiles the relevant rules first.

Agents receive only what they need.

This reduces:

- prompt conflict;
- context dilution;
- accidental legacy-rule revival;
- model disagreement;
- token waste;
- hidden authority drift.

---

# 13. Recommended app-level content hierarchy

```text
NICHE
Psychology
    ↓
DOMAIN
Relationship & Emotional Psychology
    ↓
PROBLEM FAMILY
Emotional Withdrawal
    ↓
SUB-SERIES
Fear-Based Withdrawal
    ↓
MECHANISM VARIANT
Fear of disappointing spouse after job loss
    ↓
STORY UNIVERSE
Mark & Sarah
    ↓
STORY ARC
Job-loss withdrawal and reconnection
    ↓
EPISODE / MULTI-PART ARC
    ↓
PRODUCTION
    ↓
DISTRIBUTION DERIVATIVES
```

This should be first-class application data, not filename conventions.

---

# 14. Correct Mark & Sarah series direction

Current agreed canon should replace the archived v1 bible.

## Mark

- approximately 40;
- white American;
- software engineer;
- Seattle–Bellevue–Redmond region;
- husband and father;
- not permanently defined by one psychological mechanism.

## Sarah

- approximately 36;
- white American;
- business operations professional;
- works from home;
- carries substantial family/home responsibility;
- co-lead, not permanent emotional therapist.

## Marriage

- together approximately 14 years;
- three children approximately 12, 9 and 6;
- shared continuity accumulates;
- the marriage cannot permanently end in this series;
- separation/divorce is not engagement bait;
- healthy temporary space can be modeled when constructive.

## Children

Children become prominent only when materially relevant to:

- parenting;
- household load;
- school schedules;
- family responsibilities;
- couple-time tension.

Otherwise they exist naturally in the world without hijacking the episode.

---

# 15. Anti-AI-Slop Quality Standard — minimum blocking gates

A final production should fail ORACLE if any blocking condition remains.

## 15.1 Story

Fail if:

- the story repeats the same emotional realization;
- the conflict has no causal escalation;
- the ending appears because runtime ended;
- a multi-part episode does not have a predefined final arc;
- the mechanism is a label rather than demonstrated behavior.

## 15.2 Dialogue

Fail if:

- characters regularly speak like therapists, essayists, or motivational speakers without character justification;
- dialogue explains what the performance already shows;
- multiple scenes repeat the same confession/reframe pattern;
- both characters have interchangeable speech;
- dialogue does not produce a consequence;
- exact or near-exact lines recur without deliberate callback.

## 15.3 Character

Fail if:

- face identity drifts;
- age drifts;
- ethnicity/presentation drifts;
- voice identity drifts;
- work/family canon changes;
- one spouse repeatedly becomes the moral authority;
- episode behavior contradicts prior continuity without cause.

## 15.4 Performance

Fail if:

- a visible speaker has no meaningful mouth/performance motion when cinematic dialogue is expected;
- facial emotion contradicts the line;
- reaction shots are missing from major emotional exchanges;
- emotional state jumps without a causal beat.

## 15.5 Visuals

Fail if:

- scenes appear as unrelated AI images;
- visual style changes arbitrarily;
- wardrobe/location continuity breaks;
- every scene uses the same two-person facing composition;
- still-image pan/zoom is used as a substitute for acted dialogue throughout the film.

## 15.6 Voice and audio

Fail if:

- Mark/Sarah voice identity changes;
- one voice is materially harder to understand;
- speech is mechanically uniform across emotions;
- music masks dialogue;
- silence/room tone is absent where the style requires intimacy;
- the same music file is lazily reused across every scene without an intentional score rule.

## 15.7 Production integrity

Fail if:

- placeholder assets are present;
- stale assets from another run are reused without exact provenance match;
- the run lacks an immutable manifest;
- PROMETHEUS silently makes creative choices missing from the PKP.

---

# 16. The right long-form dialogue realization model

For the flagship psychology series, default cinematic grammar should be:

### Two-person master

Establish geography and emotional distance.

### Speaker coverage

Use medium/close speaker shots with lip sync when needed.

### Listener reaction

Use reaction shots aggressively.

The listener often carries more psychology than the speaker.

### Shared silence

Use a two-shot or environmental frame after emotionally significant lines.

### Inserts

Hands, unfinished meal, laptop, phone, school calendar, coffee, doorway, work notification, etc. may carry subtext.

### Physical action

Dialogue should coexist with ordinary domestic action.

Characters should not simply stand face-to-face delivering psychology.

This is how the production avoids “two AI portraits talking at each other.”

---

# 17. Relationship dialogue must lead somewhere

A scene is not complete because both characters spoke.

A scene is complete when the relationship state changes.

Use the following test.

At scene exit, at least one must be true:

- someone knows something they did not know;
- someone realizes an assumption was wrong;
- someone chooses to stay in the conversation;
- someone asks for space and commits to returning;
- someone apologizes;
- someone accepts responsibility;
- a practical action is agreed;
- a misunderstanding becomes clearer;
- emotional distance increases for a story reason;
- emotional distance decreases for a story reason;
- a new question becomes unavoidable.

This is a much stronger rule than “4–5 dialogue beats.”

---

# 18. What should be retained from the old GENESIS corpus

Do not delete the archive.

It contains valuable thinking.

Retain conceptually:

- immutable/versioned production knowledge;
- provenance;
- confidence;
- character consistency;
- scene/shot hierarchy;
- dialogue intention/subtext;
- audio intent;
- animation/lip-sync intent;
- quality criteria;
- independent validation;
- provider abstraction;
- run manifests;
- reusable character/environment assets.

But do not make Hermes treat all 267 GENESIS files as current law.

They should become:

> **legacy architecture evidence and reusable design material**

until explicitly adopted into the new authority hierarchy.

---

# 19. What should be superseded

## Supersede

- Mark & Sarah Character Bible v1
- Mark & Sarah Screenplay as a canonical series template
- mandatory “both characters in every scene”
- mandatory 4–5 dialogue beats
- permanent “Mark withdraws / Sarah understands” polarity
- PKP-08 mandatory clinical psychology taxonomy for this niche
- any rule allowing PROMETHEUS to create actual screenplay dialogue
- shared mutable output directories as release authority
- pre-render “production ready” certificates used as final certification
- static-image conversation as the flagship realization style

## Preserve as historical examples only

- Ethan / Claire examples
- Arjun / Maya examples
- irreversible-separation versions of Emotional Withdrawal
- cinematic-monologue variants that conflict with the current Mark & Sarah series profile

These may be useful examples for other future series, but they are not Mark & Sarah canon.

---

# 20. Commercial layer needs modernization

The archived PKP-16 Distribution Specification is oriented toward:

- theatrical;
- streaming;
- broadcast;
- physical media.

That is not enough for the actual business.

The commercial system must explicitly model:

- YouTube long-form;
- YouTube Shorts;
- Instagram Reels;
- Facebook;
- Pinterest;
- Threads;
- future social platforms.

The business law remains:

> **Maximum curiosity. Minimum deception.**

Strong hooks are allowed.

Prohibited:

- false diagnosis;
- fear-mongering;
- manufactured relationship paranoia;
- misleading thumbnails;
- fake consequences;
- rage bait.

One canonical production should create multiple distribution derivatives.

---

# 21. Recommended document set after this audit

Do not create 50 new authoritative documents.

Create the following small, clear set.

## Constitutions

1. `00_CINEMA_MASTER_CONSTITUTION.md`
2. `01_COMMERCIAL_DISTRIBUTION_CONSTITUTION.md`
3. `10_PSYCHOLOGY_SUB_CONSTITUTION.md`
4. `11_MARK_SARAH_SERIES_CONSTITUTION.md`

## Ontology

5. `RELATIONSHIP_PSYCHOLOGY_CONTENT_ONTOLOGY.yaml`

## Canon and registries

6. `MARK_SARAH_CHARACTER_BIBLE_v2.yaml`
7. `MARK_SARAH_VOICE_REGISTRY.yaml`
8. `MARK_SARAH_VISUAL_IDENTITY_REGISTRY.yaml`
9. `PSYCHOLOGY_CONTENT_COVERAGE_REGISTRY.yaml`

## Production standards

10. `DIALOGUE_AND_PERFORMANCE_STANDARD.md`
11. `EMOTIONAL_CONTINUITY_STANDARD.md`
12. `VISUAL_CHARACTER_CONTINUITY_STANDARD.md`
13. `VOICE_AUDIO_STANDARD.md`
14. `MOTION_AND_LIPSYNC_STANDARD.md`
15. `ANTI_AI_SLOP_QUALITY_STANDARD.md`
16. `MULTIPART_STORY_STANDARD.md`

## Production contracts

17. `EPISODE_CONTRACT.schema.yaml`
18. `PKP.schema.yaml`
19. `ORACLE_VALIDATION_REPORT.schema.yaml`
20. `IMMUTABLE_RUN_MANIFEST.schema.yaml`

Everything else should derive from or reference these.

---

# 22. Correct authority order

When documents disagree, resolve in this order:

```text
1. Cinema Master Constitution
2. Niche Sub-Constitution
3. Series Constitution
4. Approved Episode Contract
5. Applicable Production Standard
6. Effective Format / Platform Profile
7. Frozen PKP
8. Provider configuration
9. Runtime implementation
10. Generated asset
```

Commercial rules are cross-cutting but subordinate to the ethical and truth constraints of levels 1–4.

A runtime implementation may never override a frozen creative decision because it is “easier to render.”

---

# 23. Application enforcement

The app should make invalid states difficult or impossible.

Recommended workflow:

```text
SELECT NICHE
    ↓
SELECT PROBLEM FAMILY
    ↓
SELECT SUB-SERIES / MECHANISM
    ↓
SELECT STORY UNIVERSE
    ↓
LOAD CONTINUITY
    ↓
CREATE EPISODE CONTRACT
    ↓
RESOLVE EFFECTIVE POLICY
    ↓
GENESIS
    ↓
HUMAN / ORACLE PRE-PRODUCTION GATE
    ↓
FREEZE PKP
    ↓
PROMETHEUS
    ↓
ORACLE MEDIA GATE
    ↓
ATLAS RELEASE RECORD
    ↓
DISTRIBUTION DERIVATIVES
```

The production engine should not begin expensive media generation until:

- episode mechanism is clear;
- full story arc is clear;
- multi-part conclusion is known;
- screenplay is approved;
- dialogue is approved;
- character continuity is loaded;
- voice identities are locked;
- scene emotional states are valid;
- shot/motion/lip-sync requirements are explicit.

---

# 24. Recommended immediate P0 sequence

Do **not** build new rendering features first.

### P0.1 — Freeze authority

Create the four constitutions.

### P0.2 — Replace Mark & Sarah canon

Create Character Bible v2 with:

- stable identity;
- family/work/location;
- co-lead relationship;
- stable versus episodic state separation.

### P0.3 — Freeze voices and visual identities

Create immutable Mark/Sarah reference records.

### P0.4 — Create dialogue/performance and emotional-continuity standards

This must happen before another screenplay is treated as production-ready.

### P0.5 — Create anti-AI-slop ORACLE gates

Make failure explicit.

### P0.6 — Define one executable PKP

No duplicate brief/screenplay/dialogue authority.

### P0.7 — Run one vertical slice

Use one Emotional Withdrawal sub-series, for example:

**Fear-Based Withdrawal → job-loss / professional-failure variant**

Produce only enough scenes to prove:

- same Mark;
- same Sarah;
- same voices;
- real back-and-forth dialogue;
- emotional state continuity;
- correct speaker lip sync;
- meaningful reaction shots;
- causal dialogue;
- no static portrait conversation;
- immutable run provenance.

Only after that works should the platform scale to a complete episode.

---

# 25. Final architecture position

The project should now be understood as two separate concerns.

## A. Creative / constitutional operating system

Defines:

- values;
- content boundaries;
- audience;
- story ontology;
- series canon;
- relationship worldview;
- quality standards;
- commercial ethics;
- approved creative decisions.

This layer should change slowly.

---

## B. Production technology

Defines:

- model/provider;
- ComfyUI workflow;
- image generation;
- image-to-video;
- lip sync;
- TTS;
- audio mix;
- FFmpeg;
- render;
- retries;
- caching;
- GPU scheduling.

This layer may change frequently.

The production technology is replaceable.

The creative truth is not.

That is the separation required to make videoGen a studio system rather than a collection of AI experiments.

---

# 26. Bottom line

The archive contains many good ideas.

The failure was not lack of thinking.

It was failure to establish **one authority graph**.

The new system should therefore optimize for:

> **few constitutions, explicit ownership, frozen dialogue, persistent character/voice identity, causal emotional continuity, performed cinematic dialogue, immutable production handoff, independent anti-slop validation, and replaceable production technology.**

The current film proves that the renderer can create a valid audiovisual artifact.

It does **not** yet prove that the system can create a consistent Mark & Sarah performance.

That is the next bar.

