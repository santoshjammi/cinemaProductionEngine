import json, sys, os
sys.path.insert(0, '.')

# 1. Setup Directories for the Slice
DIRS = ["pipeline/architect/scenes", "builder/scene_4/{image,audio}", "quarantine"]
for d in DIRS:
    os.makedirs(d, exist_ok=True)

# 2. Load Contract and Context
with open('pipeline/contracts/narrative_contract.json') as f:
    contract = json.load(f)

ctx_capsule = {
    'production_id': contract['production_id'],
    'contract_version': contract.get('contract_version', '1.0'),
    'immutable_constraints': {
        'characters': [c['id'] for c in contract['characters']],
        'ending_type': contract['ending'],
        'mechanism': contract.get('core_conflict', {}).get('mechanism'),
        'tone_tags': contract['tone']
    },
    'parent_memory': {
        'story_id': contract.get('story_id'),
        'stage': 'lost_emotional_safety'
    }
}

# 3. Generate Scene 4 Artifacts (Simulated Architect Output)
scene_4_artifacts = {
    "artifact_id": "SCENE-EW001-04",
    "dialogue": [
        {"speaker_id": "CHAR-SARAH", "text": "I just want to know what's wrong. You've been distant for weeks."},
        {"speaker_id": "CHAR-MARK", "text": "Nothing's wrong. I'm just... tired."}
    ],
    "screenplay_block": {
        "slug": "INT LIVING ROOM - NIGHT",
        "action": "SARAH reaches for Mark's hand across the table. He pulls back, looking at the wall.",
        "dialogue_sarah": "I just want to know what's wrong. You've been distant for weeks.",
        "dialogue_mark": "Nothing's wrong. I'm just... tired."
    },
    "image_prompt": "Medium close-up — warm lighting. SARAH reaches for MARK across a table. MARK pulls his hand back abruptly, staring at the wall. Tension between them.",
    "video_motion": "Sarah reaches forward. Mark flinches away and turns to the wall. Silence holds for 5 seconds.",
    "audio_cues": {
        "speaker": "CHAR-SARAH",
        "emotion": "cautious_hope turning into hurt",
        "pause_after_line": 3
    }
}

# 4. Validate Artifacts against the Contract (Simulated Guardian)
report = {'status': 'accepted', 'violations': [], 'builder_admission': 'approved'}
content_str = json.dumps(scene_4_artifacts).lower()

if 'reconciliation' in content_str or 'repair' in content_str:
    report['violations'].append('ENDING_CHANGED')
    report['status'] = 'rejected'
    report['builder_admission'] = 'denied'

# 5. Write to Filesystem (Sealed Package)
os.makedirs('packages/ew001/scene_4', exist_ok=True)
with open('packages/ew001/manifest.json', 'w') as f:
    json.dump({
        "production_id": "EW001",
        "validation_status": report['status'],
        "package_sealed": True,
        "builder_admission": report['builder_admission']
    }, f)

print("--- SCENE 4 VERTICAL SLICE RESULT ---")
print(f"Context Mechanism: {ctx_capsule['immutable_constraints']['mechanism']}")
print(f"Parent Stage Injected: {ctx_capsule['parent_memory']['stage']}")
print(f"Guardian Status: {report['status']}")
print(f"Builder Admission: {report['builder_admission']}")

if report['status'] == 'rejected':
    print(f"[!] Failed validation: {report['violations']}")
else:
    print("[OK] Scene 4 passed all checks. Ready for rendering.")
