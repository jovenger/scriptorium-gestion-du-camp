
""

















from __future__ import annotations

import json
import os
import re
from pathlib import Path

from . import chemins

RACINE = Path(__file__).resolve().parents[1]
DOSSIER = RACINE / "gestion_du_camp" / "langues"
SOURCE = "fr"
ANGLAIS = "en"
PAR_LE_JEU = "jeu"

NOMS = {"fr": "Français", "en": "English", "de": "Deutsch", "ru": "Русский", "ja": "日本語", "zh_hans": "简体中文", "zh_hant": "繁體中文"}

DU_JEU = {"french": "fr", "english": "en", "german": "de", "japanese": "ja", "chineses": "zh_hans", "chineset": "zh_hant",
          "russian": "ru"}
FICHIER_DU_CHOIX = "langue_du_programme.txt"
LIGNE_DU_JOURNAL = re.compile(r"\[Localization\] - language from profile: '(\w+)'")
LETTRES = re.compile(r"[^\W\d_]")
NOMBRE = re.compile(r"\d+(?:[   ]\d{3})*(?:[.,]\d+)?")
SEPARATEURS = ("\n", " ; ", " · ", " — ", " : ", ", ", " / ", " - ")
ENTRE_PARENTHESES = re.compile(r"(.+?) \((.+)\)", re.S)

PONCTUATION = {"ja": {" : ": "：", " ; ": "；", ", ": "、"}, "zh_hans": {" : ": "：", " ; ": "；", ", ": "，"}, "zh_hant": {" : ": "：", " ; ": "；", ", ": "，"}}

RELEVE = os.environ.get("SCRIPTORIUM_LANGUE_RELEVE")

_langue = SOURCE
_tables: list[dict[str, str]] = []
_souvenirs: dict[str, str] = {}
_vus: set[str] = set()


def table(code: str) -> dict[str, str]:
    try:
        return json.loads((DOSSIER / f"{code}.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def appliquer(code: str) -> None:
    ""
    global _langue, _tables
    _langue = code if code in NOMS else ANGLAIS
    _souvenirs.clear()
    _tables = [] if _langue == SOURCE else [table(c) for c in dict.fromkeys((_langue, ANGLAIS))]


def langue() -> str:
    return _langue


def code_du_jeu(nom: str | None) -> str:
    ""
    return DU_JEU.get(str(nom or "").strip().lower(), ANGLAIS)


def lire_le_choix() -> str:
    ""
    try:
        choix = (chemins.dossier_local() / FICHIER_DU_CHOIX).read_text(encoding="utf-8").strip()
    except OSError:
        return PAR_LE_JEU
    return choix if choix in NOMS else PAR_LE_JEU


def retenir_le_choix(choix: str) -> None:
    d = chemins.dossier_local()
    d.mkdir(parents=True, exist_ok=True)
    (d / FICHIER_DU_CHOIX).write_text(choix, encoding="utf-8")


def langue_du_journal(journal: Path | None = None) -> str | None:
    ""
    try:
        with open(journal or chemins.journal_du_jeu(), "rb") as f:
            debut = f.read(512 * 1024).decode("utf-8", "replace")
    except OSError:
        return None
    m = LIGNE_DU_JOURNAL.search(debut)
    return m.group(1) if m else None


def langue_voulue(du_jeu: str | None = None) -> str:
    ""
    choix = lire_le_choix()
    if choix != PAR_LE_JEU:
        return choix
    return code_du_jeu(du_jeu or langue_du_journal())


def _noter(texte: str) -> None:
    if RELEVE and texte not in _vus and not any(texte in t.values() for t in _tables):
        _vus.add(texte)
        with open(RELEVE, "a", encoding="utf-8") as f:
            f.write(json.dumps(texte, ensure_ascii=False) + "\n")


def _dans_les_tables(texte: str) -> str | None:
    for t in _tables:
        r = t.get(texte)
        if r:
            return r
    return None


def _sans_ses_nombres(texte: str) -> str | None:
    nombres = NOMBRE.findall(texte)
    if not nombres:
        return None
    i = iter(range(len(nombres)))
    r = _dans_les_tables(NOMBRE.sub(lambda _m: "{%d}" % next(i), texte))
    if r is None:
        return None
    try:
        return r.format(*nombres)
    except (IndexError, KeyError, ValueError):
        return None


def _avec_sa_majuscule(texte: str) -> str | None:
    ""
    r = _dans_les_tables(texte[0].lower() + texte[1:]) if texte[0].isupper() else None
    return r[0].upper() + r[1:] if r else None


def _par_morceaux(texte: str) -> str | None:
    m = ENTRE_PARENTHESES.fullmatch(texte)
    if m:
        faits = [_traduire(m.group(1)), _traduire(m.group(2))]
        if faits != [m.group(1), m.group(2)]:
            return f"{faits[0]} ({faits[1]})"
    for sep in SEPARATEURS:
        if sep in texte:
            morceaux = texte.split(sep)
            faits = [_traduire(m) for m in morceaux]
            if faits != morceaux:
                return PONCTUATION.get(_langue, {" : ": ": ", " ; ": "; "}).get(sep, sep).join(faits)
    return None


def _traduire(texte: str) -> str:
    coeur = texte.strip()
    if not LETTRES.search(coeur):
        return texte
    r = _souvenirs.get(coeur)
    if r is None:
        r = _dans_les_tables(coeur) or _sans_ses_nombres(coeur) or _avec_sa_majuscule(coeur) or _par_morceaux(coeur)
        if r is None:
            _noter(coeur)
            r = coeur
        _souvenirs[coeur] = r
    return texte.replace(coeur, r, 1)


def T(texte, *valeurs):
    ""
    if not isinstance(texte, str):
        return texte
    if _langue == SOURCE:
        return texte.format(*valeurs) if valeurs else texte
    if not valeurs:
        return _traduire(texte)
    coeur = texte.strip()
    gabarit = _dans_les_tables(coeur)
    if gabarit is None and LETTRES.search(re.sub(r"\{[^}]*\}", " ", coeur)):
        _noter(coeur)
    vals = [_traduire(v) if isinstance(v, str) else v for v in valeurs]
    try:
        return texte.replace(coeur, gabarit or coeur, 1).format(*vals)
    except (IndexError, KeyError, ValueError):
        return texte.format(*vals)
