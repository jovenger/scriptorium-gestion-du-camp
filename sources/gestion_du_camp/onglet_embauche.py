
""










from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import threading

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QComboBox, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QMessageBox, QPushButton,
                             QSpinBox, QTableWidget, QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget)

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))
from noyau.langue_du_programme import T, langue


from gestion_du_camp import habillage as hb
from gestion_du_camp.habillage import CARTE, ENCRE, OR, PALE, VERT, ROUGE, FOND


RANGS = [("faible", "Recrue", "recrue"), ("moyen", "Confirmé", "confirme"), ("fort", "Vétéran", "veteran")]


STYLES = [(0, "Au hasard"), (2, "Épée et bouclier"), (3, "Hache et bouclier"), (4, "Épée longue (à deux mains)"),
          (5, "Masse et bouclier"), (8, "Hache"), (9, "Armes d'hast (lance, glaive, guisarme…)")]





SERVICE = [
    ("bains", "Les dames des bains", "les bains et le lavoir, et leur tente ; pour Henry, le bain 1 h, les soins 2 h (deux fois le prix, un pansement), la compagnie 3 h (trois fois)", 5000),
    ("forge", "Le forgeron", "sa forge, et sa tente ; il répare les pièces sous 15 % (et toutes, sans aide) ; une pièce refaite revient à 60 %", 5000),
    ("coursier", "Le coursier", "les courses du camp et les tiennes ; sa tente", 5000),


    ("chasseurs", "Les deux chasseurs", "à cheval, le gibier du secteur ; leur poste de chasse", 5000),


    ("jardiniers", "Le jardinier", "bêche, sème et récolte tes potagers ; l'étal du potager ; la jardinière le rejoint si le "
     "travail déborde 7 jours de suite (payée par sa caisse)", 5000),
    ("eau", "Le porteur d'eau", "au puits, plusieurs voyages par jour ; son eau sert aux bains, à la cuisine et au potager ; sa charrette à eau", 5000),
    ("bois", "Le bûcheron", "le bois de chauffe, le charbon et les branches ; sa réserve de bois ; son aide le rejoint si le "
     "travail déborde 7 jours de suite (payé par sa caisse)", 5000),

    ("taverne", "Le tavernier", "la bière et le vin au verre : +3 et +5 au moral pendant 24 h, 8 au plus ; son étal de tavernier", 5000),

    ("aide_forge", "L'aide du forgeron", "les petites réparations à l'établi de la forge, pour que le forgeron "
     "ait le temps de fabriquer ses armes (il faut la forge) ; les pièces entre 15 et 30 %, à 75 % du prix du forgeron ; "
     "la pièce revient à 60 %, comme chez lui", 1500),

    ("armurier", "L'armurier", "répare et ajuste les armures, fabrique les pièces simples ; sa petite forge de camp ; Henry paie ses armes et armures un peu plus que ce qu'un marchand du jeu en rachète, jamais moins que la moitié de leur prix", 5000),



    ("directeur", "Le Directeur", "le Directeur du camp : ses missions, la banque, les ordres ; engagé, il pose sa tente et son "
     "lit à côté de la tienne (compris dans la patente)", 0),

    ("palefrenier", "Le palefrenier", "soigne les chevaux de la ligne des chevaux (achète d'abord une ligne, puis ses chevaux) ; le coffre le paie : 110 par semaine, plus 8 gros par cheval pour le fourrage", 1500),

    ("vivandiere", "La vivandière", "vend un en-cas (pain et lard) aux hommes à son comptoir, payé à sa caisse ; elle rembourse au coffre les vivres pris (pose d'abord son comptoir)", 5000),

    ("boucher", "Le boucher", "achète la viande des chasseurs, la sale à son coin et la fume au fumoir (pose d'abord son coin). Un boucher vit d'un camp d'environ 40 hommes ; en dessous, il vend trop peu pour son salaire", 5000),
]

SANS_RENVOI = {"directeur"}

REFUS_DU_DIRECTEUR = {
    "pas_de_camp": "Le Directeur : il n'y a pas encore de camp. Pose d'abord ta tente dans l'Aménagement du camp.",
    "pose_ta_tente_d_abord": "Le Directeur : pose d'abord ta tente dans l'Aménagement du camp ; il pose la sienne à côté.",
    "pas_de_place": "Le Directeur : pas de place libre à côté de ta tente. Fais un peu de place, puis réessaie.",
}




PAR_LE_FORGERON = {"aide_forge"}




def lire_les_compagnons() -> list[tuple[int, str, int]]:
    if str(RACINE) not in sys.path:
        sys.path.insert(0, str(RACINE))
    from noyau import noms_a_l_ecran
    return [(i, nom, prix) for i, (nom, prix, _) in enumerate(noms_a_l_ecran.compagnons_de_la_prise(), 1)]


def lire_les_prix(choix: dict | None = None) -> dict:
    ""



    out = {"rangs": {}, "archer": None, "arbaletrier": None, "compagnons": []}
    try:
        out["compagnons"] = lire_les_compagnons()
    except (OSError, ValueError):
        pass
    try:
        pe = (RACINE / "choses" / "prix_d_embauche" / "prix_d_embauche.lua").read_text(encoding="utf-8")
    except OSError:
        return out
    if choix is None:
        try:
            choix = json.loads((RACINE / "local" / "regles.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            choix = {}
    for cle, ou in (("RECRUE", ("rangs", "faible")), ("CONFIRME", ("rangs", "moyen")),
                    ("VETERAN", ("rangs", "fort")), ("ARCHER", ("archer",)), ("ARBALETRIER", ("arbaletrier",))):
        m_pe = re.search(rf"pe\.{cle}\s*=\s*(\d+)", pe)
        v = choix.get(f"prix_d_embauche.{cle}", int(m_pe.group(1)) if m_pe else None)
        if v is None:
            continue
        if len(ou) == 2:
            out["rangs"][ou[1]] = int(v)
        else:
            out[ou[0]] = int(v)
    return out


def gros(n: float) -> str:
    return f"{n:,.0f}".replace(",", " ") + " gros"


def sceller(sur, texte: str) -> None:
    ""
    try:
        hb.apposer_un_sceau(sur, T(texte))
    except Exception:
        pass


class OngletEmbauche(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.mod = lire_les_prix()
        self.embauches: set[int] = set()
        self.setStyleSheet(hb.feuille())
        v = QVBoxLayout(self)
        v.setContentsMargins(18, 16, 18, 16)
        v.setSpacing(10)
        haut = QHBoxLayout()
        entete = QLabel(T("Embauche"))
        entete.setObjectName("Entete")
        haut.addWidget(entete)
        haut.addStretch(1)
        b = QPushButton(T("Actualiser"))
        b.clicked.connect(self.actualiser)
        haut.addWidget(b)
        v.addLayout(haut)


        bandeau = QHBoxLayout()
        self.v_bourse = self._carte(bandeau, "dans la caisse du camp (c'est elle qui paie)")
        self.v_compagnie = self._carte(bandeau, "hommes dans la compagnie")
        v.addLayout(bandeau)



        self.sous = QTabWidget()
        page = QWidget()
        v1 = QVBoxLayout(page)
        v1.setContentsMargins(0, 10, 0, 0)

        titre = QLabel(T("Fantassins, archers et arbalétriers"))
        titre.setObjectName("Section")
        v1.addWidget(titre)
        grille = QGridLayout()
        grille.setHorizontalSpacing(14)
        self.nombres: dict[str, QSpinBox] = {}
        self.boutons: dict[str, QPushButton] = {}





        prix_recrue = self.mod["rangs"].get("faible")
        lignes = [("faible", "Recrue (arme au hasard)", prix_recrue)]
        for code, texte in STYLES:
            if code:
                lignes.append((f"faible:{code}", T("Recrue — {0}", texte), prix_recrue))
        lignes.append(("archer", "Archer", self.mod["archer"]))
        lignes.append(("arbaletrier", "Arbalétrier", self.mod["arbaletrier"]))
        for i, (tier, nom, prix) in enumerate(lignes):
            grille.addWidget(QLabel(T(nom)), i, 0)
            grille.addWidget(QLabel(T(gros(prix)) + T(" l'homme") if prix else T("prix introuvable")), i, 1)
            s = QSpinBox()
            s.setRange(1, 50)
            s.setValue(1)
            grille.addWidget(s, i, 2)
            bt = QPushButton()
            bt.clicked.connect(lambda _=False, t=tier: self.engager(t, self.nombres[t].value()))
            grille.addWidget(bt, i, 3)
            s.valueChanged.connect(lambda n, t=tier, p=prix, bt=bt: bt.setText(T("Engager ({0})", gros((p or 0) * n))))
            bt.setText(T("Engager ({0})", gros(prix or 0)))
            bt.setEnabled(prix is not None)
            self.nombres[tier], self.boutons[tier] = s, bt
        grille.setColumnStretch(4, 1)
        v1.addLayout(grille)



        titre = QLabel(T("Taille de la compagnie"))
        titre.setObjectName("Section")
        v1.addWidget(titre)
        rang_taille = QHBoxLayout()
        self.taille = QSpinBox()
        self.taille.setRange(0, 80)
        self.taille.setValue(0)
        self.taille.setToolTip(T("Le Directeur remplace les morts jusqu'à cette taille ; vos embauches l'augmentent."))
        rang_taille.addWidget(self.taille)


        self.bt_taille = QPushButton(T("Appliquer"))
        self.bt_taille.clicked.connect(self.regler_la_taille)
        self.bt_taille.setEnabled(False)
        self.taille.setEnabled(False)
        rang_taille.addWidget(self.bt_taille)
        self.v_taille = QLabel(T("La taille n'est pas encore lue dans le jeu : « Appliquer » attend sa vraie valeur."))
        self.v_taille.setWordWrap(True)
        rang_taille.addWidget(self.v_taille, 1)
        v1.addLayout(rang_taille)
        self._taille_lue = None


        titre = QLabel(T("Compagnons nommés (un seul de chaque)"))
        titre.setObjectName("Section")
        v1.addWidget(titre)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([T("Nom"), T("Prix"), "", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        v1.addWidget(self.table, 1)
        self.sous.addTab(page, T("Mercenaires"))

        self.sous.addTab(self._page_du_service(), T("Artisans"))
        v.addWidget(self.sous, 1)
        self.etat = QLabel("")
        self.etat.setObjectName("Titre")
        self.etat.setWordWrap(True)
        v.addWidget(self.etat)
        self._remplir_les_compagnons()

    def _page_du_service(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)
        v.setContentsMargins(0, 10, 0, 0)
        titre = QLabel(T("Le Directeur et les artisans du camp (une personne de chaque, payée une fois par la caisse)"))
        titre.setObjectName("Section")
        v.addWidget(titre)
        grille = QGridLayout()
        grille.setHorizontalSpacing(14)
        grille.setVerticalSpacing(10)
        self.service_etat: dict[str, QLabel] = {}
        self.service_boutons: dict[str, tuple[QPushButton, QPushButton]] = {}
        for i, (nom, texte, quoi, prix) in enumerate(SERVICE):

            if nom in PAR_LE_FORGERON:
                continue

            ligne = 0 if nom == "directeur" else i + 1
            t = QLabel()
            t.setTextFormat(Qt.TextFormat.RichText)
            t.setText(T("{0}<br><span style='color:{1}; font-size:9pt'>{2}</span>", texte, PALE, quoi))
            t.setWordWrap(True)
            t.setMinimumWidth(260)
            grille.addWidget(t, ligne, 0)
            grille.addWidget(QLabel(T(gros(prix)) if prix > 0 else T("compris dans la patente")), ligne, 1)
            e = QLabel("—")
            grille.addWidget(e, ligne, 2)
            b1 = QPushButton(T("Engager ({0})", gros(prix)) if prix > 0 else T("Engager"))
            b1.clicked.connect(lambda _=False, n=nom: self.engager_le_service(n))
            b2 = QPushButton(T("Renvoyer"))
            b2.clicked.connect(lambda _=False, n=nom: self.renvoyer_le_service(n))
            b2.setVisible(nom not in SANS_RENVOI)
            grille.addWidget(b1, ligne, 3)
            grille.addWidget(b2, ligne, 4)
            self.service_etat[nom] = e
            self.service_boutons[nom] = (b1, b2)
        grille.setColumnStretch(0, 1)
        v.addLayout(grille)
        aide = QLabel(T("Une fois engagés, leur poste et leur tente apparaissent au camp : place-les où tu veux "
                      "dans l'Aménagement du camp, rubriques « Artisans ». Renvoyés, ils partent avec leur tente ; "
                      "réengagés, ils reviennent là où tu les avais mis."))
        aide.setObjectName("Titre")
        aide.setWordWrap(True)
        v.addWidget(aide)
        v.addStretch(1)
        return page

    def _montrer_le_service(self, engages: dict) -> None:
        for nom, e in self.service_etat.items():
            dedans = engages.get(nom)
            e.setText("—" if dedans is None else (T("au camp") if dedans else T("libre")))
            e.setStyleSheet(f"color: {VERT if dedans else PALE};")
            b1, b2 = self.service_boutons[nom]
            b1.setEnabled(dedans is False)
            b2.setEnabled(dedans is True)

    def engager_le_service(self, nom: str) -> None:
        texte = next(t for n, t, _, _ in SERVICE if n == nom)
        self.etat.setText(T("J'engage : {0}…", texte.lower() if langue() == "fr" else texte))
        jeton = int(time.time() * 1000) % 1_000_000_000
        r = self._parler(f'return scriptorium.embauche.engager_le_service({jeton}, "{nom}")')
        if not r:
            self.etat.setText(T("Le jeu ne répond pas : personne n'a été engagé."))
            return
        c = r.split()

        if nom == "directeur" and c[0] == "fait":
            self.etat.setText(T("Le Directeur est engagé : il arrive près de ta tente. Parle-lui : « Mes ordres », "
                              "« Posez votre tente » -- il pose sa tente et son lit ; tu pourras la déplacer sur le plan."))
            sceller(self.etat, "Engagé")
        elif nom == "directeur" and c[0] == "refus" and "_".join(c[1:]) in REFUS_DU_DIRECTEUR:

            self.etat.setText(T(REFUS_DU_DIRECTEUR["_".join(c[1:])]))
        elif c[0] == "fait" and len(c) >= 2:
            self.etat.setText(T("{0} : engagé pour {1}, payé par la caisse du camp. Le poste et la tente se montent au camp dans quelques secondes ; place-les dans l'Aménagement du camp, rubriques « Artisans ».", texte, gros(float(c[1]))))
            sceller(self.etat, "Engagé")
        elif c[0] == "deja":
            self.etat.setText(T("{0} : déjà au camp. La caisse n'a rien payé.", texte))
        elif c[0] == "refus" and len(c) >= 2 and c[1] == "sansforge":
            self.etat.setText(T("{0} : il faut d'abord engager le forgeron (sa forge). La caisse n'a rien payé.", texte))
        elif c[0] == "refus" and len(c) >= 4 and c[1] == "caisse":
            self.etat.setText(T("La caisse du camp n'a que {0} pour {1} : mets de l'argent dans la caisse depuis l'onglet Banque.", gros(float(c[2])), gros(float(c[3]))))
        else:
            self.etat.setText(T("Le jeu a refusé : ") + T(r))
        self.actualiser()

    def renvoyer_le_service(self, nom: str) -> None:
        texte = next(t for n, t, _, _ in SERVICE if n == nom)
        if QMessageBox.question(self, T("Renvoyer"), T("Renvoyer : {0} ? Le poste et la tente partent avec. Il faudra payer de nouveau pour réengager.", texte.lower() if langue() == "fr" else texte)) != QMessageBox.StandardButton.Yes:
            return
        jeton = int(time.time() * 1000) % 1_000_000_000
        r = self._parler(f'return scriptorium.embauche.renvoyer_le_service({jeton}, "{nom}")')
        if not r:
            self.etat.setText(T("Le jeu ne répond pas : personne n'a été renvoyé."))
        elif r.split()[0] == "fait":
            self.etat.setText(T("{0} : renvoyé. Le poste et la tente sont retirés.", texte))
        else:
            self.etat.setText(T("Le jeu a répondu : ") + T(r))
        self.actualiser()

    def sortir_les_artisans(self) -> QWidget:
        ""

        page = self.sous.widget(1)
        self.sous.removeTab(1)
        self.sous.tabBar().hide()
        page.setStyleSheet(hb.feuille())
        return page

    def _carte(self, rang: QHBoxLayout, titre: str) -> QLabel:
        c = QFrame()
        c.setObjectName("Carte")
        v = QVBoxLayout(c)
        val = QLabel("—")
        val.setObjectName("Valeur")
        val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t = QLabel(T(titre))
        t.setObjectName("Titre")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(val)
        v.addWidget(t)
        rang.addWidget(c)
        return val

    def _remplir_les_compagnons(self) -> None:
        cc = self.mod["compagnons"]
        self.table.setRowCount(len(cc))
        for i, (ident, nom, prix) in enumerate(cc):
            self.table.setItem(i, 0, QTableWidgetItem(T(nom)))
            it = QTableWidgetItem(T(gros(prix)))
            it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 1, it)
            dedans = ident in self.embauches
            it = QTableWidgetItem(T("dans la compagnie") if dedans else T("libre"))
            it.setForeground(QColor(VERT if dedans else PALE))
            it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 2, it)
            bt = QPushButton(T("Engager"))
            bt.setEnabled(not dedans)
            bt.clicked.connect(lambda _=False, k=ident: self.engager(str(k), 1))
            self.table.setCellWidget(i, 3, bt)


    def _parler(self, code: str) -> str | None:
        try:
            for chemin in (str(RACINE), str(RACINE / "outils_de_session")):
                if chemin not in sys.path:
                    sys.path.insert(0, chemin)
            from essais.cycle_en_jeu import Jeu
            from dire import parler
            r = parler(Jeu(), code, 20)
            return r[3:].strip() if r and r.startswith("hex") else r
        except Exception:
            return None





    VEILLE = 10_000

    def showEvent(self, e) -> None:
        super().showEvent(e)
        if getattr(self, "_veille", None) is None:
            self._veille = QTimer(self)
            self._veille.timeout.connect(self._relever_en_fond)
            self._cueillette = QTimer(self)
            self._cueillette.timeout.connect(self._cueillir)
            self._en_cours, self._resultat = False, None
        self._veille.start(self.VEILLE)
        self._cueillette.start(300)

        self._relever_en_fond()

    def hideEvent(self, e) -> None:
        super().hideEvent(e)
        if getattr(self, "_veille", None) is not None:
            self._veille.stop()

    def _relever_en_fond(self) -> None:
        if getattr(self, "_en_cours", False):
            return
        self._en_cours = True

        def fil() -> None:
            try:
                r = self._parler("return scriptorium.embauche.etat()")
                r2 = self._parler("return scriptorium.embauche.etat_du_service()") if r else None
                r3 = self._parler("return scriptorium.reembauche_des_mercenaires.taille_texte()") if r else None
                self._resultat = (r, r2, r3)
            finally:
                self._en_cours = False
        threading.Thread(target=fil, daemon=True).start()

    def _cueillir(self) -> None:
        res, self._resultat = getattr(self, "_resultat", None), None
        if res is not None:
            self._appliquer(*res)
        if getattr(self, "_veille", None) is not None and not self._veille.isActive():
            self._cueillette.stop()

    def actualiser(self) -> None:
        self.etat.setText(T("Je demande l'état de la compagnie au jeu…"))
        if getattr(self, "_veille", None) is not None:
            self._relever_en_fond()
            return
        r = self._parler("return scriptorium.embauche.etat()")
        r2 = self._parler("return scriptorium.embauche.etat_du_service()") if r else None
        r3 = self._parler("return scriptorium.reembauche_des_mercenaires.taille_texte()") if r else None
        self._appliquer(r, r2, r3)



    def _montrer_la_taille(self, r3: str | None) -> None:
        c = (r3 or "").split()
        if len(c) < 3 or c[0] != "taille" or not c[1].isdigit():

            if self._taille_lue is None:
                self.bt_taille.setEnabled(False)
                self.taille.setEnabled(False)
                self.v_taille.setText(T("La taille n'est pas encore lue dans le jeu : « Appliquer » attend sa vraie valeur."))
            return
        n = int(c[1])
        if self._taille_lue is None or (n != self._taille_lue and not self.taille.hasFocus()):
            self._taille_lue = n
            self.taille.setValue(n)
        self.taille.setEnabled(True)
        self.bt_taille.setEnabled(True)
        self.v_taille.setText(T("Taille voulue : {0} hommes ; aujourd'hui : {1}. Le Directeur remplace les morts jusqu'à cette "
                                "taille ; vos embauches l'augmentent.", n, c[2]))

    def regler_la_taille(self) -> None:
        if self._taille_lue is None:
            return
        n = int(self.taille.value())
        r = self._parler(f"return scriptorium.reembauche_des_mercenaires.regler_la_taille({n})")
        if self._taille_lue is None:
            return
        if not r or not str(r).startswith("taille"):
            self.etat.setText(T("Le jeu ne répond pas : la taille n'a pas changé."))
            return
        try:
            self._taille_lue = int(str(r).split()[1])
        except (IndexError, ValueError):
            self._taille_lue = None
        self.etat.setText(T("Taille de la compagnie : {0} hommes.", str(r).split()[1]))
        sceller(self.etat, "Réglé")

    def _appliquer(self, r: str | None, r2: str | None, r3: str | None = None) -> None:
        if not r or not r.startswith("etat"):
            self.etat.setText(T("Le jeu ne répond pas : est-il lancé, et pas en pause ni dans un menu ?"))
            return
        c = r.split()
        try:
            hommes, plafond, bourse = int(float(c[1])), int(float(c[2])), int(float(c[3]))
        except (IndexError, ValueError):
            self.etat.setText(T("Réponse du jeu illisible : ") + T(r))
            return
        embauches = {int(x) for x in c[4:] if x.isdigit()}
        self.v_bourse.setText(T(gros(bourse)))
        self.v_compagnie.setText(T("{0} / {1}", hommes, plafond))
        if embauches != getattr(self, "_embauches_montres", None):
            self.embauches = embauches
            self._embauches_montres = embauches
            self._remplir_les_compagnons()
        if r2 and r2.startswith("service"):
            d = r2.split()[2:]
            self._montrer_le_service({n: (d[i] == "1") for i, (n, _, _, _) in enumerate(SERVICE) if i < len(d)})
        self._montrer_la_taille(r3)
        self.etat.setText(T("À jour (redemandé au jeu toutes les 10 secondes)."))

    def engager(self, genre: str, nombre: int) -> None:
        self.etat.setText(T("J'engage…"))
        jeton = int(time.time() * 1000) % 1_000_000_000
        style = ""
        if ":" in genre:
            genre, code = genre.split(":", 1)
            style = f", {int(code)}"
        r = self._parler(f'return scriptorium.embauche.engager({jeton}, "{genre}", {int(nombre)}{style})')
        if not r:
            self.etat.setText(T("Le jeu ne répond pas : rien n'a été engagé."))
            return
        c = r.split()
        if c[0] == "fait" and len(c) >= 5:
            venus, paye = int(float(c[1])), int(float(c[2]))
            if venus > 0:
                self.etat.setText(T("{0} homme(s) engagé(s) pour {1}, payés par la caisse du camp. Ils arrivent à côté d'Henry.", venus, gros(paye)))
                sceller(self.etat, "Engagé")
            else:
                self.etat.setText(T("Personne n'est venu : compagnie pleine, ou compagnon déjà engagé "
                                  "(le jeu affiche la raison). La caisse n'a rien payé."))
        elif c[0] == "refus" and len(c) >= 4 and c[1] == "caisse":
            self.etat.setText(T("La caisse du camp n'a que {0} pour {1} : mets de l'argent dans la caisse depuis l'onglet Banque.", gros(float(c[2])), gros(float(c[3]))))
        else:
            self.etat.setText(T("Le jeu a refusé : ") + T(r))
        self.actualiser()
