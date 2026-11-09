
""

























from __future__ import annotations

import importlib.util
import sys
import threading
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from noyau import chemins, langue_du_programme as lg
from noyau.langue_du_programme import T

from PyQt6.QtCore import QEvent, QObject, QPoint, Qt, QTimer
from PyQt6.QtWidgets import (QApplication, QButtonGroup, QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
                             QScrollArea, QStackedWidget, QVBoxLayout, QWidget)

from gestion_du_camp import habillage as hb

NOM_INSTANCE = "ScriptoriumGestionDuCamp"


ONGLETS = ["accueil", "coffre", "hommes", "artisans", "construire", "plan", "objectifs"]
TITRES = {"accueil": "Le camp aujourd'hui", "coffre": "Le coffre", "hommes": "Les hommes", "artisans": "Les artisans",
          "construire": "Construire", "plan": "Le plan du camp", "objectifs": "Les objectifs"}

ANCIENS = {"banque": ("coffre", None), "embauche": ("hommes", "engager"), "personnel": ("hommes", "compagnie"),
           "metiers": ("artisans", "metiers"), "amenagement": ("plan", "objets"), "emplacements": ("plan", "zones")}
EDITEUR = RACINE / "choses" / "editeur_du_camp" / "fenetre_editeur.py"
EMPLACEMENTS = RACINE / "choses" / "editeur_du_camp" / "fenetre_emplacements.py"


def _module(nom: str, chemin: Path):
    spec = importlib.util.spec_from_file_location(nom, chemin)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class EnAttente(QWidget):
    ""

    def __init__(self, texte: str) -> None:
        super().__init__()
        v = QVBoxLayout(self)
        self.etiquette = QLabel(T(texte))
        self.etiquette.setObjectName("Note")
        self.etiquette.setWordWrap(True)
        v.addWidget(self.etiquette)
        v.addStretch(1)


def defilante(vue: QWidget) -> QScrollArea:
    ""
    zone = QScrollArea()
    zone.setWidgetResizable(True)
    zone.setFrameShape(QFrame.Shape.NoFrame)
    zone.setStyleSheet("QScrollArea { background: transparent; } QScrollArea > QWidget > QWidget { background: transparent; }")
    zone.viewport().setAutoFillBackground(False)
    zone.setWidget(vue)
    zone.contenu = vue
    return zone


def cacher_l_ancien_titre(vue: QWidget) -> None:
    ""
    for lab in vue.findChildren(QLabel):
        if lab.objectName() == "Entete":
            lab.hide()


def orner(w: QWidget) -> None:
    ""
    for lab in w.findChildren(QLabel):
        if lab.objectName() == "Entete":
            lab.setFont(hb.police(24, False, True))
        elif lab.objectName() == "Section":
            lab.setFont(hb.police(15, False, True))


class Rubrique(QWidget):
    ""

    def __init__(self, titre: str, sous_titre: str) -> None:
        super().__init__()
        self.setStyleSheet(hb.feuille())
        v = QVBoxLayout(self)
        v.setContentsMargins(26, 20, 26, 14)
        v.setSpacing(6)
        t = QLabel(T(titre))
        t.setObjectName("Entete")
        v.addWidget(t)
        s = QLabel(T(sous_titre))
        s.setObjectName("Note")
        s.setWordWrap(True)
        v.addWidget(s)
        self.rang_des_puces = QHBoxLayout()
        self.rang_des_puces.setSpacing(8)
        self.rang_des_puces.addStretch(1)
        v.addLayout(self.rang_des_puces)
        self.pile = QStackedWidget()
        v.addWidget(self.pile, 1)
        self.groupe = QButtonGroup(self)
        self.groupe.setExclusive(True)
        self.vues: dict[str, QWidget] = {}
        self.quand_montree = None
        orner(self)

    def ajouter(self, cle: str, titre: str, vue: QWidget, defilable: bool = True) -> None:
        b = QPushButton(T(titre))
        b.setObjectName("Puce")
        b.setCheckable(True)
        b.clicked.connect(lambda _=False, c=cle: self.montrer(c))
        self.groupe.addButton(b)
        self.rang_des_puces.insertWidget(self.rang_des_puces.count() - 1, b)
        cacher_l_ancien_titre(vue)


        if defilable:
            vue = defilante(vue)
        self.vues[cle] = vue
        vue._puce = b
        self.pile.addWidget(vue)
        if len(self.vues) == 1:
            b.setChecked(True)

    def remplacer(self, cle: str, vue: QWidget) -> None:
        avant = self.vues[cle]
        i = self.pile.indexOf(avant)
        garde = self.pile.currentIndex() == i
        hb.arreter_l_entree(avant)
        self.pile.removeWidget(avant)
        avant.hide()
        avant.deleteLater()
        cacher_l_ancien_titre(vue)
        self.pile.insertWidget(i, vue)
        vue._puce = avant._puce
        self.vues[cle] = vue
        if garde:
            self.pile.setCurrentIndex(i)

    def vue(self) -> str | None:
        for c, w in self.vues.items():
            if self.pile.currentWidget() is w:
                return c
        return None

    def montrer(self, cle: str | None) -> None:
        if cle not in self.vues:
            return
        w = self.vues[cle]
        w._puce.setChecked(True)
        if self.pile.currentWidget() is not w:
            self.pile.setCurrentWidget(w)
            hb.entree(w)
        if self.quand_montree:
            self.quand_montree(cle)


class Accueil(QWidget):
    ""



    def __init__(self, cadre) -> None:
        super().__init__()
        self.cadre = cadre
        self.setStyleSheet(hb.feuille())
        v = QVBoxLayout(self)
        v.setContentsMargins(26, 20, 26, 14)
        v.setSpacing(8)
        haut = QHBoxLayout()
        t = QLabel(T("Le camp aujourd'hui"))
        t.setObjectName("Entete")
        haut.addWidget(t)
        haut.addStretch(1)
        haut.addWidget(hb.Flamme())
        v.addLayout(haut)
        self.sous = QLabel(T("Ce que le camp a à vous dire, d'un coup d'œil."))
        self.sous.setObjectName("Note")
        v.addWidget(self.sous)
        grille = QGridLayout()
        grille.setSpacing(12)
        self.cartes = {}
        for i, (cle, quoi) in enumerate((("coffre", "au coffre du camp"), ("semaine", "bénéfice de la semaine"),
                                          ("hommes", "hommes dans la compagnie"), ("objectifs", "objectifs de la semaine"))):
            c = QFrame()
            c.setObjectName("Carte")
            cv = QVBoxLayout(c)
            cv.setContentsMargins(16, 12, 16, 12)
            val = QLabel("—")
            val.setObjectName("Valeur")
            lab = QLabel(T(quoi))
            lab.setObjectName("Titre")
            lab.setWordWrap(True)
            cv.addWidget(val)
            cv.addWidget(lab)
            grille.addWidget(c, i // 2, i % 2)
            self.cartes[cle] = val
        v.addLayout(grille)
        attention = QFrame()
        attention.setObjectName("Carte")
        attention.setStyleSheet(f"QFrame#Carte {{ border-left: 4px solid {hb.CIRE}; }}")
        av = QVBoxLayout(attention)
        av.setContentsMargins(16, 12, 16, 12)
        s = QLabel(T("Ce qui demande votre attention"))
        s.setObjectName("Section")
        av.addWidget(s)
        self.lignes = QVBoxLayout()
        self.lignes.setSpacing(4)
        av.addLayout(self.lignes)
        v.addWidget(attention)
        v.addStretch(1)
        aide = QLabel(T("Les rubriques à gauche : un clic pour y aller. La touche H rend la main au jeu."))
        aide.setObjectName("Note")
        v.addWidget(aide)
        orner(self)

    def _lien(self, texte: str, ou: str | None, vue: str | None = None) -> None:
        rang = QHBoxLayout()
        lab = QLabel("•  " + texte)
        lab.setWordWrap(True)
        rang.addWidget(lab, 1)
        if ou:
            b = QPushButton(T("Y aller"))
            b.setObjectName("Clair")
            b.clicked.connect(lambda: self.cadre.montrer(ou, vue))
            rang.addWidget(b)
        self.lignes.addLayout(rang)

    def actualiser(self) -> None:
        c = self.cadre
        b = getattr(c, "banque", None)
        if b is not None:
            self.cartes["coffre"].setText(b.c_coffre.valeur.text())
            self.cartes["semaine"].setText(b.c_semaine.valeur.text())
        e = getattr(c, "embauche", None)
        if e is not None:
            self.cartes["hommes"].setText(e.v_compagnie.text())
        o = getattr(c, "objectifs", None)
        if o is not None:
            self.cartes["objectifs"].setText(getattr(o, "atteints_sur", "—") or "—")
        while self.lignes.count():
            it = self.lignes.takeAt(0)
            lay = it.layout()
            if lay is not None:
                while lay.count():
                    w = lay.takeAt(0).widget()
                    if w is not None:
                        w.deleteLater()
        n = 0
        p = getattr(c, "personnel", None)
        besoins = getattr(p, "nombre_de_besoins", None) if p is not None else None
        if besoins:
            self._lien(T("{0} personne(s) ont un besoin (faim, fatigue, soins, forge…).", besoins), "hommes", "compagnie")
            n += 1
        if o is not None and getattr(o, "reste_a_faire", None):
            self._lien(T("Objectifs : {0}", o.reste_a_faire), "objectifs")
            n += 1
        if b is not None and getattr(b, "coffre_lu", None) is not None and b.coffre_lu < 100:
            self._lien(T("Le coffre est presque vide : les payes du soir pourraient manquer."), "coffre")
            n += 1
        if not n:
            self._lien(T("Rien d'urgent. Le camp tourne."), None)


class GestionDuCamp(QWidget):
    ""



    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(T("Gestion du camp"))
        self.resize(1320, 960)
        self.setStyleSheet(hb.feuille())
        tout = QHBoxLayout(self)
        tout.setContentsMargins(0, 0, 0, 0)
        tout.setSpacing(0)

        ruban = hb.Ruban()
        ruban.setFixedWidth(240)
        ruban.setStyleSheet(f"""
            QLabel {{ color: #e9d7b0; background: transparent; }}
            QLabel#Titre {{ color: {hb.OR_CLAIR}; }}
            QPushButton#Rubrique {{ background: transparent; color: #e9d7b0; border: none; border-radius: 8px; text-align: left;
                                   padding: 10px 14px; font-size: 13pt; font-weight: normal; }}
            QPushButton#Rubrique:hover {{ background: rgba(226, 187, 92, 35); }}
            QPushButton#Rubrique:checked {{ color: #1d130b; font-weight: bold; border: 1px solid #f1d27e;
                                   background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {hb.OR_CLAIR}, stop:1 #8a6420); }}
            QComboBox {{ background: {hb.BOIS}; color: #e9d7b0; border: 1px solid #8a6420; }}
            QComboBox QAbstractItemView {{ background: {hb.BOIS}; color: #e9d7b0; selection-background-color: #8a6420; }}
        """)
        rv = QVBoxLayout(ruban)
        rv.setContentsMargins(14, 18, 16, 14)
        rv.setSpacing(4)
        bl = QHBoxLayout()
        bl.addStretch(1)
        bl.addWidget(hb.Blason())
        bl.addStretch(1)
        rv.addLayout(bl)
        nom = QLabel(T("Gestion du camp"))
        nom.setObjectName("Titre")
        nom.setFont(hb.police(16, False, True))
        nom.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rv.addWidget(nom)
        rv.addSpacing(12)
        self.groupe = QButtonGroup(self)
        self.groupe.setExclusive(True)
        self.boutons: dict[str, QPushButton] = {}
        for cle in ONGLETS:
            b = QPushButton(T(TITRES[cle]))
            b.setObjectName("Rubrique")
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _=False, c=cle: self.montrer(c))
            self.groupe.addButton(b)
            self.boutons[cle] = b
            rv.addWidget(b)
        rv.addStretch(1)
        self.bourse = QLabel(T("Sur vous : —"))
        self.bourse.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bourse.setWordWrap(True)
        self.bourse.setStyleSheet(f"background: rgba(0,0,0,70); border-radius: 8px; padding: 8px; color: {hb.OR_CLAIR};")
        rv.addWidget(self.bourse)
        rv.addSpacing(6)

        self.liste_des_langues = QComboBox()
        self.liste_des_langues.addItem(T("Langue du jeu"), lg.PAR_LE_JEU)
        for code, nom_l in lg.NOMS.items():
            self.liste_des_langues.addItem(nom_l, code)
        self.liste_des_langues.setCurrentIndex(max(0, self.liste_des_langues.findData(lg.lire_le_choix())))
        self.liste_des_langues.activated.connect(self._langue_choisie)
        rv.addWidget(self.liste_des_langues)
        h = QLabel(T("H : revenir au jeu"))
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h.setStyleSheet("color: #bfa77a; font-size: 10pt;")
        rv.addWidget(h)
        tout.addWidget(ruban)

        fond = hb.Parchemin()
        fv = QVBoxLayout(fond)
        fv.setContentsMargins(8, 8, 8, 8)
        fv.setSpacing(0)

        self._pause = QLabel("")
        self._pause.setWordWrap(True)
        self._pause.setStyleSheet(f"background:{hb.CIRE}; color:#fbe9d6; font-weight:bold; padding:8px 14px; border-radius:8px;")
        self._pause.hide()
        fv.addWidget(self._pause)
        self.pile = QStackedWidget()
        fv.addWidget(self.pile, 1)
        tout.addWidget(fond, 1)
        self.pluie = hb.PluieDePieces(self)

        self.pages: dict[str, QWidget] = {}

        from banque import fenetre_banque as fb
        self.banque = fb.FenetreBanque()
        self.banque.apres_un_geste = self._apres_un_geste
        self.banque.quand_la_caisse_est_lue = self._caisse_lue

        self.embauche = _module("onglet_embauche", Path(__file__).with_name("onglet_embauche.py")).OngletEmbauche()
        self.personnel = _module("onglet_personnel", Path(__file__).with_name("onglet_personnel.py")).OngletPersonnel()
        hommes = Rubrique("Les hommes", "Engager, connaître ses hommes, leur donner des ordres. Tout se paie au coffre du camp.")
        hommes.ajouter("engager", "Engager", self.embauche)
        hommes.ajouter("compagnie", "La compagnie et les ordres", self.personnel)
        hommes.quand_montree = self._vue_montree

        self.metiers = _module("onglet_metiers", Path(__file__).with_name("onglet_metiers.py")).OngletMetiers()
        artisans = Rubrique("Les artisans", "Une personne de chaque, payée une fois par le coffre. Chacun a sa caisse et vit de son métier.")
        page_service = self.embauche.sortir_les_artisans()
        artisans.ajouter("engager", "Engager ou renvoyer", page_service)
        artisans.ajouter("metiers", "Ce que rapportent les métiers", self.metiers)
        artisans.quand_montree = self._vue_montree

        construire = Rubrique("Construire", "Ce qui s'achète pour le camp : payé par le coffre du camp, jamais par la bourse d'Henry.")
        construire.ajouter("liste", "Les constructions", EnAttente("Chargement des constructions…"), defilable=False)
        plan = Rubrique("Le plan du camp", "Placez les objets comme vous voulez. Vos tentes ne bougent jamais.")
        plan.ajouter("objets", "Les objets", EnAttente("Chargement des objets du jeu…"), defilable=False)
        plan.ajouter("zones", "Les zones et la ronde des gardes", EnAttente("Chargement du plan des emplacements…"), defilable=False)

        self.nom_du_camp = _module("onglet_nom_du_camp", Path(__file__).with_name("onglet_nom_du_camp.py"))
        plan.ajouter("nom", "Le nom du camp", self.nom_du_camp.OngletNomDuCamp())
        plan.quand_montree = self._vue_montree
        self.editeur = None
        self.emplacements = None
        self.constructions = None

        self.objectifs = _module("onglet_objectifs", Path(__file__).with_name("onglet_objectifs.py")).OngletObjectifs()
        self.accueil = Accueil(self)
        for cle, page in (("accueil", self.accueil), ("coffre", self.banque), ("hommes", hommes), ("artisans", artisans),
                          ("construire", construire), ("plan", plan), ("objectifs", self.objectifs)):
            self.pages[cle] = page
            self.pile.addWidget(page)
            orner(page)
        self._minuteur_pause = QTimer(self)
        self._minuteur_pause.timeout.connect(self._voir_la_pause)
        self._minuteur_pause.start(15_000)
        QTimer.singleShot(1500, self._voir_la_pause)
        self._minuteur_accueil = QTimer(self)
        self._minuteur_accueil.timeout.connect(self._accueil_si_montre)
        self._minuteur_accueil.start(5000)
        self.boutons["accueil"].setChecked(True)


    def currentIndex(self) -> int:
        return max(0, self.pile.currentIndex())

    def tabBar(self) -> QWidget:
        return self.boutons[ONGLETS[self.currentIndex()]]

    def _onglet_montre(self, i: int) -> None:
        cle = ONGLETS[i]
        if cle == "accueil":
            self.accueil.actualiser()
            QTimer.singleShot(200, self.banque.lire_la_caisse)



            QTimer.singleShot(6000, self._compagnie_si_inconnue)
        if cle == "coffre":
            QTimer.singleShot(200, self.banque.lire_la_caisse)
        if cle == "hommes":
            self._vue_montree(self.pages["hommes"].vue())
        if cle == "artisans":
            self._vue_montree(self.pages["artisans"].vue())
        if cle == "construire" and self.constructions is None:
            QTimer.singleShot(50, self._construire_les_constructions)
        elif cle == "construire":
            QTimer.singleShot(200, self.constructions.actualiser)
        if cle == "plan":
            self._vue_montree(self.pages["plan"].vue())
        if cle == "objectifs":
            QTimer.singleShot(200, self.objectifs.actualiser)

    def _vue_montree(self, vue: str | None) -> None:
        if vue == "engager":
            QTimer.singleShot(200, self.embauche.actualiser)
        elif vue == "compagnie":
            QTimer.singleShot(200, self.personnel.actualiser)
        elif vue == "metiers":
            QTimer.singleShot(200, self.metiers.actualiser)
        elif vue == "objets" and self.editeur is None:
            QTimer.singleShot(50, self._construire_l_amenagement)
        elif vue == "zones" and self.emplacements is None:
            QTimer.singleShot(50, self._construire_les_emplacements)

    def montrer(self, cle: str | None, vue: str | None = None) -> None:
        if cle in ANCIENS:
            cle, vue = ANCIENS[cle]
        if cle not in ONGLETS:
            return
        page = self.pages[cle]
        self.boutons[cle].setChecked(True)
        if self.pile.currentWidget() is not page:
            self.pile.setCurrentWidget(page)
            hb.entree(page)
        if vue and isinstance(page, Rubrique):
            page.montrer(vue)
        self._onglet_montre(ONGLETS.index(cle))

    def _accueil_si_montre(self) -> None:
        if self.isVisible() and self.pile.currentWidget() is self.accueil:
            self.accueil.actualiser()

    def _compagnie_si_inconnue(self) -> None:
        ""
        if self.pile.currentWidget() is self.accueil and self.accueil.cartes["hommes"].text() == "—":
            self._compagnie_en_fond()

    def _compagnie_en_fond(self, essai: int = 1) -> None:
        ""



        e = getattr(self, "embauche", None)
        if e is None or getattr(self, "_compagnie_demandee", False):
            return
        self._compagnie_demandee = True
        boite: dict = {}

        def fil() -> None:
            try:
                boite["r"] = e._parler("return scriptorium.embauche.etat()")
            except Exception:
                boite["r"] = None
            finally:
                boite["fini"] = True

        def cueillir() -> None:
            if not boite.get("fini"):
                QTimer.singleShot(300, cueillir)
                return
            self._compagnie_demandee = False
            r = boite.get("r")
            if r and r.startswith("etat"):
                e._appliquer(r, None)
                self._accueil_si_montre()
            elif essai < 3:
                QTimer.singleShot(3000, lambda: self._compagnie_en_fond(essai + 1))

        threading.Thread(target=fil, daemon=True).start()
        QTimer.singleShot(300, cueillir)


    def _caisse_lue(self, coffre: int, bourse: int) -> None:
        self.bourse.setText(T("Sur vous\n{0}", self.banque_gros(bourse)))
        if self.pile.currentWidget() is self.accueil:
            self.accueil.actualiser()

            if self.accueil.cartes["hommes"].text() == "—":
                QTimer.singleShot(150, self._compagnie_en_fond)

    @staticmethod
    def banque_gros(n: int) -> str:
        from banque import fenetre_banque as fb
        return fb.gros(n)

    def _apres_un_geste(self, geste: str, montant: int, depuis: QWidget | None) -> None:
        ""
        try:
            haut_du_coffre = self.banque.c_coffre.mapTo(self, QPoint(self.banque.c_coffre.width() // 2, 10))
            bourse = self.bourse.mapTo(self, QPoint(self.bourse.width() // 2, 10))
            source = depuis.mapTo(self, QPoint(depuis.width() // 2, 0)) if depuis is not None else bourse
            n = 3 + min(7, len(str(max(1, montant))))
            if geste == "deposer":
                self.pluie.lancer(source, haut_du_coffre, n)
            else:
                self.pluie.lancer(haut_du_coffre, bourse, n)
        except Exception:
            pass


    def _voir_la_pause(self) -> None:
        sens = _sens_de_la_pause()
        if sens:
            from noyau import partie_en_pause
            self._pause.setText(T(partie_en_pause.TEXTE))
            self._pause.show()
            self.setWindowTitle(T("Gestion du camp — SCRIPTORIUM EN PAUSE : relancez le jeu"))
        else:
            self._pause.hide()

            try:
                self.setWindowTitle(self.nom_du_camp.titre())
            except Exception:
                self.setWindowTitle(T("Gestion du camp"))

    def closeEvent(self, ev) -> None:

        if chemins.gele() and _jeu_ouvert():
            ev.ignore()
            cacher(self)
            return
        super().closeEvent(ev)

    def _langue_choisie(self, i: int) -> None:
        choix = self.liste_des_langues.itemData(i)
        lg.retenir_le_choix(choix)
        du_jeu = langue_du_jeu_ouvert() if choix == lg.PAR_LE_JEU and _jeu_ouvert() else None
        if lg.langue_voulue(du_jeu) != lg.langue():
            relancer(self, du_jeu)


    def _editeur(self):
        if self.editeur is None:
            QApplication.processEvents()
            fe = _module("amenagement_du_camp", EDITEUR)
            self.editeur = fe.Fenetre()
        return self.editeur

    def _construire_l_amenagement(self) -> None:
        plan = self.pages["plan"]
        if plan.vues["objets"].__class__ is not EnAttente:
            return
        try:
            ed = self._editeur()
        except Exception as err:
            plan.vues["objets"].etiquette.setText(T("L'aménagement n'a pas pu s'ouvrir : {0}", err))
            return
        plan.remplacer("objets", ed)
        cacher_l_ancien_titre(ed)
        orner(ed)

    def _construire_les_emplacements(self) -> None:
        if self.emplacements is not None:
            return
        plan = self.pages["plan"]
        QApplication.processEvents()
        try:
            fm = _module("emplacements_du_camp", EMPLACEMENTS)
            self.emplacements = fm.FenetreEmplacements()
        except Exception as err:
            plan.vues["zones"].etiquette.setText(T("Les emplacements n'ont pas pu s'ouvrir : {0}", err))
            return
        plan.remplacer("zones", self.emplacements)
        orner(self.emplacements)

    def _construire_les_constructions(self) -> None:
        if self.constructions is not None:
            return
        page = self.pages["construire"]
        try:
            ed = self._editeur()
            if page.vues["liste"].__class__ is EnAttente and self.pages["plan"].vues["objets"].__class__ is EnAttente:
                self.pages["plan"].remplacer("objets", ed)
            self.constructions = ed.page_des_constructions()
        except Exception as err:
            page.vues["liste"].etiquette.setText(T("Les constructions n'ont pas pu s'ouvrir : {0}", err))
            return
        self.constructions.setStyleSheet(hb.feuille("QDialog { background: transparent; }"))
        page.remplacer("liste", defilante(self.constructions))
        orner(self.constructions)


        QTimer.singleShot(200, self.constructions.actualiser)






def placer_sur_l_ecran_du_jeu(f) -> bool:
    ""

    try:
        import ctypes
        from ctypes import wintypes
        from PyQt6.QtCore import QPoint
        from PyQt6.QtGui import QGuiApplication
        from noyau.premier_plan import _fenetre_du_jeu
        jeu = _fenetre_du_jeu()
        if jeu is None:
            return False
        r = wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(jeu, ctypes.byref(r))
        cx, cy = (r.left + r.right) / 2, (r.top + r.bottom) / 2
        ecran = None
        for s_ in QGuiApplication.screens():
            g, dpr = s_.geometry(), s_.devicePixelRatio()
            if g.contains(QPoint(int(cx / dpr), int(cy / dpr))):
                ecran = s_
                break
        if ecran is None:
            return False
        if f.windowHandle() is not None:
            f.windowHandle().setScreen(ecran)
        zone = ecran.availableGeometry()
        larg, haut = min(f.width(), zone.width() - 40), min(f.height(), zone.height() - 40)
        f.resize(larg, haut)
        f.move(zone.x() + (zone.width() - larg) // 2, zone.y() + (zone.height() - haut) // 2)
        return True
    except Exception:
        return False


def sur_l_ecran_du_jeu_bientot(f) -> None:
    ""
    placer_sur_l_ecran_du_jeu(f)
    for ms in (400, 1200, 2500):
        QTimer.singleShot(ms, lambda: placer_sur_l_ecran_du_jeu(f))


def basculer(f) -> None:
    from noyau.premier_plan import au_premier_plan
    if f.isVisible() and not f.isMinimized() and f.isActiveWindow():
        cacher(f)
    else:

        f.show()
        sur_l_ecran_du_jeu_bientot(f)
        au_premier_plan(f)
        f.tabBar().setFocus()


        f._onglet_montre(f.currentIndex())

        for ms in (300, 800, 1500):
            QTimer.singleShot(ms, lambda: reprendre_la_main(f))
        QTimer.singleShot(100, lambda: suivre_la_langue_du_jeu(f))


def langue_du_jeu_ouvert() -> str | None:
    ""

    try:
        sys.path.insert(0, str(RACINE / "outils_de_session"))
        from essais.cycle_en_jeu import Jeu
        from dire import parler
        r = parler(Jeu(), 'return tostring(System.GetCVar("g_language"))', 2)
    except Exception:
        return None
    return r[3:].strip() if r and r.startswith("hex") else None


def suivre_la_langue_du_jeu(f) -> None:
    if lg.lire_le_choix() != lg.PAR_LE_JEU:
        return
    nom = langue_du_jeu_ouvert()
    if nom and lg.code_du_jeu(nom) != lg.langue():
        relancer(f, nom)


def relancer(f, langue_du_jeu: str | None = None) -> None:
    ""
    from PyQt6.QtCore import QProcess
    args = [] if chemins.gele() else [str(Path(__file__).resolve())]
    args += ["--relance", "--devant", "--onglet", ONGLETS[f.currentIndex()]]
    if langue_du_jeu:
        args += ["--langue-du-jeu", langue_du_jeu]
    if getattr(f, "_serveur", None) is not None:
        f._serveur.close()
    QProcess.startDetached(sys.executable, args)

    QApplication.exit(0)


def reprendre_la_main(f) -> None:
    from noyau.premier_plan import au_premier_plan
    if f.isVisible() and not f.isActiveWindow():
        au_premier_plan(f)
        f.tabBar().setFocus()


def cacher(f) -> None:
    from noyau.premier_plan import rendre_au_jeu
    f.hide()
    rendre_au_jeu()


def _sens_de_la_pause() -> str | None:
    try:
        racine = str(Path(__file__).resolve().parents[1])
        if racine not in sys.path:
            sys.path.insert(0, racine)
        from noyau import partie_en_pause
        return partie_en_pause.sens()
    except Exception:
        return None


class ToucheH(QObject):
    def __init__(self, fenetre) -> None:
        super().__init__()
        self.fenetre = fenetre

    def eventFilter(self, obj, ev) -> bool:
        if ev.type() != QEvent.Type.KeyPress or ev.key() != Qt.Key.Key_H or ev.isAutoRepeat():
            return False
        if ev.modifiers() & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier
                             | Qt.KeyboardModifier.MetaModifier):
            return False
        if QApplication.activeModalWidget() is not None or QApplication.activePopupWidget() is not None:
            return False
        if on_y_ecrit():
            return False
        if not self.fenetre.isActiveWindow():
            return False
        cacher(self.fenetre)
        return True


def on_y_ecrit() -> bool:
    ""

    from PyQt6.QtWidgets import QAbstractSpinBox, QLineEdit, QPlainTextEdit, QTextEdit
    w = QApplication.focusWidget()
    if isinstance(w, QLineEdit) and isinstance(w.parent(), QAbstractSpinBox):
        return False
    return isinstance(w, (QLineEdit, QTextEdit, QPlainTextEdit))


def garder_h_au_clavier(f) -> None:
    ""


    if sys.platform != "win32":
        return
    import ctypes
    u32 = ctypes.windll.user32
    etat = {"enfoncee": False}

    def regarder() -> None:
        enfoncee = bool(u32.GetAsyncKeyState(0x48) & 0x8000)
        avant, etat["enfoncee"] = etat["enfoncee"], enfoncee
        if not enfoncee or avant or not f.isVisible() or u32.GetForegroundWindow() != int(f.winId()):
            return
        if QApplication.activeModalWidget() is not None or QApplication.activePopupWidget() is not None:
            return
        if on_y_ecrit():
            return
        cacher(f)

    minuterie = QTimer(f)
    minuterie.timeout.connect(regarder)
    minuterie.start(50)
    f._h_au_clavier = minuterie


def _onglet_demande(argv: list[str]) -> str | None:
    if "--onglet" in argv:
        i = argv.index("--onglet")
        if i + 1 < len(argv) and (argv[i + 1] in ONGLETS or argv[i + 1] in ANCIENS):
            return argv[i + 1]
    return None


JOURNAL_DES_ERREURS = chemins.dossier_local() / "gestion_du_camp_erreurs.log"


def filet_de_securite() -> None:
    ""


    import traceback
    import datetime

    def crochet(t, v, tb) -> None:
        texte = "".join(traceback.format_exception(t, v, tb))
        try:
            JOURNAL_DES_ERREURS.parent.mkdir(parents=True, exist_ok=True)
            with open(JOURNAL_DES_ERREURS, "a", encoding="utf-8") as f:
                f.write(f"--- {datetime.datetime.now():%d/%m %H:%M:%S}\n{texte}\n")
        except OSError:
            pass
        try:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(None, T("Gestion du camp"), T("Une erreur est survenue ; le programme continue.\nElle est notée dans {0}.\n\n", JOURNAL_DES_ERREURS) + T(str(v)))
        except Exception:
            pass

    sys.excepthook = crochet


def _jeu_ouvert() -> bool:
    try:
        from noyau import lanceur
        return lanceur.en_cours()
    except Exception:
        return False


def faut_il_partir(ouvert: bool, etat: dict) -> bool:
    ""



    if ouvert:
        etat["vu"] = True
        etat["absent"] = 0
        return False
    if not etat.get("vu"):
        return False
    etat["absent"] = etat.get("absent", 0) + 1
    return etat["absent"] >= 2


def s_assurer_du_jeu() -> None:
    ""
    from PyQt6.QtWidgets import QFileDialog, QMessageBox
    from noyau import jeu
    while jeu.trouver_jeu() is None:
        QMessageBox.information(None, T("Gestion du camp"), T("Je ne trouve pas Kingdom Come: Deliverance II.\n\n"
                                "Montre-moi son dossier : celui qui contient Bin, Data et Mods."))
        d = QFileDialog.getExistingDirectory(None, T("Le dossier de Kingdom Come: Deliverance II"))
        if not d:
            return
        if jeu.trouver_jeu(d) is None:
            QMessageBox.warning(None, T("Gestion du camp"), T("Ce dossier ne contient pas le jeu."))
            continue
        chemins.retenir_le_dossier_du_jeu(d)


def brancher_la_touche_h(app, f) -> None:
    ""


    th = _module("touche_h_integree", Path(__file__).with_name("touche_h_integree.py"))
    verrou = th.prendre_le_relais()
    if verrou is not None:
        guetteur = th.GuetteurDeH(chemins.journal_du_jeu())
        guetteur.relever()

        def relever() -> None:
            from noyau.premier_plan import au_premier_plan
            evenements = guetteur.relever()
            if "amenagement" in evenements:
                f.montrer("amenagement")
                f.show()
                sur_l_ecran_du_jeu_bientot(f)
                au_premier_plan(f)

                from noyau import menu_du_jeu
                menu_du_jeu.refermer()
            elif "basculer" in evenements:
                basculer(f)

        minuterie = QTimer(f)
        minuterie.timeout.connect(relever)
        minuterie.start(th.PAS_MS)
        f._touche_h = (verrou, guetteur, minuterie)
    etat = {"vu": False, "absent": 0}

    def regarder_le_jeu() -> None:
        if faut_il_partir(_jeu_ouvert(), etat):
            app.quit()

    gardien = QTimer(f)
    gardien.timeout.connect(regarder_le_jeu)
    gardien.start(5000)
    f._gardien_du_jeu = gardien


def _argument(argv: list[str], nom: str) -> str | None:
    return argv[argv.index(nom) + 1] if nom in argv and argv.index(nom) + 1 < len(argv) else None


def main() -> int:
    if "--relance" in sys.argv:

        import time
        time.sleep(1.2)
    app = QApplication(sys.argv)
    lg.appliquer(lg.langue_voulue(_argument(sys.argv, "--langue-du-jeu")))
    filet_de_securite()
    onglet = _onglet_demande(sys.argv)

    from PyQt6.QtNetwork import QLocalServer, QLocalSocket
    sonde = QLocalSocket()
    sonde.connectToServer(NOM_INSTANCE)
    if sonde.waitForConnected(300):
        sonde.write(("devant " + (onglet or "")).encode("utf-8"))
        sonde.flush()
        sonde.waitForBytesWritten(300)
        sonde.disconnectFromServer()
        return 0
    from noyau.premier_plan import au_premier_plan
    if chemins.gele():
        s_assurer_du_jeu()
    f = GestionDuCamp()
    serveur = QLocalServer()
    QLocalServer.removeServer(NOM_INSTANCE)
    serveur.listen(NOM_INSTANCE)
    f._serveur = serveur

    def devant() -> None:
        c = serveur.nextPendingConnection()
        texte = ""
        if c is not None:
            c.waitForReadyRead(200)
            texte = bytes(c.readAll()).decode("utf-8", "replace")
        mots = texte.split()
        if mots and mots[0] == "basculer":
            basculer(f)
            return
        f.montrer(mots[1] if len(mots) > 1 else None)
        sur_l_ecran_du_jeu_bientot(f)
        au_premier_plan(f)

    serveur.newConnection.connect(devant)
    touche_h = ToucheH(f)
    app.installEventFilter(touche_h)
    garder_h_au_clavier(f)
    if chemins.gele():
        brancher_la_touche_h(app, f)
    f.show()
    f.montrer(onglet or "accueil")
    if "--devant" in sys.argv:
        sur_l_ecran_du_jeu_bientot(f)
        au_premier_plan(f)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
