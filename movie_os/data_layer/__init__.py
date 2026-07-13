"""Movie OS Data Layer — persistent character and environment storage.

Public API:

    from movie_os.data_layer import (
        CharacterRegistry, get_character_registry,
        EnvironmentRegistry, get_environment_registry,
        EntityStorage,
        # Default seeds
        seed_default_characters, seed_default_environments,
        make_ethan_morrison, make_claire_morrison, make_bedroom_morrison,
    )

    # Save a character
    from movie_os.domain import CharacterDNA, PhysicalAppearance, Gender
    char = CharacterDNA(
        key="jane_doe",
        name="Jane Doe",
        physical=PhysicalAppearance(age=30, gender=Gender.FEMALE, ...),
    )
    char_reg = get_character_registry()
    char_reg.save(char)
    char_reg.save_hero_image("jane_doe", "/path/to/hero.png")

    # Use the hero image for img2img / IPAdapter consistency
    hero_path = char_reg.get_hero_image_path("jane_doe")
    if hero_path:
        ImageIntent(prompt="...", reference_image_paths=[str(hero_path)])

    # Seed the default emotional_withdrawal characters
    from movie_os.data_layer import seed_default_characters, seed_default_environments
    char_reg = get_character_registry()
    env_reg = get_environment_registry()
    seed_default_characters(char_reg)
    seed_default_environments(env_reg)
"""

from .storage import EntityStorage
from .character_registry import CharacterRegistry
from .character_registry import get_default_registry as get_character_registry
from .character_registry import set_default_registry as set_character_registry
from .environment_registry import EnvironmentRegistry
from .environment_registry import get_default_registry as get_environment_registry
from .environment_registry import set_default_registry as set_environment_registry
from .seeds import (
    seed_default_characters, seed_default_environments,
    make_ethan_morrison, make_claire_morrison, make_bedroom_morrison,
)

__all__ = [
    "EntityStorage",
    "CharacterRegistry", "get_character_registry", "set_character_registry",
    "EnvironmentRegistry", "get_environment_registry", "set_environment_registry",
    "seed_default_characters", "seed_default_environments",
    "make_ethan_morrison", "make_claire_morrison", "make_bedroom_morrison",
]
