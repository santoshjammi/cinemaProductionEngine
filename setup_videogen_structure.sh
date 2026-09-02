#!/usr/bin/env bash

set -euo pipefail

echo "Creating videoGen canonical project structure..."

# -------------------------------------------------------------------
# Safety: run only from videoGen repository root
# -------------------------------------------------------------------

CURRENT_DIR="$(basename "$PWD")"

if [[ "$CURRENT_DIR" != "videoGen" ]]; then
  echo "ERROR: Run this script from the videoGen project root."
  echo "Current directory: $PWD"
  exit 1
fi

# -------------------------------------------------------------------
# Authoritative documentation
# -------------------------------------------------------------------

mkdir -p docs

# Existing authoritative docs should already contain:
# docs/00_governance
# docs/10_psychology
# docs/20_standards
# docs/30_app
# docs/40_contracts
# docs/50_execution
# docs/90_migration

# -------------------------------------------------------------------
# Canonical reusable assets
# -------------------------------------------------------------------

mkdir -p assets/canon/mark/visual_reference
mkdir -p assets/canon/mark/voice_reference

mkdir -p assets/canon/sarah/visual_reference
mkdir -p assets/canon/sarah/voice_reference

mkdir -p assets/canon/recurring_locations
mkdir -p assets/canon/recurring_props
mkdir -p assets/canon/music
mkdir -p assets/canon/sfx

# -------------------------------------------------------------------
# New production workspace
#
# IMPORTANT:
# Do NOT place old generated assets here.
# Only productions created under the new architecture belong here.
# -------------------------------------------------------------------

mkdir -p productions

# -------------------------------------------------------------------
# Legacy quarantine
# -------------------------------------------------------------------

mkdir -p legacy_outputs/benchmarks
mkdir -p legacy_outputs/old_renders
mkdir -p legacy_outputs/old_images
mkdir -p legacy_outputs/old_audio
mkdir -p legacy_outputs/old_video
mkdir -p legacy_outputs/old_misc

# Existing old documentation remains in:
mkdir -p unimportant_docs

# -------------------------------------------------------------------
# Runtime/application-owned directories
# These should contain generated/runtime state, never constitutional law.
# -------------------------------------------------------------------

mkdir -p runtime/cache
mkdir -p runtime/tmp
mkdir -p runtime/logs

# -------------------------------------------------------------------
# Optional local working areas
# -------------------------------------------------------------------

mkdir -p workspace/imports
mkdir -p workspace/exports

# -------------------------------------------------------------------
# Add .gitkeep files so empty canonical directories survive Git
# -------------------------------------------------------------------

find \
  assets/canon \
  productions \
  legacy_outputs \
  runtime \
  workspace \
  -type d \
  -empty \
  -exec touch {}/.gitkeep \;

# -------------------------------------------------------------------
# Legacy benchmark README
# -------------------------------------------------------------------

cat > legacy_outputs/benchmarks/README.md <<'EOF'
# Legacy Production Benchmarks

This directory contains selected pre-standardization outputs retained only
for comparison against the new videoGen production architecture.

These files have ZERO production authority.

DO NOT use them automatically as:

- character references
- voice references
- visual references
- production footage
- reusable scene assets
- canonical story material

A file placed here must exist only because it provides useful historical
quality comparison.

Example:

pre_standardization_continuous_film.mp4

Known legacy problems may include:

- character identity drift
- static-image dialogue
- inconsistent visual continuity
- weak lip sync
- synthetic performance
- dialogue repetition
- stale asset reuse
EOF

# -------------------------------------------------------------------
# Canon asset README
# -------------------------------------------------------------------

cat > assets/canon/README.md <<'EOF'
# Canonical Assets

This directory contains approved reusable identity assets.

Canonical assets must be explicitly approved and registered.

Examples:

- Mark visual reference
- Sarah visual reference
- Mark voice reference
- Sarah voice reference
- approved recurring locations
- approved recurring props

Generated assets do NOT become canonical merely because they look good.

Canon must correspond with the registries under:

docs/10_psychology/10_mark_sarah/
EOF

# -------------------------------------------------------------------
# Productions README
# -------------------------------------------------------------------

cat > productions/README.md <<'EOF'
# Productions

Only productions created under the current authoritative videoGen
architecture belong here.

Expected future structure:

EP-0001/
├── contract/
├── policy/
├── genesis/
├── runs/
├── oracle/
└── releases/

Do not create generic shared folders such as:

- outputs/latest
- images/latest
- audio/latest
- final_video.mp4

Production artifacts must be traceable through:

Episode → Policy Snapshot → PKP → Run → Asset → ORACLE → Release
EOF

echo
echo "Structure created successfully."
echo
echo "Canonical top-level structure:"
echo
echo "  docs/               authoritative law/design"
echo "  assets/canon/       approved reusable identities/assets"
echo "  productions/        new governed productions only"
echo "  legacy_outputs/     old generated artifacts"
echo "  unimportant_docs/   old documentation"
echo "  runtime/            cache/tmp/logs"
echo "  workspace/          manual import/export staging"
echo
echo "No existing files were moved or deleted."

