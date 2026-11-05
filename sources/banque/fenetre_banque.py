
""














from __future__ import annotations

import importlib.util
import re
import sys
import threading
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QMessageBox, QPushButton, QSpinBox,
    QTableWidget, QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget,
)

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))
from noyau import chemins
from noyau.langue_du_programme import T, langue

_LIVRE = RACINE / "choses" / "banque_du_camp" / "panneau.py"

FOND, CARTE, ENCRE, OR, PALE = "#1d1813", "#2a231b", "#eadfc8", "#c9a24d", "#9c8f78"
VERT, ROUGE = "#8fbf6a", "#d9735b"



PART_DIRECTEUR = 20



MINIMUM_COFFRE = 10000


def a_partager(benefice_net: float, coffre: float, reste_a_payer: float) -> float:
    ""

    return max(0.0, min(float(benefice_net), float(coffre) - float(reste_a_payer) - MINIMUM_COFFRE))


ARTISANS = [("forgeron", "La forge"), ("femmes", "Les bains"), ("coursier", "Le coursier"), ("bois", "Le bûcheron"),
            ("eau", "Le porteur d'eau"), ("chasseurs", "Les chasseurs"), ("jardiniers", "Les jardiniers"),
            ("taverne", "La taverne"), ("armurier", "L'armurier")]




LIBELLES_CAISSE = {
    "autre": "Autre mouvement",
    "releve": "Relevé",
    "embauche": "Embauche (fonds de départ)",
    "renvoi": "Renvoi",
    "remiseazero": "Remise à zéro du camp",

    "subsistance": "Avance du jour à ses gens (5 gros chacun)",
    "fonds": "Fonds de départ",
    "partage": "Partage de la caisse",
    "taxe": "Taxe du camp",
    "paye7": "Paye du 7ᵉ jour (salaires et taxe)",
    "fondsdulundi": "Fonds du lundi (mise de ses gens)",
    "primedencouragement": "Versement à la prime des commerçants",
    "dotation": "Remboursement de la dotation (au coffre du camp)",
    "mise": "Mise reprise par ses gens",
    "aides": "Aides payées",
    "compagnons": "Compagnons payés",
    "armurerie": "Armurerie",
    "croissance": "Un second engagé",
    "prelevement": "Prélèvement du Directeur",
    "materiel": "Matériel acheté en ville",
    "chevaux": "Nourriture des chevaux",
    "sortie": "Ventes au retour d'une sortie",
    "soins": "Soins après bataille",
    "bainduservice": "Bain du service",

    "mercenaires.aux.bains": "Bains des mercenaires", "mercenairesauxbains": "Bains des mercenaires",
    "service": "Vie du service (repas, besoins)",
    "forge": "Forge (réparations, commandes)",
    "forge.chez.le.coursier": "Forge (commandes passées au coursier)",
    "forgechezlecoursier": "Forge (commandes passées au coursier)",
    "coursier": "Courses du coursier",
    "taverne": "Taverne",
    "caisses": "Caisse de l'atelier",
    "salaires.des.metiers": "Paye du 7ᵉ jour", "salairesdesmetiers": "Paye du 7ᵉ jour",
    "stocks.des.metiers": "Matières et fournitures", "stocksdesmetiers": "Matières et fournitures",
    "reserves": "Repas et réserves du camp",
    "ventes.aux.producteurs": "Ventes aux hommes", "ventesauxproducteurs": "Ventes aux hommes",
    "materiel.des.commerces": "Usure et réparation du matériel",
    "evaluation.des.commerces": "Évaluation du commerce",
    "croissance.des.commerces": "Croissance du commerce",
    "compagnons.des.metiers": "Aides et compagnons",
    "aides.aux.ateliers": "Aides aux ateliers",
    "directeur.coffre": "Prélèvement du Directeur",
    "tenir.la.compagnie": "Prélèvement du Directeur (paye des hommes)",
    "sans.credit.aux.metiers": "Plus de crédit aux métiers",
    "bain.du.service": "Bain du service",
    "soins.apres.bataille": "Soins après bataille",
    "jardiniers": "Jardiniers", "chasseurs": "Chasseurs", "bucherons": "Bûcherons",
}

PRODUITS = {"biere": "de bière", "vin": "de vin", "eau": "d'eau", "boisson": "de boisson", "vivres": "de vivres",
            "bois": "de bois", "charbon": "de charbon", "branches": "de branches", "savon": "de savon",
            "pansements": "de pansements", "bain": "d'un bain", "soin": "d'un soin", "reparation": "d'une réparation",
            "legumes": "de légumes", "viande": "de viande", "fer": "de fer", "cuir": "de cuir", "tissu": "de tissu",
            "graines": "de graines", "fleches": "de flèches", "acier": "d'acier", "oeufs": "d'œufs",
            "peaux": "de peaux", "herbes": "d'herbes", "champignons": "de champignons", "baies": "de baies"}

AVEC = {"forgeron": ("la forge", "à la forge", "de la forge"), "femmes": ("les bains", "aux bains", "des bains"),
        "coursier": ("le coursier", "au coursier", "du coursier"), "bois": ("le bûcheron", "au bûcheron", "du bûcheron"),
        "eau": ("le porteur d'eau", "au porteur d'eau", "du porteur d'eau"),
        "chasseurs": ("les chasseurs", "aux chasseurs", "des chasseurs"),
        "jardiniers": ("les jardiniers", "aux jardiniers", "des jardiniers"),
        "taverne": ("la taverne", "à la taverne", "de la taverne"),
        "armurier": ("l'armurier", "à l'armurier", "de l'armurier"),
        "coffre": ("le coffre du camp", "au coffre du camp", "du coffre du camp"),
        "hommes": ("les hommes du camp", "aux hommes du camp", "des hommes du camp"),
        "ville": ("la ville", "en ville", "de la ville"),

        "jardinier": ("les jardiniers", "aux jardiniers", "des jardiniers"),
        "forge": ("la forge", "à la forge", "de la forge")}


def _produit(p: str) -> str:
    p = p.strip(".")
    return PRODUITS.get(p, "de " + p.replace(".", " "))


def libelle_caisse(l: str, montant: float = 0.0) -> str:
    ""

    base, _, qui = l.partition("..")
    _, a, de = AVEC.get(qui, (qui, "à " + qui.replace(".", " "), "de " + qui.replace(".", " "))) if qui else ("", "", "")
    for tete, mot in (("vente", "Vente"), ("achat", "Achat")):
        if base.startswith(tete) and len(base) > len(tete) and base not in LIBELLES_CAISSE:
            phrase = T("{0} {1}", mot, _produit(base[len(tete):]))
            return T("{0} {1}", phrase, a) if qui else phrase
    if base == "autre":
        return "Mouvement non expliqué"
    texte = LIBELLES_CAISSE.get(base) or base.replace(".", " ").capitalize()

    if not qui or base in ("subsistance", "fondsdulundi", "mise", "materiel", "chevaux"):
        return texte
    return T("{0}, argent reçu {1}", texte, de) if montant >= 0 else T("{0}, argent versé {1}", texte, a)



QUI_DU_SERVICE = [("ScriptoCaisse", None), ("ScriptoBainlavandiere", "une lavandière"),
                  ("ScriptoBainbaigneuse", "la dame des bains"), ("ScriptoTavernier", "le tavernier"),
                  ("ScriptoPorteurEau", "le porteur d'eau"), ("ScriptoJardinier", "un jardinier"),
                  ("ScriptoForge", "le forgeron"), ("ScriptoAideForge", "l'aide du forgeron"), ("ScriptoArmurier", "l'armurier"),
                  ("ScriptoCoursier", "le coursier"), ("ScriptoChasseur", "un chasseur"),
                  ("ScriptoBucheron", "un bûcheron"), ("ScriptoCueilleur", "un cueilleur")]


def nom_de(qui: str, noms: dict | None = None) -> str:
    ""
    if not qui:
        return ""
    if qui == "Henry":
        return "Henry"
    if qui == "venteducamp":
        return "la vente du camp"
    if qui in AVEC:
        return AVEC[qui][0]
    for tete, nom in QUI_DU_SERVICE:
        if qui.startswith(tete):
            if nom is None:
                code = qui[len(tete):]
                return AVEC.get(code, (code, ""))[0]
            return nom
    if noms and qui in noms:
        return noms[qui]
    if qui.startswith("RecrueSansNom"):
        return "un mercenaire"
    return qui


def _n(n, mot: str) -> str:
    ""
    try:
        k = int(n)
    except (TypeError, ValueError):
        k = 0
    return f"{k} {mot}" if k <= 1 else f"{k} {mot}s"



NOMS_DES_ACHATS = {"arene": "l'arène", "entrainement": "le terrain d'entraînement", "fleches": "l'établi à flèches",
                   "cuisine": "le coin cuisine", "tonneau": "le tonneau de vin", "banc": "le banc du camp",
                   "baquets": "les bassines", "pisser": "la feuillée", "palissade": "une palissade",
                   "portepalissade": "une porte de palissade", "lit": "un lit", "lithaut": "un lit haut"}




_PALETTE = RACINE / "choses" / "editeur_du_camp" / "palette.py"
_FORMES_DES_NOMS = (r'\("([a-z0-9_]+)", "([^"]+)",', r'"cle": "([a-z0-9_]+)", "nom": "([^"]+)"', r'"([a-z0-9_]+)": \("([^"]+)",')
_noms_des_objets: dict[str, str] | None = None


def nom_d_objet(code: str) -> str | None:
    global _noms_des_objets
    if _noms_des_objets is None:
        _noms_des_objets = {}
        try:
            texte = _PALETTE.read_text(encoding="utf-8")
        except OSError:
            texte = ""
        for forme in _FORMES_DES_NOMS:
            for cle, nom in re.findall(forme, texte):
                _noms_des_objets.setdefault(cle.replace("_", ""), nom)
    return _noms_des_objets.get(code)


def phrase_du_coffre(mv: dict, libelle: str, noms: dict | None = None, pct_henry: float = 0) -> str:
    ""

    code, n, qui = mv["code"], mv.get("n", 0), mv.get("qui") or ""
    q = nom_de(qui, noms)
    prod = PRODUITS.get(qui.lower(), "")
    cle_achat = qui.lower().replace("_", "").replace(" ", "")
    achat = NOMS_DES_ACHATS.get(cle_achat) or nom_d_objet(cle_achat) or q
    d = {
        "amenagement": T("Aménagement du camp : {0}", achat) if achat else libelle,
        "annulation": T("Achat annulé, remboursé au coffre : {0}", achat) if achat else libelle,
        "repas": T("Repas payés par {0}", _n(n, 'homme')), "boisson": T("Boissons payées par {0}", _n(n, 'homme')),
        "payes": T("Payes des hommes ({0})", _n(n, 'homme')), "fleches": T("Flèches payées par les archers ({0})", _n(n, 'flèche')),
        "service": "Paye du service",

        "primes": (T("Paye du soir : la part des missions ({0})", _n(n, 'homme')) if qui.lower() == "soir"
                   else T("Primes et parts des hommes ({0})", _n(n, 'homme'))),
        "postes": T("Primes de garde ({0} de ronde)", _n(n, 'quart')),

        "butin": ("Prime du contrat d'une mission, versée au camp" if qui.lower() == "prime"
                  else "Butin des batailles, rentré au coffre"),
        "revente": T("Revente du surplus en ville par le coursier ({0})", _n(n, 'objet')),
        "ausac": "Butin confié au coursier pour la revente en ville",
        "courses": (T("Achat de {0} par le camp (le menu du mod)", q) if q in ("vivres", "boisson") else "Courses du coursier pour le camp"), "impot": "Taxes des commerces au 7ᵉ jour",
        "taxe": "Taxe des métiers (20 % du bénéfice)", "commission": "Commission du coursier sur tes commandes",
        "prelevement": "Prélèvement du Directeur sur les marchands",
        "depot": T("Déposé au coffre par {0} (capital, hors bénéfice)", q or 'Henry'),
        "retrait": T("Retiré du coffre par {0} (capital, hors bénéfice)", q or 'Henry'),

        "dettes": ("Dette remboursée sur la paye du soir" if qui.lower().replace(" ", "") in ("payedusoir", "paye_du_soir")
                   else T("Dette remboursée par {0}", q or 'un homme')),
        "fournitures": T("Fournitures remboursées par {0}", q or 'un métier'),
        "avances": (T("Avance du coffre : achat {0} à crédit", prod) if prod
                    else T("Avance du coffre à {0} (achat à crédit)", q or 'un métier')),

        "provisions": (T("Achat {0} par le camp aux métiers", prod) if prod
                       else T("Achat du camp aux métiers ({0})", q.replace('accueildemission', 'accueil de mission'))),
        "soins": "Soin de toute la compagnie, payé par le camp",
        "embauche": T("Embauche : {0}", q) if q else "Embauche", "fonds": T("Fonds de départ : {0}", q) if q else "Fonds de départ",

        "renvoi": T("Bourse reprise à un renvoyé ({0})", q) if q else "Bourse reprise à un renvoyé",
        "bain": T("Bain payé par {0}", q or 'un homme'), "forge": T("Réparation payée à la forge par {0}", q or 'un homme'),
        "arme": T("Arme payée par {0}", q or 'un homme'), "achat": T("Achat payé par {0}", q or 'un homme'),
    }
    if code == "henry":
        return (T("Ta part du bénéfice de la semaine") + (f" ({n:g} %)" if n else "")
                if pct_henry and abs(n - pct_henry) < 0.01 else "Ta part d'une mission (le coffre des bandits)")
    if code == "directeur":
        return (T("Part du Directeur ({0:g} % du bénéfice)", n) if abs(n - PART_DIRECTEUR) < 0.01
                else "Part du Directeur sur une mission (le coffre des bandits)")
    if code in d:
        return d[code]
    return T(libelle) + (T(", par {0}", q) if q else "")


def livre_module():
    spec = importlib.util.spec_from_file_location("banque_livre", _LIVRE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def gros(n: float, signe: bool = False) -> str:
    s = f"{abs(n):,.0f}".replace(",", " ")
    if signe:
        return ("+ " if n >= 0 else "− ") + s + " gros"
    return ("−" if n < 0 else "") + s + " gros"


def gros_fin(n: float, signe: bool = False) -> str:
    ""
    s = f"{abs(n):,.2f}".replace(",", " ").replace(".", ",")
    s = s.rstrip("0").rstrip(",")
    if signe:
        return ("+ " if n >= 0 else "− ") + s + " gros"
    return ("−" if n < 0 else "") + s + " gros"


def heure(h: int, origine: int = 0) -> str:
    j = int((h - origine) // 86400) + 1
    s = int(h % 86400)
    return T("jour {0}, {1:02d}:{2:02d}", j, s // 3600, (s % 3600) // 60)


class Chiffre(QFrame):
    def __init__(self, titre: str) -> None:
        super().__init__()
        self.setObjectName("Carte")
        v = QVBoxLayout(self)
        self.valeur = QLabel("—")
        self.valeur.setObjectName("Valeur")
        self.valeur.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titre = QLabel(T(titre))
        self.titre.setObjectName("Titre")
        self.titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titre.setWordWrap(True)
        v.addWidget(self.valeur)
        v.addWidget(self.titre)


def tableau(colonnes: list[str]) -> QTableWidget:
    t = QTableWidget(0, len(colonnes))
    t.setHorizontalHeaderLabels([T(_x) for _x in colonnes])

    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    t.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
    t.verticalHeader().setVisible(False)
    t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    t.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
    return t


def cellule(t: QTableWidget, i: int, j: int, texte: str, couleur: str | None = None) -> None:
    item = QTableWidgetItem(T(texte))
    if j:
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    if couleur:
        item.setForeground(QColor(couleur))
    t.setItem(i, j, item)


class PageArtisan(QWidget):
    ""

    def __init__(self, code: str, nom: str) -> None:
        super().__init__()
        self.code, self.nom = code, nom
        v = QVBoxLayout(self)
        v.setContentsMargins(8, 8, 8, 8)
        self.solde = QLabel(T("Solde de la caisse : —"))
        self.solde.setObjectName("Solde")
        v.addWidget(self.solde)
        self.table = tableau(["Quand (heure du jeu)", "Mouvement", "Montant", "Solde de la caisse"])
        v.addWidget(self.table, 1)
        self._vu = None

    def remplir(self, livre: dict, origine: int) -> None:
        mouvements = (livre.get("caisses") or {}).get(self.code) or []
        solde = (livre.get("caisses_soldes") or {}).get(self.code)
        vu = (len(mouvements), mouvements[-1]["h"] if mouvements else None, solde, origine)
        if vu == self._vu:
            return
        self._vu = vu
        self.solde.setText(T("Solde de la caisse : {0}", gros_fin(solde)) if solde is not None else
                           T("Solde de la caisse : le jeu le dira au prochain relevé (chaque seconde, partie lancée)."))
        lignes = list(reversed(mouvements))[:400]
        self.table.setRowCount(len(lignes))
        for i, mv in enumerate(lignes):
            cellule(self.table, i, 0, heure(mv["h"], origine))
            cellule(self.table, i, 1, libelle_caisse(mv.get("l", ""), mv["m"]))
            cellule(self.table, i, 2, gros_fin(mv["m"], True), VERT if mv["m"] >= 0 else ROUGE)
            cellule(self.table, i, 3, gros_fin(mv["s"]))


class FenetreBanque(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(T("Banque du camp"))
        self.resize(1000, 700)
        self.setStyleSheet(f"""
            QWidget {{ background: {FOND}; color: {ENCRE}; font-family: Georgia; font-size: 11pt; }}
            QFrame#Carte {{ background: {CARTE}; border: 1px solid #4a3d2c; border-radius: 6px; }}
            QLabel#Valeur {{ color: {OR}; font-size: 20pt; }}
            QLabel#Titre {{ color: {PALE}; font-size: 10pt; }}
            QLabel#Entete {{ color: {OR}; font-size: 22pt; }}
            QLabel#Note {{ color: {PALE}; font-size: 10pt; }}
            QLabel#Solde {{ color: {OR}; font-size: 14pt; }}
            QTableWidget {{ background: {CARTE}; gridline-color: #4a3d2c; border: none; }}
            QHeaderView::section {{ background: #3a2f22; color: {OR}; border: none; padding: 6px; }}
            QTabWidget::pane {{ border: 1px solid #4a3d2c; }}
            QTabBar::tab {{ background: {CARTE}; color: {PALE}; padding: 8px 16px; border: 1px solid #4a3d2c; }}
            QTabBar::tab:selected {{ background: #3a2f22; color: {OR}; }}
            QPushButton {{ background: #3a2f22; color: {ENCRE}; border: 1px solid #6b5537; padding: 6px 14px; }}
            QPushButton:hover {{ color: {OR}; }}
            QPushButton:disabled {{ color: #5a5040; }}
            QSpinBox {{ background: {CARTE}; border: 1px solid #6b5537; padding: 4px; min-width: 90px; }}
        """)
        v = QVBoxLayout(self)
        v.setContentsMargins(18, 16, 18, 16)
        v.setSpacing(10)
        haut = QHBoxLayout()
        entete = QLabel(T("Banque du camp"))
        entete.setObjectName("Entete")
        haut.addWidget(entete)
        haut.addStretch(1)

        if not chemins.gele():
            self.bouton_zero = QPushButton(T("Remettre à zéro"))
            self.bouton_zero.clicked.connect(self.remettre_a_zero)
            haut.addWidget(self.bouton_zero)
        v.addLayout(haut)



        bandeau = QGridLayout()
        bandeau.setSpacing(10)
        self.c_coffre = Chiffre("coffre du camp")
        self.c_rentrees = Chiffre("rentrée d'argent\nde la semaine")
        self.c_depenses = Chiffre("dépenses\nde la semaine (sorties et payes dues)")
        self.c_semaine = Chiffre("bénéfice de la semaine")

        self.c_bourses = Chiffre("à payer aux combattants\n(paye du soir à 20 h, et primes)")
        self.c_part = Chiffre("part pour Henry")
        self.c_directeur = Chiffre("part pour le Directeur")
        for i, c in enumerate((self.c_coffre, self.c_rentrees, self.c_depenses, self.c_semaine)):
            bandeau.addWidget(c, 0, i)
        for i, c in enumerate((self.c_bourses, self.c_part, self.c_directeur)):
            bandeau.addWidget(c, 1, i)
        v.addLayout(bandeau)

        self.controle = QLabel("")
        self.controle.setWordWrap(True)
        v.addWidget(self.controle)



        caisse = QFrame()
        caisse.setObjectName("Carte")
        hc = QHBoxLayout(caisse)
        hc.setContentsMargins(14, 8, 14, 8)
        titre_caisse = QLabel(T("Caisse du camp"))
        titre_caisse.setObjectName("Titre")
        hc.addWidget(titre_caisse)
        self.etat_caisse = QLabel(T("dans le coffre : —   ·   sur toi : —"))
        hc.addWidget(self.etat_caisse, 1)
        self.montant = QSpinBox()
        self.montant.setRange(0, 10_000_000)
        self.montant.setSingleStep(100)
        self.montant.setSuffix(T(" gros"))
        self.montant.setMinimumWidth(140)
        hc.addWidget(self.montant)
        self.b_mettre = QPushButton(T("Mettre dans la caisse"))
        self.b_mettre.clicked.connect(lambda: self.bouger_la_caisse("deposer"))
        hc.addWidget(self.b_mettre)
        self.b_prendre = QPushButton(T("Prendre dans la caisse"))
        self.b_prendre.clicked.connect(lambda: self.bouger_la_caisse("prendre"))
        hc.addWidget(self.b_prendre)
        b_lire = QPushButton(T("Actualiser"))
        b_lire.clicked.connect(self.lire_la_caisse)
        hc.addWidget(b_lire)
        v.addWidget(caisse)



        self.onglets = QTabWidget()
        self.t_mvt = tableau(["Quand (heure du jeu)", "Mouvement", "Montant", "Solde du coffre"])
        self.onglets.addTab(self.t_mvt, T("Mouvements"))




        self.onglets.addTab(self._page_prime(), T("Prime des commerçants"))
        self.onglets.currentChanged.connect(self._onglet_change)
        self.pages_artisans: dict[str, PageArtisan] = {}
        for code, nom in ARTISANS:
            p = PageArtisan(code, nom)
            self.pages_artisans[code] = p
            self.onglets.addTab(p, T(nom))
        v.addWidget(self.onglets, 1)
        self.note = QLabel("")
        self.note.setObjectName("Note")
        self.note.setWordWrap(True)
        v.addWidget(self.note)

        self._vu = None
        self._reponse = None
        self._en_cours = False
        self.minuterie = QTimer(self)
        self.minuterie.timeout.connect(self.surveiller)
        self.minuterie.start(1000)
        self.rafraichir()


    def _parler(self, code: str) -> str | None:
        try:
            sys.path.insert(0, str(RACINE))
            sys.path.insert(0, str(RACINE / "outils_de_session"))
            from essais.cycle_en_jeu import Jeu
            from dire import parler
            return parler(Jeu(), code, 20)
        except Exception:
            return None

    def remettre_a_zero(self) -> None:
        if QMessageBox.question(
                self, T("Remettre à zéro"),
                T("Effacer tout le journal de la banque (mouvements du coffre et des artisans, bénéfice) ?\n\n"
                "Les poches des hommes, leurs dettes et les primes de combat en attente repartent "
                "elles aussi à zéro.")) \
                != QMessageBox.StandardButton.Yes:
            return
        r = self._parler("return scriptorium.banque.remettre_a_zero(_G.compagnie)")
        if not (r and "remise" in r):
            QMessageBox.warning(self, T("Remettre à zéro"), T("La partie n'a pas répondu : rien n'a été effacé. "
                                "Le jeu doit être lancé, la partie chargée."))
            return
        livre_module().remettre_a_zero()
        self._vu = None
        self.rafraichir()


    def _montrer_caisse(self, r: str | None) -> bool:
        m = re.search(r"caisse (-?\d+)-(-?\d+)", r or "")
        if not m:
            return False
        self.etat_caisse.setText(T("dans le coffre : {0}   ·   sur toi : {1}", gros(int(m.group(1))), gros(int(m.group(2)))))
        return True

    def lire_la_caisse(self) -> None:


        if self._en_cours:
            return
        self._en_cours = True
        self.etat_caisse.setText(T("je demande à la partie…"))

        def fil() -> None:
            try:
                caisse = self._parler("return scriptorium.banque.caisse(_G.compagnie)")

                self._reponse_prime = self._parler("return scriptorium.caisse_de_prime.etat(_G.compagnie)") if caisse else None
                self._reponse = ("caisse", caisse)
            finally:
                self._en_cours = False
        threading.Thread(target=fil, daemon=True).start()

    def _cueillir(self) -> None:
        rep, self._reponse = self._reponse, None
        if rep is None:
            return
        if not self._montrer_caisse(rep[1]):
            self.etat_caisse.setText(T("La partie n'a pas répondu : le jeu doit être lancé, "
                                     "la partie chargée."))
        prime, self._reponse_prime = getattr(self, "_reponse_prime", None), None
        if prime:
            self._montrer_prime(prime)

    def bouger_la_caisse(self, geste: str) -> None:
        n = int(self.montant.value())
        if n <= 0:
            self.etat_caisse.setText(T("Choisis d'abord un montant."))
            return
        self.etat_caisse.setText(T("je demande à la partie…"))
        QApplication.processEvents()

        import random
        jeton = random.randint(1, 9_000_000)

        r = self._parler(f"return scriptorium.banque.{geste}_une_fois(_G.compagnie, {n}, 'j{jeton}')") or ""
        if not self._montrer_caisse(r):
            self.etat_caisse.setText(T("La partie n'a pas répondu : rien n'a bougé. Le jeu doit être "
                                     "lancé, la partie chargée."))
            return
        fait = re.search(r"(depot|retrait) (\d+) caisse", r)
        texte = self.etat_caisse.text()
        if fait:
            n_fait = int(fait.group(2))
            quoi = "mis dans la caisse" if fait.group(1) == "depot" else "pris dans la caisse"
            reste = ""
            if fait.group(1) == "retrait" and n_fait < n:
                reste = " (pas plus : le coffre n'en avait pas davantage, ou ta bourse n'en prenait pas " \
                        "plus -- ce qui reste est toujours au coffre)"
            self.etat_caisse.setText(T("{0} {1}{2}.   {3}", gros(n_fait), quoi, reste, texte))
        elif "refuse-bourse" in r and geste == "deposer":
            self.etat_caisse.setText(T("Tu n'as pas assez sur toi.   {0}", texte))
        elif "refuse-vide" in r:
            self.etat_caisse.setText(T("Le coffre est vide.   {0}", texte))
        else:
            self.etat_caisse.setText(T("Refusé.   {0}", texte))


    def _montrer_prime(self, r: str) -> bool:
        e = re.search(r"caisseprime ([\d.]+) (\d+)", r or "")
        if not e:
            return False
        self.montant_prime_vu.setText(T(gros_fin(float(e.group(1)))))
        self.ayants_prime.setText(T("dans la caisse de prime (à part du coffre du camp)   ·   {0} homme(s) y ont droit aujourd'hui (au moins 7 jours complets au camp)", e.group(2)))
        return True

    def lire_la_prime(self) -> None:

        self.lire_la_caisse()

    def distribuer_la_prime(self) -> None:
        pc = int(self.pourcent_prime.value())
        if pc <= 0:
            self.etat_prime.setText(T("Choisis d'abord un pourcentage."))
            return
        rep = QMessageBox.question(self, T("Distribuer la prime"),
                                   T("Distribuer {0} % de la caisse de prime, à part égale, à tous les hommes qui ont au moins 7 jours complets au camp ?", pc))
        if rep != QMessageBox.StandardButton.Yes:
            return
        import random
        jeton = random.randint(1, 9_000_000)
        r = self._parler(f"return scriptorium.caisse_de_prime.distribuer(_G.compagnie, {pc}, 'henry', 'j{jeton}')") or ""
        f = re.search(r"prime ([\d.]+) (\d+) ([\d.]+) ([\d.]+)", r)
        if f:
            self.etat_prime.setText(T("{0} distribués à part égale à {1} homme(s), {2} chacun.   Il reste {3} dans la caisse de prime.", gros(float(f.group(1))), f.group(2), gros(float(f.group(3))), gros(float(f.group(4)))))
            self.montant_prime_vu.setText(T(gros_fin(float(f.group(4)))))
        elif "refus personne" in r:
            self.etat_prime.setText(T("Personne n'y a droit aujourd'hui : il faut au moins 7 jours complets au camp."))
        elif "refus vide" in r or "refus peu" in r:
            self.etat_prime.setText(T("La caisse de prime est vide (ou trop peu pour une part)."))
        else:
            self.etat_prime.setText(T("La partie n'a pas répondu : rien n'a été distribué."))

    def deposer_a_la_prime(self, qui: str) -> None:
        n = int(self.montant_prime.value())
        if n <= 0:
            self.etat_prime.setText(T("Choisis d'abord un montant."))
            return
        import random
        jeton = random.randint(1, 9_000_000)
        r = self._parler(f"return scriptorium.caisse_de_prime.deposer(_G.compagnie, {n}, '{qui}', 'j{jeton}')") or ""
        f = re.search(r"depot (\d+) ([\d.]+)", r)
        if f:
            de = "de ta bourse" if qui == "henry" else "du coffre du camp"
            self.etat_prime.setText(T("{0} mis dans la caisse de prime ({1}).", gros(int(f.group(1))), de))
            self.montant_prime_vu.setText(T(gros_fin(float(f.group(2)))))
        elif "refus bourse" in r:
            self.etat_prime.setText(T("Tu n'as pas assez sur toi."))
        elif "refus coffre" in r:
            self.etat_prime.setText(T("Le coffre du camp n'a pas assez."))
        else:
            self.etat_prime.setText(T("La partie n'a pas répondu : rien n'a bougé."))


    def _page_prime(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(14, 12, 14, 12)
        self.montant_prime_vu = QLabel(T("— gros"))
        self.montant_prime_vu.setStyleSheet("font-size: 30px; font-weight: bold;")
        v.addWidget(self.montant_prime_vu)
        self.ayants_prime = QLabel(T("dans la caisse de prime (à part du coffre du camp)"))
        self.ayants_prime.setWordWrap(True)
        v.addWidget(self.ayants_prime)
        regle = QLabel(T("Chaque lundi, après la paye et les taxes, chaque commerçant donne selon son envie (au moins 1 % de la "
                       "caisse de son commerce) ; le Directeur contrôle, puis distribue tout, à part égale, à tous les hommes "
                       "qui ont au moins 7 jours complets au camp."))
        regle.setWordWrap(True)
        regle.setObjectName("Note")
        v.addWidget(regle)
        h1 = QHBoxLayout()
        h1.addWidget(QLabel(T("Distribuer maintenant :")))
        self.pourcent_prime = QSpinBox()
        self.pourcent_prime.setRange(1, 100)
        self.pourcent_prime.setValue(100)
        self.pourcent_prime.setSuffix(T(" % de la caisse"))
        h1.addWidget(self.pourcent_prime)
        b_distribuer = QPushButton(T("Distribuer à part égale"))
        b_distribuer.clicked.connect(self.distribuer_la_prime)
        h1.addWidget(b_distribuer)
        h1.addStretch(1)
        v.addLayout(h1)
        h2 = QHBoxLayout()
        h2.addWidget(QLabel(T("Mettre dans la caisse :")))
        self.montant_prime = QSpinBox()
        self.montant_prime.setRange(0, 10_000_000)
        self.montant_prime.setSingleStep(100)
        self.montant_prime.setSuffix(T(" gros"))
        self.montant_prime.setMinimumWidth(140)
        h2.addWidget(self.montant_prime)
        b_henry = QPushButton(T("De ma bourse"))
        b_henry.clicked.connect(lambda: self.deposer_a_la_prime("henry"))
        h2.addWidget(b_henry)
        b_coffre = QPushButton(T("Du coffre du camp"))
        b_coffre.clicked.connect(lambda: self.deposer_a_la_prime("coffre"))
        h2.addWidget(b_coffre)
        b_lire_prime = QPushButton(T("Actualiser"))
        b_lire_prime.clicked.connect(self.lire_la_prime)
        h2.addWidget(b_lire_prime)
        h2.addStretch(1)
        v.addLayout(h2)
        self.etat_prime = QLabel("")
        self.etat_prime.setWordWrap(True)
        v.addWidget(self.etat_prime)
        self.t_prime = tableau(["Quand (heure du jeu)", "Mouvement", "Montant"])
        v.addWidget(self.t_prime, 1)

        self._minuteur_prime = QTimer(page)
        self._minuteur_prime.timeout.connect(self._relire_si_ouverte)
        self._minuteur_prime.start(20_000)
        return page

    def _prime_ouverte(self) -> bool:
        try:
            return self.onglets.tabText(self.onglets.currentIndex()) == T("Prime des commerçants")
        except Exception:
            return False

    def _onglet_change(self, _i: int) -> None:
        if self._prime_ouverte():
            self.lire_la_prime()

    def _relire_si_ouverte(self) -> None:
        if self._prime_ouverte() and self.isVisible():
            self.lire_la_caisse()

    def _historique_prime(self, journal: list, origine: int) -> None:
        ""
        lignes = [mv for mv in journal if str(mv.get("code", "")).startswith("prime_")]
        empreinte = (len(lignes), lignes[-1]["h"] if lignes else None, origine)
        if empreinte == getattr(self, "_empreinte_prime", None):
            return
        self._empreinte_prime = empreinte
        noms = dict(ARTISANS)
        lignes = list(reversed(lignes))[:300]
        self.t_prime.setRowCount(len(lignes))
        for r_, mv in enumerate(lignes):
            code, qui, n = mv["code"], str(mv.get("qui") or ""), int(mv.get("n") or 0)
            if code == "prime_caisse":
                nom = noms.get(qui, qui)
                texte, entre = T("Don de {0}", nom[:1].lower() + nom[1:] if langue() == "fr" else nom), True
            elif code == "prime_henry":
                texte, entre = "Mis par Henry (sa bourse)", True
            elif code == "prime_coffre":
                texte, entre = "Mis par le Directeur (coffre du camp)", True
            else:
                par = "par le Directeur" if qui.lower().startswith("directeur") else "par Henry"
                texte, entre = T("Distribuée {0}, à part égale entre {1} homme(s)", par, n), False
            cellule(self.t_prime, r_, 0, heure(mv["h"], origine))
            cellule(self.t_prime, r_, 1, texte)
            cellule(self.t_prime, r_, 2, gros(mv["gros"] if entre else -mv["gros"], True), VERT if entre else ROUGE)

    def lire_le_jeu(self) -> None:
        ""





        if not getattr(self, "_lecture_en_cours", False):
            self._lecture_en_cours = True

            def fil() -> None:
                try:
                    if getattr(self, "_livre", None) is None:
                        self._livre = livre_module()
                    ordres = [] if getattr(self, "_ordres", False) else None
                    self._livre.rattraper(commandes=ordres)
                    self._ordres = True
                    if ordres:
                        self._ordres_recus = (getattr(self, "_ordres_recus", None) or []) + ordres
                except Exception:
                    pass
                finally:
                    self._lecture_en_cours = False
            threading.Thread(target=fil, daemon=True).start()
        ordres, self._ordres_recus = getattr(self, "_ordres_recus", None) or [], []
        for o in ordres:
            try:
                if o == "coffret banque":
                    sys.path.insert(0, str(RACINE))
                    from noyau.premier_plan import au_premier_plan

                    au_premier_plan(self.window())
                    QTimer.singleShot(300, self.lire_la_caisse)
                elif o == "coffret panneau" and not chemins.gele():
                    import subprocess
                    exe = Path(sys.executable)
                    w = exe.with_name("pythonw.exe")
                    subprocess.Popen([str(w if w.is_file() else exe), str(RACINE / "lancer.py")], cwd=str(RACINE),
                                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            except Exception:
                pass

    def surveiller(self) -> None:
        self._cueillir()
        self.lire_le_jeu()
        try:
            vu = chemins.dossier_local().joinpath("banque.json").stat().st_mtime
        except Exception:
            vu = None
        if vu != self._vu:
            self._vu = vu
            self.rafraichir()


    def _noms_des_hommes(self) -> dict:
        import time as _t
        if getattr(self, "_noms_lus", 0) and _t.time() - self._noms_lus < 60:
            return self._noms
        self._noms_lus = _t.time()
        noms = getattr(self, "_noms", {}) or {}
        try:
            racine = livre_module().racine_du_jeu()
            with open(Path(racine) / "kcd.log", "rb") as f:
                brut = f.read().decode("utf-8", "replace")
            for ligne in brut.splitlines():
                i = ligne.find("[ScriptoPersonnel] h|")
                if i >= 0:
                    c = ligne[i + len("[ScriptoPersonnel] h|"):].split("|")
                    if len(c) > 1 and c[0] and c[1]:

                        noms[re.sub(r"[^A-Za-z0-9]", "", c[0])] = c[1]
        except Exception:
            pass
        self._noms = noms
        return noms


    def rafraichir(self) -> None:
        try:
            mod = livre_module()
            livre = mod.lire()
        except Exception as e:
            self.note.setText(T("Journal illisible : {0}", e))
            return
        journal = livre.get("journal", [])
        origine = livre.get("origine") or (min((mv["h"] for mv in journal), default=0) // 86400) * 86400
        self._origine = origine
        effet = mod.EFFET_AU_COFFRE


        payes = livre.get("payes") or []
        depuis = max(payes) if payes else None
        semaine = [mv for mv in journal if depuis is None or mv.get("h", 0) > depuis]



        du_coffre = [mv for mv in semaine if effet.get(mv["code"], 0) != 0]


        soldes = sorted(livre.get("soldes") or [], key=lambda x: x[0])
        import bisect
        heures_s = [s[0] for s in soldes]
        solde_de: dict[int, float] = {}
        par_heure: dict[int, list[int]] = {}
        for i, mv in enumerate(du_coffre):
            par_heure.setdefault(mv["h"], []).append(i)
        for h, idx in par_heure.items():
            k = bisect.bisect_right(heures_s, h) - 1
            if k < 0 or heures_s[k] != h:
                continue
            s = soldes[k][1]
            for i in reversed(idx):
                solde_de[i] = s
                mv = du_coffre[i]
                s -= effet.get(mv["code"], 0) * mv["gros"]
        try:
            _pct_h = float((livre.get("prix") or {}).get("part", 0) or 0)
        except (TypeError, ValueError):
            _pct_h = 0.0
        try:
            self._historique_prime(journal, origine)
        except Exception:
            pass
        noms = self._noms_des_hommes()


        empreinte = (len(du_coffre), du_coffre[-1]["h"] if du_coffre else None, len(soldes), origine, len(noms))
        refaire = empreinte != getattr(self, "_empreinte_mvt", None)
        self._empreinte_mvt = empreinte
        lignes = list(reversed(list(enumerate(du_coffre))))[:500] if refaire else []
        if refaire:
            self.t_mvt.setRowCount(len(lignes))
        for r_, (i, mv) in enumerate(lignes):
            libelle = mod.MOUVEMENTS.get(mv["code"], (mv["code"], True))[0]
            entre = effet.get(mv["code"], 0) > 0
            cellule(self.t_mvt, r_, 0, heure(mv["h"], origine))
            cellule(self.t_mvt, r_, 1, phrase_du_coffre(mv, libelle, noms, _pct_h))
            cellule(self.t_mvt, r_, 2, gros(mv["gros"] if entre else -mv["gros"], True), VERT if entre else ROUGE)
            cellule(self.t_mvt, r_, 3, gros(solde_de[i]) if i in solde_de else "—")




        cette_semaine = mod.depuis(journal, depuis)
        _du = livre.get("a_payer") or {}
        _du_total = sum(_du.get(k, 0) for k in ("solde", "primes", "autres"))
        _entre = cette_semaine.get("entrees", 0)
        _sorti = cette_semaine.get("sorties", 0)
        self._depenses_semaine = _sorti + _du_total
        self._benefice_net = _entre - self._depenses_semaine
        self.c_coffre.valeur.setText(T(gros(livre.get("coffre", 0))))
        self.c_rentrees.valeur.setText(T(gros(_entre)))
        self.c_depenses.valeur.setText(T(gros(-self._depenses_semaine)))
        self.c_semaine.valeur.setText(T(gros(self._benefice_net, True)))
        self.c_bourses.valeur.setText(T(gros(_du.get("solde", 0) + _du.get("primes", 0))) if _du else "—")

        try:
            _pct = float((livre.get("prix") or {}).get("part", 0) or 0)
        except (TypeError, ValueError):
            _pct = 0.0



        _partage = a_partager(self._benefice_net, livre.get("coffre", 0) or 0, _du_total)
        for carte, code, pct, qui in ((self.c_part, "henry", _pct, "Henry"),
                                      (self.c_directeur, "directeur", PART_DIRECTEUR, "le Directeur")):
            lignes_part = [mv for mv in semaine if mv["code"] == code]
            de_la_semaine = sum(mv["gros"] for mv in lignes_part if pct and abs(mv.get("n", 0) - pct) < 0.01)
            missions = sum(mv["gros"] for mv in lignes_part) - de_la_semaine
            en_plus = T("\n+ {0} déjà touchés (parts de mission)", gros(missions)) if missions > 0 else ""
            if de_la_semaine > 0:
                carte.titre.setText(T("part pour {0}\n(touchée à la paye){1}", qui, en_plus))
                carte.valeur.setText(T(gros(de_la_semaine)))
            else:
                carte.titre.setText(T("part pour {0}\n(prévue : {1:g} % du bénéfice, sur ce qui dépasse {2} au coffre après les payes){3}", qui, pct, gros(MINIMUM_COFFRE), en_plus))
                carte.valeur.setText(T(gros(_partage * pct / 100)))


        try:
            ctl = mod.verifier_les_comptes(livre)
            faux = [j for j in ctl["jours"] if abs(j["ecart"]) >= 2]
            if not ctl["jours"]:
                self.controle.setText(T("Contrôle des comptes : il commence avec les prochains mouvements du coffre."))
            elif not faux:
                self.controle.setText(T("Contrôle des comptes : juste. Sur {0} jour(s) vérifié(s), chaque mouvement du coffre est expliqué par le journal.", len(ctl['jours'])))
            else:
                d = faux[-1]
                self.controle.setText(T("Contrôle des comptes : {0} jour(s) avec un écart (en tout {1}). Dernier : jour {2}, le coffre a bougé de {3}, le journal explique {4}.", len(faux), gros(ctl['ecart'], True), d['jour'], gros(d['reel'], True), gros(d['attendu'], True)))
        except Exception as err:
            self.controle.setText(T("Contrôle des comptes indisponible : {0}", err))


        for p in self.pages_artisans.values():
            p.remplir(livre, origine)


        if _du:
            self.note.setText(T("Bénéfice net = ") + T(gros(_entre)) + T(" entrés  −  ") + T(gros(_sorti)) + T(" déjà sortis  −  ")
                              + T(gros(_du.get("solde", 0))) + T(" de soldes dues  −  ") + T(gros(_du.get("primes", 0)))
                              + T(" de primes dues  −  ") + T(gros(_du.get("autres", 0))) + T(" dus aux métiers  =  ")
                              + T(gros(self._benefice_net, True)) + ".")
        else:
            self.note.setText(T("Ce qui est dû aux hommes s'affiche dès que la partie le publie."))






PROGRAMME = RACINE / "gestion_du_camp" / "programme.py"


def main() -> int:
    import subprocess
    exe = Path(sys.executable)
    w = exe.with_name("pythonw.exe")
    subprocess.Popen([str(w if w.is_file() else exe), str(PROGRAMME), "--onglet", "banque", "--devant"],
                     cwd=str(RACINE), creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
