import json, sys
from movie_os.genesis2.phases.phase10_validation import ValidationPhase
from movie_os.genesis2.phase_base import slice_phase_data

RUN = sys.argv[1]
pkg = json.load(open(f'{RUN}/genesis/production_knowledge_package.json'))

# Reconstruct context as the engine does
context = {"synopsis": pkg.get("synopsis", ""), "constraints": pkg.get("constraints", {})}
for r in pkg.get("phase_results", []):
    if r.get("status") == "completed" and r.get("knowledge"):
        context[f"phase_{r['phase_number']:02d}"] = r["knowledge"]

vp = ValidationPhase.__new__(ValidationPhase)
# slice_context truncates strings to max_str_len=1000
prev = vp.slice_context(context, [f"phase_{i:02d}" for i in range(1, 10)])
p08 = prev.get("phase_08", {})
print("phase_08 after slice_context:")
for k, v in p08.items():
    vs = str(v)
    print(f"  {k}: len={len(vs)} | tail: ...{vs[-80:]!r}")
