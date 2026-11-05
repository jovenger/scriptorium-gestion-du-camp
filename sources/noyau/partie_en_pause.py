
""






from __future__ import annotations

import re
import sys
import time
from pathlib import Path

TEXTE_AVEC_VEILLEUR = ("Scriptorium en pause : une partie a été chargée dans le jeu ouvert. Si c'est la dernière sauvegarde, le "
         "veilleur relance le jeu tout seul dessus (une à deux minutes) ; sinon, quittez et relancez le jeu.")

TEXTE_DU_JOUEUR = "Scriptorium en pause : une partie a été chargée dans le jeu ouvert. Quittez le jeu et relancez-le."
TEXTE = TEXTE_DU_JOUEUR if getattr(sys, "frozen", False) else TEXTE_AVEC_VEILLEUR
_MOTIF = re.compile(rb"scriptorium_partie_etrangere_(recule|avance|oui)")
_cache: dict = {"t": 0.0, "taille": -1, "sens": None, "journal": None}


def _journal() -> Path | None:
    if _cache["journal"] is None:
        try:
            from noyau import jeu
            inst = jeu.trouver_jeu()
            _cache["journal"] = inst.journal if inst else None
        except Exception:
            return None
    return _cache["journal"]


def sens(journal: Path | None = None) -> str | None:
    ""
    j = journal or _journal()
    if j is None:
        return None
    try:
        taille = j.stat().st_size
    except OSError:
        return None
    if journal is None and taille == _cache["taille"] and time.time() - _cache["t"] < 10:
        return _cache["sens"]
    try:
        m = _MOTIF.search(j.read_bytes())
    except OSError:
        return None
    s = m.group(1).decode() if m else None
    if journal is None:
        _cache.update(t=time.time(), taille=taille, sens=s)
    return s
