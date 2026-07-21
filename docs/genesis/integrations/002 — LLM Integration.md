Genesis Integration (GINT)
GINT-002 — LLM Integration

Document ID: GINT-002
Title: LLM Integration
Version: 1.0.0
Status: Active
Authority: Derived from GFS-000

1. Purpose

Defines how Genesis integrates with Large Language Models for reasoning,
discovery, and authoring tasks. Genesis is model-independent by design
(GFS-000 §16); this document defines the abstraction layer that makes that
independence real.

2. Scope

- Covers the LLM provider abstraction, prompt delivery, response parsing, and
  confidence handling.
- Supports two reference providers: LMStudio (local) and OpenAI (remote).
- Does not cover prompt authoring (covered by GPROMPT-NNN) or agent behavior
  (covered by GAS-NNN).

3. Provider Abstraction

Every provider implements this contract:

```
interface LLMProvider:
    complete(prompt: Prompt, config: ModelConfig) -> Response
    embed(text: str, config: ModelConfig) -> Embedding
    stream(prompt: Prompt, config: ModelConfig) -> Iterator[Token]
```

- `Prompt` is the structured object produced from a GPROMPT-NNN template.
- `ModelConfig` declares provider, model, temperature, max_tokens, retry policy.
- `Response` contains `content`, `usage`, `finish_reason`, `raw`.
- `Embedding` is a `float[]` with a declared dimensionality.

4. Supported Providers

### LMStudio (local)

- Endpoint: `http://localhost:1234/v1`
- Auth: none (local) or API key from env
- Use: development, offline runs, tests
- Config:
  ```yaml
  llm:
    provider: lmstudio
    model: llama-3-70b
    endpoint: http://localhost:1234/v1
    temperature: 0.2
    max_tokens: 4096
  ```

### OpenAI (remote)

- Endpoint: `https://api.openai.com/v1`
- Auth: `OPENAI_API_KEY` environment variable
- Use: production reasoning where local capacity is insufficient
- Config:
  ```yaml
  llm:
    provider: openai
    model: gpt-4o
    endpoint: https://api.openai.com/v1
    temperature: 0.2
    max_tokens: 4096
  ```

5. Prompt Delivery

- Prompts are built from GPROMPT-NNN templates by the orchestrator.
- The system prompt is sent verbatim; the user prompt is filled with inputs
  and PKG context.
- Tool calls are not used for reasoning; agents emit structured JSON that is
  validated against GSS-NNN schemas. Tools are reserved for filesystem and
  graph access where needed.

6. Response Parsing

- Every response is parsed as JSON when the prompt declares a JSON output.
- Parse failures are retried up to the declared retry limit.
- After retries, parse failure is reported to the orchestrator and the agent
  escalates per its spec.

7. Confidence Handling

- LLMs do not produce calibrated confidence. Genesis derives confidence from:
  - self-reported confidence in the structured output (if requested),
  - agreement across N samples at temperature > 0,
  - consistency with existing PKG assertions,
  - schema validation success.
- Confidence is recorded on every assertion; promotion to `Confirmed` requires
  meeting the threshold declared in the governing ontology or agent spec.

8. Caching

- Identical (prompt, config) pairs are cached by a hash key.
- Cache lives in `.genesis/cache/llm/` and is keyed by provider and model.
- A `--no-cache` flag bypasses the cache.
- Cache entries expire after the configured TTL (default 30 days).

9. Cost and Usage Tracking

- Every call records `usage` (prompt tokens, completion tokens) and provider.
- A usage log is written to `runtime/llm-usage.jsonl`.
- The CLI `genesis status` summarizes usage by agent and provider.

10. Failure Modes

- Provider unreachable: CLI exits 3 (dependency missing).
- Rate limit: retried with exponential backoff per the retry policy.
- Insufficient context window: the orchestrator truncates PKG context per the
  agent's declared priority and retries once.
- Unsanitized output: schema validation rejects it; the agent escalates.

11. Security

- No secrets in prompts.
- No PII sent to remote providers without explicit per-production consent in
  the brief's constraints.
- Local provider (LMStudio) is the default for productions with PII
  constraints.

12. Dependencies

- Prompts: GPROMPT-NNN set
- Agents: GAS-NNN set (declare model config per agent)
- Schemas: GSS-NNN set (output validation)
- CLI: GTOOL-001 (`--config` llm section)