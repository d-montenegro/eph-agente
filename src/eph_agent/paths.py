"""Resolución de rutas del repositorio, instalado o ejecutado desde ``src``."""

from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    """Devuelve la raíz del repo (o ``EPH_ROOT`` si está definida).

    Cuando el paquete se instala, ``__file__`` vive en site-packages y no sirve
    para ubicar ``semantic/``, ``config/`` o ``web/dist``. En ese caso se usa el
    directorio de trabajo o la variable ``EPH_ROOT``.
    """
    configured = os.environ.get("EPH_ROOT")
    if configured:
        return Path(configured).resolve()

    candidate = Path(__file__).resolve().parents[2]
    if (candidate / "semantic").is_dir():
        return candidate

    cwd = Path.cwd()
    if (cwd / "semantic").is_dir():
        return cwd.resolve()

    return candidate
