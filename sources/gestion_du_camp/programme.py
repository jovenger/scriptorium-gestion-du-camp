
""























from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from noyau import chemins, langue_du_programme as lg
from noyau.langue_du_programme import T

from PyQt6.QtCore import QEvent, QObject, Qt, QTimer
from PyQt6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QLabel, QTabWidget, QVBoxLayout, QWidget

NOM_INSTANCE = "ScriptoriumGestionDuCamp"
ONGLETS = ["banque", "embauche", "amenagement", "emplacements", "personnel", "metiers", "objectifs"]
TITRES = {"banque": "Banque", "embauche": "Embauche", "amenagement": "Aménagement du camp", "emplacements": "Emplacements", "personnel": "Personnel", "metiers": "Métiers",
          "objectifs": "Objectifs"}
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
        self.etiquette.setWordWrap(True)
        v.addWidget(self.etiquette)
        v.addStretch(1)


class GestionDuCamp(QTabWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(T("Gestion du camp"))
        self.resize(1320, 960)

        self._pause = QLabel("")
        self._pause.setStyleSheet("background:#8b1e1e;color:#fff;font-weight:bold;padding:4px 10px;")
        self._pause.hide()

        coin = QWidget()
        rang = QHBoxLayout(coin)
        rang.setContentsMargins(0, 0, 6, 0)
        rang.addWidget(self._pause)
        self.liste_des_langues = QComboBox()
        self.liste_des_langues.addItem(T("Langue du jeu"), lg.PAR_LE_JEU)
        for code, nom in lg.NOMS.items():
            self.liste_des_langues.addItem(nom, code)
        self.liste_des_langues.setCurrentIndex(max(0, self.liste_des_langues.findData(lg.lire_le_choix())))
        self.liste_des_langues.activated.connect(self._langue_choisie)
        rang.addWidget(self.liste_des_langues)
        self.setCornerWidget(coin, Qt.Corner.TopRightCorner)
        self._minuteur_pause = QTimer(self)
        self._minuteur_pause.timeout.connect(self._voir_la_pause)
        self._minuteur_pause.start(15_000)
        QTimer.singleShot(1500, self._voir_la_pause)
        self.pages: dict[str, QWidget] = {}

        from banque import fenetre_banque as fb
        self.banque = fb.FenetreBanque()
        self._ajouter("banque", self.banque)

        self.embauche = _module("onglet_embauche", Path(__file__).with_name("onglet_embauche.py")).OngletEmbauche()
        self._ajouter("embauche", self.embauche)

        self._ajouter("amenagement", EnAttente("Chargement des objets du jeu…"))
        self.editeur = None

        self._ajouter("emplacements", EnAttente("Chargement du plan des emplacements…"))
        self.emplacements = None

        self.personnel = _module("onglet_personnel", Path(__file__).with_name("onglet_personnel.py")).OngletPersonnel()
        self._ajouter("personnel", self.personnel)

        self.metiers = _module("onglet_metiers", Path(__file__).with_name("onglet_metiers.py")).OngletMetiers()
        self._ajouter("metiers", self.metiers)

        self.objectifs = _module("onglet_objectifs", Path(__file__).with_name("onglet_objectifs.py")).OngletObjectifs()
        self._ajouter("objectifs", self.objectifs)
        self.currentChanged.connect(self._onglet_montre)


    def _voir_la_pause(self) -> None:
        sens = _sens_de_la_pause()
        if sens:
            from noyau import partie_en_pause
            self._pause.setText(T(partie_en_pause.TEXTE))
            self._pause.show()
            self.setWindowTitle(T("Gestion du camp — SCRIPTORIUM EN PAUSE : relancez le jeu"))
        else:
            self._pause.hide()
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

    def _ajouter(self, cle: str, page: QWidget) -> None:
        self.pages[cle] = page
        self.addTab(page, T(TITRES[cle]))

    def _onglet_montre(self, i: int) -> None:
        if ONGLETS[i] == "amenagement" and self.editeur is None:
            QTimer.singleShot(50, self._construire_l_amenagement)
        if ONGLETS[i] == "emplacements" and self.emplacements is None:
            QTimer.singleShot(50, self._construire_les_emplacements)
        if ONGLETS[i] == "banque":
            QTimer.singleShot(200, self.banque.lire_la_caisse)
        if ONGLETS[i] == "embauche":
            QTimer.singleShot(200, self.embauche.actualiser)
        if ONGLETS[i] == "personnel":
            QTimer.singleShot(200, self.personnel.actualiser)
        if ONGLETS[i] == "metiers":
            QTimer.singleShot(200, self.metiers.actualiser)
        if ONGLETS[i] == "objectifs":
            QTimer.singleShot(200, self.objectifs.actualiser)

    def _construire_l_amenagement(self) -> None:
        if self.editeur is not None:
            return
        QApplication.processEvents()
        try:
            fe = _module("amenagement_du_camp", EDITEUR)
            self.editeur = fe.Fenetre()
        except Exception as err:
            self.pages["amenagement"].etiquette.setText(T("L'aménagement n'a pas pu s'ouvrir : {0}", err))
            return
        i = ONGLETS.index("amenagement")
        garde = self.currentIndex() == i
        self.removeTab(i)
        self.insertTab(i, self.editeur, T(TITRES["amenagement"]))
        self.pages["amenagement"] = self.editeur
        if garde:
            self.setCurrentIndex(i)

    def _construire_les_emplacements(self) -> None:
        if self.emplacements is not None:
            return
        QApplication.processEvents()
        try:
            fm = _module("emplacements_du_camp", EMPLACEMENTS)
            self.emplacements = fm.FenetreEmplacements()
        except Exception as err:
            self.pages["emplacements"].etiquette.setText(T("Les emplacements n'ont pas pu s'ouvrir : {0}", err))
            return
        i = ONGLETS.index("emplacements")
        garde = self.currentIndex() == i
        self.removeTab(i)
        self.insertTab(i, self.emplacements, T(TITRES["emplacements"]))
        self.pages["emplacements"] = self.emplacements
        if garde:
            self.setCurrentIndex(i)

    def montrer(self, cle: str | None) -> None:
        if cle in ONGLETS:
            self.setCurrentIndex(ONGLETS.index(cle))
            self._onglet_montre(ONGLETS.index(cle))






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
        if i + 1 < len(argv) and argv[i + 1] in ONGLETS:
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
    etat = {"vu": False}

    def regarder_le_jeu() -> None:
        if _jeu_ouvert():
            etat["vu"] = True
        elif etat["vu"]:
            etat["vu"] = False
            if not f.isVisible():
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
    f.montrer(onglet or "banque")
    if "--devant" in sys.argv:
        sur_l_ecran_du_jeu_bientot(f)
        au_premier_plan(f)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
