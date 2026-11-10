
""





















from __future__ import annotations

import math
import re
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from PyQt6.QtCore import QPointF, QRectF, QSize, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QCursor, QFont, QIcon, QPainter, QPen, QPolygonF
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QHBoxLayout, QLabel, QListWidget, QMenu,
                             QListWidgetItem, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSpinBox)

from noyau import chemins
sys.path.insert(0, str(Path(__file__).resolve().parent))
from aides_des_objets import aide as aide_de_l_objet
from noyau.langue_du_programme import T


JOURNAL = chemins.journal_du_jeu()

IMAGES = Path(__file__).resolve().with_name("images")
MARQUE = "[ScriptoPlan] "


COULEURS = {
    "cabane": "#8b5a2b", "lit_cabane": "#c49a6c", "tente": "#d9d4c7", "dortoir": "#4d7c4d",
    "lit": "#b8a27a", "lit_tente": "#b8a27a", "feu": "#e4572e", "buche": "#7a5230",
    "bains": "#2b7bb9", "baquets": "#5fa8d3", "forge": "#6b6b6b", "forge_du_mod": "#6b6b6b",
    "chasse": "#3c7a3c", "charrette": "#a0522d", "entrainement": "#b91c1c", "ratelier": "#7f1d1d",
    "poste": "#9d4edd", "tombe": "#555555", "croix": "#777777", "caisse": "#8b4513",
    "coffret": "#daa520", "intendant": "#1f4e79", "coursier": "#1f4e79", "lampe": "#f2c14e",
    "auberge": "#b07d48", "alchimie": "#7c3aed", "piece_du_mod": "#999999",
}
NOMS = {
    "cabane": "cabane d'Henry", "tente": "tente", "dortoir": "tente verte", "feu": "feu",
    "bains": "bains", "forge": "forge", "chasse": "chasse", "charrette": "charrette",
    "entrainement": "pantins", "poste": "poste", "baquets": "bassines", "caisse": "caisse",
    "intendant": "intendant", "coursier": "coursier",
}







ENTREES = {"tente": math.pi / 2, "dortoir": math.pi / 2}



SENS_RATELIER = -4.5
SENS_PANTIN = 1.0
TIR_CIBLE, TIR_DISQUE_RZ = (0.3951, -0.1147), 1.2741
TIR_DISTANCES = {"cible": 10, "cible_pres": 7, "cible_moyen": 10, "cible_loin": 15, "cible_tres_loin": 25}


SENS_CIBLE = 3.0





PLACES_MARCHANDES = ("vendeur", "pupitre")
_places_de_vente: dict | None = None


def places_de_vente(cle: str) -> list[tuple[float, float, float]]:
    ""
    global _places_de_vente
    if _places_de_vente is None:
        _places_de_vente = {}
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("editeur_palette_places", Path(__file__).with_name("palette.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            for _, objets in mod.catalogue():
                for o in objets:
                    pl = [(float(x["x"]), float(x["y"]), float(x.get("rz", 0.0))) for x in o["pieces"]
                          if x.get("so") in PLACES_MARCHANDES]
                    if pl:
                        _places_de_vente[o["cle"]] = pl
        except Exception:
            pass
    return _places_de_vente.get(cle, [])


def marchand_sur_le_plan(o: dict, dt: float = 0.0, a0: float | None = None, c0: float | None = None):
    ""
    a0 = o["avant"] if a0 is None else a0
    c0 = o["cote"] if c0 is None else c0
    th = o["angle"] + dt
    out = []
    for x, y, rz in places_de_vente(o["cle"]):
        pa, pc_ = tourner(x, y, th)
        ga, gc = tourner(-math.sin(rz) * 1.5, math.cos(rz) * 1.5, th)
        out.append(((a0 + pa, c0 + pc_), (a0 + pa + ga, c0 + pc_ + gc)))
    return out





CLIENT_DEVANT = 2.4


RAYON_PERSONNE = 0.35


def client_sur_le_plan(o: dict, dt: float = 0.0, a0: float | None = None, c0: float | None = None):
    ""

    a0 = o["avant"] if a0 is None else a0
    c0 = o["cote"] if c0 is None else c0
    th = o["angle"] + dt
    if o["cle"] == "rond_client":
        ga, gc = tourner(0.0, 1.5, th)
        return [((a0, c0), (a0 + ga, c0 + gc))]
    if o["cle"] == "rond_marchand":
        return []
    out = []
    for x, y, rz in places_de_vente(o["cle"]):
        ux, uy = -math.sin(rz), math.cos(rz)
        if abs(rz) < 1e-6:
            continue
        cx, cy = x + ux * CLIENT_DEVANT, y + uy * CLIENT_DEVANT
        pa, pc_ = tourner(cx, cy, th)
        ga, gc = tourner(-ux * 1.2, -uy * 1.2, th)
        out.append(((a0 + pa, c0 + pc_), (a0 + pa + ga, c0 + pc_ + gc)))
    return out


def sens_de_l_objet(o: dict, dt: float = 0.0, a0: float | None = None, c0: float | None = None):
    ""

    a0 = o["avant"] if a0 is None else a0
    c0 = o["cote"] if c0 is None else c0
    th = o["angle"] + dt
    cle = o["cle"]
    if cle == "ratelier":
        fa, fc = tourner(SENS_RATELIER, 0.0, th)
        return (a0, c0), (a0 + fa, c0 + fc), False
    if cle == "mannequin_paille":

        fa, fc = tourner(0.0, 2.0 * SENS_PANTIN, th)
        return (a0, c0), (a0 + fa, c0 + fc), False
    if cle in TIR_DISTANCES:
        t = o.get("tir")
        xa, xc = disque_sur_le_plan(o, dt, a0, c0)
        if t:


            pa, pc_ = t["poste"]
            ra, rc = tourner(pa - o["avant"], pc_ - o["cote"], dt)
            return (xa, xc), (a0 + ra, c0 + rc), True

        face = th + TIR_DISQUE_RZ - math.pi / 2
        ua, uc = math.cos(face), math.sin(face)
        return (xa + ua * SENS_CIBLE, xc + uc * SENS_CIBLE), (xa, xc), False
    return None


def disque_sur_le_plan(o: dict, dt: float = 0.0, a0: float | None = None, c0: float | None = None):
    ""
    a0 = o["avant"] if a0 is None else a0
    c0 = o["cote"] if c0 is None else c0
    t = o.get("tir")
    if t:
        xa0, xc0 = t["disque"]
        qa, qc = tourner(xa0 - o["avant"], xc0 - o["cote"], dt)
        return a0 + qa, c0 + qc
    da, dc = tourner(TIR_CIBLE[0], TIR_CIBLE[1], o["angle"] + dt)
    return a0 + da, c0 + dc



def prix_du_camp() -> tuple[dict[str, int], int]:
    ""
    import re
    try:
        t = (Path(__file__).resolve().parents[1] / "prix_du_camp" / "prix_du_camp.lua").read_text(encoding="utf-8")
        bloc = t[t.index("pr.PRIX = {"):]
        bloc = bloc[:bloc.index("\n\t}")]
        prix = {k: int(v) for k, v in re.findall(r"\b([a-z_0-9]+) = (\d+)", bloc)}
        decor = int(re.search(r"pr\.DECOR = (\d+)", t).group(1))
        return prix, decor
    except (OSError, ValueError, AttributeError):
        return {}, 0


def prix_d_un_objet(cle: str) -> int:
    prix, decor = prix_du_camp()
    return prix.get(cle, decor if cle.startswith("decor_") else 0)


def lire_le_releve(depuis: int = 0, complet: bool = False) -> dict | None:
    ""

    try:
        with open(JOURNAL, "rb") as f:
            f.seek(depuis)
            brut = f.read().decode("utf-8", "replace")
    except OSError:
        return None
    lignes = [l.split(MARQUE, 1)[1].strip() for l in brut.splitlines() if MARQUE in l]
    fin = max((i for i, l in enumerate(lignes) if l.startswith("fin|")), default=None)
    if fin is None:
        return None
    debut = max((i for i, l in enumerate(lignes[:fin]) if l.startswith("debut|")), default=None)
    if debut is None:
        return None
    if complet and "changements" in lignes[debut].split("|")[5:]:
        entiers = [i for i, l in enumerate(lignes[:fin]) if l.startswith("debut|") and "changements" not in l.split("|")[5:]]
        if not entiers:
            return None
        debut = entiers[-1]
        fin = min((i for i, l in enumerate(lignes) if i > debut and l.startswith("fin|")), default=None)
        if fin is None:
            return None
    d = lignes[debut].split("|")
    releve = {"origine": (float(d[1]), float(d[2])), "cap": float(d[4]), "places": {}, "pieces": [],
              "objets": {}, "installations": {}, "sans_camp": "sans_camp" in d[5:],

              "changements": "changements" in d[5:], "partis": []}
    for l in lignes[debut + 1:fin]:
        c = l.split("|")
        if c[0] == "p" and len(c) >= 5:
            releve["places"][c[1]] = (float(c[2]), float(c[3]), float(c[4]))
        elif c[0] == "i" and len(c) >= 7:
            releve.setdefault("installations", {})[c[1]] = {"avant": float(c[2]), "cote": float(c[3]),
                                                          "rayon": float(c[4]), "etat": c[5], "genre": c[6]}
        elif c[0] == "o" and len(c) >= 7:
            releve["objets"][int(c[1])] = {"cle": c[2], "avant": float(c[3]), "cote": float(c[4]),
                                           "angle": float(c[5]), "pose": c[6] == "1",
                                           "reserve": RESERVE_LUE.get(c[7], c[7]) if len(c) > 7 else None}
        elif c[0] == "t" and len(c) >= 6:

            n_ = int(c[1]) if c[1].isdigit() else c[1]
            releve.setdefault("tir", {})[n_] = {"poste": (float(c[2]), float(c[3])), "disque": (float(c[4]), float(c[5]))}
        elif c[0] == "x" and len(c) >= 4:
            releve["partis"].append((c[1], round(float(c[2]), 1), round(float(c[3]), 1)))

        elif c[0] == "zt" and len(c) >= 5:
            releve.setdefault("zones_types", {})[c[1]] = {"rayon": float(c[2]), "libre": c[3] == "1",
                                                         "objets": [x for x in c[4].split("+") if x]}
        elif c[0] == "z" and len(c) >= 5:
            releve.setdefault("zones", {})[c[1]] = {"avant": float(c[2]), "cote": float(c[3]), "rayon": float(c[4])}
        elif c[0] == "r" and len(c) >= 4:
            releve.setdefault("ronde", []).append((int(c[1]), float(c[2]), float(c[3])))
        elif c[0] == "rr" and len(c) >= 3:
            releve["ronde_reglages"] = (int(float(c[1])), int(float(c[2])))
        elif c[0] == "e" and len(c) >= 10:
            releve["pieces"].append({"famille": c[1], "nom": c[2], "x": float(c[3]), "y": float(c[4]),
                                     "a": float(c[5]), "mn": (float(c[6]), float(c[7])),
                                     "mx": (float(c[8]), float(c[9]))})
    releve["ronde"] = [(a, c) for _, a, c in sorted(releve.get("ronde", []))]
    for n_, t_ in releve.get("tir", {}).items():
        if n_ in releve["objets"]:
            releve["objets"][n_]["tir"] = t_
    return releve





MARQUE_VEG = "[ScriptoVeg] "
GARDE_VEG = chemins.dossier_local() / "vegetation_du_camp.json"
COULEURS_VEG = {"f": ("#2e6b2e", 150, "forêt"), "b": ("#4f9a3a", 140, "buissons"), "h": ("#a9c25a", 140, "herbes hautes"),
                "c": ("#d9b44a", 150, "champ (blé)"), "d": ("#c8c48a", 80, "herbe sèche"), "s": ("#a88b62", 80, "terre"),
                "m": ("#7a5a3a", 110, "boue"), "w": ("#4a7ec2", 150, "eau"), "r": ("#c9b38a", 130, "chemin"),
                "k": ("#8a8a8a", 120, "roche"), "a": ("#e2d29a", 100, "sable")}


def lire_la_vegetation(depuis: int = 0) -> dict | None:
    ""
    try:
        with open(JOURNAL, "rb") as f:
            f.seek(depuis)
            brut = f.read().decode("utf-8", "replace")
    except OSError:
        return None
    lignes = [l.split(MARQUE_VEG, 1)[1].strip() for l in brut.splitlines() if MARQUE_VEG in l]
    debut = max((i for i, l in enumerate(lignes) if l.startswith("debut|")), default=None)
    if debut is None:
        return None
    d = lignes[debut].split("|")
    v = {"x": float(d[1]), "y": float(d[2]), "cap": float(d[3]), "pas": float(d[4]), "rayon": float(d[5]),
         "lignes": {}, "fini": False, "inconnues": []}
    for l in lignes[debut + 1:]:
        c = l.split("|")
        if c[0] == "l" and len(c) >= 3:
            v["lignes"][int(c[1])] = c[2]
        elif c[0] == "fin":
            v["fini"] = True
            v["inconnues"] = [x for x in (c[2] if len(c) > 2 else "").split("+") if x]
            break
    v["n"] = int(round(2 * v["rayon"] / v["pas"])) + 1
    return v


def cle_de_vegetation(x: float, y: float, cap: float) -> str:
    return f"{x:.0f}|{y:.0f}|{cap:.2f}"


def garder_la_vegetation(v: dict) -> None:
    import json
    try:
        tout = json.loads(GARDE_VEG.read_text(encoding="utf-8")) if GARDE_VEG.is_file() else {}
    except (OSError, ValueError):
        tout = {}
    w = dict(v)
    w["lignes"] = {str(k): l for k, l in v["lignes"].items()}
    tout[cle_de_vegetation(v["x"], v["y"], v["cap"])] = w
    GARDE_VEG.parent.mkdir(parents=True, exist_ok=True)
    GARDE_VEG.write_text(json.dumps(tout, ensure_ascii=False), encoding="utf-8")


def vegetation_gardee(releve: dict) -> dict | None:
    ""
    import json
    try:
        tout = json.loads(GARDE_VEG.read_text(encoding="utf-8")) if GARDE_VEG.is_file() else {}
    except (OSError, ValueError):
        return None
    ox, oy = releve["origine"]
    for v in tout.values():
        if math.hypot(v["x"] - ox, v["y"] - oy) <= 2.0 and abs(v["cap"] - releve["cap"]) <= 0.02:
            v["lignes"] = {int(k): l for k, l in v["lignes"].items()}
            return v
    return None


def cle_de_piece(p: dict) -> tuple:
    return (p["nom"], round(p["x"], 1), round(p["y"], 1))


def fusionner_le_decor(decor: dict, releve: dict) -> dict:
    ""

    if not releve.get("changements"):
        decor = {cle_de_piece(p): p for p in releve["pieces"]}
    else:
        for k in releve.get("partis", []):
            decor.pop(k, None)
        for p in releve["pieces"]:
            decor[cle_de_piece(p)] = p
    releve["pieces"] = list(decor.values())
    return decor


def vers_le_plan(releve: dict, x: float, y: float) -> tuple[float, float]:
    ""
    ox, oy = releve["origine"]
    ca, sa = math.cos(releve["cap"]), math.sin(releve["cap"])
    dx, dy = x - ox, y - oy
    return ca * dx + sa * dy, -sa * dx + ca * dy


def coins(piece: dict) -> list[tuple[float, float]]:
    ""
    (x0, y0), (x1, y1) = piece["mn"], piece["mx"]
    if abs(x1 - x0) < 0.05 and abs(y1 - y0) < 0.05:
        x0, y0, x1, y1 = -0.25, -0.25, 0.25, 0.25
    c, s = math.cos(piece["a"]), math.sin(piece["a"])
    return [(piece["x"] + c * lx - s * ly, piece["y"] + s * lx + c * ly)
            for lx, ly in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]






COUVRANTS = re.compile(r"^tente_|^cabane_|^auvent_|^abri_|^mini_tente|^tente$|decor_tent_with|decor_canopy")
RONDES = re.compile(r"ronde|yourte|^tente_henry|^tente_intendant|^mini_tente")
ABRI_ROND = "ScriptoBain_abri"


def contour(piece: dict, ronde: bool = False) -> list[tuple[float, float]]:
    ""

    if not ronde:
        return coins(piece)
    (x0, y0), (x1, y1) = piece["mn"], piece["mx"]
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, abs(x1 - x0) / 2, abs(y1 - y0) / 2
    c, s_ = math.cos(piece["a"]), math.sin(piece["a"])
    pts = []
    for i in range(24):
        t = i * math.pi / 12
        lx, ly = cx + rx * math.cos(t), cy + ry * math.sin(t)
        pts.append((piece["x"] + c * lx - s_ * ly, piece["y"] + s_ * lx + c * ly))
    return pts


def numero_d_ajout(nom: str) -> int | None:
    ""
    m = re.match(r"ScriptoEditeur_(\d+)_", nom)
    return int(m.group(1)) if m else None


def tourner(a: float, c: float, theta: float) -> tuple[float, float]:
    ""

    ct, st = math.cos(theta), math.sin(theta)
    return a * ct - c * st, a * st + c * ct


NOMS_DES_PLACES = {
    "auberge": "auberge", "des": "table de dés", "des2": "2ᵉ table de dés", "cuisine": "coin cuisine",
    "tonneau": "tonneau de vin", "banc": "banc", "charrette": "charrette", "feu1": "feu 1", "feu2": "feu 2",
    "feu3": "feu 3", "feu4": "feu 4", "forge": "forge", "chasse": "chasse", "alchimie": "alchimie",
    "baquets": "bassines", "pisser": "feuillée", "verte1": "tente du Directeur", "verte2": "tente du forgeron",
    "verte3": "tente du coursier", "verte4": "tente des femmes", "bains": "bains", "arene": "arène",
    "entrainement": "entraînement", "fleches": "établi à flèches", "coursier": "coursier",
}




INSTALLATIONS_POSABLES = ["tonneau", "banc", "cuisine", "pisser", "arene", "entrainement", "fleches", "baquets"]







ORGANISATION = [
    ("Henry et le Directeur", ["tente_henry_vide", "coffret_banque",
                              "mini_tente", "tente_intendant", "bureau_directeur", "meule", "baquet", "point_d_eau", "prie_dieu", "fumoir", "sechoir"]),
    ("Tentes et lits (à réserver à qui tu veux)",
     ["tente_hommes", "tente_carree_verte", "*Tentes", "lit", "lit_haut", "lit_double", "lit_banc"]),
    ("Artisans : postes et ateliers",
     ["place:forge", "place:bains", "place:coursier", "poste_de_chasse", "etal_cueillette", "decor_cart_with_water",
      "decor_stash_industriall_with_firewood", "pupitre_coursier", "caisse_atelier", "atelier_armurier", "porte_armure",
      "coin_boucher",

      "ligne_des_chevaux"]),
    ("Artisans : vente et paiement",
     ["etal_taverne", "etal_jardiniers", "etal_bucheron", "etal_chasseurs", "comptoir_bains", "etal_vivandiere"]),
    ("Potagers", ["potager_petit", "potager_moyen", "potager_grand"]),


    ("Entraînement", ["ratelier", "mannequin_paille", "cible", "ratelier_camp", "ratelier_garde", "hallebardes", "haches"]),

    ("Justice du camp", ["pilori"]),

    ("Défense du camp", ["tour_de_guet", "palissade", "porte_palissade", "pieux", "brasero"]),
    ("Feu, cuisine, boisson", ["feu_camp", "feu_de_chambree", "*Feu, cuisine, boisson"]),
    ("S'asseoir et manger", ["*S'asseoir et manger"]),
    ("Installations et loisirs", ["place:des", "place:des2"] + ["place:" + n for n in INSTALLATIONS_POSABLES]),

    ("Chevaux et bêtes", ["abreuvoir", "chariot_couvert", "chariot_a_bancs", "chariot_de_foin"]),

    ("L'ordre du camp", ["banniere", "pavois", "pavois_b", "pavois_sur_pied", "latrines"]),
    ("Ranger", ["coffre"]),
    ("Lumière", ["*Lumière"]),
]
CACHES = {"rond_marchand", "rond_client",

          "cible_pres", "cible_moyen", "cible_loin", "cible_tres_loin",


          "intendant",


          "tente_henry", "cabane_henry", "cabane_henry_vide"}

REFUS_DE_POSE = {
    "directeur_pas_engage": "La tente du Directeur : engage d'abord le Directeur (onglet Embauche, Artisans) ; il la "
                            "pose lui-même, avec son lit.",
    "deja": "Il n'y en a qu'une : elle est déjà au camp.",


    "inconnu": "Cet objet n'est pas connu du mod installé : mettez le mod à jour (le programme et le mod doivent être de la même version).",
    "pas_de_camp": "Le camp n'est pas dressé : rien n'est posé.",
    "pas_pose": "Le jeu n'a pas pu poser l'objet à cette place : essayez un peu plus loin.",
    "a_acheter": "Cette installation s'achète d'abord : page « Construire ».",

    "pose_ta_tente_d_abord": "Il n'y a pas encore de camp : pose d'abord ta tente.",
    "pas_de_mod": "Le mod ne répond pas encore : attendez quelques secondes, puis recommencez.",
    "pas_de_construction_libre": "La construction du camp n'est pas prête dans le mod : rechargez la partie.",
    "sans_repere": "Le camp n'a pas pu se repérer ici : essayez un autre endroit.",
    "rate": "Le jeu n'a pas pu le faire : réessayez.",
}
TROP_PRES = "Trop près d'une tente, d'un feu ou de la cuisine : les latrines se posent à 20 m au moins."
TROP_EN_PENTE = "Le sol est trop en pente ici ({0}°) : on ne dresse pas un camp sur une telle pente. Choisissez un endroit plus plat."
PAS_ASSEZ = "Le coffre du camp n'a pas assez : il faut {0} gros. Rien n'est posé."
REFUSE = "Le jeu a refusé : {0}"


def refus_en_clair(rep: str | None) -> str | None:
    ""

    r = (rep or "").strip().replace(" ", "_")
    if not r or r.isdigit() or r == "ok":
        return None
    if r in REFUS_DE_POSE:
        return T(REFUS_DE_POSE[r])
    m = re.fullmatch(r"pente_(\d+)", r)
    if m:
        return T(TROP_EN_PENTE, m.group(1))
    if r.startswith("trop_pres"):
        return T(TROP_PRES)
    m = re.fullmatch(r"coffre_(\d+)", r)
    if m:
        return T(PAS_ASSEZ, m.group(1))
    return T(REFUSE, r.replace("_", " "))

NOMS_AMENAGEMENT = {
    "place:forge": "Forge (le forgeron)", "place:bains": "Bains et lavoir (les dames des bains)",
    "place:coursier": "Poste du coursier", "place:des": "Table de dés", "place:des2": "2ᵉ table de dés",
    "poste_de_chasse": "Poste de chasse (l'établi des chasseurs)",
    "etal_cueillette": "Étal du potager (l'établi du jardinier)",
    "decor_cart_with_water": "Charrette à eau (l'établi du porteur d'eau)",
    "decor_stash_industriall_with_firewood": "Réserve de bois (l'établi du bûcheron)",
    "tente_carree_verte": "Grande tente carrée verte", "tente_hommes": "Tente des hommes (4 lits)",
    "lit": "Lit bas", "caisse_atelier": "Caisse d'atelier (à réserver à un métier)",
    "pupitre_coursier": "Pupitre du coursier (il y attend les commandes)",
    "bureau_directeur": "Bureau du Directeur (il y travaille entre ses tournées)",
    "ligne_des_chevaux": "Ligne des chevaux (le poste du palefrenier)",

    "tente_henry_vide": "Ta tente, vide (à aménager)",
    "cabane_henry_vide": "Ta cabane, vide (à aménager)",
    "coffret_banque": "Coffret : Banque / Scriptorium",
    "mini_tente": "Tente miniature : Gestion du camp",
    "meule": "Meule à aiguiser (affûter ses armes)",
    "baquet": "Baquet pour se laver",
    "point_d_eau": "Point d'eau (se laver, laver son linge)",
    "prie_dieu": "Prie-Dieu (prier)",
    "fumoir": "Fumoir (fumer la viande)",
    "sechoir": "Séchoir (sécher viande, fruits, herbes)",
    "etal_jardiniers": "Étal du jardinier (vente des légumes)",
    "etal_bucheron": "Étal du bûcheron (vente du bois et du charbon)",
    "etal_chasseurs": "Étal des chasseurs (vente du gibier et des peaux)",
    "comptoir_bains": "Comptoir de la Dame des bains (on la paie ici)",
    "etal_taverne": "Étal du tavernier (bière et vin au verre)",
    "tonneau_vin": "Tonneau de vin (réserve-le à la taverne : on y sert le vin payé)",
    "tonneau_biere": "Tonneau de bière (réserve-le à la taverne : on y tire la bière payée)",
    "rond_marchand": "Rond du marchand (à réserver à un métier)",
    "rond_client": "Rond du client (à réserver au même métier)",
    "ratelier": "Râtelier d'entraînement (jusqu'à 3 duos à l'épée de bois)",
    "mannequin_paille": "Mannequin de paille (un homme le frappe à la hache)",
    "cible": "Cible de tir (arc ou arbalète)",
    "potager_petit": "Petit potager (3,5 × 3,5 m)", "potager_moyen": "Potager moyen (5 × 5 m)",
    "potager_grand": "Grand potager (7 × 7 m), avec son épouvantail",

    "place:tonneau": "Installation : tonneau de vin du camp", "place:banc": "Installation : banc du camp",
    "place:cuisine": "Installation : coin cuisine du camp", "place:pisser": "Installation : feuillée",
    "place:arene": "Installation : arène du pugilat", "place:entrainement": "Installation : terrain d'entraînement",
    "place:fleches": "Installation : établi à flèches", "place:baquets": "Installation : bassines",
}





UNIQUES = {"etal_vivandiere", "coin_boucher", "etal_taverne", "comptoir_bains", "pupitre_coursier", "atelier_armurier",
           "etal_bucheron", "bureau_directeur"}
DEJA_AU_CAMP = " — déjà au camp"


def organiser(cat: list) -> list:
    ""

    par_cle, par_rub = {}, {}
    for titre, objets in cat:
        par_rub[titre] = objets
        for o in objets:
            par_cle.setdefault(o["cle"], o)
    for nom in INSTALLATIONS_POSABLES + ["forge", "bains", "coursier", "des", "des2"]:
        par_cle.setdefault("place:" + nom, {"cle": "place:" + nom, "nom": NOMS_DES_PLACES.get(nom, nom).capitalize(),
                                            "pieces": []})
    vus, out = set(), []

    def prendre(cle):
        if cle in vus or cle not in par_cle:
            return None
        vus.add(cle)
        o = dict(par_cle[cle])
        o["nom"] = NOMS_AMENAGEMENT.get(cle, o["nom"])
        return o

    for titre, cles in ORGANISATION:
        objets = []
        for c in cles:
            for k in ([o["cle"] for o in par_rub.get(c[1:], [])] if c.startswith("*") else [c]):
                o = prendre(k)
                if o is not None:
                    objets.append(o)
        if objets:
            out.append((titre, objets))

    vus.update(CACHES)
    decor = [o for o in (prendre(x["cle"]) for x in par_rub.get("Décor du jeu", [])) if o is not None]
    autres = [o for o in (prendre(k) for k in par_cle) if o is not None]
    if decor:
        out.append(("Décor du jeu", decor))
    if autres:
        out.append(("Autres", autres))
    return out




RESERVES = [("henry", "Henry"), ("femmes", "les dames des bains"), ("forgeron", "le forgeron"),
            ("coursier", "le coursier"), ("intendant", "le Directeur"), ("chasseurs", "les chasseurs"),
            ("jardiniers", "les jardiniers"), ("eau", "le porteur d'eau"), ("bois", "le bûcheron"),
            ("taverne", "la taverne"),

            ("armurier", "l'armurier"),

            ("compagnons", "les compagnons"),

            ("colonel", "le colonel")]
RESERVE_LUE = {"0": None, "1": "henry"}

A_QUI = {"henry": "à Henry", "femmes": "aux dames des bains", "forgeron": "au forgeron", "coursier": "au coursier",
         "intendant": "au Directeur", "chasseurs": "aux chasseurs", "jardiniers": "aux jardiniers",
         "eau": "au porteur d'eau", "bois": "au bûcheron", "taverne": "à la taverne", "compagnons": "aux compagnons",
         "armurier": "à l'armurier", "colonel": "au colonel"}

LEURS_LITS = {"femmes": " Leurs lits sont à elles : elles y dormiront.",
              "chasseurs": " Leurs lits sont à eux : ils y dormiront.",
              "jardiniers": " Leurs lits sont à eux : ils y dormiront.",
              "taverne": " Ses lits sont au tavernier : il y dormira.",
              "armurier": " Ses lits sont à l'armurier : il y dormira.",
              "compagnons": " Leurs lits sont à eux : ils y dormiront, et nulle part ailleurs."}


def reserve_a(code) -> str:
    ""
    return A_QUI.get(code, T("à {0}", dict(RESERVES).get(code, code)))
COULEUR_RESERVE = {"henry": "#c9a24d"}

METIERS = {"forge": "le forgeron", "bains": "les dames des bains", "coursier": "le coursier"}



PIECES_DES_INSTALLATIONS = {
    "des": ("ScriptoPoste_des_",), "des2": ("ScriptoPoste_des2_",), "cuisine": ("ScriptoPoste_cuisine_",),
    "tonneau": ("ScriptoPoste_tonneau_",), "banc": ("ScriptoPoste_banc_",), "pisser": ("ScriptoPoste_pisser_",),
    "arene": ("ScriptoPoste_combat_",), "entrainement": ("ScriptoPoste_exercice_",),
    "fleches": ("ScriptoPoste_fleches_",), "bains": ("ScriptoBain",), "baquets": ("ScriptoBaquet",),


    "forge": ("ScriptoForge",), "coursier": ("ScriptoCoursier",), "auberge": (), "chasse": (),
    "charrette": (), "alchimie": (), "feu1": (), "feu2": (), "feu3": (), "feu4": (),
    "verte1": ("ScriptoDortoir_",), "verte2": ("ScriptoDortoir_",), "verte3": ("ScriptoDortoir_",),
    "verte4": ("ScriptoDortoir_",),
}


def installations_presentes(r: dict, en_cours: set | None = None) -> dict:
    ""



    toutes = r.get("toutes_installations") or r.get("installations", {})
    pieces = [(pc["nom"], vers_le_plan(r, pc["x"], pc["y"])) for pc in r.get("pieces", []) if pc["famille"] != "ajout"]



    occupees = set()
    for n, (a, c) in pieces:
        meilleure, dmin = None, None
        for nom, i in toutes.items():
            tetes = PIECES_DES_INSTALLATIONS.get(nom, ())
            if i["etat"] == "retire" or not tetes or not n.startswith(tetes):
                continue
            d = (a - i["avant"]) ** 2 + (c - i["cote"]) ** 2
            if d <= (max(1.5, i["rayon"]) + 5.0) ** 2 and (dmin is None or d < dmin):
                meilleure, dmin = nom, d
        if meilleure is not None:
            occupees.add(meilleure)
    garde = {}
    for nom, i in toutes.items():
        if i["etat"] != "retire" and (nom in occupees or nom in (en_cours or set())):
            garde[nom] = i
    r = dict(r)
    r["toutes_installations"] = toutes
    r["installations"] = garde
    return r


CADRAGE_MAX = 250.0


class Plan(QWidget):
    ""










    def __init__(self, fenetre) -> None:
        super().__init__()
        self.fenetre = fenetre
        self.releve: dict | None = None
        self.cimetiere = False

        self.ecritures = True


        self.calque: str | None = None
        self.cles_du_calque: set = set()

        self.vegetation: dict | None = None
        self.montrer_vegetation = True
        self._image_veg = None
        self.choix: set = set()
        self.geste: dict | None = None
        self._mode = None
        self._depart = None
        self._cadre = None
        self.zoom: float | None = None
        self.centre_vue = (0.0, 0.0)
        self.setMinimumSize(900, 800)
        self.setMouseTracking(False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.minuterie = QTimer(self)
        self.minuterie.setSingleShot(True)
        self.minuterie.timeout.connect(self._fin_de_molette)

        self.point_de_tir = None
        self._souris: QPointF | None = None

    def commencer_point_de_tir(self, n) -> None:
        self.point_de_tir = n
        self._souris = None
        self.setMouseTracking(True)
        self.fenetre.etat.setText(T("Point de tir : bouge la souris, puis clic gauche là d'où les hommes doivent tirer. "
                                  "La cible se tournera vers eux. Clic droit ou Échap : annuler."))
        self.update()

    def finir_point_de_tir(self) -> None:
        self.point_de_tir = None
        self._souris = None
        self.setMouseTracking(False)
        self.update()


    @property
    def choisi(self) -> int | None:
        objs = [k[1] for k in self.choix if k[0] == "o"]
        return objs[0] if len(self.choix) == 1 and objs else None

    @choisi.setter
    def choisi(self, n: int | None) -> None:
        self.choix = {("o", n)} if n is not None else set()

    def poser(self, releve: dict | None) -> None:
        if releve is not None:
            releve = installations_presentes(releve, getattr(self.fenetre, "en_cours", set()))
        self.releve = releve
        objs = (releve or {}).get("objets", {})
        places = (releve or {}).get("installations", {})
        self.choix = {k for k in self.choix if (k[0] == "o" and k[1] in objs) or (k[0] == "i" and k[1] in places)}
        self.geste = None
        self.update()

    def poser_la_vegetation(self, v: dict | None) -> None:
        self.vegetation = v
        self._image_veg = None
        if v:
            from PyQt6.QtGui import QImage
            n = v["n"]
            img = QImage(n, n, QImage.Format.Format_ARGB32)
            img.fill(QColor(0, 0, 0, 0))
            for k, ligne in v["lignes"].items():
                for l_, lettre in enumerate(ligne):
                    c = COULEURS_VEG.get(lettre)
                    if c is None:
                        continue
                    coul = QColor(c[0])
                    coul.setAlpha(c[1])

                    img.setPixelColor(n - 1 - l_, n - 1 - k, coul)
            self._image_veg = img
        self.update()

    def _dessiner_la_vegetation(self, p) -> None:
        v = self.vegetation
        if not self.montrer_vegetation or v is None or self._image_veg is None or not self.releve:
            return

        da, dc = vers_le_plan(self.releve, v["x"], v["y"])
        demi = v["rayon"] + v["pas"] / 2
        haut_gauche = self._ecran(da + demi, dc + demi)
        bas_droit = self._ecran(da - demi, dc - demi)
        p.save()
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        p.drawImage(QRectF(haut_gauche, bas_droit), self._image_veg)
        p.restore()

    def recadrer(self) -> None:
        self.zoom = None
        self.update()


    def _ecran(self, avant: float, cote: float) -> QPointF:
        ca, cc = self.centre_vue
        return QPointF(self.width() / 2 - (cote - cc) * self.zoom, self.height() / 2 - (avant - ca) * self.zoom)

    def _plan(self, pt: QPointF) -> tuple[float, float]:
        ca, cc = self.centre_vue
        return ca + (self.height() / 2 - pt.y()) / self.zoom, cc + (self.width() / 2 - pt.x()) / self.zoom

    def _ajuster(self, r: dict) -> None:
        ""
        if self.zoom is not None:
            return
        tout = [vers_le_plan(r, x, y) for pc in r["pieces"] for x, y in coins(pc)]
        tout += [(a, c) for a, c, _ in r["places"].values()]
        tout += [(o["avant"], o["cote"]) for o in r.get("objets", {}).values()]
        tout += [(0.0, 0.0)]


        tout = [(a, c) for a, c in tout if math.hypot(a, c) <= CADRAGE_MAX] or [(0.0, 0.0)]
        amin, amax = min(a for a, _ in tout) - 4, max(a for a, _ in tout) + 4
        cmin, cmax = min(c for _, c in tout) - 4, max(c for _, c in tout) + 4
        marge = 40
        self.zoom = max(0.5, min((self.width() - 2 * marge) / (cmax - cmin), (self.height() - 2 * marge) / (amax - amin)))
        self.centre_vue = ((amin + amax) / 2, (cmin + cmax) / 2)


    def _centre(self, k) -> tuple[float, float]:
        r = self.releve or {}
        if k[0] == "o":
            o = r["objets"][k[1]]
            return o["avant"], o["cote"]
        i = r["installations"][k[1]]
        return i["avant"], i["cote"]

    def _pivot(self) -> tuple[float, float]:
        cs = [self._centre(k) for k in self.choix]
        return (sum(a for a, _ in cs) / len(cs), sum(c for _, c in cs) / len(cs)) if cs else (0.0, 0.0)

    def nouvelle_place(self, k, g: dict | None = None) -> tuple[float, float, float]:
        ""
        g = g if g is not None else self.geste
        a, c = self._centre(k)
        if not g or k not in self.choix:
            return a, c, 0.0
        pa, pc_ = self._pivot()
        ra, rc = tourner(a - pa, c - pc_, g["dt"])
        return pa + ra + g["da"], pc_ + rc + g["dc"], g["dt"]

    def _formes_des_ajouts(self, r: dict) -> dict:
        ""

        if getattr(self, "_ajouts_de", None) is not self.releve:
            self._ajouts_de = self.releve
            objets = (self.releve or {}).get("objets", {})
            brutes: dict = {}
            for pc in (self.releve or {}).get("pieces", []):
                if pc["famille"] != "ajout":
                    continue
                if not (abs(pc["mx"][0] - pc["mn"][0]) > 0.05 or abs(pc["mx"][1] - pc["mn"][1]) > 0.05):
                    continue
                k = numero_d_ajout(pc["nom"])
                if k is not None:
                    brutes.setdefault(k, []).append(pc)


            for k, pcs in list(brutes.items()):
                sans_ancre = [q for q in pcs if not str(q["nom"]).endswith("_ancre")]
                if sans_ancre:
                    brutes[k] = sans_ancre
            index, toits = {}, {}
            for k, pcs in brutes.items():
                cle = str(objets.get(k, {}).get("cle", ""))
                toit = None
                if COUVRANTS.search(cle):
                    aires = [abs(q["mx"][0] - q["mn"][0]) * abs(q["mx"][1] - q["mn"][1]) for q in pcs]
                    toit = aires.index(max(aires))
                ronde = bool(RONDES.search(cle))
                index[k] = [[vers_le_plan(self.releve, x, y) for x, y in contour(q, ronde and i == toit)]
                            for i, q in enumerate(pcs)]
                if toit is not None:
                    toits[k] = toit
            self._ajouts, self._toits = index, toits
        return self._ajouts

    def _formes(self, r: dict, n: int) -> list[list[tuple[float, float]]]:
        o = r["objets"][n]
        formes = list(self._formes_des_ajouts(r).get(n, []))
        if not formes:
            formes = [[(o["avant"] + a, o["cote"] + c) for a, c in ((-.3, -.3), (.3, -.3), (.3, .3), (-.3, .3))]]
        k = ("o", n)
        if self.geste and k in self.choix:
            na, nc, dt = self.nouvelle_place(k)
            formes = [[tuple(v + d for v, d in zip(tourner(a - o["avant"], c - o["cote"], dt), (na, nc)))
                       for a, c in f] for f in formes]
        return formes

    def dans_le_calque(self, k) -> bool:
        ""
        if self.calque is None:
            return True
        if k[0] == "o":
            return str((self.releve or {}).get("objets", {}).get(k[1], {}).get("cle", "")) in self.cles_du_calque
        return ("place:" + str(k[1])) in self.cles_du_calque

    def _element_sous(self, pt: QPointF):
        if not self.releve:
            return None
        a, c = self._plan(pt)
        meilleur, dist = None, 1e9
        for n, o in self.releve.get("objets", {}).items():
            if not self.dans_le_calque(("o", n)):
                continue
            for f in self._formes(self.releve, n):
                amin, amax = min(x for x, _ in f), max(x for x, _ in f)
                cmin, cmax = min(y for _, y in f), max(y for _, y in f)
                if amin - .3 <= a <= amax + .3 and cmin - .3 <= c <= cmax + .3:
                    d = (a - o["avant"]) ** 2 + (c - o["cote"]) ** 2
                    if d < dist:
                        meilleur, dist = ("o", n), d
        if meilleur is not None:
            return meilleur
        for nom, i in self.releve.get("installations", {}).items():
            if not self.dans_le_calque(("i", nom)):
                continue
            d = (a - i["avant"]) ** 2 + (c - i["cote"]) ** 2
            if d <= max(1.5, i["rayon"]) ** 2 and d < dist:
                meilleur, dist = ("i", nom), d
        return meilleur


    def mousePressEvent(self, ev) -> None:
        if not self.releve or self.zoom is None:
            return
        pt = ev.position()
        if self.point_de_tir is not None:
            n = self.point_de_tir
            self.finir_point_de_tir()
            if ev.button() == Qt.MouseButton.LeftButton:
                a, c = self._plan(pt)
                self.fenetre.placer_point_de_tir(n, a, c)
            else:
                self.fenetre.montrer_le_choix()
            return
        if ev.button() == Qt.MouseButton.MiddleButton:
            self._mode, self._depart = "vue", (pt, self.centre_vue)
            return
        if ev.button() == Qt.MouseButton.RightButton:


            self._mode, self._depart = "droit", (pt, self.centre_vue)
            return
        if ev.button() != Qt.MouseButton.LeftButton:
            return
        a, c = self._plan(pt)
        if self.fenetre.a_poser is not None:
            self.fenetre.ajouter_ici(a, c)
            return
        ctrl = bool(ev.modifiers() & Qt.KeyboardModifier.ControlModifier)
        k = self._element_sous(pt)
        self.geste = None
        if k is not None and ctrl:
            self.choix ^= {k}
            self._mode = None
        elif k is not None:
            if k not in self.choix:
                self.choix = {k}
            self._mode, self._depart = "deplacer", (a, c)
        else:
            if not ctrl:
                self.choix = set()
            self._mode, self._cadre = "cadre", (pt, pt)
        self.fenetre.montrer_le_choix()
        self.update()

    def mouseMoveEvent(self, ev) -> None:
        pt = ev.position()
        if self.point_de_tir is not None:
            self._souris = pt
            self.update()
            return
        if self._mode == "droit":
            p0 = self._depart[0]
            if abs(pt.x() - p0.x()) + abs(pt.y() - p0.y()) > 5:
                self._mode = "vue"
        if self._mode == "vue":
            p0, (ca, cc) = self._depart
            self.centre_vue = (ca + (pt.y() - p0.y()) / self.zoom, cc + (pt.x() - p0.x()) / self.zoom)
            self.update()
        elif self._mode == "deplacer" and self.choix:
            a, c = self._plan(pt)
            dt = self.geste["dt"] if self.geste else 0.0
            self.geste = {"da": a - self._depart[0], "dc": c - self._depart[1], "dt": dt}
            self.update()
        elif self._mode == "cadre":
            self._cadre = (self._cadre[0], pt)
            self.update()

    def mouseReleaseEvent(self, ev) -> None:
        mode, self._mode = self._mode, None
        if mode == "droit":
            self._menu(ev.position())
            return
        if mode == "deplacer":
            g = self.geste
            if g and (abs(g["da"]) > 0.1 or abs(g["dc"]) > 0.1):
                self.fenetre.appliquer_le_geste(set(self.choix), g)
            else:
                self.geste = None
        elif mode == "cadre" and self._cadre is not None:
            p0, p1 = self._cadre
            self._cadre = None
            x0, x1 = sorted((p0.x(), p1.x()))
            y0, y1 = sorted((p0.y(), p1.y()))
            if x1 - x0 > 4 and y1 - y0 > 4 and self.releve:
                for n in self.releve.get("objets", {}):
                    if not self.dans_le_calque(("o", n)):
                        continue
                    q = self._ecran(*self._centre(("o", n)))
                    if x0 <= q.x() <= x1 and y0 <= q.y() <= y1:
                        self.choix.add(("o", n))
                for nom in self.releve.get("installations", {}):
                    if not self.dans_le_calque(("i", nom)):
                        continue
                    q = self._ecran(*self._centre(("i", nom)))
                    if x0 <= q.x() <= x1 and y0 <= q.y() <= y1:
                        self.choix.add(("i", nom))
            self.fenetre.montrer_le_choix()
            self.update()

    def wheelEvent(self, ev) -> None:
        if self.zoom is None:
            return
        pas = 1 if ev.angleDelta().y() > 0 else -1
        ctrl = bool(ev.modifiers() & Qt.KeyboardModifier.ControlModifier)
        if ctrl or not self.choix or self._mode is not None:

            pt = ev.position()
            a, c = self._plan(pt)
            self.zoom = max(0.3, min(80.0, self.zoom * (1.2 ** pas)))
            a2, c2 = self._plan(pt)
            ca, cc = self.centre_vue
            self.centre_vue = (ca + a - a2, cc + c - c2)
            self.update()
            return
        rad = math.radians(5 if ev.modifiers() & Qt.KeyboardModifier.ShiftModifier else 15)
        g = self.geste or {"da": 0.0, "dc": 0.0, "dt": 0.0}
        g["dt"] += pas * rad
        self.geste = g
        self.update()
        self.minuterie.start(700)

    def _fin_de_molette(self) -> None:
        if self.choix and self.geste and abs(self.geste["dt"]) > 1e-6:
            self.fenetre.appliquer_le_geste(set(self.choix), self.geste)

    def _menu(self, pt: QPointF) -> None:
        from PyQt6.QtWidgets import QMenu
        a, c = self._plan(pt)
        k = self._element_sous(pt)
        if k is not None and k not in self.choix:
            self.choix = {k}
            self.fenetre.montrer_le_choix()
            self.update()
        m = QMenu(T(self))
        if k is not None:
            objs = [x for x in self.choix if x[0] == "o"]
            places = [x for x in self.choix if x[0] == "i"]
            n = len(self.choix)
            m.addAction(T("Retirer ({0})", n) if n > 1 else T("Retirer"), self.fenetre.retirer)
            if objs:
                m.addAction(T("Copier ({0})", len(objs)) if len(objs) > 1 else T("Copier"), self.fenetre.copier)
                sm = m.addMenu(T("Réservé à…"))
                for code, texte in RESERVES:
                    sm.addAction(T(texte[0].upper() + texte[1:]), lambda c=code: self.fenetre.reserver(c))
                sm.addSeparator()
                sm.addAction(T("Personne (ouvert aux hommes)"), lambda: self.fenetre.reserver(None))
            if places:
                m.addAction(T("Remettre à sa place d'origine"), self.fenetre.remettre)

            if k[0] == "o" and self.releve and str(self.releve["objets"].get(k[1], {}).get("cle", "")) in TIR_DISTANCES:
                m.addSeparator()
                m.addAction(T("Placer le point de tir"), lambda n=k[1]: self.commencer_point_de_tir(n))
        else:
            act = m.addAction(T("Coller ici"), lambda: self.fenetre.coller(a, c))
            act.setEnabled(bool(self.fenetre.presse_papiers))
            m.addAction(T("Recadrer (tout le camp)"), self.recadrer)
        m.exec(self.mapToGlobal(pt.toPoint()))

    def keyPressEvent(self, ev) -> None:
        ctrl = bool(ev.modifiers() & Qt.KeyboardModifier.ControlModifier)
        if ctrl and ev.key() == Qt.Key.Key_C:
            self.fenetre.copier()
            return
        if ctrl and ev.key() == Qt.Key.Key_V and self.zoom is not None:
            a, c = self._plan(QPointF(self.mapFromGlobal(QCursor.pos())))
            self.fenetre.coller(a, c)
            return
        if ev.key() == Qt.Key.Key_Delete and self.choix:
            self.fenetre.retirer()
        elif ev.key() == Qt.Key.Key_Escape and self.point_de_tir is not None:
            self.finir_point_de_tir()
            self.fenetre.montrer_le_choix()
        elif ev.key() == Qt.Key.Key_Escape:
            self.fenetre.a_poser = None
            self.choix = set()
            self.geste = None
            self.fenetre.montrer_le_choix()
            self.update()


    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        try:
            from gestion_du_camp import habillage as _hb
            _hb.peindre_le_parchemin(p, self.rect())
        except Exception:
            p.fillRect(self.rect(), QColor("#eadab6"))
        if not self.releve:
            p.setPen(QColor("#3a2716"))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                       T("Clique sur « Relever le camp » (le jeu doit tourner)."))
            return
        r = dict(self.releve)
        if not self.cimetiere:
            r["pieces"] = [q for q in r["pieces"] if q["famille"] not in ("tombe", "croix")]
        self._ajuster(r)

        pas = 5
        while pas * self.zoom < 28:
            pas *= 2
        a_haut, c_gauche = self._plan(QPointF(0, 0))
        a_bas, c_droite = self._plan(QPointF(self.width(), self.height()))
        p.setFont(QFont("Segoe UI", 7))
        for k in range(int(math.floor(a_bas / pas)) * pas, int(math.ceil(a_haut)) + 1, pas):
            y = self._ecran(k, 0).y()
            p.setPen(QPen(QColor(150, 115, 60, 70), 1))
            p.drawLine(QPointF(0, y), QPointF(self.width(), y))
            p.setPen(QColor("#7a6345"))
            p.drawText(QPointF(4, y - 2), T("{0:+d} m", k))
        for k in range(int(math.floor(c_droite / pas)) * pas, int(math.ceil(c_gauche)) + 1, pas):
            x = self._ecran(0, k).x()
            p.setPen(QPen(QColor(150, 115, 60, 70), 1))
            p.drawLine(QPointF(x, 0), QPointF(x, self.height()))
            p.setPen(QColor("#7a6345"))
            p.drawText(QPointF(x + 2, self.height() - 6), T("{0:+d}", -k))

        self._dessiner_la_vegetation(p)

        for pc in sorted(r["pieces"], key=lambda q: q["famille"] != "cabane"):
            if pc["famille"] == "ajout":
                continue
            abri = pc["nom"].startswith(ABRI_ROND)
            poly = QPolygonF([self._ecran(*vers_le_plan(r, x, y)) for x, y in contour(pc, abri)])
            coul = QColor(COULEURS.get(pc["famille"], "#999999"))
            p.setPen(QPen(coul.darker(140), 2 if abri else 1))
            coul.setAlpha(45 if abri else 170)
            p.setBrush(QBrush(coul))
            p.drawPolygon(poly)
            if pc["famille"] in ENTREES:
                d = pc["a"] + ENTREES[pc["famille"]]
                demi = max(abs(pc["mx"][0] - pc["mn"][0]), abs(pc["mx"][1] - pc["mn"][1])) / 2 or 2.0
                x0, y0 = pc["x"], pc["y"]
                x1, y1 = x0 + math.cos(d) * (demi + 1.2), y0 + math.sin(d) * (demi + 1.2)
                self._fleche(p, self._ecran(*vers_le_plan(r, x0, y0)), self._ecran(*vers_le_plan(r, x1, y1)))


        p.setFont(QFont("Segoe UI", 8))
        for nom, i in r.get("installations", {}).items():
            k = ("i", nom)
            hors = not self.dans_le_calque(k)
            p.setOpacity(0.2 if hors else 1.0)
            na, nc, _ = self.nouvelle_place(k)
            pt = self._ecran(na, nc)
            ray = max(1.5, i["rayon"]) * self.zoom
            choisi = k in self.choix
            if i["etat"] == "retire":
                p.setPen(QPen(QColor("#b0b0b0"), 1, Qt.PenStyle.DashLine))
            elif i["etat"] == "deplace":
                p.setPen(QPen(QColor("#6b4f2a"), 2 if choisi else 1))
            else:
                p.setPen(QPen(QColor("#7a7a7a"), 2 if choisi else 1, Qt.PenStyle.DashLine))
            p.setBrush(QBrush(QColor(201, 162, 77, 60)) if choisi else Qt.BrushStyle.NoBrush)
            p.drawEllipse(pt, ray, ray)
            if i["etat"] == "retire":
                p.drawLine(pt + QPointF(-ray * .6, -ray * .6), pt + QPointF(ray * .6, ray * .6))
            p.setPen(QColor("#555" if i["etat"] != "retire" else "#aaa"))
            if self.ecritures and not hors:
                p.drawText(pt + QPointF(-20, -ray - 2), T(NOMS_DES_PLACES.get(nom, nom))
                           + (T(" (retirée)") if i["etat"] == "retire" else ""))
        p.setOpacity(1.0)

        cab = [vers_le_plan(r, x, y) for pc in r["pieces"] if pc["famille"] == "cabane" for x, y in coins(pc)]
        if cab:
            amax_c = max(a for a, _ in cab)
            cmil = (min(c for _, c in cab) + max(c for _, c in cab)) / 2
            self._fleche(p, self._ecran(amax_c - 1.5, cmil), self._ecran(amax_c + 2.0, cmil))

        noms = self.fenetre.noms_de_la_palette
        for n, o in r.get("objets", {}).items():
            k = ("o", n)
            hors = not self.dans_le_calque(k)
            p.setOpacity(0.2 if hors else 1.0)
            choisi = k in self.choix
            coul = QColor((COULEUR_RESERVE.get(o.get("reserve"), "#5b7fb5") if o.get("reserve") else "#1f9d8b")
                          if o["pose"] else "#b0b0b0")
            toit = getattr(self, "_toits", {}).get(n)
            for i_f, f in enumerate([] if o["cle"] in ("rond_client", "rond_marchand") else self._formes(r, n)):
                c2 = QColor(coul)
                c2.setAlpha((90 if choisi else 40) if i_f == toit else (210 if choisi else 150))
                p.setPen(QPen(QColor("#0b3d36") if choisi else coul.darker(150), 2 if (choisi or i_f == toit) else 1))
                p.setBrush(QBrush(c2))
                p.drawPolygon(QPolygonF([self._ecran(a, c) for a, c in f]))
            a0, c0, dt = self.nouvelle_place(k)
            fa, fc = tourner(1.0, 0.0, o["angle"] + dt)
            p.setPen(QPen(QColor("#0b3d36"), 1))
            p.drawLine(self._ecran(a0, c0), self._ecran(a0 + fa, c0 + fc))

            for (ka, kc), (ra, rc_) in client_sur_le_plan(o, dt, a0, c0):
                p.setPen(QPen(QColor("#c2701c") if not choisi else QColor("#0b3d36"), 2))
                p.setBrush(QBrush(QColor(194, 112, 28, 90)))
                rp = self._rayon_personne(ka, kc)
                p.drawEllipse(self._ecran(ka, kc), rp, rp)
                self._fleche(p, self._ecran(ka, kc), self._ecran(ra, rc_), "#c2701c")
                p.setPen(QColor("#c2701c"))
                if self.ecritures:
                    p.drawText(self._ecran(ka, kc) + QPointF(rp + 3, 12), T("client"))

            for (ma, mc_), (ga, gc) in marchand_sur_le_plan(o, dt, a0, c0):
                p.setPen(QPen(QColor("#7a3fa0") if not choisi else QColor("#0b3d36"), 2))
                p.setBrush(QBrush(QColor(122, 63, 160, 90)))
                rp = self._rayon_personne(ma, mc_)
                p.drawEllipse(self._ecran(ma, mc_), rp, rp)
                self._fleche(p, self._ecran(ma, mc_), self._ecran(ga, gc), "#7a3fa0")
                p.setPen(QColor("#7a3fa0"))
                if self.ecritures:
                    p.drawText(self._ecran(ma, mc_) + QPointF(rp + 3, 12), T("marchand"))

            sens = sens_de_l_objet(o, dt, a0, c0)
            if sens is not None:
                (sa_, sc_), (ea_, ec_), tir = sens
                if tir:
                    p.setPen(QPen(QColor("#b5541b"), 1, Qt.PenStyle.DashLine))
                    p.drawLine(self._ecran(sa_, sc_), self._ecran(ea_, ec_))
                    p.setBrush(Qt.BrushStyle.NoBrush)
                    p.drawEllipse(self._ecran(ea_, ec_), 5, 5)
                    if self.ecritures:
                        p.drawText(self._ecran(ea_, ec_) + QPointF(7, 4), T("tireur"))

                    self._fleche(p, self._ecran(ea_, ec_), self._ecran(sa_, sc_), "#b5541b")
                else:
                    self._fleche(p, self._ecran(sa_, sc_), self._ecran(ea_, ec_))
            p.setPen(QColor("#0b3d36"))
            if self.ecritures and not hors:
                p.drawText(self._ecran(a0, c0) + QPointF(6, -6), T(noms.get(o["cle"], o["cle"])))
        p.setOpacity(1.0)

        if self.point_de_tir is not None and self._souris is not None and self.point_de_tir in r.get("objets", {}):
            sens = sens_de_l_objet(r["objets"][self.point_de_tir])
            if sens is not None:
                sa_, sc_ = disque_sur_le_plan(r["objets"][self.point_de_tir])
                ma, mc = self._plan(self._souris)
                p.setPen(QPen(QColor("#b5541b"), 2, Qt.PenStyle.DashLine))
                p.drawLine(self._ecran(sa_, sc_), self._souris)
                p.setBrush(QBrush(QColor(181, 84, 27, 90)))
                p.drawEllipse(self._souris, 7, 7)
                p.setPen(QColor("#b5541b"))
                p.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                p.drawText(self._souris + QPointF(10, -8), T("{0:.1f} m", math.hypot(ma - sa_, mc - sc_)))

        if self._cadre is not None:
            p0, p1 = self._cadre
            p.setPen(QPen(QColor("#1f4e79"), 1, Qt.PenStyle.DashLine))
            p.setBrush(QBrush(QColor(31, 78, 121, 30)))
            p.drawRect(QRectF(p0, p1).normalized())

        if self.montrer_vegetation and self.vegetation and self._image_veg is not None:
            vues = sorted({x for l_ in self.vegetation["lignes"].values() for x in l_ if x in COULEURS_VEG})
            p.setFont(QFont("Segoe UI", 8))
            y0 = self.height() - 22 - 16 * len(vues)
            for i, x in enumerate(vues):
                coul, alpha, nom = COULEURS_VEG[x]
                c3 = QColor(coul)
                c3.setAlpha(max(alpha, 160))
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QBrush(c3))
                p.drawRect(QRectF(50, y0 + 16 * i, 12, 12))
                p.setPen(QColor("#222"))
                p.drawText(QPointF(68, y0 + 16 * i + 11), T(nom))

        p.setPen(QPen(QColor("#000"), 2))
        o = self._ecran(0, 0)
        p.drawLine(o + QPointF(-6, 0), o + QPointF(6, 0))
        p.drawLine(o + QPointF(0, -6), o + QPointF(0, 6))

    def _rayon_personne(self, a: float, c: float) -> float:
        ""
        o, b = self._ecran(a, c), self._ecran(a + RAYON_PERSONNE, c)
        return max(4.0, math.hypot(b.x() - o.x(), b.y() - o.y()))

    def _fleche(self, p: QPainter, a: QPointF, b: QPointF, couleur: str = "#0b5d1e") -> None:
        p.setPen(QPen(QColor(couleur), 2))
        if couleur == "#b5541b":
            a = b + (a - b) * (min(1.0, 18.0 / max(1.0, math.hypot(b.x() - a.x(), b.y() - a.y()))))
        p.drawLine(a, b)
        ang = math.atan2(b.y() - a.y(), b.x() - a.x())
        for s in (-1, 1):
            p.drawLine(b, b - QPointF(math.cos(ang + s * 0.5) * 7, math.sin(ang + s * 0.5) * 7))


def parler_au_jeu(code: str, secondes: float = 25) -> str | None:
    ""

    from essais.cycle_en_jeu import Jeu
    g = Jeu()
    hexa = code.encode("ascii", "replace").hex()
    g.recepteur.aller_a_la_fin()
    fin = time.time() + secondes
    while time.time() < fin:
        g.emetteur.envoyer(["hex " + hexa])
        sous = time.time() + 4
        while time.time() < sous:
            for m in (g.recepteur.lire() or []):
                if m.texte.startswith("hex"):
                    return m.texte[3:].strip()
            QApplication.processEvents()
            time.sleep(0.2)
    return None


class Fenetre(QMainWindow):

    CLASSE_PLAN = Plan
    TITRE = "Aménagement du camp"
    AVEC_CONSTRUCTION = True

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(T(self.TITRE))
        self.a_poser: str | None = None

        self.presse_papiers: list[dict] = []

        self.en_cours: set = set()
        self.rubriques = self._palette()
        self.noms_de_la_palette = {o["cle"]: o["nom"] for _, objs in self.rubriques for o in objs}
        self.plan = self.CLASSE_PLAN(self)
        self.etat = QLabel("")
        self.etat.setWordWrap(True)
        bouton = QPushButton(T("Relever le camp"))
        bouton.clicked.connect(self.relever)
        cim = QCheckBox(T("Montrer le cimetière"))
        cim.toggled.connect(lambda v: (setattr(self.plan, "cimetiere", v), self.plan.update()))


        haut = QHBoxLayout()
        actions = QHBoxLayout()
        haut.addWidget(bouton)


        self.construction = QPushButton(T("Qui construit : ?"))
        self.construction.clicked.connect(self.basculer_la_construction)
        if self.AVEC_CONSTRUCTION:

            if not chemins.gele():
                actions.addWidget(self.construction)

            cons = QPushButton(T("Constructions du camp…"))
            cons.clicked.connect(self.ouvrir_les_constructions)
            actions.addWidget(cons)
        recadrer = QPushButton(T("Recadrer"))
        recadrer.clicked.connect(lambda: self.plan.recadrer())
        haut.addWidget(recadrer)
        actions.addWidget(cim)

        ecr = QCheckBox(T("Afficher les écritures"))
        ecr.setChecked(True)
        ecr.toggled.connect(lambda v: (setattr(self.plan, "ecritures", v), self.plan.update()))
        vider = QPushButton(T("Réinitialiser le cimetière…"))
        vider.clicked.connect(self.reinitialiser_le_cimetiere)
        actions.addWidget(vider)
        actions.addStretch(1)

        haut.addWidget(QLabel(T("Calque :")))
        self.calque = QComboBox()
        self.calque.addItem(T("Tout le camp"))
        for nom_r, _objs in self.rubriques:
            self.calque.addItem(T(nom_r))
        self.calque.currentIndexChanged.connect(self.choisir_le_calque)
        haut.addWidget(self.calque)

        veg = QCheckBox(T("Végétation"))
        veg.setChecked(True)
        veg.toggled.connect(lambda v: (setattr(self.plan, "montrer_vegetation", v), self.plan.update()))
        haut.addWidget(veg)
        sonder = QPushButton(T("Relever la végétation"))
        sonder.clicked.connect(self.relever_la_vegetation)
        haut.addWidget(sonder)
        haut.addWidget(ecr)
        haut.addStretch(1)

        self.rubrique = QComboBox()
        for nom, objs in self.rubriques:
            self.rubrique.addItem(T("{0} ({1})", nom, len(objs)))
        self.liste = QListWidget()

        self.liste.setIconSize(QSize(48, 48))
        self.rubrique.currentIndexChanged.connect(self._remplir)
        self.liste.itemClicked.connect(self._armer)
        aide = QLabel(T("Poser : choisis un objet, puis clique sur le plan.\n\n"
                      "Choisir : clic ; Ctrl + clic pour en ajouter ; ou tire un cadre dans le vide.\n"
                      "Le choix : glisser = déplacer, molette = tourner (Maj : fin), Suppr = retirer.\n"
                      "Clic droit sur un objet : retirer, copier, réserver. Clic droit dans le vide : "
                      "coller. Ctrl + C / Ctrl + V aussi.\n"
                      "Clic droit sur une cible : placer le point de tir (il suit la souris, clic gauche pour le poser).\n"
                      "Les installations (cercles) se déplacent aussi.\n\n"
                      "La vue : molette = zoom (Ctrl + molette si quelque chose est choisi), "
                      "clic droit maintenu et glissé (ou clic du milieu) = se déplacer, « Recadrer » = tout le camp.\n\n"
                      "Le jeu bouge quand tu lâches la souris."))
        aide.setWordWrap(True)
        self.retirer_bouton = QPushButton(T("Retirer ce qui est choisi"))
        self.retirer_bouton.clicked.connect(self.retirer)

        self.reserver_bouton = QPushButton(T("Réservé à…"))
        menu_res = QMenu(T(self.reserver_bouton))
        for code, texte in RESERVES:
            menu_res.addAction(T(texte[0].upper() + texte[1:]), lambda c=code: self.reserver(c))
        menu_res.addSeparator()
        menu_res.addAction(T("Personne (ouvert aux hommes)"), lambda: self.reserver(None))
        self.reserver_bouton.setMenu(menu_res)
        droite = QVBoxLayout()
        droite.addWidget(QLabel(T("<b>Ajouter un objet du jeu</b>")))
        droite.addWidget(self.rubrique)
        droite.addWidget(self.liste, 1)
        droite.addWidget(aide)
        droite.addWidget(self.reserver_bouton)


        droite.addWidget(self.retirer_bouton)
        self.remettre_bouton = QPushButton(T("Remettre l'installation à sa place d'origine"))
        self.remettre_bouton.clicked.connect(self.remettre)
        droite.addWidget(self.remettre_bouton)
        panneau = QWidget()
        panneau.setLayout(droite)


        panneau.setFixedWidth(400)
        self.liste.setMinimumHeight(430)

        self.liste.setWordWrap(True)
        self.liste.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        panneau = self._panneau(panneau)
        milieu = QHBoxLayout()
        milieu.addWidget(self.plan, 1)
        milieu.addWidget(panneau)
        corps = QVBoxLayout()
        corps.addLayout(haut)
        corps.addLayout(actions)

        corps.addWidget(self.etat)
        corps.addLayout(milieu, 1)
        w = QWidget()
        w.setLayout(corps)
        self.setCentralWidget(w)
        self._remplir(0)
        self.plan.poser(lire_le_releve(complet=True))
        if self.plan.releve:
            self.plan.poser_la_vegetation(vegetation_gardee(self.plan.releve))
        self._compter()

    def choisir_le_calque(self, i: int) -> None:
        if i <= 0 or i > len(self.rubriques):
            self.plan.calque, self.plan.cles_du_calque = None, set()
        else:
            nom_r, objs = self.rubriques[i - 1]
            self.plan.calque, self.plan.cles_du_calque = nom_r, {o["cle"] for o in objs}

        self.plan.choix = {k for k in self.plan.choix if self.plan.dans_le_calque(k)}
        self.montrer_le_choix()
        self.plan.update()

    def ouvrir_les_constructions(self) -> None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("fenetre_constructions", Path(__file__).with_name("fenetre_constructions.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self._constructions = mod.FenetreConstructions(self)
        self._constructions.show()
        self._constructions.actualiser()

    def page_des_constructions(self):
        ""

        import importlib.util
        spec = importlib.util.spec_from_file_location("fenetre_constructions", Path(__file__).with_name("fenetre_constructions.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        page = mod.FenetreConstructions(self)
        page.setWindowFlags(Qt.WindowType.Widget)
        return page

    def _panneau(self, panneau: QWidget) -> QWidget:
        ""
        return panneau



    def reinitialiser_le_cimetiere(self) -> None:
        from PyQt6.QtWidgets import QMessageBox
        rep = self._ordre("return tostring(scriptorium.emplacements.tombes())", "Je compte les tombes")
        if rep is None:
            return
        n = rep.strip()
        if not n.isdigit():
            self.etat.setText(T("Le jeu n'a pas su compter les tombes : ") + T(rep))
            return
        if n == "0":
            self.etat.setText(T("Le cimetière est déjà vide."))
            return
        if QMessageBox.question(self, T("Réinitialiser le cimetière"),
                                T("Retirer les {0} tombes (et leurs croix) du cimetière ?\n\nC'est définitif : le cimetière repartira de zéro au prochain mort.", n)) != QMessageBox.StandardButton.Yes:
            self.etat.setText(T("Le cimetière est gardé."))
            return
        rep = self._ordre("return tostring(scriptorium.emplacements.vider_le_cimetiere())", "Je vide le cimetière")
        if rep is not None:
            self.etat.setText(T("Cimetière remis à zéro : {0} tombes retirées.", n) if rep.startswith("vide")
                              else T("Le jeu a refusé : ") + T(rep))
            self.relever()

    @staticmethod
    def _palette() -> list:
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("editeur_palette", Path(__file__).with_name("palette.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            cat = mod.catalogue()
        except Exception:
            cat = []

        return organiser(cat)

    def _remplir(self, i: int) -> None:
        self.liste.clear()
        if 0 <= i < len(self.rubriques):
            for o in self.rubriques[i][1]:

                prix = prix_d_un_objet(o["cle"])
                deja = o["cle"] in UNIQUES and any(x.get("cle") == o["cle"] for x in ((self.plan.releve or {}).get("objets") or {}).values())
                it = QListWidgetItem(T(o["nom"]) + (T(" — {0} gros", prix) if prix > 0 else T(" — gratuit"))
                                     + (T(DEJA_AU_CAMP) if deja else ""))
                it.setData(Qt.ItemDataRole.UserRole, o["cle"])

                try:
                    it.setToolTip(T(aide_de_l_objet(o["cle"])))
                except SystemExit:
                    pass
                image = IMAGES / (o["cle"].replace(":", "_") + ".png")
                if image.is_file():
                    it.setIcon(QIcon(str(image)))
                self.liste.addItem(T(it))

    def _armer(self, it) -> None:
        self.a_poser = it.data(Qt.ItemDataRole.UserRole)
        self.plan.choisi = None
        self.etat.setText(T("« {0} » : clique sur le plan, là où il doit aller (Échap : annuler).", it.text()))
        self.plan.update()

    def montrer_le_choix(self) -> None:
        r = self.plan.releve or {}
        choix = self.plan.choix
        if self.a_poser is not None:
            return
        if len(choix) == 1:
            k = next(iter(choix))
            if k[0] == "o" and k[1] in r.get("objets", {}):
                o = r["objets"][k[1]]
                self.etat.setText(T("Choisi : {0} — {1:+.1f} m devant, {2:+.1f} m à gauche, tourné de {3:.0f}°", self.noms_de_la_palette.get(o['cle'], o['cle']), o['avant'], o['cote'], math.degrees(o['angle']))
                                  + (T(" — réservé {0}.", reserve_a(o['reserve']))
                                     if o.get("reserve") else "."))
                return
            if k[0] == "i" and k[1] in r.get("installations", {}):
                i = r["installations"][k[1]]
                etat = {"plan": "à sa place d'origine", "deplace": "déplacée par toi", "retire": "retirée"}[i["etat"]]
                self.etat.setText(T("Installation : {0} — {1}.", NOMS_DES_PLACES.get(k[1], k[1]), etat)
                                  + (T(" Suppr : la retirer.") if i["genre"] == "poste" else "")
                                  + (T(" (Pour renvoyer {0} : onglet Embauche.)", METIERS[k[1]]) if k[1] in METIERS else ""))
                return
        if choix:
            self.etat.setText(T("{0} éléments choisis : glisse pour les déplacer ensemble, molette pour les tourner, Suppr pour les retirer.", len(choix)))
        else:
            self._compter()

    def _compter(self) -> None:
        r = self.plan.releve
        if r:
            self.etat.setText(T("{0} pièces relevées, {1} objet(s) ajouté(s) — l'avant du camp en haut", len(r['pieces']), len(r.get('objets', {}))))
        else:
            self.etat.setText(T("Aucun relevé."))


    def _ordre(self, code: str, quoi: str) -> str | None:
        self.etat.setText(T(quoi) + "…")
        QApplication.processEvents()
        try:
            rep = parler_au_jeu(code)
        except Exception as err:
            self.etat.setText(T("Le jeu ne répond pas : {0}", err))
            return None
        if rep is None:
            self.etat.setText(T("Le jeu ne répond pas (25 s) : est-il en pause ou dans un menu ?"))
            return None
        if rep.replace(" ", "_") in ("pas_de_camp", "pas de camp"):
            self.etat.setText(T("Le camp n'est pas dressé : rien n'a bougé."))
            return None
        return rep

    def ajouter_ici(self, avant: float, cote: float) -> None:
        cle, self.a_poser = self.a_poser, None
        jeton = int(time.time() * 1000) % 1_000_000_000
        r = self.plan.releve or {}
        if r.get("sans_camp"):

            if cle not in ("tente_henry", "cabane_henry", "tente_henry_vide", "cabane_henry_vide"):
                self.etat.setText(T("Il n'y a pas encore de camp : pose d'abord TA tente (ou ta cabane), dans "
                                  "« Henry et le Directeur ». Le camp naît là où tu la poses."))
                return
            ox, oy = r["origine"]
            ca, sa = math.cos(r["cap"]), math.sin(r["cap"])
            x, y = ox + ca * avant - sa * cote, oy + sa * avant + ca * cote
            rep = self._ordre(f'return tostring(scriptorium.editeur.fonder({jeton}, "{cle}", {x:.2f}, {y:.2f}, '
                              f'{r["cap"]:.4f}))', "Je fonde ton camp ici")
            if rep is not None and rep.strip() == "patente":

                self.etat.setText(T("Il te faut d'abord la patente du camp : 30 000 gros, chez le notaire de Kuttenberg "
                                  "(devant l'hôtel de ville) ou de Troskowitz (dans la cour de l'hôtel de ville)."))
                return
            if rep is not None and rep.strip().startswith("coffre_"):

                self.etat.setText(T("Le coffre du camp n'a pas assez pour fonder le camp ici : il faut {0} gros. Rien n'est posé (ta tente, elle, est gratuite).", rep.strip()[7:]))
                return
            if rep is not None and not rep.strip().isdigit():

                self.dire_le_refus(T("Le camp n'a pas pu naître : ") + (refus_en_clair(rep) or ""))
                return
            if rep is not None:
                self.relever(choisir=int(rep))
            return
        if cle.startswith("place:"):

            nom = cle.split(":", 1)[1]
            rep = self._ordre(f'return tostring(scriptorium.editeur.deplacer_place("{nom}", {avant:.2f}, {cote:.2f}))',
                              T("J'installe « {0} »", self.noms_de_la_palette.get(cle, nom)))
            if rep is not None and rep.strip() != "ok":

                self.dire_le_refus(T("« {0} » n'a pas pu s'installer : ", self.noms_de_la_palette.get(cle, nom))
                                   + (refus_en_clair(rep) or ""))
                return
            if rep is not None:
                self.en_cours.add(nom)
                self.relever()
                self.etat.setText(T("« {0} » s'installe ici : quelques secondes, puis « Relever le camp » pour la voir.", self.noms_de_la_palette.get(cle, nom))
                                  + (T(" (S'il n'apparaît pas : {0} n'est pas engagé — onglet Embauche, Artisans.)", METIERS[qui]) if (qui := {"verte2": "forge", "verte4": "bains",
                                                             "verte3": "coursier"}.get(nom, nom)) in METIERS else ""))
            return
        rep = self._ordre(f'return tostring(scriptorium.editeur.ajouter({jeton}, "{cle}", {avant:.2f}, '
                          f'{cote:.2f}, 0))', T("Je pose « {0} »", self.noms_de_la_palette.get(cle, cle)))
        refus = refus_en_clair(rep) if rep is not None else None
        if refus:
            self.dire_le_refus(refus)
            return
        if rep is not None:
            self.relever(choisir=int(rep) if rep.strip().isdigit() else None)

    def appliquer_le_geste(self, choix: set, g: dict) -> None:
        ""
        r = self.plan.releve or {}
        faits = 0
        refus = []
        for k in sorted(choix, key=str):
            a, c, dt = self.plan.nouvelle_place(k, g)
            if k[0] == "o" and k[1] in r.get("objets", {}):
                t = r["objets"][k[1]]["angle"] + dt
                t = math.atan2(math.sin(t), math.cos(t))
                rep = self._ordre(f"return tostring(scriptorium.editeur.deplacer({k[1]}, {a:.2f}, {c:.2f}, {t:.4f}))",
                                  T("Je déplace ({0}/{1})", faits + 1, len(choix)))
            elif k[0] == "i":
                rep = self._ordre(f'return tostring(scriptorium.editeur.deplacer_place("{k[1]}", {a:.2f}, {c:.2f}))',
                                  T("Je déplace ({0}/{1})", faits + 1, len(choix)))

                self.en_cours.add(k[1])
            else:
                continue
            if rep is None:
                break
            dit = refus_en_clair(rep)
            if dit and dit not in refus:
                refus.append(dit)
            faits += 1
        self.plan.geste = None
        self.relever()
        if refus:
            self.dire_le_refus("\n".join(refus))

    def placer_point_de_tir(self, n, avant: float, cote: float) -> None:
        ""
        cible = n if isinstance(n, int) else f'"{n}"'
        rep = self._ordre(f"return tostring(scriptorium.tir.placer_poste({cible}, {avant:.2f}, {cote:.2f}))",
                          "Je place le point de tir")
        if rep is None:
            return
        if "refus" in rep:
            self.etat.setText(T("Trop près de la cible (au moins 2 m) : clic droit sur la cible pour recommencer."))
            return
        if "poste" not in rep:
            self.etat.setText(T("Le point de tir n'a pas pu être posé : ") + T(rep.replace("_", " ")) + ".")
            return
        self.relever(choisir=n if isinstance(n, int) else None)
        d = rep.split()[-1].replace(".", ",")
        self.etat.setText(T("Point de tir posé à {0} m : la cible s'est tournée vers lui. Plus il est loin, plus les hommes gagnent d'expérience à chaque flèche.", d))

    def reserver(self, qui: str | None) -> None:
        r = self.plan.releve or {}
        objs = [k[1] for k in self.plan.choix if k[0] == "o" and k[1] in r.get("objets", {})]
        if not objs:
            self.etat.setText(T("Choisis d'abord un ou plusieurs objets ajoutés (un lit, une tente…)."))
            return
        valeur = f'"{qui}"' if qui else "false"
        refus = 0
        for n in objs:
            rep = self._ordre(f"return tostring(scriptorium.editeur.reserver({n}, {valeur}))", "Je change la réservation")
            if rep is None:
                return
            if not (rep.strip().startswith("reserve") if qui else rep.strip() == "ouvert"):
                refus += 1
        self.relever()
        if refus:
            self.etat.setText(T("Le jeu a refusé pour {0} objet(s) sur {1} : rien n'a changé pour eux.", refus, len(objs)))
            return
        self.etat.setText((T("Réservé {0}.", reserve_a(qui)) if qui else T("Ouvert aux hommes."))
                          + (T(LEURS_LITS.get(qui, " Ses lits sont à lui : il y dormira.")) if qui and qui != "henry" else ""))

    def lire_la_construction(self) -> None:
        try:
            rep = parler_au_jeu("return tostring(scriptorium.construction_libre.etat())", 8)
        except Exception:
            rep = None
        if rep:
            self._libre = "libre" in rep
            self.construction.setText(T("Qui construit : moi (le mod ne pose rien)") if self._libre
                                      else T("Qui construit : le mod (comme avant)"))

    def basculer_la_construction(self) -> None:
        voulu = "false" if getattr(self, "_libre", True) else "true"
        rep = self._ordre("return tostring(scriptorium.construction_libre.choisir(_G.compagnie, "
                          + voulu + "))", "Je change qui construit")
        if rep is not None:
            self.lire_la_construction()
            self.etat.setText(T("C'est noté. Ça vaut pour le prochain camp dressé (ou le prochain chargement)."))

    def retirer(self) -> None:
        r = self.plan.releve or {}
        choix = sorted(self.plan.choix, key=str)
        if not choix:
            self.etat.setText(T("Choisis d'abord ce qu'il faut retirer (clic, Ctrl + clic, ou un cadre)."))
            return

        if len(choix) > 1:
            from PyQt6.QtWidgets import QMessageBox
            noms = [self.noms_de_la_palette.get(r["objets"][k[1]]["cle"], "objet") if k[0] == "o"
                    else NOMS_DES_PLACES.get(k[1], k[1]) for k in choix if (k[0] == "o" and k[1] in r.get("objets", {}))
                    or (k[0] == "i")]
            if QMessageBox.question(self, T("Retirer"), T("Retirer ces {0} éléments ?\n\n", len(choix)) + T("\n".join(noms[:20]))) \
                    != QMessageBox.StandardButton.Yes:
                return
        pleins, pas_encore = 0, []
        for k in choix:
            if k[0] == "o":
                rep = self._ordre(f"return tostring(scriptorium.editeur.retirer({k[1]}))", "Je retire")
                if rep is not None and "plein" in rep:
                    pleins += 1
            else:
                rep = self._ordre(f'return tostring(scriptorium.editeur.retirer_place("{k[1]}"))', "Je retire")
                if rep is not None and "pas" in rep and "encore" in rep:
                    pas_encore.append(NOMS_DES_PLACES.get(k[1], k[1]))
                    if k[1] in METIERS:
                        pas_encore[-1] = T("{0} ({1} se renvoie dans l'onglet Embauche)", pas_encore[-1], METIERS[k[1]])
            if rep is None:
                break
        self.plan.choix = set()
        self.relever()
        mots = []
        if pleins:
            mots.append(T("{0} coffre(s) contiennent des affaires : vide-les d'abord, ils restent.", pleins))
        if pas_encore:
            mots.append(T("Pas encore retirables (ils ont des gens et des routines) : {0}. Tu peux les déplacer.", ", ".join(pas_encore)))
        if mots:
            self.etat.setText(" ".join(mots))

    def copier(self) -> None:
        r = self.plan.releve or {}


        uniques = ("tente_henry", "cabane_henry", "intendant", "tente_intendant", "bureau_directeur",
                   "tente_henry_vide", "cabane_henry_vide", "coffret_banque", "mini_tente")

        objs = [k[1] for k in self.plan.choix if k[0] == "o" and k[1] in r.get("objets", {})
                and r["objets"][k[1]]["cle"] not in uniques
                and not (r["objets"][k[1]].get("reserve") == "henry" and r["objets"][k[1]]["cle"].startswith("tente"))]
        if not objs:
            self.etat.setText(T("Rien à copier : choisis un ou plusieurs objets ajoutés. Ta tente, le Directeur "
                              "et les installations sont uniques : ils ne se copient pas."))
            return
        pa = sum(r["objets"][n]["avant"] for n in objs) / len(objs)
        pc_ = sum(r["objets"][n]["cote"] for n in objs) / len(objs)
        self.presse_papiers = [{"cle": r["objets"][n]["cle"], "da": r["objets"][n]["avant"] - pa,
                                "dc": r["objets"][n]["cote"] - pc_, "angle": r["objets"][n]["angle"],
                                "reserve": r["objets"][n].get("reserve")} for n in objs]
        self.etat.setText(T("{0} objet(s) copié(s). Clic droit dans le vide (ou Ctrl + V) : coller.", len(objs)))

    def coller(self, avant: float, cote: float) -> None:
        if not self.presse_papiers:
            self.etat.setText(T("Rien à coller : copie d'abord un objet (clic droit dessus, « Copier »)."))
            return
        if (self.plan.releve or {}).get("sans_camp"):
            self.etat.setText(T("Il n'y a pas encore de camp : pose d'abord ta tente."))
            return
        neufs = []
        refus = []
        for i, o in enumerate(self.presse_papiers):
            jeton = (int(time.time() * 1000) + i) % 1_000_000_000
            rep = self._ordre(f'return tostring(scriptorium.editeur.ajouter({jeton}, "{o["cle"]}", '
                              f'{avant + o["da"]:.2f}, {cote + o["dc"]:.2f}, {o["angle"]:.4f}))',
                              T("Je colle ({0}/{1})", i + 1, len(self.presse_papiers)))
            if rep is None:
                break
            dit = refus_en_clair(rep)
            if dit and dit not in refus:
                refus.append(dit)
            if rep.strip().isdigit():
                neufs.append(int(rep))
                if o.get("reserve"):
                    self._ordre(f'return tostring(scriptorium.editeur.reserver({int(rep)}, "{o["reserve"]}"))',
                                "Je réserve")
        self.relever()
        self.plan.choix = {("o", n) for n in neufs}
        self.montrer_le_choix()
        self.plan.update()
        if refus:
            self.dire_le_refus("\n".join(refus))

    def dire_le_refus(self, texte: str) -> None:
        ""
        from PyQt6.QtWidgets import QMessageBox
        self.etat.setText(texte)
        QMessageBox.warning(self, T("Aménagement du camp"), texte)

    def releve_recu(self, r: dict) -> None:
        ""







    def showEvent(self, ev) -> None:
        super().showEvent(ev)
        self._decor = None
        QTimer.singleShot(150, self.relever)


    def relever_la_vegetation(self) -> None:
        try:
            self._taille_veg = JOURNAL.stat().st_size
        except OSError:
            self._taille_veg = 0
        rep = self._ordre("return tostring(scriptorium.vegetation.relever())", "Je lance la sonde de la végétation")
        if rep is None:
            return
        rep = rep.strip()
        if rep not in ("commence", "deja", "en_cours", "en cours"):
            self.etat.setText(T("La sonde n'a pas pu partir : ") + T(rep))
            return
        if not hasattr(self, "_suivi_veg"):
            self._suivi_veg = QTimer(self)
            self._suivi_veg.timeout.connect(self._suivre_la_vegetation)
        self._suivi_veg.start(1500)
        self._suivre_la_vegetation()

    def _suivre_la_vegetation(self) -> None:
        v = lire_la_vegetation(getattr(self, "_taille_veg", 0))
        if v is None:
            self.etat.setText(T("La sonde de la végétation démarre…"))
            return
        self.plan.poser_la_vegetation(v)
        if v["fini"]:
            self._suivi_veg.stop()
            garder_la_vegetation(v)
            self.etat.setText(T("Végétation relevée : {0} × {0} points (un tous les {1:.0f} m, sur {2:.0f} m autour du camp).", v['n'], v['pas'], v['rayon'])
                              + (T(" Surfaces sans couleur : {0}.", ', '.join(v['inconnues'])) if v["inconnues"] else ""))
        else:
            self.etat.setText(T("Végétation : {0} rangées sur {1} (la sonde du jeu avance, 8 rayons par demi-seconde)…", len(v['lignes']), v['n']))

    def remettre(self) -> None:
        places = [k[1] for k in self.plan.choix if k[0] == "i"]
        if not places:
            self.etat.setText(T("Choisis d'abord une installation (un cercle)."))
            return
        for nom in places:
            rep = self._ordre(f'return tostring(scriptorium.editeur.remettre_place("{nom}"))', "Je remets")
            if rep is None:
                break
            if rep.strip() == "pas_assez":
                self.etat.setText(T("Le coffre du camp n'a pas assez d'argent pour la racheter."))
                return
        self.relever()

    def relever(self, choisir: int | None = None) -> None:
        self.etat.setText(T("Je demande le relevé au jeu…"))
        QApplication.processEvents()
        try:
            taille = JOURNAL.stat().st_size
        except OSError:
            taille = 0
        try:
            from essais.cycle_en_jeu import Jeu
            g = Jeu()

            code = ("return tostring(scriptorium.editeur.relever(true))" if getattr(self, "_decor", None)
                    else "return tostring(scriptorium.editeur.relever())")
            g.emetteur.envoyer(["hex " + code.encode("ascii").hex()])
        except Exception as err:
            self.etat.setText(T("Le jeu ne répond pas : {0}", err))
            return
        limite = time.time() + 20
        while time.time() < limite:
            r = lire_le_releve(taille)
            if r:
                self._decor = fusionner_le_decor(getattr(self, "_decor", None) or {}, r)
                if choisir is not None:
                    self.plan.choisi = choisir
                self.plan.poser(r)
                self._compter()
                self.montrer_le_choix()
                if r.get("sans_camp"):
                    self.etat.setText(T("Pas de camp : le plan est centré sur Henry (l'avant = son regard). Choisis "
                                      "« Ta tente » ou « Ta cabane » dans « Henry et le Directeur », puis clique là où tu la "
                                      "veux : c'est là que naît ton camp."))
                if self.AVEC_CONSTRUCTION and not chemins.gele():
                    self.lire_la_construction()
                if self.plan.vegetation is None or not self.plan.vegetation.get("fini"):
                    self.plan.poser_la_vegetation(vegetation_gardee(r))
                self.releve_recu(r)

                if hasattr(self, "rubrique"):
                    self._remplir(self.rubrique.currentIndex())
                return
            QApplication.processEvents()
            time.sleep(0.3)
        self.etat.setText(T("Pas de relevé dans le journal (20 s) : le jeu est-il en pause ou dans un menu ?"))


NOM_INSTANCE = "ScriptoriumAmenagement"


def main() -> int:
    app = QApplication(sys.argv)

    from PyQt6.QtNetwork import QLocalServer, QLocalSocket
    sonde = QLocalSocket()
    sonde.connectToServer(NOM_INSTANCE)
    if sonde.waitForConnected(300):
        sonde.write(b"devant")
        sonde.flush()
        sonde.waitForBytesWritten(300)
        sonde.disconnectFromServer()
        return 0
    from noyau.premier_plan import au_premier_plan
    f = Fenetre()
    f.resize(1300, 950)
    serveur = QLocalServer()
    QLocalServer.removeServer(NOM_INSTANCE)
    serveur.listen(NOM_INSTANCE)

    def devant() -> None:
        c = serveur.nextPendingConnection()
        if c is not None:
            c.waitForReadyRead(200)
            c.readAll()
        au_premier_plan(f)

    serveur.newConnection.connect(devant)
    f.show()
    if "--devant" in sys.argv:
        au_premier_plan(f)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
