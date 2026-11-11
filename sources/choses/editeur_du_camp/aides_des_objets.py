
""




from __future__ import annotations



A_LIT = "Logement : un lit. Sans lit libre, pas de réembauche ; au lit, +12 d'énergie par heure."
A_SIEGE = "Repos : un homme assis reprend 2 d'énergie par heure ; le colonel veut un siège par homme."
A_TABLE = "Repas : ceux qui mangent debout viennent s'y asseoir. Compte comme table pour la quête."
A_DECOR = "Décor : aucun effet de jeu."
A_TENTE = "Abri : sans lit ni siège ; les lits se posent dedans. Aucun autre effet."
A_TENTE_TOILE = "Abri : un lit posé dessous rend +2 d'énergie par heure. La toile s'use : 0,5 % de son prix par semaine, au coffre."
A_TENTE_RANG = "Abri : un lit dessous, +2 d'énergie par heure ; le lit du colonel ou du Directeur dessous : +1 de moral au camp. Entretien au coffre."
AIDES = {
    "tente_henry_vide": "Logement d'Henry : la tente vide ; au plan, réservez-lui le lit qu'on y pose.",
    "coffret_banque": "Argent : touche E, la Banque du camp ; E maintenu, Scriptorium. Les pillards le visent.",
    "mini_tente": "Commandement : touche E, la Gestion du camp.",
    "coffre": "Rangement : un coffre du jeu ; ce qu'on y met reste, et revient à Henry à la vente du camp.",
    "lit": A_LIT, "lit_haut": "Logement : un lit ; au lit, +15 d'énergie par heure (un lit bas : 12) et +1 de moral le lendemain ; sans lit libre, pas de réembauche.", "lit_banc": "Logement : un lit ; au lit, +10 d'énergie par heure (un lit bas : 12) ; sans lit libre, pas de réembauche.",
    "lit_double": "Logement : deux lits. Sans lit libre, pas de réembauche ; au lit, +12 d'énergie par heure.",
    "tente_hommes": "Logement : quatre lits sous une grande tente. Le Directeur ne réengage qu'avec un lit libre.",
    "tente_intendant": "Commandement : le lit du Directeur ; elle se pose seule à son engagement.",
    "bureau_directeur": "Commandement : le Directeur y travaille ; ses rapports y sont posés (E pour lire).",
    "table_bancs": "Repas : ceux qui mangent debout s'y assoient ; table pour la quête ; sert aussi aux dés.", "table_un_banc": A_TABLE, "petite_table": A_TABLE,
    "table_une_place": "Repas : ceux qui mangent debout s'y assoient ; table pour la quête ; sert aussi aux dés.",
    "banc": A_SIEGE, "banc_trois": A_SIEGE, "banc_haut": A_SIEGE, "tabouret": A_SIEGE, "chaise": A_SIEGE, "chaise_haute": A_SIEGE,
    "feu_camp": "Feu et moral : le Directeur le recharge ; tous les feux allumés, +1 de moral par heure.",
    "feu_de_chambree": "Repas : six places ; un homme dont le lit est à 14 m ou moins y mange. Compte comme feu.",
    "foyer": "Repas d'Henry, s'il lui est réservé : il y mange et y cuisine. Compte comme feu pour la quête.",
    "brasero": "Lumière : un feu allumé de 20 h à 7 h. Compte comme feu pour la quête.",
    "torche": "Lumière : allumée jour et nuit. Aucun autre effet.",
    "lanterne": "Lumière : se pose sur une table. Aucun autre effet.", "lampe_table": "Lumière : se pose sur une table. Aucun autre effet.",
    "tour_de_guet": "Défense : un archer y veille la nuit, deux à l'alerte.",
    "porte_palissade": "Défense : le Directeur y met un garde, jour et nuit.",
    "palissade": "Défense : plus de la moitié du tour du camp fermée, plus de vol de nuit, et la diversion des pillards arrive de front.", "pieux": A_DECOR, "pavois": A_DECOR, "pavois_b": A_DECOR, "pavois_sur_pied": A_DECOR,
    "banniere": "Moral : tant qu'elle est debout, un pillage du camp ou des caisses coûte moitié moins de moral ; aucun ralliement.", "ratelier_garde": A_DECOR, "hallebardes": A_DECOR, "haches": A_DECOR, "table_vaisselle": "Repas : un homme qui mange à une table, à moins de 10 m d'elle, gagne +1 de moral ce jour-là (une fois par jour).",
    "abreuvoir": "Chevaux : le porteur d'eau le remplit. Sans lui, le palefrenier porte l'eau seau à seau : 1,5 fois plus long par bête.",
    "chariot_couvert": "Réserve : au camp, les vivres et la boisson se gardent 15 jours au lieu de 10 avant la revente du surplus.", "chariot_a_bancs": A_DECOR, "chariot_de_foin": "Réserve : au camp, le fourrage se garde pour 28 rations par cheval au lieu de 14.",
    "porte_armure": "Armurier : il y montre son travail ; il vend 6 pièces d'armure par jour au lieu de 4.", "latrines": "Hygiène : au-delà de 20 hommes, sans latrines ni feuillée, le camp se salit et le moral baisse. À 20 m des tentes, des feux et de la cuisine.",
    "mannequin_paille": "Entraînement : un homme libre s'y exerce 120 s ; +6 points de combat.",
    "ratelier": "Entraînement : les duels à l'épée de bois ; chaque combat donne +12 points de combat.",
    "ratelier_camp": "Entraînement : le point d'exercice du matin ; pas de duels.",
    "cible": "Entraînement : chasseurs et archers y tirent ; plus la cible est loin, plus le tir rapporte.",
    "meule": "Équipement : la meule du jeu, pour affûter.",
    "pilori": "Justice : le Directeur y attache les bagarreurs, de 4 h à 24 h ; sans pilori, la peine attend.",
    "baquet": "Hygiène d'Henry, s'il lui est réservé : il s'y lave.",
    "point_d_eau": "Hygiène d'Henry, s'il lui est réservé : il s'y lave, et y lave son linge avec un savon.",
    "prie_dieu": "Piété d'Henry, s'il lui est réservé : il y prie.",
    "comptoir_bains": "Hygiène : la patronne des bains s'y tient ; les bains marchent aussi sans lui.",
    "poste_de_chasse": "Métier : l'établi des chasseurs ; sans lui, pas de tannerie.",
    "etal_cueillette": "Métier : l'établi du jardinier ; la récolte y est portée.",
    "potager_petit": "Métier : environ 10 vivres par récolte, si le jardinier est engagé.",
    "potager_moyen": "Métier : environ 22 vivres par récolte, si le jardinier est engagé.",
    "potager_grand": "Métier : environ 39 vivres par récolte, si le jardinier est engagé.",
    "coin_boucher": "Métier : l'établi du boucher ; sans lui, il n'achète pas la viande des chasseurs.",
    "fumoir": "Métier : le boucher y fume sa viande salée ; sans fumoir, pas de viande salée.",
    "sechoir": "Cuisine d'Henry, s'il lui est réservé : il y sèche viande, fruits et herbes.",
    "atelier_armurier": "Métier : l'établi de l'armurier ; sans lui, ni réparation ni fabrication d'armures.",
    "caisse_atelier": "Argent : la caisse d'un métier (E). Elle se pose seule, à côté d'un étal ou d'un établi.",
    "pupitre_coursier": "Métier : le coursier y attend ses courses ; le forgeron y passe commande.",
    "etal_vivandiere": "Vente : la vivandière y vend ses en-cas ; sans table, ni vente ni poules.",
    "etal_jardiniers": "Vente : le jardinier y vend légumes et repas, s'il est derrière l'étal.",
    "etal_bucheron": "Vente : le bûcheron y vend son bois ; la forge y achète son charbon.",
    "etal_chasseurs": "Vente : les chasseurs y vendent la viande.",
    "etal_taverne": "Vente : le tavernier y vend bière et vin ; sans cet étal, aucune vente.",
    "tonneau_vin": "Vente : sans lui, la taverne ne vend pas de vin.",
    "tonneau_biere": "Vente : un client sans place à table y tire sa bière.",
    "table_boisson": "Taverne : deux clients de plus servis à la fois (deux tables au plus) ; deux hommes y boivent.",
    "cuisine": "Mise en scène : les hommes y font semblant de cuisiner ; aucun repas n'y est servi.",
    "cuisine_etageres": "Mise en scène : les hommes y font semblant de cuisiner ; aucun repas n'y est servi.",
    "ligne_des_chevaux": "Chevaux : deux places de cheval ; le palefrenier y travaille. Fourrage et pension à payer.",
    "decor_cart_with_water": "Métier : l'établi du porteur d'eau ; il y vend le verre d'eau.",
    "decor_stash_industriall_with_firewood": "Métier : l'établi du bûcheron ; sans lui, pas de coupe d'arbres près du camp.",
}


def aide(cle: str, rubrique: str = "") -> str:
    if cle in AIDES:
        return AIDES[cle]


    if cle in ("tente_riche", "tente_riche_ouverte", "tente_royale", "tente_royale_ouverte"):
        return A_TENTE_RANG
    if cle.startswith("tente_"):
        return A_TENTE_TOILE
    if rubrique == "Tentes" or cle.startswith(("tente_", "auvent_", "abri_")):
        return A_TENTE
    if cle.startswith("decor_"):
        return A_DECOR
    raise SystemExit(f"objet sans aide : {cle}")





INSTALLATIONS = {
    "arene": "Décor : aucun effet de jeu ; personne n'y est envoyé (les duels se font aux râteliers).",
    "entrainement": "Exercice : posé, les points gagnés à l'exercice du matin (assauts et tir) valent 10 % de plus ; deux hommes y font l'exercice à l'épée.",
    "fleches": "Forge : le travail des flèches au taux de l'aide ; le carquois environ 2 gros moins cher ; un homme y répare des flèches.",
    "cuisine": "Mise en scène : quatre places où les hommes touillent et mangent ; aucun repas n'est compté.",
    "tonneau": "Taverne : la réserve de vin double (80 verres au lieu de 40), achetée par le tavernier ; un homme y boit.",
    "banc": "Repos : deux hommes s'y assoient ; leur repos compte (+2 d'énergie par heure), comme sur un banc posé dans l'Aménagement.",
    "baquets": "Hygiène : deux bassines ; les hommes sales y vont se laver, un à la fois par bassine.",
    "pisser": "Hygiène : compte comme des latrines (au-delà de 20 hommes, sans elles, le camp se salit plus vite) ; un homme s'y tient 45 s.",
    "alchimie": "Décor : aucun effet de jeu ; le camp se rebâtit au même endroit pour l'accueillir.",
}






LIEN_DU_DICTIONNAIRE = "https://jovenger.github.io/scriptorium/"
LIEN_TEXTE = {
    "fr": "Le dictionnaire du camp, ce que fait chaque objet :",
    "en": "The camp dictionary, what each object does:",
    "de": "Das Lagerlexikon, was jedes Ding tut:",
    "ru": "Словарь лагеря, что делает каждая вещь:",
    "ja": "野営地事典、各物の働き：",
    "zh_hans": "营地词典，每样物品的作用：",
    "zh_hant": "營地詞典，每樣物品的作用：",
}
