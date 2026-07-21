---
name: "compliance-and-safety"
mode: "guardrail"
version: "1.0"
---

# Compliance & Safety Policies (DPDP Reference)

## Core Principles
- **Data Minimization**: Collect only what is necessary for video generation contexts.
- **User Consent**: Ensure explicit user authorization for all persistent memory writes.
- **Right to Erasure**: All `memories/` and `contexts/` must be easily mappable for deletion requests.

## Operational Guardrails
- Do not persist sensitive PII in `.aios/memories/`.
- Always validate model outputs against content safety standards before delivery.
