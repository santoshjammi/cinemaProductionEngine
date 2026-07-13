"""Movie OS prompt system.

Pipeline:
  PromptTemplate (loaded from YAML)
       ↓
  PromptBuilder (assembles context from domain objects)
       ↓
  PromptOptimizer (tunes the prompt)
       ↓
  PromptValidator (checks constraints)
       ↓
  PromptRenderer (produces the final string)

The prompt system is the central nervous system of the Movie OS.
Every prompt the LLM sees comes from this system — no hardcoded
strings in source code.

Public API:

    from movie_os.prompts import (
        PromptTemplate,            # re-exported from domain
        load_prompt_template,      # load from YAML
        save_prompt_template,      # save to YAML
        load_all_prompts,          # load a whole directory
        PromptBuilder,             # build context from domain
        PromptOptimizer,           # tune the prompt
        PromptValidator,           # check constraints
        PromptRenderer,            # end-to-end render
        ValidationResult,          # result of validation
        PromptRepository,          # the central index
        PromptNotFoundError,       # raised when a prompt ID is missing
        get_default_repository,    # global default repo (bundled prompts)
        set_default_repository,    # override for testing
    )
"""

from movie_os.domain.prompt import PromptTemplate

from .loader import (
    load_prompt_template,
    save_prompt_template,
    load_all_prompts,
)
from .builder import PromptBuilder
from .optimizer import PromptOptimizer
from .validator import PromptValidator, ValidationResult
from .renderer import PromptRenderer
from .repository import (
    PromptRepository,
    PromptNotFoundError,
    get_default_repository,
    set_default_repository,
)

__all__ = [
    "PromptTemplate",
    "load_prompt_template",
    "save_prompt_template",
    "load_all_prompts",
    "PromptBuilder",
    "PromptOptimizer",
    "PromptValidator",
    "ValidationResult",
    "PromptRenderer",
    "PromptRepository",
    "PromptNotFoundError",
    "get_default_repository",
    "set_default_repository",
]
