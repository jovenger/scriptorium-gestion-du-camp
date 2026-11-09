
""





from __future__ import annotations

import sys
import time
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QHeaderView, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))
from noyau import chemins
from noyau.langue_du_programme import T


JOURNAL = chemins.journal_du_jeu()
MARQUE = "[ScriptoMetiers] "


_LECTEUR = RACINE / "choses" / "tableaux_vivants" / "lecteur.py"
SIGNE, LECTURE = 20_000, 1_000


from gestion_du_camp import habillage as hb
from gestion_du_camp.habillage import CARTE, ENCRE, OR, PALE, VERT, ROUGE, FOND

COLONNES = ["Métier", "Engagé", "Rapporté aux réserves", "Valeur rapportée", "Paye", "Entretien\ndes outils",
            "Bilan pour le camp", "Racheté par le coursier\nà sa place"]
NOMS_PRODUITS = {"choux": "choux", "betteraves": "betteraves", "oignons": "oignons", "oeufs": "œufs", "champignons": "champignons", "herbes": "herbes", "legumes": "légumes", "vivres": "vivres", "boisson": "boisson", "charbon": "charbon", "bois": "bois de chauffe",
                 "cuir": "cuir", "branches": "branches", "biere": "bière", "vin": "vin"}


def lire_le_journal(depuis: int = 0) -> dict | None:
    ""
    try:
        with open(JOURNAL, "rb") as f:
            f.seek(depuis)
            brut = f.read().decode("utf-8", "replace")
    except OSError:
        return None
    return analyser_le_journal(brut)


def analyser_le_journal(brut: str) -> dict | None:
    ""
    lignes = [l.split(MARQUE, 1)[1].rstrip() for l in brut.splitlines() if MARQUE in l]
    fin = max((i for i, l in enumerate(lignes) if l.startswith("fin|")), default=None)
    if fin is None:
        return None
    debut = max((i for i, l in enumerate(lignes[:fin]) if l.startswith("debut|")), default=None)
    if debut is None:
        return None
    d = lignes[debut].split("|")
    out = {"jour": int(d[1]) if len(d) > 1 else None, "bilans": {}, "sorties": {}}
    for l in lignes[debut + 1:fin]:
        c = l.split("|")
        if c[0] == "b" and len(c) >= 11:
            q = {}
            for morceau in c[10].split(","):
                if ":" in morceau:
                    p, n = morceau.split(":", 1)
                    q[p] = float(n)
            out["bilans"].setdefault(c[1], {"nom": c[2].replace("bucheron", "bûcheron"), "engage": c[3] == "1"})[c[4]] = {
                "valeur": float(c[5]), "paye": float(c[6]), "outils": float(c[7]), "relais": float(c[8]),
                "net": float(c[9]), "quantites": q}
        elif c[0] == "s" and len(c) >= 6:
            out["sorties"].setdefault(c[1], []).append({"jour": int(c[2]), "heure": float(c[3]), "texte": c[4],
                                                       "valeur": float(c[5])})
    return out


def gros(n: float) -> str:

    return f"{0 if abs(n) < 0.5 else n:,.0f}".replace(",", " ") + " gros"


def quantites(q: dict) -> str:
    return ", ".join(T("{0:.0f} {1}", n, NOMS_PRODUITS.get(p, p)) for p, n in sorted(q.items()) if n > 0) or "rien"


class OngletMetiers(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.journal: dict | None = None
        self.setStyleSheet(hb.feuille())
        v = QVBoxLayout(self)
        v.setContentsMargins(18, 16, 18, 16)
        v.setSpacing(10)
        haut = QHBoxLayout()
        entete = QLabel(T("Journal des métiers"))
        entete.setObjectName("Entete")
        haut.addWidget(entete)
        haut.addStretch(1)
        self.periode = QComboBox()
        self.periode.addItems([T("Les 7 derniers jours"), T("Depuis le début du journal")])
        self.periode.currentIndexChanged.connect(self.montrer)
        haut.addWidget(self.periode)
        b = QPushButton(T("Actualiser"))
        b.clicked.connect(self.actualiser)
        haut.addWidget(b)
        v.addLayout(haut)
        self.resume = QLabel("")
        self.resume.setObjectName("Note")
        self.resume.setWordWrap(True)
        v.addWidget(self.resume)
        self.table = QTableWidget(0, len(COLONNES))
        self.table.setHorizontalHeaderLabels([T(_x) for _x in COLONNES])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        v.addWidget(self.table, 1)
        titre = QLabel(T("Les dernières sorties"))
        titre.setObjectName("Section")
        v.addWidget(titre)
        self.sorties = QTableWidget(0, 4)
        self.sorties.setHorizontalHeaderLabels([T("Métier"), T("Quand"), T("La sortie"), T("Valeur rapportée")])
        self.sorties.verticalHeader().setVisible(False)
        self.sorties.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.sorties.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        v.addWidget(self.sorties, 1)
        note = QLabel(T("Rapporté : ce que le métier a déposé aux réserves, au prix des réserves. Paye : sa base par jour "
                      "engagé et sa part de ce qu'il rapporte. Entretien : les matières prises aux réserves pour son "
                      "outil (réparations, flèches). Bilan = valeur rapportée − paye − entretien. Racheté par le coursier : "
                      "ce qu'il a fallu acheter parce que le métier n'a pas suffi."))
        note.setObjectName("Note")
        note.setWordWrap(True)
        v.addWidget(note)


    def _demarrer_le_vivant(self) -> None:
        if getattr(self, "_suiveur", None) is None:
            import importlib.util
            spec = importlib.util.spec_from_file_location("tableaux_vivants_lecteur_m", _LECTEUR)
            lv = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lv)
            self._suiveur = lv.Suiveur(JOURNAL)
            self._tampon: list[str] = []
            self._jeu = None
            self._lecture = QTimer(self)
            self._lecture.timeout.connect(self._suivre)
            self._signe = QTimer(self)
            self._signe.timeout.connect(lambda: self._faire_signe(False))
            if getattr(self, "journal", None) is None:
                r = lire_le_journal(0)
                if r:
                    self.journal = r
                    self.montrer()
        if not self._lecture.isActive():
            self._lecture.start(LECTURE)
            self._signe.start(SIGNE)

    def showEvent(self, e) -> None:
        super().showEvent(e)
        self.actualiser()

    def hideEvent(self, e) -> None:
        super().hideEvent(e)
        if getattr(self, "_suiveur", None) is not None:
            self._lecture.stop()
            self._signe.stop()

    def _faire_signe(self, plein: bool) -> bool:
        code = ("local tv = scriptorium.tableaux_vivants if tv and tv.regarder then return tv.regarder('metiers', "
                + ("true" if plein else "false") + ") end"
                + (" return tostring(scriptorium.journal_des_metiers.publier())" if plein else " return 'sans'"))
        try:
            import sys
            if str(RACINE) not in sys.path:
                sys.path.insert(0, str(RACINE))
            if self._jeu is None:
                from essais.cycle_en_jeu import Jeu
                self._jeu = Jeu()
            self._jeu.emetteur.envoyer(["hex " + code.encode("ascii").hex()])
            return True
        except Exception as err:
            self.resume.setText(T("Le jeu ne répond pas : {0}", err))
            return False

    def _suivre(self) -> None:
        lignes = self._suiveur.nouvelles_lignes()
        if self._suiveur.recommence:
            self._suiveur.recommence = False
            self._faire_signe(True)
        for l in lignes:
            if MARQUE not in l:
                continue
            if l.split(MARQUE, 1)[1].startswith("debut|"):
                self._tampon = []
            self._tampon.append(l)
            if l.split(MARQUE, 1)[1].startswith("fin|"):
                r = analyser_le_journal(chr(10).join(self._tampon))
                self._tampon = []
                if r:
                    self.journal = r
                    self.montrer()

    def actualiser(self) -> None:
        self._demarrer_le_vivant()
        if self._faire_signe(True) and getattr(self, "journal", None) is None:
            self.resume.setText(T("Je demande le journal au jeu…"))

    def montrer(self) -> None:
        r = self.journal
        if not r:
            return
        cle = "7j" if self.periode.currentIndex() == 0 else "tout"
        metiers = list(r["bilans"].items())
        self.table.setRowCount(len(metiers))
        total = 0.0
        for i, (c, b) in enumerate(metiers):
            x = b.get(cle, {"valeur": 0, "paye": 0, "outils": 0, "relais": 0, "net": 0, "quantites": {}})
            total += x["net"]
            valeurs = [b["nom"], "oui" if b["engage"] else "non", quantites(x["quantites"]), gros(x["valeur"]),
                       gros(-x["paye"]), gros(-x["outils"]), gros(x["net"]), gros(x["relais"])]
            for j, val in enumerate(valeurs):
                it = QTableWidgetItem(T(val))
                if j == 6:
                    it.setForeground(QColor(VERT if x["net"] >= 0 else ROUGE))
                if j == 7 and x["relais"] > 0:
                    it.setForeground(QColor(ROUGE))
                self.table.setItem(i, j, it)
        self.table.resizeColumnsToContents()
        lignes = [(c, s) for c, l in r["sorties"].items() for s in l]
        lignes.sort(key=lambda x: (x[1]["jour"], x[1]["heure"]), reverse=True)
        self.sorties.setRowCount(len(lignes))
        for i, (c, s) in enumerate(lignes):
            nom = r["bilans"].get(c, {}).get("nom", c)
            h = s["heure"]
            quand = T("jour {0}, {1} h {2:02d}", s['jour'], int(h), int((h % 1) * 60))
            for j, val in enumerate([nom, quand, s["texte"], gros(s["valeur"])]):
                self.sorties.setItem(i, j, QTableWidgetItem(T(val)))
        self.sorties.resizeColumnsToContents()
        self.resume.setText(T("Bilan de tous les métiers ({0}) : {1} pour le camp.", '7 derniers jours' if cle == '7j' else 'depuis le début', gros(total)))
