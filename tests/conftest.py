import os
from pathlib import Path
from typing import Any


_ORIGINAL_PATH_MKDIR = Path.mkdir


def pytest_configure(config: Any) -> None:
    if os.name != "nt" or getattr(Path, "_minigeo_mkdir_patched", False):
        return

    def windows_compatible_mkdir(
        self: Path,
        mode: int = 0o777,
        parents: bool = False,
        exist_ok: bool = False,
    ) -> None:
        # Python 3.14 on this Windows setup can create unreadable pytest tmp dirs with 0o700.
        if mode == 0o700:
            mode = 0o777
        return _ORIGINAL_PATH_MKDIR(self, mode=mode, parents=parents, exist_ok=exist_ok)

    Path.mkdir = windows_compatible_mkdir  # type: ignore[method-assign]
    Path._minigeo_mkdir_patched = True  # type: ignore[attr-defined]
