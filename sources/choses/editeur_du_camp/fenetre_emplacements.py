
""

















from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygonF
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QListWidget, QMenu, QPushButton, QSpinBox, QVBoxLayout, QWidget)

ICI = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("fenetre_editeur_emplacements", ICI / "fenetre_editeur.py")
fe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fe)
T = fe.T

RAYON_MIN, RAYON_MAX = 2, 60
RONDE_MAX = 40
COULEURS_ZONES = {"briefing": "#2f6db5", "duels": "#b52f2f", "entrainement": "#2f9d4a", "ratelier": "#c28a1c"}


def noms_des_zones() -> dict[str, str]:
    ""
    try:
        an = json.loads((ICI.parent / "zones_du_camp" / "annonces.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        an = {}
    noms = {}
    for cle, v in an.items():
        if cle.startswith("scr_gn_zone_"):
            noms[cle[len("scr_gn_zone_"):]] = v[0] if isinstance(v, list) else str(v)
    return noms


NOMS = noms_des_zones()


def nom_de_zone(cle: str) -> str:
    genre = cle.split(":", 1)[0]
    return NOMS.get(genre, "Zone « " + genre + " »")


class PlanEmplacements(fe.Plan):
    ""

    def __init__(self, fenetre) -> None:
        super().__init__(fenetre)
        self.pose: dict | None = None
        self.trace: list | None = None
        self.setMouseTracking(True)

    def _ajuster(self, r: dict) -> None:
        ""
        if self.zoom is not None:
            return
        r2 = dict(r)
        places = dict(r.get("places", {}))
        for cle, z in r.get("zones", {}).items():
            for i, (da, dc) in enumerate(((1, 0), (-1, 0), (0, 1), (0, -1))):
                places[f"_zone_{cle}_{i}"] = (z["avant"] + da * z["rayon"], z["cote"] + dc * z["rayon"], 0.0)
        for i, (a, c) in enumerate(r.get("ronde") or []):
            places[f"_ronde_{i}"] = (a, c, 0.0)
        r2["places"] = places
        super()._ajuster(r2)


    def zone_sous(self, pt: QPointF) -> str | None:
        if not self.releve:
            return None
        a, c = self._plan(pt)
        meilleure, rmin = None, 1e9
        for cle, z in self.releve.get("zones", {}).items():
            if (a - z["avant"]) ** 2 + (c - z["cote"]) ** 2 <= z["rayon"] ** 2 and z["rayon"] < rmin:
                meilleure, rmin = cle, z["rayon"]
        return meilleure

    def genre_de_l_objet(self, n) -> str | None:
        r = self.releve or {}
        o = r.get("objets", {}).get(n)
        if o is None:
            return None
        for genre, t in r.get("zones_types", {}).items():
            if o["cle"] in t.get("objets", []):
                return genre
        return None


    def commencer_zone(self, cle: str, rayon: float) -> None:
        self.trace = None
        self.pose = {"cle": cle, "rayon": max(RAYON_MIN, min(RAYON_MAX, float(rayon)))}
        self.fenetre.etat.setText(T("« {0} » : bouge la souris, molette = sa taille, clic gauche = la poser. Clic droit ou Échap : annuler.", nom_de_zone(cle)))
        self.update()

    def commencer_ronde(self) -> None:
        self.pose = None
        self.trace = []
        self.fenetre.etat.setText(T("La ronde : clic gauche = un point (sur un point : l'enlever), clic droit = la finir "
                                  "(3 points au moins). Échap : annuler."))
        self.update()

    def annuler(self) -> None:
        self.pose, self.trace = None, None
        self.fenetre._compter()
        self.update()


    def mousePressEvent(self, ev) -> None:
        if not self.releve or self.zoom is None:
            return
        pt = ev.position()
        a, c = self._plan(pt)
        if self.pose is not None:
            if ev.button() == Qt.MouseButton.LeftButton:
                cle, rayon = self.pose["cle"], self.pose["rayon"]
                self.pose = None
                self.fenetre.definir_zone(cle, a, c, rayon)
            elif ev.button() == Qt.MouseButton.RightButton:
                self.annuler()
            return
        if self.trace is not None:
            if ev.button() == Qt.MouseButton.LeftButton:
                proche = [i for i, (pa, pc_) in enumerate(self.trace) if math.hypot(pa - a, pc_ - c) < 1.5]
                if proche:
                    del self.trace[proche[0]]
                elif len(self.trace) < RONDE_MAX:
                    self.trace.append((a, c))
                self.fenetre.etat.setText(T("La ronde : {0} point(s). Clic droit pour la finir.", len(self.trace)))
                self.update()
            elif ev.button() == Qt.MouseButton.RightButton:
                points, self.trace = self.trace, None
                if len(points) >= 3:
                    self.fenetre.definir_ronde(points)
                else:
                    self.fenetre.etat.setText(T("Il faut au moins 3 points : la ronde n'a pas changé."))
                    self.update()
            return
        if ev.button() == Qt.MouseButton.MiddleButton:
            self._mode, self._depart = "vue", (pt, self.centre_vue)
            return
        if ev.button() == Qt.MouseButton.RightButton:
            self._mode, self._depart = "droit", (pt, self.centre_vue)
            return
        if ev.button() == Qt.MouseButton.LeftButton:

            k = self._element_sous(pt)
            self.choix = {k} if k is not None else set()
            self.fenetre.montrer_le_choix()
            self.update()

    def mouseMoveEvent(self, ev) -> None:
        if self.pose is not None or self.trace is not None:
            self._souris = ev.position()
            self.update()
            return
        if self._mode in ("vue", "droit"):
            super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev) -> None:
        if self.pose is not None or self.trace is not None:
            return
        mode, self._mode = self._mode, None
        if mode == "droit":
            self._menu(ev.position())

    def wheelEvent(self, ev) -> None:
        if self.zoom is None:
            return
        pas = 1 if ev.angleDelta().y() > 0 else -1
        ctrl = bool(ev.modifiers() & Qt.KeyboardModifier.ControlModifier)
        if self.pose is not None and not ctrl:
            self.pose["rayon"] = max(RAYON_MIN, min(RAYON_MAX, self.pose["rayon"] + pas))
            self.update()
            return
        pt = ev.position()
        a, c = self._plan(pt)
        self.zoom = max(0.3, min(80.0, self.zoom * (1.2 ** pas)))
        a2, c2 = self._plan(pt)
        ca, cc = self.centre_vue
        self.centre_vue = (ca + a - a2, cc + c - c2)
        self.update()

    def keyPressEvent(self, ev) -> None:
        if ev.key() == Qt.Key.Key_Escape:
            self.annuler()

    def _menu(self, pt: QPointF) -> None:
        r = self.releve or {}
        zones = r.get("zones", {})
        types = r.get("zones_types", {})
        m = QMenu(T(self))
        zc = self.zone_sous(pt)
        k = self._element_sous(pt)

        if k is not None and k[0] == "o":
            genre = self.genre_de_l_objet(k[1])
            if genre is not None:
                cle = f"{genre}:{k[1]}"
                rayon = zones.get(cle, {}).get("rayon") or types.get(genre, {}).get("rayon", 5)
                nom = self.fenetre.noms_de_la_palette.get(r["objets"][k[1]]["cle"], "cet objet")
                m.addAction((T("Changer la zone d'entraînement de « {0} »", nom) if cle in zones
                             else T("Placer la zone d'entraînement de « {0} »", nom)),
                            lambda cle=cle, rayon=rayon: self.commencer_zone(cle, rayon))
                if cle in zones:
                    m.addAction(T("Effacer la zone de « {0} »", nom), lambda cle=cle: self.fenetre.effacer_zone(cle))
                m.addSeparator()

        if zc is not None:
            m.addAction(T("Déplacer / changer la taille : {0}", nom_de_zone(zc)),
                        lambda cle=zc: self.commencer_zone(cle, zones[cle]["rayon"]))
            m.addAction(T("Effacer : {0}", nom_de_zone(zc)), lambda cle=zc: self.fenetre.effacer_zone(cle))
            m.addSeparator()

        libres = sorted(g for g, t in types.items() if t.get("libre"))
        if libres:
            sm = m.addMenu(T("Placer ici…"))
            for g in libres:
                deja = g in zones
                rayon = zones.get(g, {}).get("rayon") or types[g].get("rayon", 8)
                sm.addAction(T(nom_de_zone(g)) + (T(" (déjà posée : elle vient ici)") if deja else ""),
                             lambda g=g, rayon=rayon: self.commencer_zone(g, rayon))

        m.addAction(T("Tracer la ronde des gardes"), self.commencer_ronde)
        if r.get("ronde"):
            m.addAction(T("Effacer la ronde tracée (retour au cercle autour du camp)"), self.fenetre.effacer_ronde)
        m.addSeparator()
        m.addAction(T("Recadrer (tout le camp)"), self.recadrer)
        m.exec(self.mapToGlobal(pt.toPoint()))


    def paintEvent(self, ev) -> None:
        super().paintEvent(ev)
        if not self.releve or self.zoom is None:
            return
        r = self.releve
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        for cle, z in sorted(r.get("zones", {}).items(), key=lambda kv: -kv[1]["rayon"]):
            coul = QColor(COULEURS_ZONES.get(cle.split(":", 1)[0], "#7a5fb5"))
            centre = self._ecran(z["avant"], z["cote"])
            ray = z["rayon"] * self.zoom
            fond = QColor(coul)
            fond.setAlpha(45)
            p.setPen(QPen(coul, 2))
            p.setBrush(QBrush(fond))
            p.drawEllipse(centre, ray, ray)
            if self.ecritures:
                p.setPen(coul.darker(130))
                p.drawText(centre + QPointF(-ray * .7, -ray - 4), T("{0} ({1:.0f} m)", nom_de_zone(cle), z['rayon']))

        pts = r.get("ronde") or []
        if pts:
            ecr = [self._ecran(a, c) for a, c in pts]
            p.setPen(QPen(QColor("#1f4e79"), 2, Qt.PenStyle.DashLine))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPolygon(QPolygonF(ecr))
            p.setBrush(QBrush(QColor("#1f4e79")))
            for i, q in enumerate(ecr, 1):
                p.drawEllipse(q, 3.5, 3.5)
                if self.ecritures:
                    p.drawText(q + QPointF(5, -5), T(str(i)))

        if self.pose is not None and self._souris is not None:
            coul = QColor(COULEURS_ZONES.get(self.pose["cle"].split(":", 1)[0], "#7a5fb5"))
            ray = self.pose["rayon"] * self.zoom
            fond = QColor(coul)
            fond.setAlpha(60)
            p.setPen(QPen(coul, 2, Qt.PenStyle.DashLine))
            p.setBrush(QBrush(fond))
            p.drawEllipse(self._souris, ray, ray)
            p.setPen(coul.darker(130))
            p.drawText(self._souris + QPointF(8, -8), T("{0} : {1:.0f} m", nom_de_zone(self.pose['cle']), self.pose['rayon']))
        if self.trace is not None:
            ecr = [self._ecran(a, c) for a, c in self.trace]
            p.setPen(QPen(QColor("#b5541b"), 2))
            p.setBrush(QBrush(QColor("#b5541b")))
            for i in range(1, len(ecr)):
                p.drawLine(ecr[i - 1], ecr[i])
            if ecr and self._souris is not None:
                p.setPen(QPen(QColor("#b5541b"), 1, Qt.PenStyle.DashLine))
                p.drawLine(ecr[-1], self._souris)
                if len(ecr) >= 2:
                    p.drawLine(self._souris, ecr[0])
            for i, q in enumerate(ecr, 1):
                p.drawEllipse(q, 4, 4)
                p.drawText(q + QPointF(6, -6), T(str(i)))


class FenetreEmplacements(fe.Fenetre):
    ""
    CLASSE_PLAN = PlanEmplacements
    TITRE = "Emplacements"
    AVEC_CONSTRUCTION = False

    def __init__(self) -> None:
        super().__init__()
        self.releve_recu(self.plan.releve or {})

    def _panneau(self, _panneau: QWidget) -> QWidget:

        self._palette_cachee = _panneau
        _panneau.hide()
        w = QWidget()
        v = QVBoxLayout(w)
        v.addWidget(QLabel(T("<b>Les zones du camp</b>")))
        self.liste_zones = QListWidget()
        v.addWidget(self.liste_zones, 1)
        v.addWidget(QLabel(T("<b>La ronde des gardes</b>")))
        self.ronde_etat = QLabel("—")
        self.ronde_etat.setWordWrap(True)
        v.addWidget(self.ronde_etat)
        b = QHBoxLayout()
        tracer = QPushButton(T("Tracer la ronde"))
        tracer.clicked.connect(lambda: self.plan.commencer_ronde())
        effacer = QPushButton(T("Effacer le tracé"))
        effacer.clicked.connect(self.effacer_ronde)
        b.addWidget(tracer)
        b.addWidget(effacer)
        v.addLayout(b)
        g = QHBoxLayout()
        g.addWidget(QLabel(T("Gardes de ronde")))
        self.gardes = QSpinBox()
        self.gardes.setRange(0, 12)
        self.gardes.setSpecialValueText("?")
        g.addWidget(self.gardes)
        v.addLayout(g)
        h = QHBoxLayout()
        h.addWidget(QLabel(T("Durée d'une garde (h)")))
        self.heures = QSpinBox()
        self.heures.setRange(0, 12)
        self.heures.setSpecialValueText("?")
        h.addWidget(self.heures)
        v.addLayout(h)
        appliquer = QPushButton(T("Appliquer les réglages de la ronde"))
        appliquer.clicked.connect(self.regler_ronde)
        v.addWidget(appliquer)
        aide = QLabel(T("Clic droit sur un râtelier : sa zone d'entraînement.\n"
                      "Clic droit sur une zone : la déplacer, changer sa taille, l'effacer.\n"
                      "Clic droit dans le vide : placer la zone du briefing, des duels, d'entraînement ; tracer la ronde.\n"
                      "Une zone à poser suit la souris : molette = sa taille, clic gauche = la poser.\n\n"
                      "La vue : molette = zoom, clic droit maintenu et glissé = se déplacer."))
        aide.setWordWrap(True)
        v.addWidget(aide)
        w.setFixedWidth(300)
        return w

    def releve_recu(self, r: dict) -> None:
        self.liste_zones.clear()
        zones = r.get("zones", {})
        types = r.get("zones_types", {})
        for g in sorted(t for t, d in types.items() if d.get("libre")):
            z = zones.get(g)
            self.liste_zones.addItem(T("{0} : ", nom_de_zone(g)) + (T("posée ({0:.0f} m)", z['rayon']) if z else T("pas posée")))
        for g in sorted(t for t, d in types.items() if not d.get("libre")):
            n = sum(1 for cle in zones if cle.startswith(g + ":"))
            self.liste_zones.addItem(T("{0} : {1} posée(s)", nom_de_zone(g), n))
        pts = r.get("ronde") or []
        self.ronde_etat.setText(T("Tracée : {0} points.", len(pts)) if pts else T("Pas de tracé : les gardes tournent en cercle "
                                "autour du camp."))
        if r.get("ronde_reglages"):
            g_, h_ = r["ronde_reglages"]
            self.gardes.setValue(max(1, min(12, g_)))
            self.heures.setValue(max(1, min(12, h_)))
        else:
            self.gardes.setValue(0)
            self.heures.setValue(0)


    def definir_zone(self, cle: str, avant: float, cote: float, rayon: float) -> None:
        rep = self._ordre(f'return tostring(scriptorium.zones.definir("{cle}", {avant:.2f}, {cote:.2f}, {rayon:.1f}) ~= nil)',
                          T("Je pose « {0} »", nom_de_zone(cle)))
        if rep is not None:
            self.relever()

    def effacer_zone(self, cle: str) -> None:
        rep = self._ordre(f'scriptorium.zones.effacer("{cle}") return "ok"', T("J'efface « {0} »", nom_de_zone(cle)))
        if rep is not None:
            self.relever()

    def definir_ronde(self, points: list) -> None:
        table = "{" + ",".join(f"{{avant={a:.2f},cote={c:.2f}}}" for a, c in points) + "}"
        rep = self._ordre(f"return tostring(scriptorium.ronde_tracee.definir({table}))", "Je trace la ronde")
        if rep is not None:
            self.relever()

    def effacer_ronde(self) -> None:
        rep = self._ordre('scriptorium.ronde_tracee.effacer() return "ok"', "J'efface la ronde tracée")
        if rep is not None:
            self.relever()

    def regler_ronde(self) -> None:
        g, h = self.gardes.value(), self.heures.value()
        if g < 1 or h < 1:
            self.etat.setText(T("Choisis d'abord le nombre de gardes et la durée d'une garde (1 à 12)."))
            return
        rep = self._ordre(f"return tostring(scriptorium.ronde_tracee.regler({g}, {h}, compagnie))",
                          "Je règle la ronde")
        if rep is not None:
            self.etat.setText(T("La ronde : {0} garde(s), relevés toutes les {1} h.", g, h) if rep.strip() == "true"
                              else T("Le jeu a refusé : ") + T(rep))
