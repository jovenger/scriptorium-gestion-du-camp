
""





from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QHeaderView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))
from noyau import chemins
from noyau.langue_du_programme import T


JOURNAL = chemins.journal_du_jeu()
MARQUE = "[ScriptoObjectifs] "
LECTURE = 5_000
QUEUE = 4_000_000

FOND, CARTE, ENCRE, OR, PALE = "#1d1813", "#2a231b", "#eadfc8", "#c9a24d", "#9c8f78"
VERT, ROUGE, ORANGE = "#8fbf6a", "#d9735b", "#d9a55b"
FAMILLES = {"economie": "Économie et trésorerie", "securite": "Sécurité et notoriété",
            "infrastructure": "Infrastructure et logistique", "recrutement": "Recrutement et entraînement"}
FACONS = {"gain": "gagné cette semaine", "niveau": "aujourd'hui", "plafond": "cette semaine (au plus)",
          "semaine": "cette semaine", "max": "cette semaine (au plus)"}
COLONNES = ["Famille", "Objectif", "Où il en est", "But", "État"]


def analyser(brut: str) -> dict | None:
    ""
    lignes = [l.split(MARQUE, 1)[1].rstrip() for l in brut.splitlines() if MARQUE in l]
    fin = max((i for i, l in enumerate(lignes) if l.startswith("fin|")), default=None)
    if fin is None:
        return None
    debut = max((i for i, l in enumerate(lignes[:fin]) if l.startswith("debut|")), default=None)
    if debut is None:
        return None
    d = lignes[debut].split("|")
    out = {"semaine": int(d[1]) if len(d) > 1 and d[1].lstrip("-").isdigit() else None,
           "jours": int(d[2]) if len(d) > 2 and d[2].isdigit() else None,
           "objectifs": [], "histoire": [], "avert_suite": 0, "sans_part": False}
    for l in lignes[debut + 1:fin]:
        c = l.split("|")
        if c[0] == "o" and len(c) >= 8:
            out["objectifs"].append({"famille": c[1], "cle": c[2], "texte": c[3], "facon": c[4],
                                     "valeur": c[5], "cible": c[6], "tenu": c[7] == "1"})
        elif c[0] == "h" and len(c) >= 6:
            out["histoire"].append({"n": int(c[1]), "reussis": int(c[2]), "total": int(c[3]), "prime": int(c[4]),
                                    "avert": c[5] == "1"})
        elif c[0] == "a" and len(c) >= 3:
            out["avert_suite"], out["sans_part"] = int(c[1]), c[2] == "1"
    return out


def lire() -> dict | None:
    try:
        with open(JOURNAL, "rb") as f:
            f.seek(0, 2)
            taille = f.tell()
            f.seek(max(0, taille - QUEUE))
            brut = f.read().decode("utf-8", "replace")
    except OSError:
        return None
    return analyser(brut)


class OngletObjectifs(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setStyleSheet(f"background:{FOND}; color:{ENCRE};")
        v = QVBoxLayout(self)
        self.titre = QLabel(T("Les objectifs du Directeur"))
        self.titre.setStyleSheet(f"color:{OR}; font-size:18px; font-weight:bold;")
        v.addWidget(self.titre)
        self.resume = QLabel(T("En attente du jeu…"))
        self.resume.setWordWrap(True)
        v.addWidget(self.resume)
        self.table = QTableWidget(0, len(COLONNES))
        self.table.setHorizontalHeaderLabels([T(_x) for _x in COLONNES])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(f"background:{CARTE};")
        v.addWidget(self.table, 2)
        h = QLabel(T("L'historique des semaines"))
        h.setStyleSheet(f"color:{OR}; font-size:15px; font-weight:bold;")
        v.addWidget(h)
        self.histoire = QLabel("")
        self.histoire.setWordWrap(True)
        v.addWidget(self.histoire, 1)
        self.minuterie = QTimer(self)
        self.minuterie.timeout.connect(self.actualiser)
        self.minuterie.start(LECTURE)
        self.donnees = None

    def actualiser(self) -> None:
        d = lire()
        if d is None or d == self.donnees:
            return
        self.donnees = d
        self.montrer(d)

    def montrer(self, d: dict) -> None:
        obj = d["objectifs"]
        self.table.setRowCount(len(obj))
        for i, o in enumerate(obj):
            valeurs = [FAMILLES.get(o["famille"], o["famille"]), o["texte"],
                       T("{0} ({1})", o['valeur'] or '—', FACONS.get(o['facon'], '')), o["cible"],
                       "atteint" if o["tenu"] else "pas encore"]
            for j, val in enumerate(valeurs):
                it = QTableWidgetItem(T(str(val)))
                if j == 4:
                    it.setForeground(QColor(VERT if o["tenu"] else ORANGE))
                self.table.setItem(i, j, it)
        self.table.resizeColumnsToContents()
        tenus = sum(1 for o in obj if o["tenu"])
        jours = d.get("jours")
        txt = (T("Semaine {0} : {1} objectif(s) atteint(s) sur {2}", d['semaine'], tenus, len(obj))
               + (T(", {0} jour(s) avant le bilan du Superviseur.", jours) if jours is not None else "."))
        txt += T(" Tous atteints : le Directeur touche une prime. Sinon : un avertissement officiel.")
        if d.get("avert_suite"):
            txt += T(" Avertissements d'affilée : {0} (au 3e, il perd sa part sur le bénéfice une semaine).", d['avert_suite'])
        if d.get("sans_part"):
            txt += T(" Cette semaine, le Directeur n'a PAS de part sur le bénéfice.")
        self.resume.setText(T(txt))
        lignes = []
        for h in d["histoire"]:
            if h["avert"]:
                lignes.append(T("Semaine {0} : {1} sur {2} — avertissement officiel.", h['n'], h['reussis'], h['total']))
            else:
                lignes.append(T("Semaine {0} : {1} sur {2} — prime de {3} gros.", h['n'], h['reussis'], h['total'], h['prime']))
        self.histoire.setText(T("\n".join(lignes) or "Aucune semaine terminée pour l'instant."))
