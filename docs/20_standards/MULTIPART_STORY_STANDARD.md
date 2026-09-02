# Multi-Part Story Standard

**Version:** 1.0

## Constitutional principle

> A multi-part story may withhold resolution from the viewer, but production may not begin Part 1 without knowing the complete causal arc and intended final resolution.

## Required before Part 1

```yaml
multi_part_arc:
  arc_id:
  problem_family:
  sub_series:
  primary_mechanism:
  full_story_summary:
  final_logical_resolution:
  final_emotional_resolution:
  parts:
    - part_number:
      purpose:
      entry_state:
      turning_point:
      exit_state:
      unresolved_question:
```

## Part boundary rule

A part should end because:

- a meaningful realization occurred;
- a decision changed direction;
- a new fact recontextualized the problem;
- a practical consequence created the next phase.

Do not cut only because target runtime was reached.

## Commercial rule

A cliffhanger must be honest.

Bad:
> manufacturing an apparent breakup when the story never intended one.

Good:
> Part 1 ends when Sarah learns Mark's work situation is worse than she thought, shifting the next part from blame to shared decision-making.

## Continuity

Part N+1 must load Part N's exact exit state.

No emotional reset.
