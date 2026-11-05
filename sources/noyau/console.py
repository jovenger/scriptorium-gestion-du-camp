
""

















from __future__ import annotations

import sys

_FAIT = False


def ouvrir_en_francais() -> bool:
    ""




    global _FAIT
    if _FAIT:
        return False
    _FAIT = True
    change = False
    for flux in (sys.stdout, sys.stderr):
        try:


            flux.reconfigure(encoding="utf-8", errors="replace")
            change = True
        except (AttributeError, ValueError, OSError):


            pass
    return change
