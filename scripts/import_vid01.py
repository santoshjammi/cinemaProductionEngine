#!/usr/bin/env python3
"""Parse VID01.md and import it as a completed pipeline via /api/v1/pipeline/import."""
import json
import sys
import urllib.request
import urllib.error

VID01_SCRIPT = {
    "topic": "The Night He Stopped Reaching For Her - Emotional Withdrawal",
    "story": {
        "title": "The Night He Stopped Reaching For Her",
        "logline": "A man slowly stops reaching for the woman he loves - not because he stopped loving her, but because intimacy stopped feeling safe.",
        "synopsis": "An emotionally immersive portrait of how emotional withdrawal happens quietly between two people who still love each other. Through five acts, we witness the exact night it begins, the invisible daily distance, the internal collapse of emotional safety, the defensive retreat into self-protection, and the final tragic truth that distance is not anger - it is grief.",
        "emotional_tone": "melancholic",
        "themes": ["emotional withdrawal", "intimacy", "self-protection", "grief", "masculine vulnerability"],
        "target_audience": "adults navigating emotional distance in relationships",
        "research_context": None,
    },
    "scenes": [
        {
            "scene_number": 1,
            "title": "Opening Hook - The Night It Happens",
            "description": "Dark bedroom. Phone glow lighting half his face. His wife asleep beside him. He almost reaches toward her. Stops. Pulls hand back.",
            "location": "dark bedroom, night",
            "characters": ["Husband", "Wife"],
            "emotional_beat": "emotional tension, restraint",
            "duration": "40s",
        },
        {
            "scene_number": 2,
            "title": "The Outside Version - Nothing Looks Wrong",
            "description": "Daily life montage: driving silently, working late, eating dinner quietly, folding laundry, scrolling phone in darkness, polite interactions. No overt conflict. Physical closeness with emotional distance.",
            "location": "various domestic spaces - car, office, kitchen, laundry room",
            "characters": ["Husband", "Wife"],
            "emotional_beat": "invisible distance, quiet withdrawal",
            "duration": "80s",
        },
        {
            "scene_number": 3,
            "title": "The Internal Collapse - Vulnerability Becomes Dangerous",
            "description": "Close emotional realism: sitting alone in parked car, staring at unread messages, reheating coffee, pausing outside bedroom, shower scene with no music, mirror avoidance. The quiet kind of rejection that changes people slowly.",
            "location": "parked car, kitchen, hallway, bathroom",
            "characters": ["Husband"],
            "emotional_beat": "accumulated shame, loss of emotional safety",
            "duration": "150s",
        },
        {
            "scene_number": 4,
            "title": "The Defensive Retreat - Self-Protection",
            "description": "Emotional numbness: gaming alone, late-night scrolling, pretending to sleep, emotionally flat conversations, empty routines. He stops trying, stops risking embarrassment, stops reaching first.",
            "location": "living room, bedroom, dimly lit spaces",
            "characters": ["Husband", "Wife"],
            "emotional_beat": "numbness, avoidance conditioning, self-protection",
            "duration": "90s",
        },
        {
            "scene_number": 5,
            "title": "The Final Truth - Distance Is Grief",
            "description": "Bedroom again, parallel to opening. Both awake, emotionally distant, inches apart, worlds apart. His hand rests near hers. Doesn't touch. Fade to black.",
            "location": "dark bedroom, night",
            "characters": ["Husband", "Wife"],
            "emotional_beat": "grief, emotional resolution, tragic stillness",
            "duration": "90s",
        },
    ],
    "dialogues": [
        {
            "scene_number": 1,
            "dialogues": [
                {
                    "character": "Narrator",
                    "dialogue": "Nobody notices the exact night it happens. The night a man stops reaching for the woman he loves. Not because he stopped loving her. But because somewhere along the way... intimacy stopped feeling safe.",
                    "emotion": "melancholic",
                    "delivery": "low, restrained voice",
                },
            ],
        },
        {
            "scene_number": 2,
            "dialogues": [
                {
                    "character": "Narrator",
                    "dialogue": "From the outside, nothing looks wrong. They still talk. Still laugh sometimes. Still share a bed. Still remember groceries and birthdays and school meetings. But emotional distance rarely arrives like an explosion. It arrives quietly. Through hesitation. Through accumulated silence. Through moments too small to defend... but too painful to forget.",
                    "emotion": "reflective",
                    "delivery": "measured, contemplative",
                },
            ],
        },
        {
            "scene_number": 3,
            "dialogues": [
                {
                    "character": "Narrator",
                    "dialogue": "People assume men stop initiating intimacy because they lose attraction. Sometimes that's true. But often... what disappears first isn't desire. It's emotional safety. Rejection changes people slowly. Especially the quiet kind. The kind that never becomes a fight. A sigh. A delayed response. A tired expression. A moment that says: Not tonight. And after enough of those moments... vulnerability starts feeling dangerous.",
                    "emotion": "vulnerable",
                    "delivery": "slow, intimate, pained",
                },
            ],
        },
        {
            "scene_number": 4,
            "dialogues": [
                {
                    "character": "Narrator",
                    "dialogue": "So he adapts. He stops trying as often. Stops risking embarrassment. Stops reaching first. Not out of punishment. Out of self-protection. Because eventually the brain learns something dangerous: avoiding rejection hurts less than hoping for connection.",
                    "emotion": "resigned",
                    "delivery": "flat, defeated",
                },
            ],
        },
        {
            "scene_number": 5,
            "dialogues": [
                {
                    "character": "Narrator",
                    "dialogue": "The tragedy of emotional withdrawal is that it often happens between two people who still love each other. But love without emotional safety slowly becomes performance. And eventually... people stop reaching for places where they no longer feel emotionally wanted. Not all distance is anger. Sometimes distance is grief.",
                    "emotion": "grief",
                    "delivery": "quiet, final, sorrowful",
                },
            ],
        },
    ],
    "prompts": [
        {
            "scene_number": 1,
            "cinematic_prompt": "Dark bedroom at night, phone glow illuminating half of a man's face, his wife asleep beside him under white sheets, his hand almost reaching toward her then stopping and pulling back, shallow depth of field, muted blue and amber tones, intimate close-up, melancholic mood, cinematic lighting, 35mm film aesthetic, emotionally charged silence",
            "visual_style": "cinematic realism, moody chiaroscuro",
            "camera_angle": "close-up, eye level",
            "lighting": "low-key, phone glow practical light",
            "color_palette": ["deep blue", "warm amber", "shadow black", "muted white"],
        },
        {
            "scene_number": 2,
            "cinematic_prompt": "Montage of domestic life: man driving alone in car at dusk staring blankly, working late in dim office, eating dinner quietly across from wife at kitchen table, folding laundry mechanically, scrolling phone in dark room with blue screen glow, polite but distant conversation, emotional void between two physically close people, muted desaturated tones, medium shots, observational documentary style, melancholic suburban realism",
            "visual_style": "observational realism, desaturated",
            "camera_angle": "medium shots, static framing",
            "lighting": "natural practical, flat fluorescent",
            "color_palette": ["grey", "muted beige", "pale blue", "soft fluorescent white"],
        },
        {
            "scene_number": 3,
            "cinematic_prompt": "Man sitting alone in parked car at night staring at windshield, close-up of phone showing unread messages, reheating coffee alone in dim kitchen, pausing outside closed bedroom door hand on frame, shower scene with no music water running down face, avoiding mirror reflection, extreme emotional intimacy with isolation, tight close-ups, shallow focus, raw vulnerability, cold blue-green color grade, oppressive silence",
            "visual_style": "emotional realism, claustrophobic intimacy",
            "camera_angle": "extreme close-up, handheld",
            "lighting": "harsh practical, cold overhead",
            "color_palette": ["cold blue-green", "stark white", "deep shadow", "steam grey"],
        },
        {
            "scene_number": 4,
            "cinematic_prompt": "Man gaming alone in dark living room with TV blue glow on face, late-night phone scrolling in bed beside sleeping wife, pretending to sleep eyes open in darkness, emotionally flat conversation at kitchen table with no eye contact, empty mechanical routines, emotional numbness and avoidance, flat lighting, wide shots showing isolation within shared spaces, increasingly sparse frames, hollow atmosphere",
            "visual_style": "emotional numbness, sparse framing",
            "camera_angle": "wide shots, static distant",
            "lighting": "flat, dim, screen-lit",
            "color_palette": ["screen blue", "shadow grey", "empty black", "faint warm"],
        },
        {
            "scene_number": 5,
            "cinematic_prompt": "Dark bedroom at night parallel to opening, both husband and wife awake lying inches apart but emotionally worlds apart, his hand resting near hers on the white sheet not touching, the gap between their hands, tragic stillness, fade to black, deep emotional resonance, muted blue moonlight through curtains, intimate close-up on hands, devastating quiet, 35mm film grain, cinematic melancholy",
            "visual_style": "cinematic melancholy, tragic parallel",
            "camera_angle": "close-up on hands, overhead",
            "lighting": "moonlight, low-key natural",
            "color_palette": ["moonlit blue", "sheet white", "shadow black", "warm skin faint"],
        },
    ],
}


def main():
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/api/v1/pipeline/import"
    project_id = sys.argv[2] if len(sys.argv) > 2 else None

    payload = dict(VID01_SCRIPT)
    if project_id:
        payload["project_id"] = project_id

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        api_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            print(json.dumps(result, indent=2))
            print(f"\nPipeline ID: {result['id']}", file=sys.stderr)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()