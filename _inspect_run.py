import json, sys
from movie_os.genesis2.requirement_manifest import map_scene_to_requirements
RUN = sys.argv[1]
brief = json.load(open(f'{RUN}/genesis/movie_os_brief.json'))
print('=== scenes + mapped reqs ===')
for s in brief.get('scenes', []):
    print(f"  {s.get('number')}. {s.get('title')} | act={s.get('act')} | realized={map_scene_to_requirements(s)}")
    sd = (s.get('scene_description') or '')
    print(f"     desc: {sd[:150]}")
print()
print('=== dialogues per scene ===')
for d in brief.get('dialogues', []):
    print('  scene', d.get('scene_number'), '| lines:', len(d.get('lines',[])), '| inner:', len(d.get('inner_voice',[])))
    for ln in d.get('lines', [])[:3]:
        print(f"     [{ln.get('speaker')}] {ln.get('text','')[:80]}")
