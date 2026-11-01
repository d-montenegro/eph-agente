#!/usr/bin/env python3
"""Genera un hash PBKDF2 para config/users.yml sin escribir la contraseña."""

from __future__ import annotations

import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eph_agent.auth import hash_password  # noqa: E402


def main() -> int:
    password = getpass.getpass("Contraseña: ")
    if not password:
        print("La contraseña no puede estar vacía", file=sys.stderr)
        return 1
    print(hash_password(password))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
