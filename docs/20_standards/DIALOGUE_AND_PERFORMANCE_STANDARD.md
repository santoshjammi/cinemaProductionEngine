# Dialogue & Performance Standard

**Version:** 1.0  
**Applies to:** Dialogue-driven cinematic productions

## 1. Principle

Dialogue is a character action that changes story state.

It is not explanatory text placed over generated images.

## 2. Required dialogue-turn semantics

For important turns, GENESIS should be able to represent:

```yaml
dialogue_turn:
  line_id: SC04-MARK-03
  speaker: MARK
  text: "..."
  response_to: SC04-SARAH-02
  surface_intention: end_the_conversation
  hidden_need: reassurance_without_admitting_need
  emotional_state_before: guarded
  delivery:
    pace: restrained
    volume: low
    hesitation: true
  physical_action: looks_at_plate
  partner_effect: Sarah_reconsiders_her_assumption
  next_story_effect: Sarah_switches_from_accusation_to_question
```

Not every line requires maximal metadata. Story-critical lines do.

---

## 3. Human dialogue rules

Prefer:

- contractions;
- incomplete thoughts;
- reasonable hesitation;
- character-specific wording;
- occasional interruption;
- silence;
- mundane detail when it grounds the scene;
- reactions that are not immediate perfect understanding.

Avoid:

- therapist speeches;
- motivational slogans;
- theme statements every scene;
- equal-length alternating turns;
- over-polished emotional vocabulary;
- dialogue that repeats narration;
- dialogue that repeats what the viewer already knows.

---

## 4. Scene progression test

At scene exit, at least one should change:

- knowledge;
- interpretation;
- emotional distance;
- decision;
- commitment;
- practical plan;
- trust;
- willingness to continue;
- unresolved question.

If nothing changes, revise or remove the scene.

---

## 5. Mark & Sarah example

### Weak

**Mark:** I withdraw because I am afraid of failing you.  
**Sarah:** You do not have to hide your fear. Vulnerability is strength.  
**Mark:** You're right. I should communicate.  
**Sarah:** We can face anything if we stay in the truth.

The problem is not the sentiment. It is that both characters sound like the author.

### Better direction

**Sarah:** You've checked that same email three times.

**Mark:** It's nothing.

She looks at him. He closes the laptop too quickly.

**Sarah:** Then why are you hiding the screen?

**Mark:** I'm not hiding it.

**Sarah:** Mark.

He exhales.

**Mark:** They cut two teams today.

Sarah's expression changes. Her irritation drops before her words do.

**Sarah:** Your team?

**Mark:** Not yet.

The story state changes because Sarah learns the actual pressure.

---

## 6. Validation failures

Block or revise when:

- multiple scenes have the same confession → reframe → acceptance rhythm;
- either character sounds consistently like a therapist;
- lines can be swapped between characters without noticeable difference;
- dialogue explains every emotion;
- a conversation has no consequence;
- dialogue exists only to satisfy a quota.

---

## 7. Silence

Silence is allowed when it is legible.

A silence should have:

- a reason;
- physical behavior;
- relational meaning;
- an effect on the next beat.

Silence is not empty runtime.
