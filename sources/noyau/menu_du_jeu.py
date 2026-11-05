
""





from __future__ import annotations

import sys
import threading
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
ORDRE_DES_ATTENTES = "scriptorium.statut.fiche_pour = nil scriptorium.gestion_native.lettre_attendue = nil return 1"
ORDRE = ("scriptorium.statut.fiche_pour = nil scriptorium.gestion_native.lettre_attendue = nil "
         "if scriptorium.gestion_native.ouvert then scriptorium.gestion_native.fermer() end return 1")


ESSAI = False
ORDRES_DE_L_ESSAI = 0


def refermer(ordre: str = ORDRE, attente: int = 10) -> threading.Thread | None:
    global ORDRES_DE_L_ESSAI
    if ESSAI:
        ORDRES_DE_L_ESSAI += 1
        return None

    def fil() -> None:
        try:
            for d in (RACINE, RACINE / "outils_de_session"):
                if str(d) not in sys.path:
                    sys.path.insert(0, str(d))
            from essais.cycle_en_jeu import Jeu
            from dire import parler
            parler(Jeu(), ordre, attente)
        except Exception:
            pass
    t = threading.Thread(target=fil, daemon=True)
    t.start()
    return t
