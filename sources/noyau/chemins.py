
""








from __future__ import annotations

import os
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
FICHIER_DU_DOSSIER_DU_JEU = "dossier_du_jeu.txt"


def gele() -> bool:
    ""
    return bool(getattr(sys, "frozen", False))


def dossier_local() -> Path:
    ""
    if not gele():
        return RACINE / "local"
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or str(Path.home())
    return Path(base) / "Scriptorium" / "Gestion du camp"


def dossier_du_jeu_retenu() -> Path | None:
    ""
    try:
        texte = (dossier_local() / FICHIER_DU_DOSSIER_DU_JEU).read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return Path(texte) if texte else None


def retenir_le_dossier_du_jeu(dossier: str | os.PathLike) -> None:
    d = dossier_local()
    d.mkdir(parents=True, exist_ok=True)
    (d / FICHIER_DU_DOSSIER_DU_JEU).write_text(str(dossier), encoding="utf-8")


def journal_du_jeu() -> Path:
    ""
    from noyau import jeu
    inst = jeu.trouver_jeu()
    return inst.journal if inst is not None else dossier_local() / "kcd.log"
