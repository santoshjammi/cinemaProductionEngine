"""Movie OS configuration system.

The configuration system is the central nervous system of the Movie OS.
Every setting that was previously a CLI flag, hardcoded constant, or
magic number lives in `config/movie_os.yaml` (or wherever the user
points). The pipeline reads from this — not from code.

Public API:

    from movie_os.config import (
        load_config, load_config_from_dict, write_default_config,
        MovieOSConfig, ConfigError,
        # Enums
        LogLevel, QualityMode, AspectRatio, VideoCodec, AudioCodec,
        PipelineStep,
        # Sub-configs
        ProjectConfig, ProvidersConfig, CapabilitiesConfig,
        RenderingConfig, PipelineConfig,
        ProviderGroup, ProviderOption, CapabilityConfig,
    )

Usage:

    from movie_os.config import load_config
    config = load_config("config/movie_os.yaml")
    print(config.rendering.aspect_ratio)       # "16:9"
    print(config.providers.image.default)      # "sdxl_local"
    label, provider = config.provider_for("image")
    print(provider.settings["model"])          # "stabilityai/stable-diffusion-xl-base-1.0"
"""

from .schema import (
    SCHEMA_VERSION,
    MovieOSConfig,
    ProjectConfig,
    ProvidersConfig,
    CapabilitiesConfig,
    RenderingConfig,
    PipelineConfig,
    ProviderGroup,
    ProviderOption,
    CapabilityConfig,
    LogLevel,
    QualityMode,
    AspectRatio,
    VideoCodec,
    AudioCodec,
    PipelineStep,
)
from .loader import (
    load_config,
    load_config_from_dict,
    write_default_config,
    ConfigError,
)
from . import defaults


__all__ = [
    "SCHEMA_VERSION",
    "MovieOSConfig",
    "ProjectConfig",
    "ProvidersConfig",
    "CapabilitiesConfig",
    "RenderingConfig",
    "PipelineConfig",
    "ProviderGroup",
    "ProviderOption",
    "CapabilityConfig",
    "LogLevel",
    "QualityMode",
    "AspectRatio",
    "VideoCodec",
    "AudioCodec",
    "PipelineStep",
    "load_config",
    "load_config_from_dict",
    "write_default_config",
    "ConfigError",
    "defaults",
]
