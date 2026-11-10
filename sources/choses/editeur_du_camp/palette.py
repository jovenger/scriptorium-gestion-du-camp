
""














from __future__ import annotations

import math
import re
import zipfile
from functools import lru_cache
from pathlib import Path

def _le_pak_du_jeu() -> Path:
    ""
    import sys
    racine = str(Path(__file__).resolve().parents[2])
    if racine not in sys.path:
        sys.path.insert(0, racine)
    from noyau import jeu
    inst = jeu.trouver_jeu()
    return (inst.racine if inst else Path(".")) / "Data" / "IPL_GameData.pak"


PAK = _le_pak_du_jeu()
CHEMIN_LUA = "Scripts/mods/scriptorium_palette.lua"
COFFRE = "Objects/characters/assets/chest/chest_rustic_a.cdf"
CAISSE_ATELIER = "Caisse d'atelier (à réserver à un métier)"
TENTES = "objects/manmade/structures/living/tents/"


MUETTES = {"PrefabPort", "GhostDummy"}


RUBRIQUES = [
    ("S'asseoir et manger", [
        ("table_bancs", "Table et deux bancs", "Table/table_twoSides"),
        ("table_un_banc", "Table et un banc", "Table/table_oneSide"),
        ("petite_table", "Petite table et deux chaises", "Table/table_small_twoSides"),
        ("table_une_place", "Petite table et un tabouret", "Table/table_oneSitPlace"),
        ("banc", "Banc (deux places)", "Bench/bench_2places_low"),
        ("banc_trois", "Banc (trois places)", "Bench/bench_3places_low"),
        ("banc_haut", "Banc haut", "Bench/bench_2places_high"),
        ("tabouret", "Tabouret", "Bench/bench_1place_low"),
        ("chaise", "Chaise basse", "Chair/chair_low"),
        ("chaise_haute", "Chaise haute", "Chair/chair_high"),
    ]),
    ("Dormir", [
        ("lit", "Lit bas", "Bed/bed_low"),
        ("lit_haut", "Lit haut", "Bed/bed_high"),
        ("lit_double", "Lit double", "Bed/bed_high_double"),
        ("lit_banc", "Banc-lit", "Bed/bed_bench"),
    ]),
    ("Feu, cuisine, boisson", [
        ("foyer", "Foyer de camp (chaudron, cuisine)", "Fireplace/fireplace_camp"),
        ("tonneau_vin", "Tonneau de vin (on s'y sert)", "profession/camper/camperWineBarrel_noPoison"),
        ("tonneau_biere", "Tonneau de bière sur souche", "exteriorDecoration/camp_decoration/Beer_keg_on_stump_driping"),
        ("cuisine", "Coin cuisine", "exteriorDecoration/camp_supplies/cooking_station_v1"),
        ("cuisine_etageres", "Coin cuisine avec étagères", "exteriorDecoration/camp_supplies/cooking_station_v3_shelves"),
        ("table_boisson", "Table à boire", "exteriorDecoration/camp_decoration/table_drinking_station"),
        ("table_vaisselle", "Table avec vaisselle et lampe", "exteriorDecoration/camp_decoration/table_with_dishes_and_lamp"),
    ]),
    ("Lumière", [
        ("torche", "Torche sur pied (allumée)", "staticlights/torchStandingRustic_24h"),
        ("lanterne", "Lanterne de table", "staticlights/lanternTableFancy_b"),
        ("lampe_table", "Grosse lampe à bougies", "staticlights/lampTableRusticLarge"),
    ]),
    ("Armes et exercice", [
        ("ratelier", "Râtelier d'entraînement", "profession/camper/camperFriendlyFight_rack"),
        ("ratelier_garde", "Râtelier de la garde", "profession/guard/guardArmory_rack_ver1"),


        ("cible", "Cible de tir (arc ou arbalète)", "exteriorDecoration/archery/target_on_stand_V1"),


        ("cible_pres", "Cible d'entraînement archer – tir près (7 m)", "exteriorDecoration/archery/target_on_stand_V1"),
        ("cible_moyen", "Cible d'entraînement archer – tir moyen (10 m)", "exteriorDecoration/archery/target_on_stand_V1"),
        ("cible_loin", "Cible d'entraînement archer – tir loin (15 m)", "exteriorDecoration/archery/target_on_stand_V1"),
        ("cible_tres_loin", "Cible d'entraînement archer – tir très loin (25 m, le centre rapporte gros)", "exteriorDecoration/archery/target_on_stand_V1"),
        ("hallebardes", "Hallebardes dans un tonneau", "interiorDecoration/weaponGroups/polearms_in_barrel"),
        ("haches", "Haches dans une caisse", "interiorDecoration/weaponGroups/axes_in_box"),
    ]),



    ("Justice du camp", [
        ("pilori", "Pilori (le Directeur y met les punis)", "Pillory/pillory_v_2"),
    ]),


    ("Artisans", [
        ("atelier_armurier", "Atelier de l'armurier (petite forge de camp)", "profession/blacksmith/smithy_workshop_small"),
        ("porte_armure", "Porte-armure (l'armurier y montre son travail)", "armory/armorStand"),
    ]),
]


RANGER = ("Ranger", [("coffre", "Coffre (garde ce qu'on y met)", None)])


TENTES_CHOIX = [
    ("tente_petite", "Petite tente", "tent_small_a"),
    ("tente_petite_verte", "Petite tente verte", "tent_small_a_green"),
    ("tente_petite_rouge", "Petite tente rouge", "tent_small_a_red"),
    ("tente_petite_b", "Petite tente (autre forme)", "tent_small_b"),
    ("tente_foret_a", "Tente de forêt A", "tent_small_forest_a"),
    ("tente_foret_b", "Tente de forêt B", "tent_small_forest_b"),
    ("tente_foret_c", "Tente de forêt C", "tent_small_forest_c"),
    ("tente_rustique", "Tente rustique", "tent_small_rustic_a"),
    ("tente_usee", "Tente usée", "tent_small_shabby_a"),
    ("tente_couman", "Tente coumane", "tent_cuman_small_v3"),
    ("tente_ronde", "Grande tente ronde (celle d'Henry)", "tent_big_round_a"),
    ("tente_ronde_1", "Grande tente ronde, couleur 1", "tent_big_round_a_color1"),
    ("tente_ronde_2", "Grande tente ronde, couleur 2", "tent_big_round_a_color2"),
    ("tente_carree", "Grande tente carrée", "tent_big_square_a"),
    ("tente_carree_verte", "Grande tente carrée verte (service)", "tent_big_square_a_color3"),
    ("tente_carree_b", "Grande tente carrée B", "tent_big_square_b"),
    ("tente_carree_c", "Grande tente carrée C", "tent_big_square_c"),
    ("tente_yourte", "Yourte", "tent_big_jurt_a"),
    ("tente_riche", "Tente de seigneur", "tent_big_fancy_a"),
    ("tente_riche_ouverte", "Tente de seigneur, ouverte", "tent_big_fancy_a_open"),
    ("tente_royale", "Tente royale", "tent_big_royal_a"),
    ("tente_royale_ouverte", "Tente royale, ouverte", "tent_big_royal_a_open"),
    ("auvent_foret", "Auvent de forêt", "canopy_forest_a"),
    ("auvent_grand", "Grand auvent", "canopy_tent_big_a"),
    ("abri_foret", "Abri de forêt", "shelter_medium_forest_a"),
]

DECOR = ("exteriorDecoration/camp_decoration/", "exteriorDecoration/camp_supplies/",
         "exteriorDecoration/camp_supplies_small/")



@lru_cache(maxsize=1)
def _prefabs() -> dict:
    ""
    par_chemin, par_guid = {}, {}
    if not PAK.exists():
        return {"chemin": par_chemin, "guid": par_guid}
    with zipfile.ZipFile(PAK) as z:
        for nom in z.namelist():
            if not nom.lower().startswith("prefabs/") or not nom.endswith(".xml"):
                continue
            t = z.read(nom).decode("utf-8", "replace")
            m = re.search(r'<Prefab [^>]*Id="([0-9a-f-]{36})"', t)
            if not m:
                continue
            objets = []
            for o in re.finditer(r"<Object ([^>]*?)(/>|>(.*?)</Object>)", t, re.S):
                attr = dict(re.findall(r'(\w+)="([^"]*)"', o.group(1)))

                if attr.get("EntityClass") == "StanceSmartObject" and o.group(3):
                    corps = o.group(3)
                    pr = re.search(r"<Properties ([^>]*?)/?>", corps)
                    attr["_so"] = dict(re.findall(r'(\w+)="([^"]*)"', pr.group(1))) if pr else {}
                    for balise in ("Bed", "Script"):
                        b = re.search(r"<" + balise + r" ([^>]*?)/>", corps)
                        if b:
                            attr["_so"].update(dict(re.findall(r'(\w+)="([^"]*)"', b.group(1))))
                objets.append(attr)
            cle = nom[len("prefabs/"):-4]
            e = {"guid": m.group(1), "ignore": "<Tag>ignore</Tag>" in t, "objets": objets, "chemin": cle}
            par_chemin[cle.lower()] = e
            par_guid[m.group(1)] = e
    return {"chemin": par_chemin, "guid": par_guid}


def prefab(chemin: str) -> dict | None:
    return _prefabs()["chemin"].get(chemin.lower())



def _vec(s: str | None, defaut=(0.0, 0.0, 0.0)) -> tuple:
    if not s:
        return defaut
    return tuple(float(v) for v in s.split(","))


def _quat(s: str | None) -> tuple:
    ""
    w, x, y, z = _vec(s, (1.0, 0.0, 0.0, 0.0))
    n = math.sqrt(w * w + x * x + y * y + z * z) or 1.0
    return (w / n, x / n, y / n, z / n)


def _qmul(a: tuple, b: tuple) -> tuple:
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (aw * bw - ax * bx - ay * by - az * bz,
            aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw)


def _qrot(q: tuple, v: tuple) -> tuple:
    w, x, y, z = q
    p = _qmul(_qmul(q, (0.0,) + tuple(v)), (w, -x, -y, -z))
    return p[1:]


def angles(q: tuple) -> tuple:
    ""
    w, x, y, z = q
    m00 = 1 - 2 * (y * y + z * z)
    m10 = 2 * (x * y + w * z)
    m20 = 2 * (x * z - w * y)
    m21 = 2 * (y * z + w * x)
    m22 = 1 - 2 * (x * x + y * y)
    m01 = 2 * (x * y - w * z)
    m11 = 1 - 2 * (x * x + z * z)
    ay = math.asin(max(-1.0, min(1.0, -m20)))
    if abs(abs(ay) - math.pi / 2) < 0.01:
        return (0.0, ay, math.atan2(-m01, m11))
    return (math.atan2(m21, m22), ay, math.atan2(m10, m00))


def _lacet(q: tuple) -> float:
    return angles(q)[2]


def aplatir(chemin: str, pos=(0.0, 0.0, 0.0), rot=(1.0, 0.0, 0.0, 0.0), _prof: int = 0) -> list[dict]:
    ""


    e = prefab(chemin)
    if e is None or _prof > 6:
        return []
    out: list[dict] = []
    classes = {o.get("EntityClass") for o in e["objets"] if o.get("Type") == "Entity"}
    if (classes - MUETTES - {None}) and not e["ignore"]:
        out.append({"p": e["guid"], "x": pos[0], "y": pos[1], "z": pos[2], "rz": _lacet(rot)})
    par_id = {o.get("Id"): o for o in e["objets"]}

    def repere(o: dict, garde: int = 0) -> tuple:
        ""
        p, q = _vec(o.get("Pos")), _quat(o.get("Rotate"))
        parent = par_id.get(o.get("Parent"))
        if parent is not None and garde < 8:
            pp, pq = repere(parent, garde + 1)
            p = tuple(a + b for a, b in zip(pp, _qrot(pq, p)))
            q = _qmul(pq, q)
        return p, q

    for o in e["objets"]:
        typ = o.get("Type")





        if o.get("EntityClass") == "StanceSmartObject" and o.get("_so"):
            lp, lq = repere(o)
            p = tuple(a + b for a, b in zip(pos, _qrot(rot, lp)))
            q = _qmul(rot, lq)
            pr = o["_so"]
            cat = pr.get("sWH_AI_EntityCategory", "")
            if cat in ("Bed", "Seat", "SeatChair") and pr.get("guidSmartObjectType"):
                out.append({"so": "lit" if cat == "Bed" else "siege", "x": p[0], "y": p[1], "z": p[2],
                            "rz": _lacet(q), "guid": pr["guidSmartObjectType"],
                            "classe": pr.get("soclass_SmartObjectHelpers", ""), "cat": cat,
                            "type_lit": pr.get("esBedTypes", ""), "lecture": pr.get("esReadingQuality", ""),
                            "sommeil": pr.get("esSleepQuality", "")})
            continue
        if typ not in ("Brush", "Prefab") or o.get("HiddenInGame") == "1":
            continue




        if "nodraw" in o.get("Material", "").lower():
            continue
        lp, lq = repere(o)
        p = tuple(a + b for a, b in zip(pos, _qrot(rot, lp)))
        q = _qmul(rot, lq)
        if typ == "Brush" and o.get("Prefab", "").lower().endswith((".cgf", ".cga", ".cdf")):
            rx, ry, rz = angles(q)
            s = _vec(o.get("Scale"), (1.0, 1.0, 1.0))




            if max(s) - min(s) > 1e-3:
                s = (min(s),) * 3
            out.append({"m": o["Prefab"], "x": p[0], "y": p[1], "z": p[2], "rx": rx, "ry": ry, "rz": rz,
                        "s": s})
        elif typ == "Prefab":
            sous = _prefabs()["guid"].get(o.get("PrefabTemplate", ""))
            if sous is not None:
                out += aplatir(sous["chemin"], p, q, _prof + 1)
    return out




NOMS_DU_DECOR = {
    "barrel_with_utencils_medium": "Tonneau et ustensiles",
    "basket_rectangular_high_better_goods": "Grand panier de belles marchandises",
    "basket_rectangular_sparse": "Panier presque vide",
    "baskets_stracked_medium": "Paniers empilés",
    "beer_keg_on_stump_driping": "Tonnelet de bière sur souche (décor)",
    "bench_with_stuff_v1": "Banc encombré",
    "broken_junk_medium": "Bric-à-brac cassé",
    "cages_coveres_big": "Grandes cages bâchées",
    "cages_with_sack_medium": "Cages et sac",
    "canopy_small_shop": "Petit étal sous auvent",
    "crate_with_food_prepare_tools": "Caisse d'ustensiles de cuisine",
    "crate_with_goods_small": "Petite caisse de marchandises",
    "crate_with_pottery_goods_medium": "Caisse de poteries",
    "crate_with_sacs_small": "Petite caisse et sacs",
    "rustic_table_dishes_v1": "Table rustique et vaisselle",
    "rustic_table_dishes_v2": "Table rustique et vaisselle (2)",
    "stack_of_cages_small": "Petite pile de cages",
    "stack_of_goods_big": "Gros tas de marchandises",
    "stack_of_goods_big_v2": "Gros tas de marchandises (2)",
    "stack_of_sacks": "Pile de sacs",
    "table_drinking_station": "Table à boire (décor)",
    "table_with_dishes_and_lamp": "Table, vaisselle et lampe (décor)",
    "tent_with_goods_dealer": "Tente de marchand",
    "trunk_with_dishes": "Malle et vaisselle",
    "barrels_group_with_stuff_v1": "Tonneaux et fournitures",
    "barrels_group_with_stuff_v2": "Tonneaux et fournitures (2)",
    "barrels_group_with_stuff_v3_covered": "Tonneaux bâchés",
    "cart_with_things": "Charrette chargée",
    "cart_with_water": "Charrette à eau",
    "cooking_station_3": "Coin cuisine (3)",
    "cooking_station_v1": "Coin cuisine (décor)",
    "cooking_station_v2": "Coin cuisine (2)",
    "cooking_station_v3_shelves": "Coin cuisine et étagères (décor)",
    "crate_box_a_v1": "Caisse",
    "crate_box_a_v2": "Caisse (2)",
    "crate_box_a_v3_archers": "Caisse d'archer",
    "crate_box_a_v4_big": "Grosse caisse",
    "crate_box_a_v4_big_half_1": "Grosse caisse entamée",
    "crate_box_a_v4_big_half_2": "Grosse caisse entamée (2)",
    "crates_group_v1": "Groupe de caisses",
    "fireplace_small": "Petit feu (décor)",
    "laundry_line_with_baskets": "Corde à linge et paniers",
    "laundry_on_stick": "Linge sur un bâton",
    "rope_with_fur": "Corde et fourrures",
    "sacks_barrels": "Sacs et tonneaux",
    "stand_with_pinafore": "Support et tablier",
    "stash_forest_with_barrels": "Réserve de forêt, tonneaux",
    "stash_forest_with_sacks_and_barrel": "Réserve de forêt, sacs et tonneau",
    "stash_industriall_with_crates": "Réserve de caisses",
    "stash_industriall_with_firewood": "Réserve de bois de chauffe",
    "stash_industriall_with_sacks": "Réserve de sacs",
    "table_with_stuff": "Table encombrée",
    "table_with_supplies_v1": "Table de fournitures",
    "basket_regular_b_v1": "Panier",
    "basket_regular_b_v2": "Panier (2)",
    "basket_regular_b_v3": "Panier (3)",
    "crate_low_b_v1": "Caisse basse",
    "crate_low_b_v2_arrows": "Caisse basse de flèches",
    "crate_low_b_v3_axe": "Caisse basse et hache",
}


def au_sol(pieces: list[dict]) -> list[dict]:
    ""



    zs = [p.get("z", 0.0) for p in pieces if "m" in p or "p" in p or "so" in p]
    bas = min(zs) if zs else 0.0
    if bas <= 0.05:
        return pieces
    return [dict(p, z=p.get("z", 0.0) - bas) if "z" in p else p for p in pieces]


def _nom_du_decor(chemin: str) -> str | None:
    return NOMS_DU_DECOR.get(chemin.rsplit("/", 1)[-1].lower())









MOD_TENTE_HENRY = "objects/manmade/structures/living/tents/tent_big_round_a.cgf"
MOD_FEU = "84b335ee-22f2-411e-b3da-97f13575370c"
MOD_FEU_DECOR = "objects/manmade/task_specific_props/food_processing/cooking/camp_cooking_c_old.cgf"
MOD_RATELIER = "objects/manmade/common_decorations/weapons/polearm_pile_a.cgf"


MOD_MANNEQUIN = "objects/manmade/task_specific_props/combat/archery/target_straw.cgf"
TENTE_HOMMES = "objects/manmade/structures/living/tents/tent_big_square_a.cgf"
TENTE_INTENDANT = "objects/manmade/structures/living/tents/tent_big_round_a_color1.cgf"




TOUR_DE_GUET = "objects/manmade/structures/defensive/watchtowers/watchtower_a.cgf"
BUCHES = 6
RAYON_DES_BUCHES = 1.7





_HUNT = "objects/manmade/"
POSTE_DE_CHASSE = [
    (_HUNT + "common_furniture/tables/table_shabby_d_160_rough.cgf", 0.0, -2.0, 0.0, 0, 0, 90),
    (_HUNT + "common_furniture/chairs/low/chair_trunk_c.cgf", 0.9, 0.0, 0.0, 0, 0, 0),
    (_HUNT + "common_furniture/chairs/low/chair_trunk_c.cgf", -0.6, 0.0, 0.0, 0, 0, 0),
    (_HUNT + "common_furniture/chairs/low/chair_trunk_c.cgf", 0.2, 0.8, 0.0, 0, 0, 0),
    (_HUNT + "weapons/bows/bow_a.cgf", 0.2, 0.0, 0.82, 90, 90, 90),
    (_HUNT + "weapons/arrows/arrows_bundle_beige.cgf", 0.49, 0.07, 0.73, 90, 0, 0),
    (_HUNT + "common_furniture/furs/fur_hare.cgf", 0.0, 0.3, 0.75, 0, 0, 0),
    (_HUNT + "common_furniture/tables/table_shabby_d_80_rough.cgf", 0.2, 0.1, 0.0, 0, 0, 90),
    (_HUNT + "task_specific_props/foraging/hunting/deer_corpse.cgf", -0.1, -1.9, 0.78, 0, 0, 90),
    (_HUNT + "structures/industrial/drying_house/drying_rack_a.cgf", -0.2, 1.9, 0.0, 0, 0, 0),
    (_HUNT + "weapons/arrows/barrel_arrow_full_closed.cgf", 0.6, 2.1, 0.0, 0, 0, 90),
    (_HUNT + "common_furniture/sacks/sack_a.cgf", -1.1, 2.1, 0.0, 0, 0, 90),
    (_HUNT + "common_furniture/sacks/sack_b.cgf", -1.4, 1.7, 0.0, 0, 0, 90),
    (_HUNT + "task_specific_props/combat/archery/quiver_with_arrows.cgf", 0.1, 2.1, 0.24, 0, 0, 90),
]


def _modele(m: str, x: float = 0.0, y: float = 0.0, rz: float = 0.0) -> dict:
    return {"m": m, "x": x, "y": y, "z": 0.0, "rx": 0.0, "ry": 0.0, "rz": rz, "s": (1.0, 1.0, 1.0)}


def ajout(pieces: list[dict], achat: str | None = None) -> list[dict]:
    ""




    for p in pieces:
        p["ajout"] = True
        if achat:
            p["achat"] = achat
    return pieces




TABLE_80 = "objects/manmade/common_furniture/tables/table_shabby_d_80_rough.cgf"


PIQUET = "objects/manmade/task_specific_props/farming/animal_husbandry/horse_post_tree.cgf"
RATELIER_A_FOIN = "objects/manmade/structures/industrial/hay/hay_feeder_a.cgf"
MEULE_A = "objects/manmade/structures/industrial/hay/hay_small_pile_a.cgf"
MEULE_B = "objects/manmade/structures/industrial/hay/hay_small_pile_b.cgf"
SEAU = "objects/manmade/common_furniture/bucket/bucket_b.cgf"
CHARIOT_COUVERT = "objects/manmade/vehicles/wagons/wagon_b_covered.cgf"
CHARIOT_A_BANCS = "objects/manmade/vehicles/wagons/wagon_a_covered.cgf"



TABLE_DE_CAMP = "objects/manmade/common_furniture/tables/table_shabby_d_160_rough.cgf"
TABLE_DE_CAMP_H = 0.75
CHARIOT_DERRIERE = 3.6



POULAILLER = "objects/manmade/structures/industrial/coops/coop_a.cgf"
SAC_DE_GRAIN = "objects/manmade/common_furniture/sacks/sack_a.cgf"
PANIER_D_OEUFS = "objects/manmade/common_furniture/baskets/basket_eggs.cgf"
POULAILLER_X, POULAILLER_Y = 0.0, 7.5



BOITES = {
    "objects/manmade/structures/municipal/trading/shop_rustic_b.cgf": (-1.72, 1.60, -0.04, 1.04),
    "objects/manmade/common_furniture/tables/table_shabby_d_160_rough.cgf": (-0.79, 0.81, -0.43, 0.42),
    "objects/manmade/vehicles/wagons/wagon_b_covered.cgf": (-0.93, 1.07, -0.23, 3.88),
    "objects/manmade/task_specific_props/trade/counter_a.cgf": (-1.40, 1.40, 0.03, 0.96),

    "objects/manmade/structures/industrial/coops/coop_a.cgf": (-1.43, 0.63, -1.23, 1.14),
}
MARGE_DU_CORPS = 0.3
BOUCHER_PORTIQUE = "Objects/manmade/task_specific_props/food_processing/butchering/butchered_pig_cow_stand.cgf"
BOUCHER_COCHON = "Objects/manmade/task_specific_props/food_processing/butchering/butchered_pig.cgf"
BOUCHER_COCHON_Z = 0.0
BOUCHER_CROCHET = "Objects/manmade/task_specific_props/food_processing/butchering/butcher_hook.cgf"
BILLOT = "Objects/manmade/task_specific_props/wood_industry/woodcutting/chopping_block/chopping_block.cgf"
BILLOT_H = 0.55
COUPERET = "Objects/manmade/task_specific_props/food_processing/butchering/cleaver_a.cgf"

RONDINS_DE_CHAMBREE = ("objects/manmade/common_furniture/benches/low/bench_log_a.cgf",
                       "objects/manmade/common_furniture/benches/low/bench_log_b.cgf")
RAYON_DE_CHAMBREE, ECART_DES_PLACES = 2.1, 0.5





PIEUX = "Objects/manmade/structures/logistical/barriers/barrier_spikes.cgf"
BRASERO_CORBEILLE = "Objects/manmade/common_illumination/metal_basket_b.cgf"
BRASERO_BOIS = "Objects/manmade/task_specific_props/food_processing/cooking/fireplace_wood_c.cgf"
BRASERO_FLAMME_Z = 0.45
BRASERO_FEU = {"esAutoPhaseChangeCategory": "fireplace_burning", "sAutoPhaseChangeTimeOfDayPhases": "(7h,1);(20h,2)",
               "sAutoPhaseChangeWorldTimeDelayStdDev": "10m"}


PAVOIS_A = "Objects/manmade/task_specific_props/combat/pavises/pavise_a.cgf"
PAVOIS_B = "Objects/manmade/task_specific_props/combat/pavises/pavise_b.cgf"
PAVOIS_SUR_PIED = "Objects/manmade/task_specific_props/combat/pavises/pavise_stick.cgf"
LATRINES = "Objects/manmade/structures/living/outhouses/latrine_camp_a.cgf"
CHARIOT_DE_FOIN = "objects/manmade/vehicles/wagons/wagon_c_hay.cgf"
TABOURET = "objects/manmade/common_furniture/chairs/low/chair_trunk_c.cgf"












CARRE_DE_POTAGER = "objects/manmade/structures/theological/monasteries/unique/sedlec_monastery_dlc3/garden_curb_a.cgf"
CARRE_COTE = 8.70
CARRE_CENTRE = (-0.775, 0.74)
CARRE_DESSUS = 0.24
CARRE_BORD = 0.45
PLANTS = ("objects/manmade/food/food/vegetable/cabbage.cgf",
          "objects/natural/vegetation/plants/beet_veg.cgf",
          "objects/natural/vegetation/plants/onion_wild.cgf")
EPOUVANTAIL = "objects/manmade/task_specific_props/farming/horticulture/scarecrow.cgf"

POTAGERS = {
    "potager_petit": ("Petit potager (3,5 × 3,5 m)", 0.4, False),
    "potager_moyen": ("Potager moyen (5 × 5 m)", 0.6, False),
    "potager_grand": ("Grand potager (7 × 7 m), avec son épouvantail", 0.8, True),
}
RANG = 0.80
PAS = 0.85


def taille_du_potager(cle: str) -> tuple[float, float]:
    ""
    k = POTAGERS[cle][1]
    c = (CARRE_COTE - 2 * CARRE_BORD) * k
    return round(c, 3), round(c, 3)


def potager(cle: str) -> list[dict]:
    _, k, epouvantail = POTAGERS[cle]
    lx, ly = taille_du_potager(cle)
    leve = CARRE_DESSUS * (1 - k)
    dessus = CARRE_DESSUS
    pieces = [{"m": CARRE_DE_POTAGER, "x": round(-CARRE_CENTRE[0] * k, 3), "y": round(-CARRE_CENTRE[1] * k, 3),
               "z": round(leve, 3), "rx": 0.0, "ry": 0.0, "rz": 0.0, "s": (k, k, k)}]

    r, y = 0, -ly / 2 + 0.35
    while y <= ly / 2 - 0.35 + 1e-6:
        x = -lx / 2 + 0.35
        while x <= lx / 2 - 0.35 + 1e-6:
            pl = _modele(PLANTS[r % 3], round(x, 3), round(y, 3))
            pl["z"] = dessus
            pieces.append(pl)
            x += PAS
        r, y = r + 1, y + RANG
    if epouvantail:
        e = _modele(EPOUVANTAIL, round(lx / 2 + 0.9, 3), round(ly / 2 + 0.4, 3))
        pieces.append(e)
    return pieces


ETAL = "Objects/manmade/structures/municipal/trading/shop_rustic_b.cgf"
AUBERGE = "objects/manmade/"


def place_hors_des_meubles(objet: dict, marge: float = MARGE_DU_CORPS) -> tuple[list[str], list[str]]:
    ""

    import math as _m
    places = [p for p in objet.get("pieces", []) if p.get("so") == "vendeur"]
    connus, dedans = [], []
    for p in objet.get("pieces", []):
        m = str(p.get("m") or "").lower().replace("\\", "/")
        b = BOITES.get(m)
        if b is None:
            continue
        connus.append(m.rsplit("/", 1)[-1])
        a = float(p.get("rz") or 0.0)
        c, s = _m.cos(a), _m.sin(a)
        for pl in places:
            dx, dy = float(pl["x"]) - float(p.get("x") or 0.0), float(pl["y"]) - float(p.get("y") or 0.0)
            lx, ly = c * dx + s * dy, -s * dx + c * dy
            if b[0] - marge <= lx <= b[1] + marge and b[2] - marge <= ly <= b[3] + marge:
                dedans.append(m.rsplit("/", 1)[-1])
    return connus, dedans


def place_de_vendeur() -> dict:
    ""



    return {"so": "vendeur", "x": 0.0, "y": 1.5, "z": 0.0, "rz": 3.141593,
            "guid": "e9cb715f-bdfe-4bbe-8ad8-9f07b6ed9893", "classe": "", "cat": "", "type_lit": "",
            "lecture": "", "sommeil": ""}


def rondins_de_chambree() -> list[dict]:
    ""


    import math as _m
    assise = next((dict(p) for p in aplatir("Bench/bench_1place_low") if p.get("so") == "siege"), None)
    out: list[dict] = []
    for k, a_deg in enumerate((90.0, 210.0, 330.0)):
        a = _m.radians(a_deg)
        x, y = RAYON_DE_CHAMBREE * _m.cos(a), RAYON_DE_CHAMBREE * _m.sin(a)
        rz = _m.atan2(-x, y)
        out.append(_modele(RONDINS_DE_CHAMBREE[k % 2], x, y, rz))
        if assise is not None:
            for s in (-ECART_DES_PLACES, ECART_DES_PLACES):
                place = dict(assise)
                place.update({"x": x + _m.cos(rz) * s, "y": y + _m.sin(rz) * s, "z": 0.0, "rz": rz})
                out.append(place)
    return out


def objets_du_camp() -> list[dict]:


    import math as _m
    lits = []
    for ox, oy in ((-0.9, -0.9), (0.9, -0.9), (-0.9, 0.9), (0.9, 0.9)):


        v = _m.pi / 2
        x, y = ox * _m.cos(v) - oy * _m.sin(v), ox * _m.sin(v) + oy * _m.cos(v)
        lits += aplatir("Bed/bed_low", (x, y, 0.0), (0.0, 0.0, 0.0, 1.0))
    buches = []
    for k in range(BUCHES):
        a = 2 * _m.pi * k / BUCHES
        buches.append({"buche": True, "x": RAYON_DES_BUCHES * _m.cos(a), "y": RAYON_DES_BUCHES * _m.sin(a),
                       "z": 0.0, "feu_x": 0.0, "feu_y": 0.0})
    return [
        {"cle": "tente_henry", "nom": "Votre tente (votre lit, réservé à vous)", "source": "mod",
         "pieces": [{"recette": "tente_henry", "x": 0.0, "y": 0.0, "z": 0.0}]},
        {"cle": "cabane_henry", "nom": "Votre cabane (votre lit, réservé à vous)", "source": "mod",
         "pieces": [{"recette": "cabane_henry", "x": 0.0, "y": 0.0, "z": 0.0}]},



        {"cle": "tente_henry_vide", "nom": "Votre tente, vide (à aménager : votre lit, vos coffres…)", "source": "mod",
         "pieces": [_modele(MOD_TENTE_HENRY)]},
        {"cle": "cabane_henry_vide", "nom": "Votre cabane, vide (à aménager : votre lit, vos coffres…)", "source": "mod",
         "pieces": [{"recette": "cabane_henry_vide", "x": 0.0, "y": 0.0, "z": 0.0}]},


        {"cle": "coffret_banque", "nom": "Coffret de la banque (E : la Banque ; maintenir E : Scriptorium)", "source": "mod",
         "pieces": [{"ent": "Scriptorium_Banque", "modele": "objects/manmade/common_furniture/chests/chest-small-a.cgf",
                     "x": 0.0, "y": 0.0, "z": 0.0, "rz": 0.0}]},
        {"cle": "mini_tente", "nom": "Tente miniature (E : la Gestion du camp)", "source": "mod",
         "pieces": [{"ent": "Scriptorium_Amenagement", "modele": "objects/manmade/structures/living/tents/tent_small_a.cgf",
                     "echelle": 0.1, "x": 0.0, "y": 0.0, "z": 0.0, "rz": 0.0}]},
        {"cle": "intendant", "nom": "Le Directeur (ses missions)", "source": "mod",
         "pieces": [{"recette": "intendant", "x": 0.0, "y": 0.0, "z": 0.0}]},





        {"cle": "tente_intendant", "nom": "Tente du Directeur (son lit, réservé à lui)", "source": "mod",
         "pieces": [_modele(TENTE_INTENDANT)] + aplatir("Bed/bed_low", (1.0, 0.13, 0.0), (0.70711, 0.0, 0.0, -0.70711))
         + [{"recette": "intendant", "x": 0.0, "y": 3.2, "z": 0.0}]},
        {"cle": "tour_de_guet", "nom": "Tour de guet (on y monte ; 2 archers à l'alerte)", "source": "mod",
         "pieces": [_modele(TOUR_DE_GUET), {"recette": "tour_de_guet", "x": 0.0, "y": 0.0, "z": 0.0}]},


        {"cle": "palissade", "nom": "Palissade, un pan (8 m)", "source": "mod",
         "pieces": [_modele("Objects/manmade/structures/defensive/walls/palisade/palisade_wall_b_v4.cgf", x=3.85, y=-0.12)]},
        {"cle": "porte_palissade", "nom": "Porte de palissade", "source": "mod",
         "pieces": [_modele("Objects/manmade/structures/logistical/fences/fence_4rod_gate_02.cgf", x=-1.48, rz=-1.5708)]},
        {"cle": "tente_hommes", "nom": "Tente des hommes (4 lits)", "source": "mod",
         "pieces": [_modele(TENTE_HOMMES)] + lits},
        {"cle": "feu_camp", "nom": "Feu de camp et ses 6 bûches", "source": "mod",
         "pieces": [{"p": MOD_FEU, "x": 0.0, "y": 0.0, "z": 0.0, "rz": 0.0}, _modele(MOD_FEU_DECOR)] + buches},
        {"cle": "ratelier_camp", "nom": "Râtelier du camp (armes)", "source": "mod",
         "pieces": [_modele(MOD_RATELIER)]},
        {"cle": "mannequin_paille", "nom": "Mannequin de paille (entraînement)", "source": "mod",
         "pieces": [_modele(MOD_MANNEQUIN)]},


        {"cle": "poste_de_chasse", "nom": "Poste de chasse (l'établi des chasseurs)", "source": "mod",
         "pieces": [{"m": m, "x": fwd, "y": -lat, "z": up, "rx": _m.radians(rx), "ry": _m.radians(ry),
                     "rz": _m.radians(rz), "s": (1.0, 1.0, 1.0)}
                    for m, fwd, lat, up, rx, ry, rz in POSTE_DE_CHASSE]


                   + ajout([{"m": ETAL, "x": 4.5, "y": 0.0, "z": 0.0, "rx": 0.0, "ry": 0.0, "rz": 0.0, "s": (1.0, 1.0, 1.0)}]
                           + aplatir("exteriorDecoration/camp_supplies/rope_with_fur", (6.7, 0.6, 0.0))
                           + [dict(place_de_vendeur(), x=4.5)])},






        {"cle": "abreuvoir", "nom": "Abreuvoir des chevaux", "source": "jeu",
         "pieces": aplatir("animalcare/horseParkingSpot")},




        {"cle": "ligne_des_chevaux", "nom": "Ligne des chevaux (deux places, foin, seaux)", "source": "jeu",
         "pieces": aplatir("animalcare/horseParkingSpot")
                   + [_modele(PIQUET, -4.0, 0.0, 0.0), _modele(PIQUET, 4.0, 0.0, 0.0),
                      _modele(RATELIER_A_FOIN, 6.5, 1.0, _m.radians(90)),
                      _modele(MEULE_A, -2.5, 1.5, _m.radians(20)), _modele(MEULE_B, 2.5, 1.5, _m.radians(-30)),
                      _modele(SEAU, -1.0, 1.2, 0.0), _modele(SEAU, 1.0, 1.3, _m.radians(40))]},


        {"cle": "chariot_couvert", "nom": "Chariot couvert", "source": "jeu", "pieces": [_modele(CHARIOT_COUVERT)]},
        {"cle": "chariot_a_bancs", "nom": "Chariot couvert à bancs", "source": "jeu", "pieces": [_modele(CHARIOT_A_BANCS)]},
        {"cle": "chariot_de_foin", "nom": "Chariot de foin", "source": "jeu", "pieces": [_modele(CHARIOT_DE_FOIN)]},



        {"cle": "feu_de_chambree", "nom": "Feu de chambrée (foyer, chaudron et trois rondins)", "source": "mod",
         "pieces": [{"p": MOD_FEU, "x": 0.0, "y": 0.0, "z": 0.0, "rz": 0.0}, _modele(MOD_FEU_DECOR)] + rondins_de_chambree()},



        {"cle": "etal_vivandiere", "nom": "Table de la vivandière (sa charrette, son poulailler et sa poule, en-cas aux hommes)", "source": "jeu",
         "pieces": [_modele(TABLE_DE_CAMP)]
                   + [{"m": "Objects/manmade/" + f, "x": x, "y": y, "z": TABLE_DE_CAMP_H, "rx": 0.0, "ry": 0.0, "rz": rz, "s": (1.0, 1.0, 1.0)}
                      for f, x, y, rz in (("food/food/bread.cgf", -0.45, 0.05, 0.3), ("food/food/bread_roll.cgf", -0.15, 0.12, 0.0),
                                          ("food/food/meat_bacon.cgf", 0.25, 0.05, 1.2), ("food/food/cheese_quarter.cgf", 0.5, 0.1, 0.6))]
                   + [_modele(CHARIOT_COUVERT, -1.82, CHARIOT_DERRIERE, -_m.pi / 2)]

                   + [dict(_modele(POULAILLER, POULAILLER_X, POULAILLER_Y, _m.pi), ajout=True),
                      dict(_modele(SAC_DE_GRAIN, POULAILLER_X - 1.6, POULAILLER_Y - 0.6, 0.4), ajout=True),
                      dict(_modele(PANIER_D_OEUFS, POULAILLER_X + 1.5, POULAILLER_Y - 0.7, -0.3), ajout=True)]
                   + [dict(place_de_vendeur(), y=1.0)]},


        {"cle": "coin_boucher", "nom": "Coin du boucher (portique, cochon pendu, billot)", "source": "jeu",
         "pieces": [_modele(BOUCHER_PORTIQUE),
                    {"m": BOUCHER_COCHON, "x": 0.0, "y": 0.0, "z": BOUCHER_COCHON_Z, "rx": 0.0, "ry": 0.0, "rz": 0.0, "s": (1.0, 1.0, 1.0)},
                    _modele(BOUCHER_CROCHET, 0.75, 0.0, 0.0), _modele(BILLOT, -1.4, -0.6, 0.4),
                    {"m": COUPERET, "x": -1.4, "y": -0.6, "z": BILLOT_H, "rx": 0.0, "ry": 0.0, "rz": 0.8, "s": (1.0, 1.0, 1.0)}]},


        {"cle": "pieux", "nom": "Chevaux de frise (pieux, 3 m)", "source": "jeu", "pieces": [_modele(PIEUX)]},


        {"cle": "brasero", "nom": "Brasero (la corbeille à feu, allumée la nuit)", "source": "jeu",
         "pieces": [_modele(BRASERO_CORBEILLE),
                    {"m": BRASERO_BOIS, "x": 0.0, "y": 0.0, "z": 0.35, "rx": 0.0, "ry": 0.0, "rz": 0.0, "s": (0.94, 0.94, 0.94)},
                    {"ent": "RuntimePrefabAutoPhase", "x": 0.0, "y": 0.0, "z": BRASERO_FLAMME_Z, "rz": 0.0, "props": BRASERO_FEU}]},



        {"cle": "banniere", "nom": "Bannière (la flamme rouge à couronne du jeu)", "source": "jeu", "pieces": aplatir("flag/flag")},

        {"cle": "pavois", "nom": "Pavois peint", "source": "jeu", "pieces": [_modele(PAVOIS_A)]},
        {"cle": "pavois_b", "nom": "Pavois, second modèle", "source": "jeu", "pieces": [_modele(PAVOIS_B)]},


        {"cle": "pavois_sur_pied", "nom": "Pavois sur son pied", "source": "jeu",
         "pieces": [_modele(PAVOIS_A), _modele(PAVOIS_SUR_PIED)]},


        {"cle": "latrines", "nom": "Latrines de camp (à 20 m au moins des tentes, des feux et de la cuisine)", "source": "jeu",
         "pieces": [_modele(LATRINES)]},
        {"cle": "etal_cueillette", "nom": "Étal du potager (l'établi du jardinier)", "source": "jeu",
         "pieces": aplatir("profession/apothecary/sortingHerbs")
                   + aplatir("Stash/basket_vegetables_a", (1.6, 0.4, 0.0))
                   + aplatir("Stash/basket_vegetables_b", (-1.6, 0.4, 0.0))},






        {"cle": "etal_jardiniers", "nom": "Étal du jardinier (vente des légumes)", "source": "jeu",
         "pieces": [{"m": ETAL, "x": 0.0, "y": 0.0, "z": 0.0, "rx": 0.0, "ry": 0.0, "rz": 0.0, "s": (1.0, 1.0, 1.0)}]
                   + aplatir("stash/basket_vegetables_a", (-0.55, 0.55, 0.95))
                   + aplatir("stash/basket_vegetables_b", (0.55, 0.55, 0.95))
                   + [place_de_vendeur()]},
        {"cle": "etal_bucheron", "nom": "Étal du bûcheron (vente du bois, des branches et du charbon)", "source": "jeu",
         "pieces": [{"m": ETAL, "x": 0.0, "y": 0.0, "z": 0.0, "rx": 0.0, "ry": 0.0, "rz": 0.0, "s": (1.0, 1.0, 1.0)}]
                   + aplatir("interiordecoration/crates/crate_with_firewood", (-1.6, 0.2, 0.0))
                   + aplatir("interiordecoration/crates/crate_with_firewood", (1.6, 0.2, 0.0))
                   + [place_de_vendeur()]},


        {"cle": "etal_chasseurs", "nom": "Étal des chasseurs (vente du gibier et des peaux)", "source": "jeu",
         "pieces": [{"m": ETAL, "x": 0.0, "y": 0.0, "z": 0.0, "rx": 0.0, "ry": 0.0, "rz": 0.0, "s": (1.0, 1.0, 1.0)}]
                   + aplatir("exteriorDecoration/camp_supplies/rope_with_fur", (2.2, 0.6, 0.0))
                   + [place_de_vendeur()]},




        {"cle": "etal_taverne", "nom": "Étal du tavernier (bière et vin au verre)", "source": "jeu",
         "pieces": [{"m": ETAL, "x": 0.0, "y": 0.0, "z": 0.0, "rx": 0.0, "ry": 0.0, "rz": 0.0, "s": (1.0, 1.0, 1.0)}]
                   + [{"m": AUBERGE + f, "x": x, "y": y, "z": z, "rx": 0.0, "ry": 0.0, "rz": rz, "s": (1.0, 1.0, 1.0)}
                      for f, x, y, z, rz in (
                          ("common_furniture/barrels/barrel_beer.cgf", -1.9, 1.0, 0.0, 0.0),
                          ("common_furniture/barrels/barrel_a.cgf", 1.9, 1.0, 0.0, 0.0),
                          ("task_specific_props/household/cooking_eating/jugs/tin_jug_01.cgf", 1.9, 1.0, 0.96, 0.0),
                          ("common_furniture/barrels/barrel_small_spigot_plug.cgf", 0.7, 0.55, 0.95, 1.5708),
                          ("task_specific_props/household/cooking_eating/tankards/tankard_a.cgf", -0.55, 0.35, 0.95, 0.0),
                          ("task_specific_props/household/cooking_eating/tankards/tankard_a.cgf", -0.30, 0.45, 0.95, 0.6),
                          ("task_specific_props/household/cooking_eating/tankards/tankard_a.cgf", -0.05, 0.35, 0.95, 1.2),
                          ("task_specific_props/household/cooking_eating/jugs/jug_b_mead.cgf", 0.25, 0.45, 0.95, 0.0),
                          ("food/drinks/wineskin_rustic.cgf", -0.85, 0.5, 0.95, 0.3),
                          ("common_illumination/lamp_table_rustic_a.cgf", 0.0, 0.7, 0.95, 0.0))]
                   + [place_de_vendeur()]},



        {"cle": "comptoir_bains", "nom": "Comptoir de la Dame des bains (on la paie ici)", "source": "jeu",
         "pieces": [{"m": ETAL, "x": 0.0, "y": 0.0, "z": 0.0, "rx": 0.0, "ry": 0.0, "rz": 0.0, "s": (1.0, 1.0, 1.0)},
                    place_de_vendeur()]},



        {"cle": "rond_marchand", "nom": "Rond du marchand (à réserver à un métier)", "source": "jeu",
         "pieces": [dict(place_de_vendeur(), y=0.0, rz=0.0)]},
        {"cle": "rond_client", "nom": "Rond du client (à réserver au même métier)", "source": "jeu",
         "pieces": [{"so": "client", "x": 0.0, "y": 0.0, "z": 0.0, "rz": 0.0, "guid": "", "classe": "", "cat": "",
                     "type_lit": "", "lecture": "", "sommeil": ""}]},


        {"cle": "pupitre_coursier", "nom": "Pupitre du coursier (il y attend les commandes)", "source": "jeu",
         "pieces": aplatir("bookstand/bookstand_write")
                   + [{"so": "pupitre", "x": 0.02, "y": -0.46, "z": 0.0, "rz": 0.0,
                       "guid": "48a1d343-43bd-60ca-8814-430e2d4aea9e", "classe": "", "cat": "", "type_lit": "",
                       "lecture": "", "sommeil": ""}]


                   + ajout([_modele(TABLE_80, 1.4, 0.2, _m.radians(90)), _modele(TABOURET, 1.4, -0.7, 0.0)],
                           achat="coursier_mobilier")},






        {"cle": "bureau_directeur", "nom": "Bureau du Directeur (il y travaille entre ses tournées)", "source": "jeu",
         "pieces": [
             {"m": "Objects/manmade/common_furniture/tables/table_shabby_b_230_bright.cgf", "x": -0.01, "y": 0.327,
              "z": 0.002, "rx": 0.0, "ry": 0.0, "rz": 0.0, "s": (1.0, 1.0, 1.0)},
             {"m": "Objects/manmade/common_furniture/benches/low/bench_shabby_c.cgf", "x": 0.001, "y": -0.333,
              "z": 0.002, "rx": 0.0, "ry": 0.0, "rz": -3.14159, "s": (1.0, 1.0, 1.0)},
             {"m": "Objects/manmade/task_specific_props/read_and_write/bookstands/bookstand_table.cgf", "x": 0.063, "y": 0.286, "z": 0.746,
              "rx": 0.0, "ry": 0.0, "rz": 1.5708, "s": (1.0, 1.0, 1.0)},
             {"m": "Objects/manmade/task_specific_props/read_and_write/inkwell/inkwell.cgf", "x": 0.467, "y": 0.275, "z": 0.752,
              "rx": 0.0, "ry": 0.0, "rz": 0.0, "s": (1.0, 1.0, 1.0)},
             {"m": "Objects/manmade/task_specific_props/read_and_write/scrolls/parchment.cgf", "x": -0.28, "y": 0.2, "z": 0.752,
              "rx": 0.0, "ry": 0.0, "rz": 0.3, "s": (1.0, 1.0, 1.0)},
             {"so": "bureau", "x": 0.001, "y": -0.333, "z": 0.002, "rz": 3.14159,
              "guid": "57cbebae-c19a-443b-8945-999d8ee87955", "classe": "Sit_1Place_Bench_Low", "cat": "Seat",
              "type_lit": "Chair", "lecture": "bench_notable", "sommeil": ""}]},



        {"cle": "meule", "nom": "Meule à aiguiser (affûter ses armes)", "source": "jeu",
         "pieces": [{"ent": "Grindstone", "x": 0.0, "y": 0.0, "z": 0.0, "rz": 0.0}]},


        {"cle": "baquet", "nom": "Baquet pour se laver", "source": "jeu", "pieces": aplatir("Water/WaterTub")},
        {"cle": "point_d_eau", "nom": "Point d'eau (se laver, laver son linge)", "source": "jeu",
         "pieces": aplatir("Water/waterResource")},


        {"cle": "prie_dieu", "nom": "Prie-Dieu (prier)", "source": "jeu",
         "pieces": [{"m": "Objects/manmade/common_furniture/kneelers/kneeler.cgf", "x": -0.05, "y": -0.85, "z": 0.0,
                     "rx": 0.0, "ry": 0.0, "rz": 0.0, "s": (1.0, 1.0, 1.0)}]},



        {"cle": "fumoir", "nom": "Fumoir (fumer la viande)", "source": "jeu",
         "pieces": aplatir("profession/butcher/butcher_smokeHouse")},
        {"cle": "sechoir", "nom": "Séchoir (sécher viande, fruits, herbes)", "source": "jeu",
         "pieces": aplatir("profession/butcher/butcher_dryer")},
    ] + [{"cle": c, "nom": POTAGERS[c][0], "source": "jeu", "pieces": potager(c)} for c in POTAGERS]


def catalogue() -> list[tuple[str, list[dict]]]:
    ""
    out = []
    for rub, liste in RUBRIQUES:
        objets = []
        for cle, nom, ch in liste:
            pieces = au_sol(aplatir(ch))

            for x in pieces:
                if "m" in x:
                    x["m"] = str(x["m"]).replace(chr(92), "/")



            if cle == "cible" or cle.startswith("cible_"):
                pieces = [x for x in pieces if not str(x.get("m", "")).lower().endswith("archery/target.cgf")]
            if pieces:
                objets.append({"cle": cle, "nom": nom, "source": ch, "pieces": pieces})
        out.append((rub, objets))
    out.insert(1, (RANGER[0], [{"cle": "coffre", "nom": RANGER[1][0][1], "source": "Stash",
                                "pieces": [{"coffre": COFFRE, "x": 0.0, "y": 0.0, "z": 0.0}]},


                               {"cle": "caisse_atelier", "nom": CAISSE_ATELIER, "source": "Scriptorium_Caisse",
                                "pieces": [{"caisse": COFFRE, "x": 0.0, "y": 0.0, "z": 0.0}]}]))
    out.insert(0, ("Objets du camp", objets_du_camp()))
    out.append(("Tentes", [{"cle": c, "nom": n, "source": TENTES + f + ".cgf",
                            "pieces": [{"m": TENTES + f + ".cgf", "x": 0.0, "y": 0.0, "z": 0.0,
                                        "rx": 0.0, "ry": 0.0, "rz": 0.0, "s": (1.0, 1.0, 1.0)}]}
                           for c, n, f in TENTES_CHOIX]))
    decor = []
    for ch, e in sorted(_prefabs()["chemin"].items()):
        if ch.startswith(tuple(d.lower() for d in DECOR)) and not e["ignore"]:
            pieces = au_sol(aplatir(e["chemin"]))
            if pieces and _nom_du_decor(e["chemin"]):
                decor.append({"cle": "decor_" + re.sub(r"[^a-z0-9]+", "_", ch.rsplit("/", 1)[-1]),
                              "nom": _nom_du_decor(e["chemin"]), "source": e["chemin"], "pieces": pieces})
    out.append(("Décor du jeu", decor))
    return out


def _n(v: float) -> str:
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s






TRAVERSABLES = ("ratelier", "cible")







SOLIDES = ("cabane_henry", "cabane_henry_vide", "tente_henry", "tente_henry_vide", "tour_de_guet")


def traversable(cle: str) -> bool:
    return not any(cle == t or cle.startswith(t + "_") for t in SOLIDES)






MAISON = "Objects/manmade/"


def _decor_de(cle: str) -> list[dict]:
    for _, objets in catalogue():
        for o in objets:
            if o["cle"] == cle:
                return [x for x in o["pieces"] if ("m" in x and "shop_rustic_b" not in x["m"]) or "p" in x]
    return []


def _pieces(liste) -> list[dict]:
    return [{"m": MAISON + f, "x": x, "y": y, "z": z, "rx": 0.0, "ry": 0.0, "rz": rz, "s": (1.0, 1.0, 1.0)}
            for f, x, y, z, rz in liste]


def decors() -> dict[str, list[dict]]:
    ""
    return {
        "bois": _decor_de("etal_bucheron"),



        "jardiniers": _decor_de("etal_jardiniers") + _pieces((
            ("food/food/vegetable/basket_rectangular_a_carrots.cgf", -0.75, 0.45, 0.95, 0.0),
            ("food/food/vegetable/basket_rectangular_a_leek.cgf", -0.2, 0.45, 0.95, 0.0),
            ("food/food/vegetable/basket_rectangular_a_turnip.cgf", 0.35, 0.45, 0.95, 0.0),
            ("food/food/vegetable/cabbage_head.cgf", 0.8, 0.35, 0.95, 0.0),
            ("food/food/vegetable/cabbage_head.cgf", 0.95, 0.6, 0.95, 0.9),
            ("food/food/vegetable/garlic_bundle.cgf", 0.6, 0.2, 0.95, 0.4),
            ("food/food/sacks/sack_onions.cgf", -1.9, 0.8, 0.0, 0.0),
            ("food/food/vegetable/basket_d_carrot_parsnip.cgf", 1.9, 0.8, 0.0, 0.0))),
        "chasseurs": _decor_de("etal_chasseurs"),
        "taverne": _decor_de("etal_taverne"),


        "femmes": _pieces((
            ("task_specific_props/baths/washbasin_a.cgf", -2.1, -0.3, 0.0, 0.0),
            ("task_specific_props/baths/comb.cgf", 0.05, 0.35, 0.95, 0.4),
            ("task_specific_props/baths/razor_barber.cgf", 0.25, 0.4, 0.95, 1.1),
            ("task_specific_props/household/cleaning/scrub_brush.cgf", 0.5, 0.45, 0.95, 0.3),
            ("task_specific_props/medical_care/bandage.cgf", 0.75, 0.4, 0.95, 0.0),
            ("task_specific_props/household/washing/laundry_bundle.cgf", -0.8, 0.5, 0.95, 0.5),
            ("common_furniture/baskets/basket_laundry.cgf", -1.9, 0.8, 0.0, 0.0),
            ("common_furniture/bucket/bucket_a_a_water.cgf", 1.9, 0.8, 0.0, 0.0))),

        "eau": _pieces((
            ("common_furniture/bucket/bucket_a_a_water.cgf", -1.9, 0.8, 0.0, 0.0),
            ("common_furniture/bucket/bucket_a_a_water.cgf", 1.9, 0.8, 0.0, 0.6),
            ("task_specific_props/metal_industry/mining/water_bucket.cgf", -0.5, 0.45, 0.95, 0.0),
            ("task_specific_props/household/cooking_eating/jugs/tin_jug_01.cgf", 0.1, 0.45, 0.95, 0.0),
            ("task_specific_props/household/cooking_eating/tankards/tankard_a.cgf", 0.45, 0.35, 0.95, 0.0),
            ("task_specific_props/household/cooking_eating/tankards/tankard_a.cgf", 0.7, 0.4, 0.95, 0.8))),
    }







MAISON_D_HENRY = "structures/living/houses/wooden/small_roof_to_ground_house_a"
DEMI_TOUR = (0.0, 0.0, 0.0, 1.0)


LIT_DE_LA_CABANE = (-3.13, -1.6, 0.3)







RONDIN_DU_FEU = "objects/manmade/common_furniture/chairs/low/chair_trunk_c.cgf"


def rondins_du_feu() -> list[dict]:
    import math as _m
    assise = next((dict(p) for p in aplatir("Bench/bench_1place_low") if p.get("so") == "siege"), None)
    out: list[dict] = []
    for k in range(BUCHES):
        a = 2 * _m.pi * k / BUCHES
        x, y = RAYON_DES_BUCHES * _m.cos(a), RAYON_DES_BUCHES * _m.sin(a)
        rz = _m.atan2(-x, y)
        out.append(_modele(RONDIN_DU_FEU, x, y, rz))
        if assise is not None:
            place = dict(assise)
            place.update({"x": x, "y": y, "z": 0.0, "rz": rz})
            out.append(place)
    return out


def objets_du_monde_du_socle() -> list[dict]:
    maison = aplatir(MAISON_D_HENRY, (0.0, 0.0, 0.0), DEMI_TOUR)
    for x in maison:
        if "m" in x:
            x["m"] = str(x["m"]).replace(chr(92), "/")
    lit = aplatir("Bed/bed_low", LIT_DE_LA_CABANE, (1.0, 0.0, 0.0, 0.0))
    return [
        {"cle": "cabane_henry__socle", "nom": "Votre cabane (votre lit, réservé à vous)", "source": MAISON_D_HENRY,
         "pieces": maison + lit},
        {"cle": "cabane_henry_vide__socle", "nom": "Votre cabane, vide (à aménager : votre lit, vos coffres…)",
         "source": MAISON_D_HENRY, "pieces": [dict(x) for x in maison]},
        {"cle": "feu_camp__socle", "nom": "Feu de camp et ses 6 rondins", "source": "mod",
         "pieces": [{"p": MOD_FEU, "x": 0.0, "y": 0.0, "z": 0.0, "rz": 0.0}, _modele(MOD_FEU_DECOR)] + rondins_du_feu()},
    ]


def texte_lua() -> str:
    ""
    lignes = ["-- GENERE par choses/editeur_du_camp/palette.py a chaque construction. Ne pas retoucher.",
              "SCRIPTORIUM_PALETTE = {"]
    for _, objets in catalogue() + [("monde du socle", objets_du_monde_du_socle())]:
        for o in objets:
            ps = []
            for p in o["pieces"]:
                if "p" in p:
                    ps.append(f'{{ p = "{p["p"]}", x = {_n(p["x"])}, y = {_n(p["y"])}, z = {_n(p["z"])}, '
                              f'rz = {_n(p["rz"])} }}')
                elif "so" in p:
                    aj = (", ajout = true" if p.get("ajout") else "") + (f', achat = "{p["achat"]}"' if p.get("achat") else "")
                    ps.append(f'{{ so = "{p["so"]}", x = {_n(p["x"])}, y = {_n(p["y"])}, z = {_n(p["z"])}, '
                              f'rz = {_n(p["rz"])}, guid = "{p["guid"]}", classe = "{p["classe"]}", '
                              f'cat = "{p["cat"]}", type_lit = "{p["type_lit"]}", lecture = "{p["lecture"]}", '
                              f'sommeil = "{p["sommeil"]}"{aj} }}')
                elif "coffre" in p:
                    ps.append(f'{{ coffre = "{p["coffre"]}", x = 0, y = 0, z = 0 }}')
                elif "caisse" in p:
                    ps.append(f'{{ caisse = "{p["caisse"]}", x = 0, y = 0, z = 0 }}')
                elif "recette" in p:
                    ps.append(f'{{ recette = "{p["recette"]}", x = {_n(p["x"])}, y = {_n(p["y"])}, z = 0 }}')
                elif "ent" in p:


                    en_plus = (f', modele = "{p["modele"]}"' if p.get("modele") else "") + \
                              (f', echelle = {_n(p["echelle"])}' if p.get("echelle") else "") + \
                              (", props = { " + ", ".join(f'{k} = "{v}"' for k, v in p["props"].items()) + " }"
                               if p.get("props") else "")
                    ps.append(f'{{ ent = "{p["ent"]}", x = {_n(p["x"])}, y = {_n(p["y"])}, z = {_n(p["z"])}, '
                              f'rz = {_n(p["rz"])}{en_plus} }}')
                elif "buche" in p:
                    ps.append(f'{{ buche = true, x = {_n(p["x"])}, y = {_n(p["y"])}, z = 0, '
                              f'feu_x = {_n(p["feu_x"])}, feu_y = {_n(p["feu_y"])} }}')
                else:
                    sx, sy, sz = p["s"]
                    ech = "" if (sx, sy, sz) == (1.0, 1.0, 1.0) else f", sx = {_n(sx)}, sy = {_n(sy)}, sz = {_n(sz)}"
                    np = ", np = true" if traversable(o["cle"]) else ""


                    chemin = str(p["m"]).replace(chr(92), "/")
                    aj = (", ajout = true" if p.get("ajout") else "") + (f', achat = "{p["achat"]}"' if p.get("achat") else "")
                    ps.append(f'{{ m = "{chemin}", x = {_n(p["x"])}, y = {_n(p["y"])}, z = {_n(p["z"])}, '
                              f'rx = {_n(p["rx"])}, ry = {_n(p["ry"])}, rz = {_n(p["rz"])}{ech}{np} {aj} }}')
            nom = o["nom"].replace('"', "'")
            lignes.append(f'\t["{o["cle"]}"] = {{ nom = "{nom}", pieces = {{ ' + ", ".join(ps) + " } },")
    lignes.append("}")

    lignes.append("SCRIPTORIUM_DECORS = {")
    for qui, ps in decors().items():
        d = [(f'{{ p = "{x["p"]}", x = {_n(x["x"])}, y = {_n(x["y"])}, z = {_n(x["z"])}, rz = {_n(x["rz"])} }}'
              if "p" in x else
              f'{{ m = "{x["m"]}", x = {_n(x["x"])}, y = {_n(x["y"])}, z = {_n(x["z"])}, rx = {_n(x["rx"])}, '
              f'ry = {_n(x["ry"])}, rz = {_n(x["rz"])} }}') for x in ps]
        lignes.append(f'\t["{qui}"] = {{ ' + ", ".join(d) + " },")
    lignes.append("}")
    return "\n".join(lignes) + "\n"
