
""










from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))
from noyau import chemins
from noyau.langue_du_programme import T
from gestion_du_camp import habillage as hb

JOURNAL = chemins.journal_du_jeu()
MARQUE = "[ScriptoNomDuCamp] "
LONGUEUR = 24
QUEUE = 2_000_000


def permis(c: str) -> bool:
    cp = ord(c)
    if c.isascii():
        return c.isalpha() or c in " '-"
    if c == "’":
        return True

    return 0xC0 <= cp <= 0x17F and cp not in (0xD7, 0xF7)





MANQUENT = {
    "ja": "ĀāĂăĈĉĊċĐđĒēĔĕĖėĜĝĞğĠġĢģĤĥĦħĨĩĪīĬĭĮįİĲĳĴĵĶķĸĹĺĻļĽľĿŀŅņŉŊŋŌōŎŏŔŕŖŗŜŝŞşŢţŦŧŨũŪūŬŭŰűŲųŴŵŶŷſ",
    "zh_hans": "ĄąĆćĈĉĊċČčĎďĔĕĖėĘęĜĝĞğĠġĢģĤĥĦħĬĭĮįİıĲĳĴĵĶķĸĹĺĻļĽľĿŀŁłŅņŉŊŋŐőŔŕŖŗŘřŚśŜŝŞşŠšŢţŤťŦŧŮůŰűŲųŴŵŶŷŸŹźŻżŽžſ",
    "zh_hant": "ĀāĂăĈĉĊċĐđĒēĔĕĖėĜĝĞğĠġĢģĤĥĦħĨĩĪīĬĭĮįİıĲĳĴĵĶķĸĹĺĻļĽľĿŀŅņŉŊŋŌōŎŏŔŕŖŗŜŝŞşŢţŦŧŨũŪūŬŭŲųŴŵŶŷŸſ",
}
LANGUES_TOUCHEES = {"ja": "japonais", "zh_hans": "chinois simplifié", "zh_hant": "chinois traditionnel"}


def langues_touchees(texte: str) -> list[str]:
    ""
    return [LANGUES_TOUCHEES[k] for k, m in MANQUENT.items() if any(c in m for c in texte)]


def avertissement(texte: str) -> str:
    ""
    l = langues_touchees(texte)
    return T("Certaines lettres de ce nom ne s'afficheront pas pour un joueur en {0}.", ", ".join(T(x) for x in l)) if l else ""


def valider(texte: str) -> tuple[str | None, str]:
    ""
    t = " ".join(unicodedata.normalize("NFC", texte or "").split())
    if not t:
        return None, "vide"
    if len(t) > LONGUEUR:
        return None, "trop_long"
    if not all(permis(c) for c in t) or not any(c.isalpha() for c in t):
        return None, "caracteres"
    return t, ""


REFUS = {
    "vide": "Écrivez d'abord un nom.",
    "trop_long": "Ce nom est trop long : 24 caractères au plus.",
    "caracteres": "Ce nom n'est pas accepté : seulement des lettres latines (accents permis), des espaces, l'apostrophe et "
                  "le trait d'union.",
    "pas_de_partie": "Le jeu n'a pas de partie en cours : chargez votre partie, puis recommencez.",
}


def en_lua(texte: str) -> str:
    ""
    sortie = []
    for o in texte.encode("utf-8"):
        c = chr(o)
        if 32 <= o < 127 and c not in "\\\"'":
            sortie.append(c)
        else:
            sortie.append("\\%d" % o)
    return '"' + "".join(sortie) + '"'


def dernier_nom() -> tuple[int, str] | None:
    ""
    try:
        with open(JOURNAL, "rb") as f:
            f.seek(0, 2)
            taille = f.tell()
            f.seek(max(0, taille - QUEUE))
            brut = f.read().decode("utf-8", "replace")
    except OSError:
        return None
    i = brut.rfind(MARQUE)
    if i < 0:
        return None
    ligne = brut[i + len(MARQUE):].split("\n", 1)[0].strip()
    numero, _, nom = ligne.partition("|")
    try:
        return int(numero), nom.strip()
    except ValueError:
        return None


def titre() -> str:
    ""
    d = dernier_nom()
    return T("Gestion du camp") + (" — " + d[1] if d and d[1] else "")


class OngletNomDuCamp(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setStyleSheet(hb.feuille())
        v = QVBoxLayout(self)
        v.setContentsMargins(18, 16, 18, 16)
        v.setSpacing(10)
        entete = QLabel(T("Le nom du camp"))
        entete.setObjectName("Entete")
        v.addWidget(entete)
        expl = QLabel(T("Dans le jeu, le menu U (« Nommer le camp ») choisit un nom dans la liste : c'est lui qui va sur la "
                        "carte et la boussole. Ici, vous pouvez écrire votre propre nom : il remplace celui de la liste dans "
                        "le bandeau d'arrivée au camp, les notes du Directeur et ce programme. Renommer est gratuit, à tout "
                        "moment."))
        expl.setObjectName("Note")
        expl.setWordWrap(True)
        v.addWidget(expl)
        self.actuel = QLabel("")
        v.addWidget(self.actuel)
        ligne = QHBoxLayout()
        self.saisie = QLineEdit()
        self.saisie.setMaxLength(LONGUEUR)
        self.saisie.setPlaceholderText(T("Votre nom de camp (24 caractères au plus)"))
        self.saisie.returnPressed.connect(self.donner)
        self.saisie.textChanged.connect(self._prevenir)
        ligne.addWidget(self.saisie, 1)
        b = QPushButton(T("Donner ce nom"))
        b.clicked.connect(self.donner)
        ligne.addWidget(b)
        r = QPushButton(T("Retirer le nom libre"))
        r.setToolTip(T("Le camp reprend le nom choisi dans la liste du jeu."))
        r.clicked.connect(self.retirer)
        ligne.addWidget(r)
        v.addLayout(ligne)
        regle = QLabel(T("Lettres latines, accentuées ou non, espaces, apostrophe et trait d'union : 24 caractères au plus."))
        regle.setObjectName("Note")
        regle.setWordWrap(True)
        v.addWidget(regle)
        self.prevenir = QLabel("")
        self.prevenir.setObjectName("Note")
        self.prevenir.setWordWrap(True)
        v.addWidget(self.prevenir)
        self.resume = QLabel("")
        self.resume.setObjectName("Note")
        self.resume.setWordWrap(True)
        v.addWidget(self.resume)
        v.addStretch(1)
        self.montrer()

    def _prevenir(self, texte: str) -> None:
        self.prevenir.setText(avertissement(texte))

    def showEvent(self, e) -> None:
        super().showEvent(e)
        self.montrer()



    RELIRE_MS = (1500, 4000, 9000)

    def _relire_bientot(self) -> None:
        for ms in self.RELIRE_MS:
            QTimer.singleShot(ms, self._relire)

    def _relire(self) -> None:
        self.montrer()
        try:
            fenetre = self.window()
            if fenetre is not None and fenetre is not self and T("Gestion du camp") in fenetre.windowTitle():
                fenetre.setWindowTitle(titre())
        except Exception:
            pass

    def montrer(self) -> None:
        d = dernier_nom()
        if d is None:
            self.actuel.setText(T("Nom du camp : inconnu (le jeu ne l'a pas encore publié)."))
        elif d[1]:
            self.actuel.setText(T("Nom du camp : {0}", d[1]))
        else:
            self.actuel.setText(T("Nom du camp : Le camp de la compagnie (aucun nom choisi)."))

    def _envoyer(self, argument: str) -> bool:
        try:
            from essais.cycle_en_jeu import Jeu
            code = "return tostring(scriptorium.nom_du_camp.nommer_libre(" + argument + "))"
            Jeu().emetteur.envoyer(["hex " + code.encode("ascii").hex()])
        except Exception as err:
            self.resume.setText(T("Le jeu ne répond pas : {0}", err))
            return False
        return True

    def donner(self) -> None:
        nom, raison = valider(self.saisie.text())
        if nom is None:
            self.resume.setText(T(REFUS[raison]))
            return
        if self._envoyer(en_lua(nom)):
            self.resume.setText(T("Nom donné : {0}. Il paraît au prochain bandeau d'arrivée et dans les notes.", nom)
                                + ((" " + avertissement(nom)) if avertissement(nom) else ""))
            self.saisie.clear()
            self._relire_bientot()

    def retirer(self) -> None:
        if self._envoyer('"effacer"'):
            self.resume.setText(T("Nom libre retiré : le camp reprend le nom de la liste."))
            self._relire_bientot()
