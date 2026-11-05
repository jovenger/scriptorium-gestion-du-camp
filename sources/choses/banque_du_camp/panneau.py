
""








from __future__ import annotations

import json
import re
import time
from pathlib import Path

import sys
_RACINE = str(Path(__file__).resolve().parents[2])
if _RACINE not in sys.path:
    sys.path.insert(0, _RACINE)
from noyau import chemins as _chemins

LIVRE = _chemins.dossier_local() / "banque.json"


MOUVEMENTS = {
    "butin": ("Butin des batailles", True),
    "rations": ("Vivres pris sur les corps", True),
    "repas": ("Repas payés par les hommes", True),
    "boisson": ("Boissons payées par les hommes", True),
    "arme": ("Armes payées par les hommes", True),
    "fleches": ("Flèches payées par les archers", True),
    "bain": ("Bains payés par les hommes", True),
    "forge": ("Réparations payées à la forge", True),
    "achat": ("Achats des hommes", True),
    "dettes": ("Dettes remboursées sur la paye", True),
    "revente": ("Revente du surplus en ville", True),

    "commission": ("Commission du coursier (tes commandes)", True),
    "payes": ("Payes des hommes", False),
    "femmes": ("Paye des femmes des bains", False),
    "forgeron": ("Paye du forgeron", False),
    "matieres": ("Matières de la forge", False),
    "courses": ("Courses du coursier pour le camp", False),


    "embauche": ("Embauches (mercenaires et service)", False),

    "soins": ("Soin de toute la compagnie, payé par le camp", False),



    "primes": ("Primes et parts des hommes (combats, missions)", False),
    "postes": ("Primes de garde (une par ronde de 3 h)", False),


    "service": ("Paye du service (métiers engagés)", False),



    "vente": ("Ventes aux métiers (repas, boisson, bain, soins, réparations)", True),
    "taxe": ("Taxe des métiers (20 % du bénéfice)", True),

    "impot": ("Taxes des commerces (40 % de la paye, 20 % de la caisse au-dessus de 200)", True),


    "fournitures": ("Fournitures remboursées par les métiers", True),
    "avances": ("Avances du coffre (achats à crédit, première semaine des métiers)", False),
    "provisions": ("Achats du camp aux métiers (bois des feux, cantine)", False),

    "fonds": ("Fonds de départ des ateliers", False),

    "ausac": ("Butin confié au coursier (revendu à sa course)", False),
    "henry": ("Ta part du bénéfice", False),
    "directeur": ("Part du Directeur", False),
    "prelevement": ("Prélèvement du Directeur sur les marchands", True),
    "renvoi": ("Bourse d'un commerçant renvoyé", True),

    "amenagement": ("Aménagement : constructions du camp", False),

    "annulation": ("Achat annulé, remboursé au coffre", True),


    "parts": ("Parts du butin aux combattants (fin de bataille)", False),
    "porteurs": ("Pièces des corps portés, gardées par les porteurs", False),
    "succession": ("Bourse d'un mort sans héritier", True),

    "caisse_atelier": ("Caisses d'atelier : prélevé ou donné par Henry", False),


    "rancon": ("Rançon d'un prisonnier", True),

    "amende": ("Amende (fuite en duel)", True),
    "prime_caisse": ("Caisse de prime : don d'un commerçant", False),
    "prime_henry": ("Caisse de prime : versé par Henry", False),
    "prime_coffre": ("Caisse de prime : versé par le coffre du camp", False),
    "prime_versee": ("Prime d'encouragement versée aux hommes", False),

    "retenue": ("Part retenue : parti en mission au lieu du pilori", True),

    "loyer": ("Loyer d'un compagnon", True),


    "depot": ("Déposé au coffre", True),
    "retrait": ("Retiré du coffre", False),
}


CODES_SANS_SOULIGNE = {c.replace("_", ""): c for c in MOUVEMENTS}


SORTIES_DU_BENEFICE = ("payes", "femmes", "forgeron", "henry", "matieres", "courses", "embauche", "soins", "primes", "postes", "amenagement", "parts",
                       "service", "fonds", "directeur", "ausac", "provisions", "avances", "prime_coffre")



CAPITAL = ("depot", "retrait")


NATURE = ("rations", "vente", "porteurs", "caisse_atelier", "prime_caisse", "prime_henry", "prime_versee")

RESERVES = ("vivres", "boisson", "savon", "fer", "charbon", "garde", "pommeau", "rivets", "tissu", "cuir",
            "tr_armes", "tr_armure", "tr_habits", "tr_bottes", "bois", "pansements", "branches", "graines", "biere", "vin", "acier", "acier_fin")



COURSES = {
    "vivres": "Vivres", "boisson": "Boisson", "savon": "Savon", "fer": "Fer",
    "charbon": "Charbon", "garde": "Gardes d'épée", "pommeau": "Pommeaux",
    "rivets": "Rivets et ferrures", "tissu": "Tissu", "cuir": "Cuir",
    "trarmes": "Trousses d'armes", "trarmure": "Trousses d'armure",
    "trhabits": "Trousses de tailleur", "trbottes": "Trousses de cordonnier",
    "bois": "Bois de chauffe",
    "acier": "Acier (médiocre)", "acierfin": "Acier fin",
}
PRIX = ("repas", "boisson", "arme", "carquois", "bain", "part", "filles", "forgeron", "reparme", "repbouclier",
        "reparmure", "recrue", "confirme", "veteran", "marge", "prime",

        "bois", "charbon", "branches", "biere", "vin", "eau")


def vide() -> dict:
    return {"journal": [], "prix": {}, "bourses": 0, "dettes": 0}


def lire() -> dict:
    try:
        d = json.loads(LIVRE.read_text(encoding="utf-8"))
        return d if "journal" in d else vide()
    except Exception:
        return vide()


def _ecrire(livre: dict) -> None:
    LIVRE.parent.mkdir(parents=True, exist_ok=True)
    tmp = LIVRE.with_suffix(".tmp")
    tmp.write_text(json.dumps(livre, ensure_ascii=False), encoding="utf-8")
    tmp.replace(LIVRE)


def cle_mvt(mv: dict) -> tuple:
    return (mv.get("h"), mv.get("code"), mv.get("gros"), mv.get("n"), mv.get("qui"))


def _etiqueter_le_don(livre: dict, code: str, don: float) -> bool:
    ""



    for mv in reversed((livre.get("caisses") or {}).get(code, [])[-200:]):
        if mv.get("l") == "autre" and mv.get("m", 0) < 0 and abs(-mv["m"] - don) <= 1 + 0.02 * don:
            mv["l"] = "primedencouragement"
            return True
    return False


def appliquer(livre: dict, texte: str, deja: dict | None = None, etats: bool = True) -> bool:
    ""




    d = re.match(r"caisse prime commerce-([a-z0-9]+)-(\d+)-(\d+)-(\d+)", texte.strip())
    if d:
        code, don = d.group(1), int(d.group(4))
        if don > 0 and not _etiqueter_le_don(livre, code, don):
            attente = livre.setdefault("dons_prime_attente", [])
            attente.append([code, don])
            del attente[:-50]
        return True
    m = re.match(r"banque (mvt|prix|bourses|origine|semaine|reserves|limites|postes|paye|achats|solde|caisse) (.*)$",
                 texte.strip())
    if not m:
        return False
    genre, reste = m.group(1), m.group(2).replace(" ", "")
    if not etats and genre not in EVENEMENTS:
        return True
    if genre == "mvt":

        p = re.match(r"(\d+)-([a-z]+)-(\d+)-(\d+)(?:-([A-Za-z0-9]+))?", reste)
        if not p or p.group(2) not in CODES_SANS_SOULIGNE:
            return True
        mv = {"h": int(p.group(1)), "code": CODES_SANS_SOULIGNE[p.group(2)], "gros": int(p.group(3)),
              "n": int(p.group(4)), "vu": time.time()}
        if p.group(5):
            mv["qui"] = p.group(5)
        if deja is not None and deja.get(cle_mvt(mv), 0) > 0:
            deja[cle_mvt(mv)] -= 1
            return True
        livre["journal"].append(mv)
    elif genre == "caisse":



        p = re.match(r"(\d+)-([a-z0-9]+)-(-?\d+)-(-?\d+)-([a-z0-9.]+)$", reste)
        if not p:
            return True
        code, lib = p.group(2), p.group(5)
        montant, solde = int(p.group(3)) / 100, int(p.group(4)) / 100
        livre.setdefault("caisses_soldes", {})[code] = solde
        if lib != "releve":
            l = livre.setdefault("caisses", {}).setdefault(code, [])
            mv = {"h": int(p.group(1)), "m": montant, "s": solde, "l": lib}

            if mv not in l[-40:]:
                l.append(mv)
                del l[:-400]

                if lib == "autre" and montant < 0:
                    attente = livre.get("dons_prime_attente") or []
                    for k, (c_, don) in enumerate(attente):
                        if c_ == code and _etiqueter_le_don(livre, code, don):
                            del attente[k]
                            break
    elif genre == "solde":

        n = entiers_signes(reste)
        if len(n) >= 2:
            soldes = livre.setdefault("soldes", [])
            soldes.append([int(n[0]), int(n[1])])
            del soldes[:-5000]

            if livre.pop("_reprise", False):
                reprises = livre.setdefault("reprises", [])
                reprises.append(int(n[0]))
                del reprises[:-2000]
    elif genre == "paye":


        n = re.findall(r"\d+", reste)
        if n:
            payes = livre.setdefault("payes", [])
            h = int(n[0])
            if h not in payes:
                payes.append(h)
                del payes[:-60]
    elif genre == "achats":

        bouts = [x for x in reste.split("-") if x != ""]
        if len(bouts) >= 5 and bouts[0].isdigit():
            lignes = []
            for i in range(2, len(bouts) - 2, 3):
                c, q, prix = bouts[i], bouts[i + 1], bouts[i + 2]
                if q.isdigit() and prix.isdigit():
                    lignes.append({"c": c, "q": int(q), "gros": int(prix)})
            if lignes:
                fiches = livre.setdefault("achats", [])
                fiche = {"h": int(bouts[0]), "gros": int(bouts[1]), "lignes": lignes}


                if not fiches or (fiches[-1].get("h"), fiches[-1].get("gros")) != (fiche["h"], fiche["gros"]):
                    fiches.append(fiche)
                    del fiches[:-200]
    elif genre == "prix":
        n = re.findall(r"\d+(?:\.\d+)?", reste)
        if len(n) >= 7:
            livre["prix"] = {k: float(v) for k, v in zip(PRIX, n)}
    elif genre == "origine":




        n = entiers_signes(reste)
        if len(n) >= 4:
            livre["origine"], livre["coffre"], livre["du_filles"], livre["jours_dus"] = (int(x) for x in n[:4])
    elif genre == "reserves":
        n = re.findall(r"\d+(?:\.\d+)?", reste)
        if len(n) >= len(RESERVES) + 2:
            livre["reserves"] = {k: float(v) for k, v in zip(RESERVES, n)}
            livre["courses"] = {"etat": int(float(n[len(RESERVES)])), "depart": int(float(n[len(RESERVES) + 1]))}
    elif genre == "limites":
        n = re.findall(r"\d+(?:\.\d+)?", reste)
        if len(n) >= 2 * len(RESERVES):
            livre["limites"] = {k: [float(n[2 * i]), float(n[2 * i + 1])] for i, k in enumerate(RESERVES)}
    elif genre == "postes":

        n = re.findall(r"\d+", reste)
        if len(n) >= 3:
            livre["postes"] = {"du": int(n[0]), "hommes": int(n[1]), "jours": int(n[2])}
    elif genre == "bourses":

        n = re.findall(r"\d+", reste)
        if len(n) >= 2:
            livre["bourses"], livre["dettes"] = int(n[0]), int(n[1])
        if len(n) >= 5:


            livre["a_payer"] = {"solde": int(n[2]), "primes": int(n[3]), "autres": int(n[4])}
    return True


def inscrire(texte: str) -> bool:
    ""
    livre = lire()
    if not appliquer(livre, texte):
        return False
    _ecrire(livre)
    return True














EVENEMENTS = ("mvt", "paye", "achats", "solde", "caisse")
VERROU = LIVRE.with_name("banque.verrou")
_RACINE_JEU: list = []


def racine_du_jeu() -> Path | None:
    if not _RACINE_JEU:
        try:
            import sys
            racine = str(Path(__file__).resolve().parents[2])
            if racine not in sys.path:
                sys.path.insert(0, racine)
            from noyau.jeu import trouver_jeu
            inst = trouver_jeu()
            _RACINE_JEU.append(inst.racine if inst else None)
        except Exception:
            _RACINE_JEU.append(None)
    return _RACINE_JEU[0]


def session_de(chemin: Path) -> str | None:
    ""

    try:
        with open(chemin, "r", encoding="utf-8", errors="replace") as f:
            tete = f.read(300)
    except OSError:
        return None
    m = re.search(r'BackupNameAttachment="([^"]+)"', tete)
    return m.group(1).strip() if m else None


def _lignes(brut: str) -> list[str]:
    from noyau.pont import MOTIF_LIGNE
    out = []
    for ligne in brut.splitlines():
        t = MOTIF_LIGNE.search(ligne)
        if t:
            out.append(t.group("message").strip().replace("_", " "))
    return out


def _verrouiller():
    try:
        import msvcrt
    except ImportError:
        return open(VERROU, "a+b")
    VERROU.parent.mkdir(parents=True, exist_ok=True)
    f = open(VERROU, "a+b")
    try:
        f.seek(0)
        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        return f
    except OSError:
        f.close()
        return None





_COPIES: dict = {"t": 0.0, "cle": None, "l": []}
GARDER_COPIES = 30.0


def copies_des_journaux(racine: Path, cle_en_cours=None) -> list:
    ""
    import os
    maintenant = time.time()
    cle = (str(racine), cle_en_cours)
    if (_COPIES["l"] or _COPIES["t"]) and maintenant - _COPIES["t"] < GARDER_COPIES and _COPIES["cle"] == cle:
        return _COPIES["l"]
    l = []
    try:
        with os.scandir(Path(racine) / "LogBackups") as it:
            for e in it:
                if e.name.startswith("kcd") and e.name.endswith(".log"):
                    st = e.stat()
                    l.append((st.st_mtime, st.st_size, Path(e.path)))
    except OSError:
        l = []
    l.sort(key=lambda x: x[0])
    _COPIES.update(t=maintenant, cle=cle, l=l)
    return l


def rattraper(racine: Path | None = None, commandes: list | None = None) -> int:
    ""



    racine = racine or racine_du_jeu()
    if racine is None:
        return 0
    verrou = _verrouiller()
    if verrou is None:
        return 0
    try:
        livre = lire()
        lu = livre.setdefault("lu", {})
        en_cours = Path(racine) / "kcd.log"
        cle_en_cours = session_de(en_cours)

        borne = livre.get("remis_le")
        if borne is None:
            vus = [mv.get("vu") for mv in livre.get("journal", []) if mv.get("vu")]
            borne = min(vus) if vus else time.time()
            livre["remis_le"] = borne
        infos = copies_des_journaux(racine, cle_en_cours)
        copies = [x[2] for x in infos]
        tailles = {x[2]: (x[1], x[0]) for x in infos}
        change = False

        if "reprises" not in livre:
            livre["reprises"] = reprises_des_journaux(copies + [en_cours])
            change = True

        traitees = livre.setdefault("copies_lues", {})
        n = 0
        for c in copies + [en_cours]:
            courant = c == en_cours
            if courant:
                try:
                    st = c.stat()
                    taille, fin = st.st_size, st.st_mtime
                except OSError:
                    continue
            else:
                taille, fin = tailles[c]
            if not courant and traitees.get(c.name) == taille:
                continue
            cle = session_de(c)
            if cle is None:
                continue
            if not courant and (cle == cle_en_cours or fin < borne):
                if cle != cle_en_cours:
                    traitees[c.name] = taille
                    change = True
                continue
            debut = int(lu.get(cle, 0))
            if debut >= taille:
                continue
            deja = None
            if debut == 0:
                livre["_reprise"] = True
            if cle not in lu:


                from collections import Counter
                deja = Counter(cle_mvt(mv) for mv in livre.get("journal", []))
            try:
                with open(c, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(debut)
                    brut = f.read()
                    lu[cle] = f.tell()
                    change = True
            except OSError:
                continue
            if not courant:
                traitees[c.name] = taille
            for t in _lignes(brut):
                if t.startswith("banque "):
                    if appliquer(livre, t, deja, etats=courant):
                        n += 1
                elif courant and commandes is not None and t in ("coffret banque", "coffret panneau"):
                    commandes.append(t)
        if change:
            _ecrire(livre)
        return n
    finally:
        try:
            verrou.close()
        except Exception:
            pass


def traiter(texte: str) -> bool:
    ""


    if not texte.strip().startswith("banque "):
        return False
    rattraper()
    return True


def entiers_signes(reste: str) -> list[int]:
    ""





    out, signe = [], 1
    for bout in reste.split("-"):
        if bout == "":
            signe = -1
            continue
        try:
            out.append(signe * int(bout))
        except ValueError:
            pass
        signe = 1
    return out


def jour_de(h: int, origine: int = 0) -> int:
    ""
    return int((h - origine) // 86400) + 1


def agreger(journal: list[dict], taille: int, origine: int = 0) -> list[dict]:
    ""


    groupes: dict[int, dict] = {}
    for mv in journal:




        k = (jour_de(mv["h"], origine) - 1) // taille
        g = groupes.setdefault(k, {"premier": k * taille + 1, "dernier": (k + 1) * taille,
                                   **{c: 0 for c in MOUVEMENTS}})
        g[mv["code"]] += mv["gros"]
    sortie = []
    for k in sorted(groupes, reverse=True):
        g = groupes[k]
        g["entrees"] = sum(g[c] for c, (_, e) in MOUVEMENTS.items() if e and c not in CAPITAL and c not in NATURE)
        g["capital"] = g["depot"] - g["retrait"]
        g["hommes"] = sum(g[c] for c in ("repas", "boisson", "arme", "fleches", "bain", "forge", "achat", "dettes"))







        g["sorties"] = sum(g[c] for c in SORTIES_DU_BENEFICE)
        g["benefice"] = g["entrees"] - g["sorties"]
        sortie.append(g)
    return sortie


def depuis(journal: list[dict], h0: float | int | None) -> dict:
    ""





    if h0 is None:
        return totaux(journal)



    return totaux([mv for mv in journal if mv.get("h", 0) > h0])


def par_semaine_payee(journal: list[dict], payes: list) -> list[dict]:
    ""




    bornes = [0] + sorted(float(h) for h in (payes or []))
    lignes = []
    for i in range(len(bornes) - 1, -1, -1):
        debut = bornes[i]
        fin = bornes[i + 1] if i + 1 < len(bornes) else None

        lot = [mv for mv in journal
               if (mv.get("h", 0) > debut or debut == 0)
               and (fin is None or mv.get("h", 0) <= fin)]
        if not lot and i != len(bornes) - 1:
            continue
        t = totaux(lot)
        lignes.append({"numero": i + 1, "debut": debut, "fin": fin,
                       "part": t.get("henry", 0), "benefice": t.get("benefice", 0),
                       "payes": t.get("payes", 0), "entrees": t.get("entrees", 0),
                       "en_cours": fin is None})
    return lignes


def totaux(journal: list[dict]) -> dict:
    t = agreger([dict(mv, h=0) for mv in journal], 1)
    return t[0] if t else {**{c: 0 for c in MOUVEMENTS}, "entrees": 0, "benefice": 0, "hommes": 0}


def remettre_a_zero() -> None:
    ""






    livre = lire()


    garde = {k: livre[k] for k in ("prix", "bourses", "dettes", "postes", "lu", "copies_lues")
             if k in livre}

    garde["remis_le"] = time.time()
    garde.setdefault("prix", {})
    garde.setdefault("bourses", 0)
    garde.setdefault("dettes", 0)
    _ecrire({"journal": [], "payes": [], "achats": [], **garde})


def achats_par_semaine(fiches: list[dict], payes: list) -> list[dict]:
    ""




    bornes = [0] + sorted(float(h) for h in (payes or []))
    groupes = []
    for i in range(len(bornes) - 1, -1, -1):
        debut = bornes[i]
        fin = bornes[i + 1] if i + 1 < len(bornes) else None
        lot = [f for f in (fiches or [])
               if f.get("h", 0) >= debut and (fin is None or f.get("h", 0) < fin)]
        if not lot and i != len(bornes) - 1:
            continue
        groupes.append({"numero": i + 1, "en_cours": fin is None, "fiches": list(reversed(lot)),
                        "gros": sum(f.get("gros", 0) for f in lot),
                        "articles": sum(l.get("q", 0) for f in lot for l in f.get("lignes", []))})
    return groupes






EFFET_AU_COFFRE = {
    "repas": 1, "boisson": 1, "arme": 1, "fleches": 1, "bain": 1, "forge": 1, "achat": 1, "dettes": 1,
    "revente": 1, "butin": 1, "depot": 1, "commission": 1,
    "payes": -1, "femmes": -1, "forgeron": -1, "matieres": 0, "courses": -1, "embauche": -1, "primes": -1,
    "postes": -1, "henry": -1, "retrait": -1, "service": -1, "rations": 0,
    "vente": 0, "taxe": 1, "impot": 1, "fournitures": 1, "avances": -1, "provisions": -1, "fonds": -1, "ausac": -1,

    "directeur": -1, "prelevement": 1, "renvoi": 1, "retenue": 1, "loyer": 1,


    "caisse_atelier": 0,

    "amenagement": -1, "annulation": 1,


    "parts": -1, "porteurs": 0, "succession": 1,

    "prime_caisse": 0, "prime_henry": 0, "prime_coffre": -1, "prime_versee": 0,

    "rancon": 1, "amende": 1,
}







def reprises_des_journaux(journaux) -> list[int]:
    ""
    l = []
    for c in journaux:
        try:
            with open(c, "r", encoding="utf-8", errors="replace") as f:
                for ligne in f:
                    i = ligne.find("scriptorium_banque_solde_")
                    if i >= 0:
                        m = re.match(r"(\d+)", ligne[i + len("scriptorium_banque_solde_"):])
                        if m:
                            l.append(int(m.group(1)))
                        break
        except OSError:
            continue
    return sorted(set(l))


def verifier_les_comptes(livre: dict) -> dict:
    ""

    soldes = sorted(livre.get("soldes") or [], key=lambda x: x[0])
    if len(soldes) < 2:
        return {"jours": [], "ecart": 0, "depuis": soldes[0][0] if soldes else None}

    fins: dict[int, tuple[int, int]] = {}
    for h, c in soldes:
        fins[h // 86400] = (h, c)
    jours = sorted(fins)
    journal = sorted(livre.get("journal") or [], key=lambda mv: mv["h"])
    reprises = set(livre.get("reprises") or [])

    def explique(ha, hb):
        return sum(EFFET_AU_COFFRE.get(mv["code"], 0) * mv["gros"] for mv in journal if ha < mv["h"] <= hb)
    out, total, total_ch = [], 0, 0
    for j0, j1 in zip(jours, jours[1:]):
        (h0, c0), (h1, c1) = fins[j0], fins[j1]
        attendu = explique(h0, h1)

        chargement = 0
        for (ha, ca), (hb, cb) in zip(soldes, soldes[1:]):
            if h0 <= ha and hb <= h1 and hb in reprises:
                chargement += (cb - ca) - explique(ha, hb)
        reel = c1 - c0
        ecart = reel - attendu - chargement
        total += ecart
        total_ch += chargement
        out.append({"jour": j1, "attendu": attendu, "reel": reel, "ecart": ecart, "chargement": chargement})
    return {"jours": out, "ecart": total, "chargements": total_ch, "depuis": soldes[0][0]}
