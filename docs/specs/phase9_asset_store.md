# Spec: Phase 9 — Asset & Knowledge Management

## Objective

Build a unified asset and knowledge store on top of Movie OS. Every
generated artifact (image, audio clip, music bed, SFX, video, even
prompt snippets and QA reports) becomes a first-class Asset with
metadata, tags, version history, and semantic search.

**Why SQLite + filesystem**: metadata queries need indexes (SQLite),
but the actual files belong on disk (cheap, version-controllable,
inspectable). The existing CharacterRegistry/EnvironmentRegistry are
already filesystem-based — this phase generalizes that pattern to
all assets.

**Why embeddings**: hundreds of generated images and audio clips
become impossible to navigate by filename alone. A semantic search
("show me all the lonely dark-room shots") is essential for the
creative review loop.

**Why full history**: a video is the result of dozens of regenerations.
Losing the prior versions means losing the ability to A/B compare or
revert when a "better" idea actually turns out worse.

**Success criteria**:
- `AssetStore` is the single source of truth for all generated
  artifacts (replaces direct file paths in agents)
- Every Asset has: id, type, path, tags, prompt, model, seed,
  created_at, version_of (chain of prior versions)
- Tag search returns assets matching any/all of N tags
- Embedding search ("semantic find") returns top-K assets by
  cosine similarity
- Version chain: rendering the same prompt twice creates v1 and
  v2 linked by `version_of`
- CLI: `python -m movie_os asset list/search/show/tag/rollback`
- Migration: existing CharacterRegistry/EnvironmentRegistry data
  becomes Asset records (backward compatible — old APIs still work)
- 40+ tests cover the AssetStore, embedding index, version chain

## Tech Stack

- **SQLite** (`sqlite3` stdlib + `sqlite-vec` extension) — metadata
  + vector index
- **sentence-transformers** (`>=2.2`) — text embeddings for prompts
  and captions
- **numpy** — vector math
- **Pillow** — image thumbnails
- **pydantic v2** — Asset schema
- **Python 3.11+**

## Commands

```bash
# Initialize the asset store (creates .movie_os/asset_store.db)
python -m movie_os asset init

# List all assets
python -m movie_os asset list --type image --limit 20

# Search by tag
python -m movie_os asset search --tag irreversible_moment --tag dark

# Semantic search
python -m movie_os asset find "a man sitting alone in a dark room"

# Show details
python -m movie_os asset show <asset_id>

# Tag an asset
python -m movie_os asset tag <asset_id> --add favorite --add v2

# Roll back to a prior version
python -m movie_os asset rollback <asset_id>
```

## Project Structure

```
movie_os/asset_store/
├── __init__.py
├── schema.py             # Asset, AssetType, AssetVersion Pydantic
├── store.py              # AssetStore — SQLite + filesystem
├── embeddings.py         # EmbeddingIndex — sqlite-vec wrapper
├── migrations.py         # Schema versioning
├── search.py             # Tag + semantic search
├── version_chain.py      # History + rollback
├── migrate_registries.py # CharacterRegistry/EnvironmentRegistry → Asset
└── cli.py                # CLI subcommands

movie_os/data/
├── assets.db             # SQLite (created on first run)
└── files/<asset_id>/     # Asset files
    ├── v1/
    │   └── image.png
    ├── v2/
    │   └── image.png
    └── thumbnail.jpg

movie_os/tests/
├── test_phase9_store.py
├── test_phase9_embeddings.py
├── test_phase9_search.py
├── test_phase9_versioning.py
└── test_phase9_migration.py
```

## Data Model

```python
class AssetType(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    MUSIC = "music"
    SFX = "sfx"
    PROMPT = "prompt"
    TIMELINE = "timeline"
    CHARACTER = "character"
    ENVIRONMENT = "environment"

class Asset(BaseModel):
    id: UUID
    type: AssetType
    path: Path                  # Symlink to current version
    tags: list[str]
    prompt: str | None
    model: str | None
    seed: int | None
    metadata: dict
    created_at: datetime
    updated_at: datetime
    current_version: int
    version_of: UUID | None     # If this is a v2 of another asset

class AssetVersion(BaseModel):
    id: UUID
    asset_id: UUID
    version: int
    path: Path                  # Immutable: files/v1/image.png
    created_at: datetime
    notes: str | None           # e.g. "increased denoise 0.6 → 0.8"
```

## SQLite Schema

```sql
CREATE TABLE assets (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  current_path TEXT NOT NULL,
  tags TEXT NOT NULL,         -- JSON array
  prompt TEXT,
  model TEXT,
  seed INTEGER,
  metadata TEXT,              -- JSON
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  current_version INTEGER NOT NULL DEFAULT 1,
  version_of TEXT,
  FOREIGN KEY (version_of) REFERENCES assets(id)
);

CREATE TABLE asset_versions (
  id TEXT PRIMARY KEY,
  asset_id TEXT NOT NULL,
  version INTEGER NOT NULL,
  path TEXT NOT NULL,
  created_at TEXT NOT NULL,
  notes TEXT,
  FOREIGN KEY (asset_id) REFERENCES assets(id)
);

CREATE INDEX idx_assets_type ON assets(type);
CREATE INDEX idx_assets_tags ON assets(tags);
CREATE INDEX idx_versions_asset ON asset_versions(asset_id);

-- Vector index for embeddings (sqlite-vec virtual table)
CREATE VIRTUAL TABLE asset_embeddings USING vec0(
  asset_id TEXT PRIMARY KEY,
  embedding float[384]        -- sentence-transformer dimension
);
```

## Code Style

```python
class AssetStore:
    def __init__(self, db_path: Path, files_dir: Path):
        self.db = sqlite3.connect(db_path)
        self.files_dir = files_dir

    def create(
        self,
        type: AssetType,
        source_path: Path,
        *,
        tags: list[str] | None = None,
        prompt: str | None = None,
        model: str | None = None,
        seed: int | None = None,
        metadata: dict | None = None,
    ) -> Asset:
        asset_id = uuid4()
        version = 1
        # Copy file to versioned location
        version_dir = self.files_dir / str(asset_id) / f"v{version}"
        version_dir.mkdir(parents=True)
        new_path = version_dir / source_path.name
        shutil.copy2(source_path, new_path)
        # Insert into DB
        ...
        return Asset(...)
```

- Use sqlite3 stdlib directly — no ORM
- One public method per user action (create, get, list, search, tag, version)
- Files are immutable per version — never overwrite v1 once written

## Testing Strategy

- **test_phase9_store.py**: create, get, list, delete, update
- **test_phase9_embeddings.py**: embed text, store embedding, query
  by similarity returns expected top-K
- **test_phase9_search.py**: tag search, AND/OR semantics, scoring
- **test_phase9_versioning.py**: create v1, update → v2, rollback
  restores v1 path
- **test_phase9_migration.py**: existing CharacterRegistry data
  appears as Character-type Assets
- Use `:memory:` SQLite for unit tests
- Coverage target: 80%

## Boundaries

- **Always do**: copy files into the asset store (never reference
  external paths), generate a thumbnail for image assets, embed
  the prompt on creation
- **Ask first**: changing the SQLite schema (after migrations exist),
  switching to a different embedding model
- **Never do**: delete versions (only mark `deleted=true`), store
  binary blobs in SQLite (files on disk only), call external APIs

## Phasing

- **9.1**: Schema, AssetStore CRUD, file copy on create, list/get
- **9.2**: Tag search, tag CLI
- **9.3**: EmbeddingIndex with sqlite-vec, semantic search CLI
- **9.4**: Version chain, rollback CLI
- **9.5**: Migration from CharacterRegistry/EnvironmentRegistry

## Open Questions

- (none — clarified with user)
