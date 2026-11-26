
""





from __future__ import annotations

import re
import sys
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QDialog, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))
from noyau import chemins, partie_en_pause
from noyau.langue_du_programme import T
from gestion_du_camp import habillage as hb

JOURNAL = chemins.journal_du_jeu()
QUEUE = 4_000_000
PAS_MS = 1000
SILENCE_S = 12


TOUCHES = ("u", "f2", "insert", "end", "pgup", "pgdn")

QUESTION = ('local tm = scriptorium.touche_du_menu local k = tm and tm.touche and tm.touche() '
            'if k then scriptorium.valeur("touche_du_menu", "actuelle-" .. k) end '
            'local rm = scriptorium.retrait_du_mod '
            'if rm then scriptorium.valeur("retrait_du_mod", "etat-" .. ((rm.fait and "fait") or (rm.attente ~= nil and "attente") or "non")) end')
RETIRER = 'scriptorium.retrait_du_mod.retirer(rawget(_G, "compagnie"))'
RENONCER = 'scriptorium.retrait_du_mod.renoncer()'

_TOUCHE = re.compile(rb"scriptorium_touche_du_menu_(?:choix|actuelle)-([a-z0-9]+)")
_RETRAIT = re.compile(rb"scriptorium_retrait_du_mod_([A-Za-z0-9_.-]+)")


def nom_de_la_touche(k: str) -> str:
    return {"u": "U", "f2": "F2", "insert": T("Inser"), "end": T("Fin"), "pgup": T("Page haut"),
            "pgdn": T("Page bas")}.get(k, k)


def commande_de_la_touche(k: str) -> str:
    assert k in TOUCHES
    return 'scriptorium.touche_du_menu.choisir(nil, "%s")' % k


def lire_la_touche(donnees: bytes) -> str | None:
    ""
    m = None
    for m in _TOUCHE.finditer(donnees):
        pass
    k = m.group(1).decode() if m else None
    return k if k in TOUCHES else None


def lire_le_retrait(donnees: bytes) -> tuple[str, str] | None:
    ""

    etat = None
    for m in _RETRAIT.finditer(donnees):
        mot = m.group(1).decode()
        if mot.startswith(("fait-", "deja", "etat-fait")):
            etat = ("fait", "")
        elif mot.startswith("attente-dit-"):
            n = re.search(r"-(\d+)-gel-", mot)
            etat = ("attente", n.group(1) if n and n.group(1) != "0" else "")
        elif mot.startswith("attente-renoncee"):
            etat = ("renonce", "")
        elif mot.startswith(("attente-autre-partie", "attente-oubliee", "etat-non", "partie-non-retiree")):
            etat = ("non", "")
        elif mot.startswith(("etat-attente", "attente-troupe", "retenu-")):
            etat = ("attente", etat[1] if etat and etat[0] == "attente" else "")
        elif mot.startswith("refus-combat"):
            etat = ("combat", "")
        elif mot.startswith("refus-"):
            etat = ("refus", "")
    return etat


def lire_le_journal(depuis: int = 0) -> bytes:
    try:
        with open(JOURNAL, "rb") as f:
            f.seek(0, 2)
            taille = f.tell()
            f.seek(max(0, taille - QUEUE, depuis if depuis <= taille else 0))
            return f.read()
    except OSError:
        return b""


def taille_du_journal() -> int:
    try:
        return JOURNAL.stat().st_size
    except (OSError, AttributeError):
        return 0


def envoyer(code: str) -> None:
    from essais.cycle_en_jeu import Jeu
    Jeu().emetteur.envoyer(["hex " + code.encode("ascii").hex()])


class ReglagesDuMod(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(T("Réglages du mod"))
        self.setStyleSheet(hb.feuille())
        self.setMinimumWidth(560)
        self.depuis_la_question = taille_du_journal()
        self.depuis_le_retrait: int | None = None
        self.secondes = 0
        v = QVBoxLayout(self)
        v.setContentsMargins(20, 18, 20, 16)
        v.setSpacing(10)


        v.addWidget(self._entete(T("La touche du menu du mod")))
        self.actuelle = self._note(T("Lecture de la touche dans le jeu…"))
        v.addWidget(self.actuelle)
        grille = QGridLayout()
        self.boutons: dict[str, QPushButton] = {}
        for i, k in enumerate(TOUCHES):
            b = QPushButton(nom_de_la_touche(k))
            b.clicked.connect(lambda _=False, x=k: self.choisir(x))
            self.boutons[k] = b
            grille.addWidget(b, 0, i)
        v.addLayout(grille)
        v.addSpacing(10)


        v.addWidget(self._entete(T("Retirer le mod de cette partie")))
        v.addWidget(self._note(T("De jour, au calme, Henry debout. Un camp fondé est vendu au notaire, les hommes sont payés "
                                 "et rentrent chez eux, les coffres et l'argent vont à Henry. Tout ce qui est au mod quitte "
                                 "la partie, puis la partie est sauvegardée. Quittez ensuite le jeu sans rien charger, et "
                                 "enlevez le mod.")))
        ligne = QHBoxLayout()
        self.retrait = QPushButton(T("Retirer le mod…"))
        self.retrait.clicked.connect(self.demander)
        self.renoncement = QPushButton(T("Renoncer au retrait"))
        self.renoncement.clicked.connect(self.renoncer)
        self.renoncement.hide()
        ligne.addWidget(self.retrait)
        ligne.addWidget(self.renoncement)
        ligne.addStretch(1)
        v.addLayout(ligne)

        self.confirmation = QHBoxLayout()
        self.sur = QLabel(T("Sûr ? Cela ne pourra pas être défait."))
        self.oui = QPushButton(T("Oui, retirer le mod"))
        self.oui.clicked.connect(self.retirer)
        self.non = QPushButton(T("Non, le garder"))
        self.non.clicked.connect(lambda: self._confirmer(False))
        for w in (self.sur, self.oui, self.non):
            self.confirmation.addWidget(w)
        self.confirmation.addStretch(1)
        v.addLayout(self.confirmation)
        self._confirmer(False)
        self.resume = self._note("")
        v.addWidget(self.resume)
        v.addSpacing(6)
        bas = QHBoxLayout()
        bas.addStretch(1)
        fermer = QPushButton(T("Fermer"))
        fermer.clicked.connect(self.accept)
        bas.addWidget(fermer)
        v.addLayout(bas)

        self.minuterie = QTimer(self)
        self.minuterie.timeout.connect(self.relire)
        self.minuterie.start(PAS_MS)
        if self._mod_retire():
            self._arreter()
        else:
            self._envoyer(QUESTION)


    def _entete(self, texte: str) -> QLabel:
        q = QLabel(texte)
        q.setObjectName("Entete")
        return q

    def _note(self, texte: str) -> QLabel:
        q = QLabel(texte)
        q.setObjectName("Note")
        q.setWordWrap(True)
        return q

    def _confirmer(self, montrer: bool) -> None:
        for w in (self.sur, self.oui, self.non):
            w.setVisible(montrer)

    def _mod_retire(self) -> bool:
        try:
            return partie_en_pause.retire()
        except Exception:
            return False

    def _arreter(self) -> None:
        for b in self.boutons.values():
            b.setEnabled(False)
        self.retrait.setEnabled(False)
        self.actuelle.hide()
        self.renoncement.hide()
        self._confirmer(False)
        self.resume.setText(T("Le mod est retiré de cette partie."))

    def _envoyer(self, code: str) -> bool:
        try:
            envoyer(code)
        except Exception as err:
            self.resume.setText(T("Le jeu ne répond pas : {0}", err))
            return False
        return True


    def choisir(self, k: str) -> None:
        self.depuis_la_question = taille_du_journal()
        if self._envoyer(commande_de_la_touche(k)):
            self.resume.setText(T("Touche demandée au jeu : {0}.", nom_de_la_touche(k)))

    def demander(self) -> None:
        self._confirmer(True)

    def retirer(self) -> None:
        self._confirmer(False)
        self.depuis_le_retrait = taille_du_journal()
        if self._envoyer(RETIRER):
            self.resume.setText(T("Demande envoyée. Le jeu répond dans sa barre du bas."))

    def renoncer(self) -> None:
        self.depuis_le_retrait = taille_du_journal()
        self._envoyer(RENONCER)

    def relire(self) -> None:
        self.secondes += 1
        if self._mod_retire():
            self._arreter()
            return
        donnees = lire_le_journal()
        k = lire_la_touche(donnees)
        if k is not None:
            self.actuelle.setText(T("Aujourd'hui : {0}.", nom_de_la_touche(k)))
            for x, b in self.boutons.items():
                b.setEnabled(x != k)
        elif self.secondes >= SILENCE_S:
            self.actuelle.setText(T("Le jeu n'a pas répondu : chargez votre partie, puis rouvrez cette page."))

        depuis = self.depuis_la_question if self.depuis_le_retrait is None else self.depuis_le_retrait
        nouvelle = lire_le_retrait(lire_le_journal(depuis))
        if nouvelle is None:
            return
        etat, hommes = nouvelle
        attend = etat == "attente"
        self.renoncement.setVisible(attend)
        if etat == "fait":
            self._arreter()
        elif attend:
            self.resume.setText(T("Le retrait attend le retour de la troupe (hommes dehors : {0}). Il se fera de lui-même.", hommes)
                                if hommes else T("Le retrait attend le retour de la troupe. Il se fera de lui-même."))
        elif etat == "renonce":
            self.resume.setText(T("Retrait abandonné : le mod reste en place."))
        elif etat == "combat":
            self.resume.setText(T("Le jeu a refusé : un combat est en cours. Mettez-vous à l'abri, puis recommencez."))
        elif etat == "refus":
            self.resume.setText(T("Le jeu a refusé le retrait : la raison est écrite dans sa barre du bas."))
