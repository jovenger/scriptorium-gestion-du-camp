
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









_RETIRE = (b"scriptorium_retrait_du_mod_fait-", b"scriptorium_partie_retiree")
_ACTIF = (b"scriptorium_agent_demarre_v", b"scriptorium_agent_repris_g", b"scriptorium_retrait_du_mod_partie-non-retiree")

TEXTE_RETIRE = ("Le mod a été retiré de cette partie et n'y fait plus rien : les ordres du programme ne partiraient plus, ses "
                "pages sont donc arrêtées. Quittez le jeu, puis enlevez le mod. Pour une autre partie avec le mod, relancez le jeu.")
_cache_retire: dict = {"t": 0.0, "taille": -1, "retire": False}


def retire_dans(donnees: bytes) -> bool:
    ""
    dernier_retrait = max(donnees.rfind(m) for m in _RETIRE)
    dernier_depart = max(donnees.rfind(m) for m in _ACTIF)
    return dernier_retrait >= 0 and dernier_retrait > dernier_depart


def retire(journal: Path | None = None) -> bool:
    ""
    j = journal or _journal()
    if j is None:
        return False
    try:
        taille = j.stat().st_size
    except OSError:
        return False
    if journal is None and taille == _cache_retire["taille"] and time.time() - _cache_retire["t"] < 10:
        return _cache_retire["retire"]
    try:
        r = retire_dans(j.read_bytes())
    except OSError:
        return False
    if journal is None:
        _cache_retire.update(t=time.time(), taille=taille, retire=r)
    return r


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
