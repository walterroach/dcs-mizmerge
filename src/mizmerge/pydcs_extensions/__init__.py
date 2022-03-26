from .a4ec import *


def load_mods() -> None:
    """Loads all mods.

    Note that this function doesn't *do* anything. Its purpose is to prevent editors
    from removing `import pydcs_extensions` when it is "unused", because mod imports
    have side effects (unit types are registered with pydcs).
    """
