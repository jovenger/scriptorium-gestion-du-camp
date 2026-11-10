
""









from __future__ import annotations

from PyQt6.QtWidgets import (QDialog, QGridLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout)

from noyau import chemins
from noyau.langue_du_programme import T

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
from aides_des_objets import INSTALLATIONS, LIEN_DU_DICTIONNAIRE

NOMS = {"tour": "Tour d'archers", "charrette_d_archers": "Charrette d'archers", "mur": "Palissade", "porte": "Porte de palissade",
        "alchimie": "Atelier d'alchimie", "arene": "Arène", "entrainement": "Terrain d'entraînement", "fleches": "Établi à flèches",
        "cuisine": "Coin cuisine", "tonneau": "Tonneau de vin", "banc": "Banc du camp", "baquets": "Bassines", "pisser": "Feuillée"}


NOMS_2_0 = {"bains_agrandis": "Agrandir les bains", "coursier_mobilier": "La table et le tabouret du coursier", "cheval": "Un cheval"}
ETATS = {"debout": "Debout au camp : {n}", "reserve": "Payée, en réserve", "rien": "Pas encore au camp"}
RESULTATS = {
    "bati": "C'est construit : le camp s'est rebâti avec.",
    "installee": "C'est acheté : elle est devant Henry. Déplacez-la sur le plan du camp si besoin.",
    "deja": "Elle est déjà au camp.",
    "pas_assez": "Le coffre du camp n'a pas assez d'argent.",
    "pas_de_camp": "Pas de camp dressé ici.",
    "pas_calme": "Pas maintenant : le camp n'est pas au calme.",
    "limite": "Plus de place : le maximum est atteint.",
    "rate": "Ça n'a pas marché.",
    "achete": "C'est acheté : c'est en place, ou ça le sera au prochain battement du camp.",

    "pas_de_place": "Pas de place libre : posez d'abord une ligne des chevaux (Le plan du camp, Les objets, Artisans : postes et ateliers).",
}
AIDE_VISEE = ("Le programme se cache : vise dans le jeu avec la souris, clic gauche pour poser, clic droit pour annuler "
              "(déjà payée, elle reste en réserve). H rouvre le programme.")
AIDE_CAMP = "Le camp se rebâtit au même endroit pour l'accueillir (seulement au calme)."
TITRE_1403 = "Le camp de 1403 : les ajouts à acheter"
AIDE_1403 = ("Ce que la version 2 ajoute au camp. Tout s'achète ici, payé par le coffre du camp ; ce que vous avez déjà reste "
             "tel quel.")
SANS_LIGNE = "Il faut d'abord la ligne des chevaux"


ACHETE_OU = {"bains_agrandis": "Acheté : les bains se reposent plus grands, si la place est libre",
             "coursier_mobilier": "Acheté : posés au pupitre du coursier (Le plan du camp, Les objets, Artisans : postes et ateliers)"}


def lire_l_etat(reponse: str) -> tuple[int | None, list[dict]]:
    ""
    mots = reponse.split()
    if "COFFRE" not in mots:
        return None, []
    i = mots.index("COFFRE")
    if "ACHATS" in mots[i:]:
        mots = mots[:mots.index("ACHATS", i)]
    try:
        coffre = int(float(mots[i + 1]))
    except (IndexError, ValueError):
        return None, []
    liste, k = [], i + 2
    while k + 6 <= len(mots):
        cle, etat, n, prix, gratuit, visee = mots[k:k + 6]
        try:
            liste.append({"cle": cle, "etat": etat, "n": int(float(n)), "prix": int(float(prix)), "gratuit": gratuit == "1",
                          "visee": visee == "1"})
        except ValueError:
            break
        k += 6
    return coffre, liste


def lire_les_achats(reponse: str) -> list[dict]:
    ""

    mots = reponse.split()
    if "ACHATS" not in mots:
        return []
    liste, k = [], mots.index("ACHATS") + 1
    while k + 6 <= len(mots):
        cle, etat, n, places, prix, repetable = mots[k:k + 6]
        cle = cle.replace("-", "_")
        try:
            a = {"cle": cle, "etat": etat, "n": int(float(n)), "places": int(float(places)), "prix": int(float(prix)),
                 "repetable": repetable == "1", "gratuit": False, "visee": False, "achat": True}
        except ValueError:
            break
        if cle in NOMS_2_0:
            a["nom"] = NOMS_2_0[cle]
            liste.append(a)
        k += 6
    return liste


def etat_d_achat(a: dict) -> str:
    ""
    if a["repetable"]:
        return SANS_LIGNE if a["places"] == 0 else "{0} / {1}".format(a["n"], a["places"])
    return ACHETE_OU.get(a["cle"], "acheté") if a["etat"] == "achete" else "Pas encore au camp"


def bouton_d_achat(a: dict) -> bool:
    ""
    if a["repetable"]:
        return a["places"] > 0 and a["etat"] != "achete"
    return a["etat"] != "achete"


def action_de(c: dict) -> str | None:
    ""
    if not c["visee"]:
        if c["etat"] == "debout":
            return None
        return "La poser (déjà payée)" if c["gratuit"] else "Acheter et poser (coffre du camp)"
    if c["gratuit"]:
        return "En poser une autre (déjà payée)" if c["etat"] == "debout" else "La poser (déjà payée)"
    return "En acheter une autre (coffre du camp)" if c["etat"] == "debout" else "Acheter et poser (coffre du camp)"


class FenetreConstructions(QDialog):
    def __init__(self, fenetre) -> None:
        super().__init__(fenetre)
        self.fenetre = fenetre
        self.setWindowTitle(T("Constructions du camp"))
        self.resize(720, 520)
        self.v = QVBoxLayout(self)
        self.titre = QLabel(T("<b>Ce qui s'achète pour le camp</b> — payé par le coffre du camp, jamais par la bourse d'Henry."))
        self.titre.setWordWrap(True)
        self.v.addWidget(self.titre)
        self.coffre = QLabel(T("Coffre du camp : ?"))
        self.v.addWidget(self.coffre)

        self.lien = QLabel(T("Le dictionnaire du camp, ce que fait chaque objet :")
                           + f' <a href="{LIEN_DU_DICTIONNAIRE}">{LIEN_DU_DICTIONNAIRE}</a>')
        self.lien.setOpenExternalLinks(True)
        self.v.addWidget(self.lien)
        self.grille = QGridLayout()
        self.v.addLayout(self.grille)

        self.titre_1403 = QLabel(T("<b>{0}</b>", TITRE_1403))
        self.aide_1403 = QLabel(T(AIDE_1403))
        self.aide_1403.setWordWrap(True)
        self.grille_1403 = QGridLayout()
        self.v.addWidget(self.titre_1403)
        self.v.addWidget(self.aide_1403)
        self.v.addLayout(self.grille_1403)
        self.titre_1403.setVisible(False)
        self.aide_1403.setVisible(False)
        self.message = QLabel("")
        self.message.setWordWrap(True)
        self.v.addWidget(self.message)

        self.v.addStretch(1)
        aide = QLabel(T("Atelier d'alchimie : ") + T(AIDE_CAMP) + T("\nInstallations : posées devant Henry, à déplacer ensuite sur le plan."))
        aide.setWordWrap(True)
        self.v.addWidget(aide)
        actualiser = QPushButton(T("Actualiser"))
        actualiser.clicked.connect(self.actualiser)
        self.v.addWidget(actualiser)
        self.liste: list[dict] = []
        self.valeur_coffre: int | None = None

    def _vider(self, grille=None) -> None:

        grille = self.grille if grille is None else grille
        while grille.count():
            w = grille.takeAt(0).widget()
            if w is not None:
                w.deleteLater()

    def actualiser(self) -> None:
        rep = self.fenetre._ordre("return tostring(scriptorium.constructions.etat_tous())", "Je lis les constructions")
        if rep is None:
            self.message.setText(T(self.fenetre.etat.text()))
            return
        coffre, liste = lire_l_etat(rep)
        if coffre is None:
            self.message.setText(T("Le jeu n'a pas répondu comme prévu : ") + T(rep[:120]))
            return
        self.valeur_coffre, self.liste = coffre, liste
        self.coffre.setText(T("Coffre du camp : {0} gros", coffre))
        self._vider()
        for i, c in enumerate(liste):
            etiquette = QLabel(T("<b>{0}</b>", NOMS.get(c['cle'], c['cle'])))

            if c["cle"] in INSTALLATIONS:
                etiquette.setToolTip(T(INSTALLATIONS[c["cle"]]))
            self.grille.addWidget(etiquette, i, 0)
            self.grille.addWidget(QLabel(T(ETATS.get(c["etat"], c["etat"]).format(n=c["n"]))), i, 1)
            self.grille.addWidget(QLabel(T("{0} gros", c['prix'])), i, 2)
            a = action_de(c)
            if a is not None:
                b = QPushButton(T(a))
                b.clicked.connect(lambda _=False, c=c: self.construire(c))
                self.grille.addWidget(b, i, 3)
            else:
                self.grille.addWidget(QLabel(T("Elle est déjà au camp.")), i, 3)
        self._montrer_les_achats(lire_les_achats(rep))

    def _montrer_les_achats(self, achats: list[dict]) -> None:
        ""
        self._vider(self.grille_1403)
        self.titre_1403.setVisible(bool(achats))
        self.aide_1403.setVisible(bool(achats))
        for i, a in enumerate(achats):
            self.grille_1403.addWidget(QLabel(T("<b>{0}</b>", a["nom"])), i, 0)
            self.grille_1403.addWidget(QLabel(T(etat_d_achat(a))), i, 1)
            self.grille_1403.addWidget(QLabel(T("{0} gros", a["prix"])), i, 2)
            if bouton_d_achat(a):
                b = QPushButton(T("Acheter (coffre du camp)"))
                b.clicked.connect(lambda _=False, a=a: self.construire(a))
                self.grille_1403.addWidget(b, i, 3)

    def construire(self, c: dict) -> None:
        nom = c.get("nom") or NOMS.get(c["cle"], c["cle"])
        if not c["gratuit"]:
            if QMessageBox.question(self, T("Constructions du camp"),
                                    T("Acheter « {0} » pour {1} gros, pris dans le coffre du camp ?", nom, c['prix'])
                                    + (T("\n\nLe coffre a {0} gros.", self.valeur_coffre) if self.valeur_coffre is not None else "")) \
                    != QMessageBox.StandardButton.Yes:
                return
        rep = self.fenetre._ordre(f'return tostring(scriptorium.constructions.construire("{c["cle"]}"))',
                                  T("J'achète « {0} »", nom) if c.get("achat") else T("Je construis « {0} »", nom))
        if rep is None:
            self.message.setText(T(self.fenetre.etat.text()))
            return
        r = rep.strip().replace(" ", "_")
        if r == "visee":
            self.fenetre.etat.setText(T("« {0} » : vise dans le jeu — clic gauche pour poser, clic droit pour annuler. H rouvre le programme.", nom))
            if self.isWindow():
                self.close()
            try:
                from noyau.premier_plan import rendre_au_jeu
                self.fenetre.window().hide()
                rendre_au_jeu()
            except Exception:
                pass
            return
        self.message.setText(T(RESULTATS.get(r, "Réponse du jeu : " + rep)))
        if r in ("bati", "installee", "achete"):
            try:
                from gestion_du_camp import habillage as hb
                hb.apposer_un_sceau(self.message, T("Acheté"))
            except Exception:
                pass
        self.actualiser()
