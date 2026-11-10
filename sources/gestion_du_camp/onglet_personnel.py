
""










from __future__ import annotations

import re
import sys
import time
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QApplication, QComboBox, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QMessageBox, QPushButton,
                             QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))
from noyau import chemins
from noyau.langue_du_programme import T


JOURNAL = chemins.journal_du_jeu()
MARQUE = "[ScriptoPersonnel] "


from gestion_du_camp import habillage as hb
from gestion_du_camp.habillage import CARTE, ENCRE, OR, PALE, VERT, ROUGE, ORANGE, FOND


COLONNES = ["Nom", "Groupe", "Grade", "Niveau\n(sur 30)", "Poste en ce moment", "Besoins",
            "Santé", "Propreté", "En poche", "Dettes", "Dû cette\nsemaine", "Moral, faim,\nénergie",

            "Estime\nenvers toi", "Expérience",

            "Tir\n(niveau · points)"]
FILTRES = ["Tout le monde", "Mercenaires", "Compagnons", "Artisans", "Ceux qui ont un besoin"]
MARQUE_TIR = "[ScriptoTir] "
MARQUE_PROG = "[ScriptoProgression] "



_LECTEUR = RACINE / "choses" / "tableaux_vivants" / "lecteur.py"
_mod_vivant = None
SIGNE = 20_000
LECTURE = 1_000


def _vivant():
    global _mod_vivant
    if _mod_vivant is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("tableaux_vivants_lecteur", _LECTEUR)
        _mod_vivant = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_mod_vivant)
    return _mod_vivant


def lire_le_registre(depuis: int = 0) -> dict | None:
    ""
    try:
        with open(JOURNAL, "rb") as f:
            f.seek(depuis)
            brut = f.read().decode("utf-8", "replace")
    except OSError:
        return None
    return analyser_le_registre(brut)


def analyser_le_registre(brut: str) -> dict | None:
    ""
    lignes = [l.split(MARQUE, 1)[1].rstrip() for l in brut.splitlines() if MARQUE in l]
    fin = max((i for i, l in enumerate(lignes) if l.startswith("fin|")), default=None)
    if fin is None:
        return None
    debut = max((i for i, l in enumerate(lignes[:fin]) if l.startswith("debut|")), default=None)
    if debut is None:
        return None
    d = lignes[debut].split("|")
    gens = []
    for l in lignes[debut + 1:fin]:
        c = l.split("|")
        if c[0] != "h" or len(c) < 13:
            continue
        gens.append({"cle": c[1], "nom": c[2], "groupe": c[3], "grade": c[4], "niveau": _nombre(c[5]),
                     "poste": c[6].replace("corvee_bois", "corvée de bois").replace("corvee_eau", "corvée d'eau"),
                     "sante": _nombre(c[7]), "proprete": _nombre(c[8]), "bourse": _nombre(c[9]),
                     "dettes": _nombre(c[10]), "du": _nombre(c[11]),
                     "besoins": [b for b in re.split(r", (?![^()]*\))", c[12]) if b],

                     "faim": _nombre(c[13]) if len(c) > 13 else None,
                     "energie": _nombre(c[14]) if len(c) > 14 else None,
                     "moral": _nombre(c[15]) if len(c) > 15 else None,
                     "exp": _nombre(c[16]) if len(c) > 16 else None,
                     "rang": c[17] if len(c) > 17 else "",
                     "estime": _nombre(c[18]) if len(c) > 18 else None,
                     "complot": _nombre(c[19]) if len(c) > 19 else None})

    tir = [l.split(MARQUE_TIR, 1)[1].rstrip() for l in brut.splitlines() if MARQUE_TIR in l]
    fin_t = max((i for i, l in enumerate(tir) if l.startswith("fin|")), default=None)
    debut_t = None
    if fin_t is not None:
        debut_t = max((i for i, l in enumerate(tir[:fin_t]) if l.startswith("debut|")), default=None)
    if debut_t is not None:
        par_nom = {}
        for l in tir[debut_t + 1:fin_t]:
            c = l.split("|")
            if c[0] == "t" and len(c) >= 7:
                par_nom[c[1]] = {"niveau": c[2], "points": _nombre(c[3]), "tirees": _nombre(c[4]),
                                 "touches": _nombre(c[5]), "centres": _nombre(c[6])}
        for g in gens:
            if g["cle"] in par_nom:
                g["tir"] = par_nom[g["cle"]]

    prog = [l.split(MARQUE_PROG, 1)[1].rstrip() for l in brut.splitlines() if MARQUE_PROG in l]
    fin_p = max((i for i, l in enumerate(prog) if l.startswith("fin|")), default=None)
    debut_p = None
    if fin_p is not None:
        debut_p = max((i for i, l in enumerate(prog[:fin_p]) if l.startswith("debut|")), default=None)
    if debut_p is not None:
        par_nom = {}
        for l in prog[debut_p + 1:fin_p]:
            c = l.split("|")
            if c[0] == "p" and len(c) >= 7:
                par_nom[c[1]] = {"grade": c[2], "combat": c[3], "tir": c[4], "pts_combat": _nombre(c[5]),
                                 "pts_tir": _nombre(c[6])}
        for g in gens:
            if g["cle"] in par_nom:
                g["prog"] = par_nom[g["cle"]]
    return {"heure": float(d[1]) if len(d) > 1 and d[1] else None, "gens": gens}


def _nombre(s: str) -> float | None:
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _humeur(g: dict) -> str:
    if g.get("moral") is None and g.get("faim") is None and g.get("energie") is None:
        return "à venir"
    morceaux = []
    for cle, nom in (("moral", "moral"), ("faim", "rassasié"), ("energie", "énergie")):
        if g.get(cle) is not None:

            morceaux.append(T("{0} {1}", nom, _vivant().palier(g[cle])))
    return ", ".join(morceaux)


def _estime(g: dict) -> str:
    ""
    v = g.get("estime")
    if v is None:
        return ""
    mot = ("te hait" if v <= -60 else "mécontent" if v <= -30 else "neutre" if v < 20
           else "t'apprécie" if v < 60 else "dévoué")
    txt = T("{0} ({1:+.0f})", mot, v)
    if g.get("complot") is not None:
        txt += T(" · ⚠ complote")
    return txt


def _experience(g: dict) -> str:

    p = g.get("prog")
    if p and g.get("groupe") == "Service" and p.get("pts_combat") is not None:


        xp = max(0.0, min(500.0, (p["pts_combat"] - 600) / 4.8))
        return T("service {0:.0f}/500 · combat {1} · tir {2}", xp, p['combat'], p['tir'])
    if p:
        return (T("combat {0} ({1:.0f}/100) · tir {2} ({3:.0f}/100)", p['combat'], (p['pts_combat'] or 0) % 100, p['tir'], (p['pts_tir'] or 0) % 100))
    if g.get("exp") is None and not g.get("rang"):
        return "à venir"
    return T("{0} {1:.0f} pts", g.get('rang') or '', g['exp']).strip() if g.get("exp") is not None else g.get("rang")


def _tir(g: dict) -> str:
    ""
    t = g.get("tir")
    if not t:
        return ""
    txt = T("niv. {0} · {1:.0f}/100 pts", t['niveau'], t['points'] or 0)
    if t.get("tirees"):
        txt += T(" · {0:.0f} % dans la cible, {1:.0f} au centre", 100 * (t['touches'] or 0) / t['tirees'], t['centres'] or 0)
    return txt


def gros(n: float | None) -> str:
    return "" if n is None else f"{n:,.0f}".replace(",", " ")


class OngletPersonnel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.registre: dict | None = None
        self.setStyleSheet(hb.feuille())
        v = QVBoxLayout(self)
        v.setContentsMargins(18, 16, 18, 16)
        v.setSpacing(10)
        haut = QHBoxLayout()
        entete = QLabel(T("Personnel du camp"))
        entete.setObjectName("Entete")
        haut.addWidget(entete)
        haut.addStretch(1)
        self.filtre = QComboBox()

        self.filtre.addItems([T(_x) for _x in FILTRES])
        self.filtre.currentIndexChanged.connect(self.montrer)
        haut.addWidget(self.filtre)
        b = QPushButton(T("Actualiser"))
        b.clicked.connect(self.actualiser)
        haut.addWidget(b)


        r = QPushButton(T("Renvoyer celui-ci"))
        r.setToolTip(T("Choisis un mercenaire dans le tableau : il quitte la compagnie. Le camp reste debout."))
        r.clicked.connect(self.renvoyer)
        haut.addWidget(r)
        v.addLayout(haut)



        import sys
        if str(RACINE) not in sys.path:
            sys.path.insert(0, str(RACINE))
        from noyau import ordres_du_colonel as oc
        ordres = QGridLayout()
        ordres.addWidget(QLabel(T("Ordres au colonel :")), 0, 0)
        for k, (quoi, bouton, aide, _) in enumerate(oc.ORDRES):
            b_ = QPushButton(T(bouton))
            b_.setToolTip(T(aide))
            b_.clicked.connect(lambda _c=False, q=quoi: self.ordonner_au_colonel(q))
            ordres.addWidget(b_, k // 4, 1 + k % 4)

        bd = QPushButton(T("Une mission difficile"))
        bd.setToolTip(T("Le Directeur prend la bande la plus dure avec les meilleurs, à sa prochaine décision."))
        bd.clicked.connect(self.demander_une_mission_difficile)
        ordres.addWidget(QLabel(T("Au Directeur :")), 3, 0)
        ordres.addWidget(bd, 3, 1)
        v.addLayout(ordres)
        self.resume = QLabel("")
        self.resume.setObjectName("Note")
        self.resume.setWordWrap(True)
        v.addWidget(self.resume)
        self.table = QTableWidget(0, len(COLONNES))
        self.table.setHorizontalHeaderLabels([T(_x) for _x in COLONNES])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)


        h = self.table.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        v.addWidget(self.table, 1)
        note = QLabel(T("Le niveau est la moyenne de ses valeurs de combat dans le jeu (maniement, défense, force, "
                      "agilité, vitalité), sur 30 : sous 12, il lui faut de l'entraînement. La santé et la propreté "
                      "sont mesurées par le jeu. Le moral, la faim et l'énergie viennent du moteur des besoins du camp."))
        note.setObjectName("Note")
        note.setWordWrap(True)
        v.addWidget(note)




    def _demarrer_le_vivant(self) -> None:
        if getattr(self, "_suiveur", None) is None:
            lv = _vivant()
            self._suiveur = lv.Suiveur(JOURNAL)
            self._etat = lv.RegistreVivant()
            self._jeu = None
            self._lecture = QTimer(self)
            self._lecture.timeout.connect(self._suivre)
            self._signe = QTimer(self)
            self._signe.timeout.connect(lambda: self._faire_signe(False))

            if self.registre is None:
                r = lire_le_registre(0)
                if r:
                    self.registre = r
                    self.montrer()
        if not self._lecture.isActive():
            self._lecture.start(LECTURE)
            self._signe.start(SIGNE)

    def _arreter_le_vivant(self) -> None:
        if getattr(self, "_suiveur", None) is not None:
            self._lecture.stop()
            self._signe.stop()

    def showEvent(self, e) -> None:
        super().showEvent(e)
        self.actualiser()

    def hideEvent(self, e) -> None:
        super().hideEvent(e)
        self._arreter_le_vivant()

    def _faire_signe(self, plein: bool) -> bool:

        code = ("local tv = scriptorium.tableaux_vivants if tv and tv.regarder then return tv.regarder('personnel', "
                + ("true" if plein else "false") + ") end"
                + (" return tostring(scriptorium.personnel.publier())" if plein else " return 'sans'"))
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
        if lignes and self._etat.lire(lignes) and self._etat.pret:
            r = analyser_le_registre(self._etat.texte())
            if r:
                self.registre = r
                self.montrer()


    def actualiser(self) -> None:
        self._demarrer_le_vivant()
        if self._faire_signe(True) and self.registre is None:
            self.resume.setText(T("Je demande le registre au jeu…"))


    def ordonner_au_colonel(self, quoi: str) -> None:
        try:
            import sys
            if str(RACINE) not in sys.path:
                sys.path.insert(0, str(RACINE))
            from essais.cycle_en_jeu import Jeu
            code = f"return tostring(scriptorium.devoirs_du_colonel.ordonner('{quoi}', 'henry'))"
            Jeu().emetteur.envoyer(["hex " + code.encode("ascii", "replace").hex()])
        except Exception as err:
            self.resume.setText(T("Le jeu ne répond pas : {0}", err))
            return
        from noyau import ordres_du_colonel as oc
        self.resume.setText(T("Ordre donné. {0} Il s'y met dès que c'est possible.", oc.phrase(quoi)))

    def demander_une_mission_difficile(self) -> None:
        try:
            import sys
            if str(RACINE) not in sys.path:
                sys.path.insert(0, str(RACINE))
            from essais.cycle_en_jeu import Jeu
            code = "return tostring(scriptorium.missions_du_directeur.demander_une_mission_difficile())"
            Jeu().emetteur.envoyer(["hex " + code.encode("ascii", "replace").hex()])
        except Exception as err:
            self.resume.setText(T("Le jeu ne répond pas : {0}", err))
            return
        self.resume.setText(T("Mission difficile demandée : à sa prochaine décision, le Directeur prend la bande la plus dure "
                            "avec les meilleurs."))


    def renvoyer(self) -> None:
        ligne = self.table.currentRow()
        it = self.table.item(ligne, 0) if ligne >= 0 else None
        g = it.data(Qt.ItemDataRole.UserRole) if it is not None else None
        if not g:
            QMessageBox.information(self, T("Renvoyer"), T("Choisis d'abord un homme dans le tableau."))
            return
        if g.get("groupe") != "Mercenaires":
            QMessageBox.information(self, T("Renvoyer"), T("{0} n'est pas un mercenaire : seuls les mercenaires se renvoient ici (le service se renvoie dans l'onglet Embauche).", g.get('nom')))
            return
        rep = QMessageBox.question(self, T("Renvoyer"), T("Renvoyer {0} ?\n\nIl quitte la compagnie pour de bon. Le camp reste debout.", g.get('nom')))
        if rep != QMessageBox.StandardButton.Yes:
            return
        cle = str(g.get("cle", "")).replace("\\", "").replace("'", "")
        try:
            import sys
            if str(RACINE) not in sys.path:
                sys.path.insert(0, str(RACINE))
            from essais.cycle_en_jeu import Jeu
            code = f"return tostring(scriptorium.renvoi.renvoyer('{cle}', true))"
            Jeu().emetteur.envoyer(["hex " + code.encode("ascii", "replace").hex()])
        except Exception as err:
            self.resume.setText(T("Le jeu ne répond pas : {0}", err))
            return
        self.resume.setText(T("{0} est renvoyé. Je relis le registre…", g.get('nom')))
        QApplication.processEvents()
        time.sleep(1.5)
        self.actualiser()

    def montrer(self) -> None:
        r = self.registre
        if not r:
            return
        choix = FILTRES[max(0, self.filtre.currentIndex())]
        gens = r["gens"]
        if choix in ("Mercenaires", "Compagnons", "Artisans"):
            voulu = "Service" if choix == "Artisans" else choix
            gens = [g for g in gens if g["groupe"] == voulu]
        elif choix == "Ceux qui ont un besoin":
            gens = [g for g in gens if g["besoins"]]


        empreinte = (choix, tuple((g["cle"], g["nom"], g["grade"], g["niveau"], g["poste"], tuple(g["besoins"]),
                                   _vivant().palier(g["sante"]), g["proprete"], g["bourse"], g["dettes"], g["du"],
                                   _humeur(g), _estime(g), _experience(g), _tir(g), str(g.get("prog"))) for g in gens))
        if empreinte == getattr(self, "_empreinte", None):
            return
        self._empreinte = empreinte
        choisi = None
        ligne = self.table.currentRow()
        it0 = self.table.item(ligne, 0) if ligne >= 0 else None
        if it0 is not None:
            choisi = (it0.data(Qt.ItemDataRole.UserRole) or {}).get("cle")
        defile = self.table.verticalScrollBar().value()
        premiere = self.table.rowCount() == 0
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(gens))
        for i, g in enumerate(gens):


            groupe = g["groupe"]
            if "_archer_" in g["cle"] and groupe == "Mercenaires":
                groupe = "Mercenaire, archer"
            if groupe == "Service":
                groupe = "Artisan"

            grade = (g.get("prog") or {}).get("grade") or g["grade"]
            valeurs = [g["nom"], groupe, grade, g["niveau"], g["poste"], ", ".join(T(b) for b in g["besoins"]) or "rien",

                       None if g["sante"] is None else float(_vivant().palier(g["sante"])), g["proprete"], g["bourse"], g["dettes"], g["du"], _humeur(g), _estime(g), _experience(g),
                       _tir(g)]
            for j, val in enumerate(valeurs):
                it = QTableWidgetItem()
                if isinstance(val, float):
                    it.setData(Qt.ItemDataRole.DisplayRole, round(val, 1) if j == 3 else round(val))
                elif val is None:
                    it.setText("—")
                else:
                    it.setText(T(str(val)))
                if j == 0:
                    it.setData(Qt.ItemDataRole.UserRole, {"cle": g["cle"], "nom": g["nom"], "groupe": g["groupe"]})
                if j == 6 and isinstance(val, float) and val < 80:
                    it.setForeground(QColor(ROUGE))
                if j == 7 and isinstance(val, float) and val <= 50:
                    it.setForeground(QColor(ORANGE))
                if j == 9 and isinstance(val, float) and val > 0:
                    it.setForeground(QColor(ROUGE))
                if j == 3 and isinstance(val, float) and val < 12:
                    it.setForeground(QColor(ORANGE))
                if j == 5 and g["besoins"]:
                    it.setForeground(QColor(ORANGE))
                if j in (11, 13) and val == "à venir":
                    it.setForeground(QColor(PALE))
                if j == 12 and g.get("estime") is not None:
                    if g["estime"] <= -30 or g.get("complot") is not None:
                        it.setForeground(QColor(ROUGE if (g["estime"] <= -60 or g.get("complot") is not None) else ORANGE))
                    elif g["estime"] >= 20:
                        it.setForeground(QColor(VERT))
                it.setToolTip(T(g["cle"]))
                self.table.setItem(i, j, it)
        self.table.setSortingEnabled(True)
        if premiere:
            self.table.resizeColumnsToContents()
        if choisi is not None:
            for i in range(self.table.rowCount()):
                it = self.table.item(i, 0)
                if it is not None and (it.data(Qt.ItemDataRole.UserRole) or {}).get("cle") == choisi:
                    self.table.setCurrentCell(i, max(0, self.table.currentColumn()))
                    break
        self.table.verticalScrollBar().setValue(defile)
        tous = r["gens"]
        besoin = sum(1 for g in tous if g["besoins"])
        self.nombre_de_besoins = besoin
        heure = r.get("heure")
        h = f"{int(heure)} h {int((heure % 1) * 60):02d}" if heure is not None else "?"
        self.resume.setText(T("Relevé à {0} (heure du jeu) : {1} personnes au camp, dont {2} mercenaires, {3} compagnons et {4} artisans. {5} ont un besoin.", h, len(tous), sum(1 for g in tous if g['groupe'] == 'Mercenaires'), sum(1 for g in tous if g['groupe'] == 'Compagnons'), sum(1 for g in tous if g['groupe'] == 'Service'), besoin))
