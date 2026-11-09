
""












from __future__ import annotations

import math
import random

from PyQt6.QtCore import QEasingCurve, QPoint, QPointF, QPropertyAnimation, QRectF, Qt, QTimer, QVariantAnimation
from PyQt6.QtGui import QBrush, QColor, QFont, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QWidget


PARCHEMIN = "#ead9b5"
PARCHEMIN_FONCE = "#d6bf90"
CARTE = "#f4e9cf"
CARTE_FONCEE = "#e6d3a8"
ENCRE = "#3a2716"
PALE = "#6b5338"
OR = "#7d5617"
OR_CLAIR = "#e2bb5c"
BOIS = "#2e1e13"
BOIS_CLAIR = "#4a3120"
BORD = "#b99d6b"
CIRE = "#8e1f1a"
VERT = "#3f6b2e"
ROUGE = "#9a2a1f"
ORANGE = "#a8561a"

FOND = "transparent"

POLICE = "Palatino Linotype"
POLICES = '"Palatino Linotype", "Book Antiqua", Georgia, serif'


def police(taille: float = 11.0, gras: bool = False, petites_capitales: bool = False) -> QFont:
    f = QFont(POLICE)
    f.setPointSizeF(taille)
    f.setBold(gras)
    if petites_capitales:
        f.setCapitalization(QFont.Capitalization.SmallCaps)
        f.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 104)
    return f


def feuille(extra: str = "") -> str:
    ""
    return f"""
        QWidget {{ background: transparent; color: {ENCRE}; font-family: {POLICES}; font-size: 12pt; }}
        QLabel#Entete {{ color: {ENCRE}; font-size: 24pt; }}
        QLabel#Section {{ color: {OR}; font-size: 15pt; }}
        QLabel#Valeur {{ color: {OR}; font-size: 20pt; }}
        QLabel#Titre {{ color: {PALE}; font-size: 10.5pt; }}
        QLabel#Note {{ color: {PALE}; font-size: 10.5pt; font-style: italic; }}
        QLabel#Solde {{ color: {OR}; font-size: 15pt; }}
        QFrame#Carte {{ background: rgba(255, 248, 230, 150); border: 1px solid {BORD}; border-radius: 10px; }}
        QFrame#Carte QLabel {{ background: transparent; }}
        QPushButton {{ background: {ENCRE}; color: #f3e6c6; border: none; border-radius: 7px; padding: 7px 16px;
                      font-weight: bold; }}
        QPushButton:hover {{ background: #563b22; }}
        QPushButton:pressed {{ background: #24170c; padding-top: 8px; padding-bottom: 6px; }}
        QPushButton:disabled {{ background: #b9a684; color: #e9dcc0; }}
        QPushButton:focus {{ outline: none; }}
        QPushButton#Clair {{ background: transparent; color: {ENCRE}; border: 1.5px solid {ENCRE}; }}
        QPushButton#Clair:hover {{ background: rgba(58, 39, 22, 25); }}
        QPushButton#Piece {{ color: #2a1a0c; border-radius: 15px; padding: 6px 14px;
                      background: qradialgradient(cx:0.35, cy:0.3, radius:0.9, fx:0.35, fy:0.3,
                                  stop:0 #f8e19a, stop:0.6 #c99a36, stop:1 #8a6420); border: 1px solid #6b4c17; }}
        QPushButton#Piece:hover {{ background: qradialgradient(cx:0.35, cy:0.3, radius:0.9, fx:0.35, fy:0.3,
                                  stop:0 #fff0b8, stop:0.6 #d8a940, stop:1 #93702a); }}
        QPushButton#PieceArgent {{ color: #2a2620; border-radius: 15px; padding: 6px 14px; border: 1px solid #5d574b;
                      background: qradialgradient(cx:0.35, cy:0.3, radius:0.9, fx:0.35, fy:0.3,
                                  stop:0 #f5f1e8, stop:0.6 #b9b2a3, stop:1 #7d7565); }}
        QPushButton#PieceArgent:hover {{ background: qradialgradient(cx:0.35, cy:0.3, radius:0.9, fx:0.35, fy:0.3,
                                  stop:0 #ffffff, stop:0.6 #c8c1b2, stop:1 #8a8272); }}
        QPushButton#Puce {{ background: transparent; color: {ENCRE}; border: 1px solid {BORD}; border-radius: 14px;
                      padding: 5px 14px; font-weight: normal; }}
        QPushButton#Puce:hover {{ background: rgba(184, 137, 46, 45); }}
        QPushButton#Puce:checked {{ background: {ENCRE}; color: #f3e6c6; border-color: {ENCRE}; }}
        QSpinBox, QLineEdit, QComboBox {{ background: #fff8e6; color: {ENCRE}; border: 1px solid {BORD};
                      border-radius: 6px; padding: 4px 8px; min-height: 22px; }}
        QSpinBox:focus, QLineEdit:focus, QComboBox:focus {{ border: 1.5px solid {OR}; }}
        QComboBox QAbstractItemView {{ background: #fbf1da; color: {ENCRE}; selection-background-color: {OR_CLAIR};
                      selection-color: {ENCRE}; border: 1px solid {BORD}; }}
        QCheckBox {{ spacing: 6px; }}
        QTableWidget, QTableView, QListWidget, QTreeWidget {{ background: rgba(255, 248, 230, 170); alternate-background-color:
                      rgba(234, 217, 181, 120); gridline-color: rgba(185, 157, 107, 110); border: 1px solid {BORD};
                      border-radius: 8px; selection-background-color: rgba(226, 187, 92, 150); selection-color: {ENCRE}; }}
        QHeaderView::section {{ background: {CARTE_FONCEE}; color: {ENCRE}; border: none;
                      border-bottom: 1px solid {BORD}; padding: 6px; font-weight: bold; }}
        QTableCornerButton::section {{ background: {CARTE_FONCEE}; border: none; }}
        QTabWidget::pane {{ border: none; }}
        QTabBar::tab {{ background: transparent; color: {ENCRE}; border: 1px solid {BORD}; border-radius: 13px;
                      padding: 5px 14px; margin: 2px 4px 8px 0; }}
        QTabBar::tab:hover {{ background: rgba(184, 137, 46, 45); }}
        QTabBar::tab:selected {{ background: {ENCRE}; color: #f3e6c6; border-color: {ENCRE}; }}
        QScrollBar:vertical {{ background: transparent; width: 11px; margin: 2px; }}
        QScrollBar::handle:vertical {{ background: rgba(125, 86, 23, 120); border-radius: 4px; min-height: 30px; }}
        QScrollBar:horizontal {{ background: transparent; height: 11px; margin: 2px; }}
        QScrollBar::handle:horizontal {{ background: rgba(125, 86, 23, 120); border-radius: 4px; min-width: 30px; }}
        QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
        QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
        QMenu {{ background: #fbf1da; color: {ENCRE}; border: 1px solid {BORD}; padding: 4px; }}
        QMenu::item {{ padding: 5px 18px; border-radius: 4px; }}
        QMenu::item:selected {{ background: rgba(226, 187, 92, 160); }}
        QToolTip {{ background: #fbf1da; color: {ENCRE}; border: 1px solid {BORD}; padding: 4px; }}
        QMessageBox, QDialog {{ background: {PARCHEMIN}; }}
        {extra}
    """



_GRAIN: QImage | None = None


def _grain() -> QImage:
    ""
    global _GRAIN
    if _GRAIN is None:
        img = QImage(160, 160, QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(QColor(0, 0, 0, 0))
        r = random.Random(1403)
        p = QPainter(img)
        for _ in range(2600):
            a = r.randint(6, 26)
            p.setPen(QColor(90, 55, 20, a))
            p.drawPoint(r.randint(0, 159), r.randint(0, 159))
        for _ in range(90):
            a = r.randint(4, 12)
            p.setPen(QPen(QColor(120, 80, 30, a), r.choice((1, 2))))
            x, y = r.randint(0, 159), r.randint(0, 159)
            p.drawLine(x, y, x + r.randint(-6, 6), y + r.randint(-2, 2))
        p.end()
        _GRAIN = img
    return _GRAIN


def peindre_le_parchemin(p: QPainter, rect) -> None:
    r = QRectF(rect)
    g = QRadialGradient(r.center(), max(r.width(), r.height()) * 0.75)
    g.setColorAt(0.0, QColor("#efe0bf"))
    g.setColorAt(0.62, QColor(PARCHEMIN))
    g.setColorAt(1.0, QColor(PARCHEMIN_FONCE))
    p.fillRect(r, g)

    t1 = QRadialGradient(QPointF(r.left() + r.width() * 0.2, r.top() + r.height() * 0.1), r.width() * 0.45)
    t1.setColorAt(0, QColor(255, 255, 255, 70))
    t1.setColorAt(1, QColor(255, 255, 255, 0))
    p.fillRect(r, t1)
    t2 = QRadialGradient(QPointF(r.left() + r.width() * 0.85, r.top() + r.height() * 0.9), r.width() * 0.5)
    t2.setColorAt(0, QColor(120, 80, 30, 55))
    t2.setColorAt(1, QColor(120, 80, 30, 0))
    p.fillRect(r, t2)
    p.fillRect(r, QBrush(_grain()))

    for i, a in enumerate((60, 34, 18, 8)):
        p.setPen(QPen(QColor(90, 55, 20, a), 6))
        p.drawRect(r.adjusted(i * 5 + 3, i * 5 + 3, -i * 5 - 3, -i * 5 - 3))


class Parchemin(QWidget):
    ""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

    def paintEvent(self, ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        peindre_le_parchemin(p, self.rect())
        p.end()


class Ruban(QWidget):
    ""

    def paintEvent(self, ev) -> None:
        p = QPainter(self)
        g = QLinearGradient(0, 0, 0, self.height())
        g.setColorAt(0, QColor(BOIS_CLAIR))
        g.setColorAt(1, QColor(BOIS))
        p.fillRect(self.rect(), g)
        p.fillRect(QRectF(0, 0, self.width(), self.height()), QBrush(_grain()))
        p.setPen(QPen(QColor(OR_CLAIR), 1))
        p.drawLine(self.width() - 2, 0, self.width() - 2, self.height())
        p.setPen(QPen(QColor("#120c07"), 2))
        p.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
        p.end()


class Blason(QWidget):
    ""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(60, 70)

    def paintEvent(self, ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        ecu = QPainterPath()
        ecu.moveTo(4, 4)
        ecu.lineTo(w - 4, 4)
        ecu.lineTo(w - 4, h * 0.45)
        ecu.cubicTo(w - 4, h * 0.75, w * 0.7, h * 0.88, w / 2, h - 3)
        ecu.cubicTo(w * 0.3, h * 0.88, 4, h * 0.75, 4, h * 0.45)
        ecu.closeSubpath()
        p.setPen(QPen(QColor(OR_CLAIR), 2.5))
        p.setBrush(QColor(CIRE))
        p.drawPath(ecu)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(OR_CLAIR))
        p.drawPath(_etoile(QPointF(w / 2, h * 0.42), 15, 6.5))
        p.end()


def _etoile(c: QPointF, r1: float, r2: float, branches: int = 5) -> QPainterPath:
    chemin = QPainterPath()
    for i in range(branches * 2):
        r = r1 if i % 2 == 0 else r2
        a = -math.pi / 2 + i * math.pi / branches
        pt = QPointF(c.x() + r * math.cos(a), c.y() + r * math.sin(a))
        chemin.moveTo(pt) if i == 0 else chemin.lineTo(pt)
    chemin.closeSubpath()
    return chemin



def arreter_l_entree(page: QWidget) -> None:
    ""

    anims = getattr(page, "_animations_d_entree", None)
    if not anims:
        return
    page._animations_d_entree = None
    fondu, glisse, fin = anims
    try:
        fondu.finished.disconnect()
    except (TypeError, RuntimeError):
        pass
    fondu.stop()
    glisse.stop()
    page.setGraphicsEffect(None)
    page.move(fin)


def entree(page: QWidget, depuis_la_gauche: bool = True) -> None:
    ""
    arreter_l_entree(page)
    effet = QGraphicsOpacityEffect(page)
    page.setGraphicsEffect(effet)
    fondu = QPropertyAnimation(effet, b"opacity", page)
    fondu.setDuration(320)
    fondu.setStartValue(0.0)
    fondu.setEndValue(1.0)
    fondu.setEasingCurve(QEasingCurve.Type.OutCubic)
    fin = page.pos()
    glisse = QPropertyAnimation(page, b"pos", page)
    glisse.setDuration(320)
    glisse.setStartValue(fin + QPoint(-28 if depuis_la_gauche else 28, 0))
    glisse.setEndValue(fin)
    glisse.setEasingCurve(QEasingCurve.Type.OutCubic)

    def fini() -> None:
        page._animations_d_entree = None
        page.setGraphicsEffect(None)
        page.move(fin)
    fondu.finished.connect(fini)
    page._animations_d_entree = (fondu, glisse, fin)
    fondu.start()
    glisse.start()


class PluieDePieces(QWidget):
    ""

    def __init__(self, fenetre: QWidget) -> None:
        super().__init__(fenetre)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.pieces: list[tuple[QPointF, QPointF, float, float]] = []
        self.t = 0.0
        self.hide()
        self.anim = QVariantAnimation(self)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setDuration(1000)
        self.anim.valueChanged.connect(self._pas)
        self.anim.finished.connect(self.hide)

    def lancer(self, depuis: QPoint, vers: QPoint, nombre: int = 6) -> None:
        self.setGeometry(self.parentWidget().rect())
        self.raise_()
        r = random.Random()
        self.pieces = []
        for i in range(max(1, min(10, nombre))):
            a = QPointF(depuis) + QPointF(r.uniform(-18, 18), r.uniform(-6, 6))
            b = QPointF(vers) + QPointF(r.uniform(-14, 14), r.uniform(-6, 6))
            self.pieces.append((a, b, i * 0.06, r.uniform(0.85, 1.15)))
        self.show()
        self.anim.stop()
        self.anim.start()

    def _pas(self, v) -> None:
        self.t = float(v)
        self.update()

    def paintEvent(self, ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        for a, b, retard, taille in self.pieces:
            k = (self.t - retard) / max(0.01, 1.0 - 0.06 * len(self.pieces))
            if k <= 0 or k >= 1:
                continue
            k = 1 - (1 - k) ** 2
            haut = min(a.y(), b.y()) - 90
            milieu = QPointF((a.x() + b.x()) / 2, haut)
            x = (1 - k) ** 2 * a.x() + 2 * (1 - k) * k * milieu.x() + k ** 2 * b.x()
            y = (1 - k) ** 2 * a.y() + 2 * (1 - k) * k * milieu.y() + k ** 2 * b.y()
            rayon = 9 * taille * (1 - 0.35 * k)
            g = QRadialGradient(QPointF(x - rayon * 0.3, y - rayon * 0.35), rayon * 1.4)
            g.setColorAt(0, QColor("#fff1b8"))
            g.setColorAt(0.55, QColor("#d9a73c"))
            g.setColorAt(1, QColor("#8a6420"))
            p.setPen(QPen(QColor(90, 60, 15, 160), 1))
            p.setBrush(g)
            p.setOpacity(1.0 if k < 0.8 else max(0.0, (1 - k) / 0.2))
            p.drawEllipse(QPointF(x, y), rayon, rayon * (0.55 + 0.45 * abs(math.cos(k * 9 + taille))))
        p.end()


class Sceau(QWidget):
    ""

    def __init__(self, parent: QWidget, texte: str) -> None:
        super().__init__(parent)
        self.texte = texte
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setFixedSize(96, 96)
        self.echelle, self.opacite = 2.2, 0.0
        self.anim = QVariantAnimation(self)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setDuration(2300)
        self.anim.valueChanged.connect(self._pas)
        self.anim.finished.connect(self.deleteLater)

    def _pas(self, v) -> None:
        t = float(v)
        if t < 0.2:
            k = t / 0.2
            self.echelle = 2.2 - 1.3 * QEasingCurve(QEasingCurve.Type.OutBack).valueForProgress(k)
            self.opacite = min(1.0, k * 1.6)
        elif t < 0.8:
            self.echelle, self.opacite = 0.9 + 0.1 * min(1.0, (t - 0.2) / 0.05), 1.0
        else:
            self.echelle, self.opacite = 1.0, max(0.0, 1 - (t - 0.8) / 0.2)
        self.update()

    def paintEvent(self, ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setOpacity(self.opacite)
        c = QPointF(self.width() / 2, self.height() / 2)
        p.translate(c)
        p.rotate(-12)
        p.scale(self.echelle, self.echelle)
        r = 34

        bave = QPainterPath()
        for i in range(24):
            a = i * math.tau / 24
            rr = r + (4 if i % 3 == 0 else 1.5)
            pt = QPointF(rr * math.cos(a), rr * math.sin(a))
            bave.moveTo(pt) if i == 0 else bave.lineTo(pt)
        bave.closeSubpath()
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#7a1712"))
        p.drawPath(bave)
        g = QRadialGradient(QPointF(-8, -10), r * 1.4)
        g.setColorAt(0, QColor("#b8352b"))
        g.setColorAt(1, QColor(CIRE))
        p.setBrush(g)
        p.drawEllipse(QPointF(0, 0), r, r)
        p.setPen(QPen(QColor("#c9554c"), 2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QPointF(0, 0), r - 7, r - 7)
        p.setPen(QColor("#f1d9c0"))
        from PyQt6.QtGui import QFontMetricsF
        taille = 10.5
        while taille > 6 and QFontMetricsF(police(taille, True, True)).horizontalAdvance(self.texte) > 2 * r - 14:
            taille -= 0.5
        p.setFont(police(taille, True, True))
        p.drawText(QRectF(-r, -r, 2 * r, 2 * r), Qt.AlignmentFlag.AlignCenter, self.texte)
        p.end()


def apposer_un_sceau(sur: QWidget, texte: str) -> None:
    ""
    fen = sur.window()
    s = Sceau(fen, texte)
    coin = sur.mapTo(fen, QPoint(sur.width() - 70, -20))
    s.move(max(0, coin.x()), max(0, coin.y()))
    s.show()
    s.raise_()
    s.anim.start()


class Flamme(QWidget):
    ""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(26, 54)
        self.t = 0.0
        self.minuterie = QTimer(self)
        self.minuterie.timeout.connect(self._pas)
        self.minuterie.start(60)

    def _pas(self) -> None:
        self.t += 0.06
        self.update()

    def paintEvent(self, ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        p.setPen(Qt.PenStyle.NoPen)
        cire = QLinearGradient(0, 24, 0, 54)
        cire.setColorAt(0, QColor("#efe2c4"))
        cire.setColorAt(1, QColor("#cdb88d"))
        p.setBrush(cire)
        p.drawRoundedRect(QRectF(w / 2 - 5, 24, 10, 30), 2, 2)
        bouge = math.sin(self.t * 3.1) * 0.08 + math.sin(self.t * 7.3) * 0.05
        haut = 22 * (1 + math.sin(self.t * 5.7) * 0.06)
        p.translate(w / 2, 25)
        p.rotate(bouge * 25)
        halo = QRadialGradient(QPointF(0, -8), 16)
        halo.setColorAt(0, QColor(255, 200, 90, 90))
        halo.setColorAt(1, QColor(255, 200, 90, 0))
        p.setBrush(halo)
        p.drawEllipse(QPointF(0, -8), 16, 16)
        flamme = QPainterPath()
        flamme.moveTo(0, 0)
        flamme.cubicTo(-6, -4, -5, -haut * 0.6, 0, -haut)
        flamme.cubicTo(5, -haut * 0.6, 6, -4, 0, 0)
        g = QRadialGradient(QPointF(0, -5), haut * 0.8)
        g.setColorAt(0, QColor("#fff6c8"))
        g.setColorAt(0.5, QColor("#f2ab33"))
        g.setColorAt(1, QColor(200, 80, 10, 40))
        p.setBrush(g)
        p.drawPath(flamme)
        p.end()
