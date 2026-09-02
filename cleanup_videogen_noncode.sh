#!/usr/bin/env bash
set -euo pipefail

# videoGen repository hygiene script
# Scope: NON-CODE cleanup/consolidation only.
#
# Default: DRY RUN
# Apply:   ./cleanup_videogen_noncode.sh --apply
#
# This script DOES NOT touch:
# - *.py / *.js / *.ts / *.tsx source files
# - src/, backend/, frontend/, pipeline/, movie_os/, prometheus/, builder/
# - tests/
# - package.json / pyproject.toml / requirements.txt
# - .git metadata
# - models/
#
# It intentionally leaves ambiguous legacy runtime/code structures for a later
# dependency-aware code rationalization pass.

MODE="dry-run"
if [[ "${1:-}" == "--apply" ]]; then
  MODE="apply"
elif [[ "${1:-}" != "" && "${1:-}" != "--dry-run" ]]; then
  echo "Usage: $0 [--dry-run|--apply]"
  exit 2
fi

if [[ "$(basename "$PWD")" != "videoGen" ]]; then
  echo "ERROR: Run this from the videoGen repository root."
  echo "Current directory: $PWD"
  exit 1
fi

echo "============================================================"
echo " videoGen NON-CODE cleanup"
echo " Mode: $MODE"
echo " Root: $PWD"
echo "============================================================"
echo

do_cmd() {
  if [[ "$MODE" == "apply" ]]; then
    "$@"
  else
    printf '[DRY-RUN] '
    printf '%q ' "$@"
    printf '\n'
  fi
}

ensure_dir() {
  if [[ "$MODE" == "apply" ]]; then
    mkdir -p "$1"
  else
    echo "[DRY-RUN] mkdir -p '$1'"
  fi
}

move_path() {
  local src="$1"
  local dst="$2"
  if [[ -e "$src" || -L "$src" ]]; then
    ensure_dir "$(dirname "$dst")"
    if [[ -e "$dst" || -L "$dst" ]]; then
      echo "SKIP: destination already exists: $dst"
    else
      do_cmd mv "$src" "$dst"
    fi
  fi
}

remove_path() {
  local p="$1"
  if [[ -e "$p" || -L "$p" ]]; then
    do_cmd rm -rf "$p"
  fi
}

remove_empty_dir() {
  local p="$1"
  if [[ -d "$p" ]]; then
    if [[ -z "$(find "$p" -mindepth 1 -maxdepth 1 ! -name '.DS_Store' -print -quit 2>/dev/null)" ]]; then
      do_cmd rm -rf "$p"
    else
      echo "KEEP: non-empty directory: $p"
    fi
  fi
}

echo "1) Remove OS/editor/Python generated debris"
echo "-------------------------------------------"

# macOS metadata
if [[ "$MODE" == "apply" ]]; then
  find . -name '.DS_Store' -type f -delete
else
  find . -name '.DS_Store' -type f -print | sed 's#^#[DRY-RUN] rm #'
fi

# Python bytecode/caches. Exclude .git just for paranoia.
if [[ "$MODE" == "apply" ]]; then
  find . -path './.git' -prune -o -type d -name '__pycache__' -prune -exec rm -rf {} +
  find . -path './.git' -prune -o -type f -name '*.pyc' -delete
  find . -path './.git' -prune -o -type d -name '.pytest_cache' -prune -exec rm -rf {} +
else
  find . -path './.git' -prune -o -type d -name '__pycache__' -print | sed 's#^#[DRY-RUN] rm -rf #'
  find . -path './.git' -prune -o -type f -name '*.pyc' -print | sed 's#^#[DRY-RUN] rm #'
  find . -path './.git' -prune -o -type d -name '.pytest_cache' -print | sed 's#^#[DRY-RUN] rm -rf #'
fi

echo
echo "2) Remove temporary setup/listing/package debris"
echo "------------------------------------------------"

remove_path "contents.txt"
remove_path "videoGen_authoritative_docs_v1.0.zip"

# The setup script has served its purpose, but it is retained because the user
# explicitly asked not to touch code/scripts yet.
echo "KEEP: setup_videogen_structure.sh (deferred; script/code cleanup later)"

# Empty accidental docs directory from previous merge.
remove_empty_dir "docs/20_app"

echo
echo "3) Consolidate preferred Mark/Sarah voice references"
echo "----------------------------------------------------"

ensure_dir "assets/canon/mark/voice_reference"
ensure_dir "assets/canon/sarah/voice_reference"

# Current naming strongly indicates Brian = Mark, Ava = Sarah.
# These are moved as reference candidates; the YAML registry should later bind hashes/IDs.
MARK_SRC="finalAudio-MarkAndSarah/voice_sample_brian.mp3"
SARAH_SRC="finalAudio-MarkAndSarah/voice_sample_ava.mp3"
MARK_DST="assets/canon/mark/voice_reference/mark_brian_reference.mp3"
SARAH_DST="assets/canon/sarah/voice_reference/sarah_ava_reference.mp3"

move_path "$MARK_SRC" "$MARK_DST"
move_path "$SARAH_SRC" "$SARAH_DST"

# Root copies exist in the repository listing. Remove only if byte-identical
# to the canonical destination after apply; in dry-run just report intent.
for pair in \
  "voice_sample_brian.mp3|$MARK_DST" \
  "voice_sample_ava.mp3|$SARAH_DST"
do
  src="${pair%%|*}"
  dst="${pair##*|}"

  if [[ -f "$src" ]]; then
    if [[ "$MODE" == "apply" ]]; then
      if [[ -f "$dst" ]] && cmp -s "$src" "$dst"; then
        rm -f "$src"
        echo "REMOVED duplicate: $src"
      else
        echo "KEEP: $src (not byte-identical to canonical target)"
      fi
    else
      echo "[DRY-RUN] compare '$src' with '$dst'; remove source only if identical"
    fi
  fi
done

remove_empty_dir "finalAudio-MarkAndSarah"

echo
echo "4) Quarantine pre-standardization production data"
echo "-------------------------------------------------"

# productions/ should contain only productions created under the new authority model.
if [[ -d "productions/psychological/ew001" ]]; then
  move_path \
    "productions/psychological/ew001" \
    "legacy_outputs/old_misc/pre_standardization_productions/psychological/ew001"
fi
remove_empty_dir "productions/psychological"

echo
echo "5) Consolidate legacy architecture documents still at repository root"
echo "--------------------------------------------------------------------"

LEGACY_ARCHIVE="unimportant_docs/root_legacy_architecture_2026-07-21"
ensure_dir "$LEGACY_ARCHIVE"

# These are documentation artifacts from the superseded July architecture wave.
# Exact filenames are used intentionally; no source code is matched.
legacy_docs=(
  "00 — Cinema Production Engine Vision, Philosophy & Reference Architecture.md"
  "002 — Director Intelligence & Creative Reasoning Architecture Specification.md"
  "003 — Creative Intent Specification (CIS) Architecture.md"
  "004 — Creative Object Model (COM) & Semantic Architecture Specification.md"
  "005 — Cognitive Intelligence Architecture & Creative Faculties Specification.md"
  "006 — Artificial Creative Intelligence Constitution & Architectural Governance.md"
  "007 — Creative Intent Record (CIR) Architecture.md"
  "008 — GENESIS Compiler Architecture.md"
  "009 — Production Knowledge Package (PKP) Architecture.md"
  "010 — PROMETHEUS Runtime Architecture.md"
  "011 — ORACLE Validation Architecture.md"
  "012 — ATLAS Knowledge Architecture.md"
  "013 — Repository & Metadata Architecture.md"
  "014 — Governance & Constitutional Compliance Engine.md"
  "015 — Architecture Registry.md"
  "016 — Machine Readable Architecture Metadata.md"
  "017 — Constitutional Validation Rules.md"
  "018 — GENESIS Developer Platform.md"
  "REPO_MAP.md"
)

for f in "${legacy_docs[@]}"; do
  if [[ -f "$f" ]]; then
    move_path "$f" "$LEGACY_ARCHIVE/$f"
  fi
done

echo
echo "6) Remove empty legacy placeholders that contain no implementation"
echo "-----------------------------------------------------------------"

# Both names currently exist as empty or effectively empty placeholders.
remove_empty_dir "move-os"
remove_empty_dir "move_os/domain"
remove_empty_dir "move_os"

# Old empty asset placeholder
remove_empty_dir "assets/characters"

echo
echo "7) Generated Hermes image inspections"
echo "-------------------------------------"
echo "KEEP: .hermes/* (tool state). Not touched automatically."
echo "      latest_scene_frames/ and evolution_frames can be deleted later"
echo "      after confirming Hermes does not depend on them."

echo
echo "8) Explicitly DEFERRED until code dependency analysis"
echo "-----------------------------------------------------"

cat <<'EOF'
The following are intentionally NOT touched yet because moving/removing them can
break imports, tests, runtime paths, or developer tooling:

CODE / RUNTIME TREES
  movie_os/
  prometheus/
  pipeline/
  src/
  backend/
  frontend/
  builder/
  story_factory/
  openmontage_adapter/
  scripts/
  audio/
  config/
  packages/
  e2e/
  tests/
  models/

POTENTIALLY CODE-REFERENCED DATA / LEGACY WORK AREAS
  artifacts/
  images/
  synopsis/
  scene_blueprints/
  exports/
  quarantine/
  gir_examples/
  grammar/
  stories/
  videoContentStructure/
  memory/
  projects/
  skills/
  .ai/
  .aios/
  .intelligence/
  .project-ai/
  .hermes/

ROOT RUNNERS / UTILITIES
  generate_films.py
  enrich_dialogue.py
  run_prometheus_hq.py
  run_space_between_us.py
  render_space_between_us.py
  quality_gate.py
  phase1_visual_integ.py
  final_launch_comfyui.py
  launch_v*.py
  launch_comfyui.py
  generate_scene4_flux_workflow.py
  build_scene_4.py
  test_vertical_slice.py
  run_pipeline*.py
  run_production.py
  run_genesis*.py
  render_v5.py
  run_genesis_to_prometheus.py
  download_flux*.py
  verify_pipeline.py
  fix_movie_os.py

OLD TOP-LEVEL PROJECT DOCS THAT MAY STILL BE REFERENCED BY TOOLING
  README.md
  ARCHITECTURE.md
  PIPELINE.md
  PROJECT_STATUS.md
  PENDING_ISSUES.md
  LOCAL_DEPLOYMENT_BRIEF.md
  SPEC.md
  TECH_STACK.md
  TESTING.md
  etc.

DEPENDENCY / ENVIRONMENT DIRECTORIES
  node_modules/
  venv/

These should be handled only after a repository import/reference scan.
EOF

echo
echo "9) Important manual warning: .git size"
echo "--------------------------------------"
cat <<'EOF'
The repository listing shows a very large temporary Git pack file:

  .git/objects/pack/tmp_pack_z4ftrE   (~4.5 GB)

DO NOT delete it through this script.

First run a Git integrity check in a separate maintenance step:
  git fsck --full

Then decide whether to clean abandoned temporary pack data / run git gc.
Git metadata cleanup is intentionally outside this script.
EOF

echo
echo "============================================================"
if [[ "$MODE" == "dry-run" ]]; then
  echo "DRY RUN COMPLETE."
  echo "Review the commands above, then run:"
  echo "  ./cleanup_videogen_noncode.sh --apply"
else
  echo "NON-CODE CLEANUP COMPLETE."
fi
echo "============================================================"
