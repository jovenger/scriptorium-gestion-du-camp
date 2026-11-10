
""




from __future__ import annotations



A_LIT = "Logement : un lit. Sans lit libre, pas de réembauche ; au lit, +12 d'énergie par heure."
A_SIEGE = "Repos : un homme assis reprend 2 d'énergie par heure ; le colonel veut un siège par homme."
A_TABLE = "Repas : ceux qui mangent debout viennent s'y asseoir. Compte comme table pour la quête."
A_DECOR = "Décor : aucun effet de jeu."
A_TENTE = "Abri : sans lit ni siège ; les lits se posent dedans. Aucun autre effet."
AIDES = {
    "tente_henry_vide": "Logement d'Henry : la tente vide ; au plan, réservez-lui le lit qu'on y pose.",
    "coffret_banque": "Argent : touche E, la Banque du camp ; E maintenu, Scriptorium. Les pillards le visent.",
    "mini_tente": "Commandement : touche E, la Gestion du camp.",
    "coffre": "Rangement : un coffre du jeu ; ce qu'on y met reste, et revient à Henry à la vente du camp.",
    "lit": A_LIT, "lit_haut": "Logement : un lit, ni plus ni moins qu'un lit bas ; sans lit libre, pas de réembauche.", "lit_banc": "Logement : un lit, ni plus ni moins qu'un lit bas ; sans lit libre, pas de réembauche.",
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
    "palissade": A_DECOR, "pieux": A_DECOR, "pavois": A_DECOR, "pavois_b": A_DECOR, "pavois_sur_pied": A_DECOR,
    "banniere": A_DECOR, "ratelier_garde": A_DECOR, "hallebardes": A_DECOR, "haches": A_DECOR, "table_vaisselle": A_DECOR,
    "abreuvoir": A_DECOR, "chariot_couvert": A_DECOR, "chariot_a_bancs": A_DECOR, "chariot_de_foin": A_DECOR,
    "porte_armure": A_DECOR, "latrines": "Décor : aucun effet de jeu ; à 20 m au moins des tentes, des feux et de la cuisine.",
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
    "table_boisson": "Mise en scène : deux hommes y font semblant de boire.",
    "cuisine": "Mise en scène : les hommes y font semblant de cuisiner ; aucun repas n'y est servi.",
    "cuisine_etageres": "Mise en scène : les hommes y font semblant de cuisiner ; aucun repas n'y est servi.",
    "ligne_des_chevaux": "Chevaux : deux places de cheval ; le palefrenier y travaille. Fourrage et pension à payer.",
    "decor_cart_with_water": "Métier : l'établi du porteur d'eau ; il y vend le verre d'eau.",
    "decor_stash_industriall_with_firewood": "Métier : l'établi du bûcheron ; sans lui, pas de coupe d'arbres près du camp.",
}


def aide(cle: str, rubrique: str = "") -> str:
    if cle in AIDES:
        return AIDES[cle]

    if rubrique == "Tentes" or cle.startswith(("tente_", "auvent_", "abri_")):
        return A_TENTE
    if cle.startswith("decor_"):
        return A_DECOR
    raise SystemExit(f"objet sans aide : {cle}")





INSTALLATIONS = {
    "arene": "Décor : aucun effet de jeu ; personne n'y est envoyé (les duels se font aux râteliers).",
    "entrainement": "Mise en scène : deux hommes y font l'exercice à l'épée ; aucun gain.",
    "fleches": "Mise en scène : un homme y répare des flèches ; aucune flèche n'est fabriquée.",
    "cuisine": "Mise en scène : quatre places où les hommes touillent et mangent ; aucun repas n'est compté.",
    "tonneau": "Mise en scène : un homme y fait semblant de boire ; aucun effet.",
    "banc": "Mise en scène : deux hommes y somnolent ; aucun repos n'est compté.",
    "baquets": "Hygiène : deux bassines ; les hommes sales y vont se laver, un à la fois par bassine.",
    "pisser": "Mise en scène : un homme s'y tient 45 s ; aucun besoin lié.",
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
