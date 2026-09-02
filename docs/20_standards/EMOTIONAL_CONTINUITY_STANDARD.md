# Emotional Continuity Standard

**Version:** 1.0

## Principle

Emotion must evolve causally from scene to scene.

Do not assign independent mood labels to scenes and hope the sequence feels coherent.

## Required scene state

```yaml
scene_state:
  scene_id:
  entry:
    mark_emotion:
    sarah_emotion:
    relationship_distance:
    unresolved_question:
  pressure:
    event:
    interpretation:
  turning_point:
    new_information:
    changed_interpretation:
  exit:
    mark_emotion:
    sarah_emotion:
    relationship_distance:
    decision:
    unresolved_question:
    next_scene_cause:
```

## Rule

The next scene's entry state must derive from:

- the previous scene's exit; or
- an explicitly declared off-screen event/time transition.

## Emotional progression

Good progression can include reversal.

Example:

```text
irritated → confused → concerned → defensive → ashamed → honest → cautiously relieved
```

Bad progression:

```text
sad → sad → sad → sad → healing
```

Intensity alone is not progression.

## Relationship distance

For relationship cinema, track an abstract distance state if useful.

Example:

```yaml
relationship_distance:
  scale: 0.0_to_1.0
  entry: 0.55
  exit: 0.42
  reason: "Sarah learns Mark's silence is connected to work fear rather than disinterest."
```

This is a planning aid, not a clinical metric.

## Blocking failures

- emotional state jumps without cause;
- a character forgets a discovery from the previous scene;
- repair appears without acknowledged injury;
- anger disappears because the screenplay needs a tender ending;
- a multi-part story resets characters at the start of the next part.
