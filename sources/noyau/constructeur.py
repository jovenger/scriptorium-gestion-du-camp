""








from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from . import archives, jeu, reglages

NOM_MOD = "scriptorium"
RACINE_PROJET = Path(__file__).resolve().parent.parent
SOURCE_LUA = RACINE_PROJET / "agent" / "scriptorium.lua"



CHEMIN_INTERNE_LUA = f"Scripts/mods/{NOM_MOD}.lua"




CHEMIN_ORDRES = f"Mods/{NOM_MOD}/local/ordres.txt"




CHEMIN_CFG = f"mods/{NOM_MOD}/local/ordres.cfg"






PAK_PRINCIPAL = f"20_{NOM_MOD}.pak"
ANCIEN_PAK_PRINCIPAL = f"{NOM_MOD}.pak"


@dataclass
class ResultatInstallation:
    dossier: Path
    pak: Path
    ordres: Path
    verifie: bool
    detail: str


def dossier_mod(inst: jeu.Installation) -> Path:
    return inst.mods / NOM_MOD


def pak_installe(inst: jeu.Installation) -> Path:
    ""

    data = dossier_mod(inst) / "Data"
    neuf = data / PAK_PRINCIPAL
    return neuf if neuf.exists() or not (data / ANCIEN_PAK_PRINCIPAL).exists() else data / ANCIEN_PAK_PRINCIPAL


def _verifier_coherence_chemins() -> None:
    ""




    if not SOURCE_LUA.exists():
        raise FileNotFoundError(f"agent Lua introuvable : {SOURCE_LUA}")
    texte = SOURCE_LUA.read_text(encoding="utf-8")


    if CHEMIN_CFG.lower() not in texte.lower():
        raise ValueError(
            f"incoherence : le Lua ne pointe pas vers '{CHEMIN_CFG}'. "
            "Corriger scriptorium.CFG dans agent/scriptorium.lua."
        )


def installer(inst: jeu.Installation, version: str | None = None) -> ResultatInstallation:
    ""







    if version is None:
        from . import version as _version
        version = _version.courte().lstrip("v")
    _verifier_coherence_chemins()

    dossier = jeu.cible_reelle(dossier_mod(inst))
    (dossier / "Data").mkdir(parents=True, exist_ok=True)
    (dossier / "local").mkdir(parents=True, exist_ok=True)

    lua = SOURCE_LUA.read_text(encoding="utf-8")


    from . import choses as _choses
    lua += _choses.lua_des_choses()

    if _choses.POUR_LES_JOUEURS:
        from . import sans_essais as _sans_essais
        lua = _sans_essais.sans_crochets_de_mesure(lua)













    try:
        from . import butin as _butin
        lua = _butin.entete(inst.racine / "Data" / "Tables.pak") + lua
        from . import noblesse as _noblesse
        lua = _noblesse.entete(
            inst.racine / "Data" / "Tables.pak") + lua
    except Exception as erreur:
        detail = str(erreur).replace(chr(10), " ")
        lua = ("-- bareme du butin absent : " + detail + chr(10) + "SCRIPTORIUM_BUTIN = nil" + chr(10)) + lua












    from . import lumiere_naturelle as _lum
    debut = lua.find("scriptorium.HDR_INTERIEURS = {")
    if debut == -1:
        raise RuntimeError(
            "agent/scriptorium.lua : le bloc scriptorium.HDR_INTERIEURS est "
            "introuvable. Il est engendre depuis noyau/lumiere_naturelle.py "
            "-- sans lui, l'agent poserait une lumiere perimee.")
    fin = lua.index(chr(10) + "}", debut) + 2
    lua = lua[:debut] + _lum.table_lua() + lua[fin:]

    pak = jeu.cible_reelle(dossier / "Data" / PAK_PRINCIPAL)








    from . import socle_incorpore as _socle
    socle_dedans = _socle.actif()
    if socle_dedans:
        lua = _socle.entete_de_demarrage() + lua
    contenu = {
        CHEMIN_INTERNE_LUA: lua,
        CHEMIN_INTERNE_LUA.lower(): lua,
    }







    from . import cerveau
    contenu.update(cerveau.fichiers())






    for chemin, texte in _choses.fichiers_du_pak().items():
        contenu[chemin] = _choses.fusionner(contenu[chemin], texte) if chemin in contenu else texte






























    from . import entites_du_camp
    contenu.update(entites_du_camp.fichiers())






    from . import cerveau_du_feu
    contenu.update(cerveau_du_feu.fichiers(inst.racine))







    from . import postures as _postures
    contenu.update(_postures.fichiers())



    from . import mise_aux_des as _mise
    contenu.update(_mise.fichiers())

    from . import modeles_a_nous as _ma0
    _ma0.poser_les_modeles(contenu, [m for m in (_mise.modele(), cerveau_du_feu.modele(inst.racine)) if m])

    _ma0.copier_les_cerveaux(contenu, _mise.PAK_DU_JEU.parent.parent)

























    from . import modeles_a_nous as _ma
    _ma.ajouter_l_ame_des_chevaux(contenu)


    pak_du_socle, compte_socle = (_socle.incorporer(contenu) if socle_dedans else ({}, {}))

    archives.ecrire_pak(pak, contenu)
    pak_socle = jeu.cible_reelle(dossier / "Data" / _socle.PAK)
    if socle_dedans:
        archives.ecrire_pak(pak_socle, pak_du_socle)
    elif pak_socle.exists():
        pak_socle.unlink()
    ancien_pak = jeu.cible_reelle(dossier / "Data" / ANCIEN_PAK_PRINCIPAL)
    if ancien_pak.exists():
        ancien_pak.unlink()







    from . import annonces
    dossier_loc = jeu.cible_reelle(dossier / "localization")
    dossier_loc.mkdir(parents=True, exist_ok=True)
    nos_textes = annonces.paks()

    if socle_dedans:
        for nom_pak, siens in _socle.textes().items():
            deja = set(nos_textes.get(nom_pak, {})) & set(siens)
            if deja:
                raise ValueError(f"le socle et Scriptorium livrent tous deux {sorted(deja)} dans {nom_pak}")
            nos_textes.setdefault(nom_pak, {}).update(siens)
    for nom_pak in sorted(nos_textes):
        archives.ecrire_pak(jeu.cible_reelle(dossier_loc / nom_pak), nos_textes[nom_pak])





    for sous_chemin in (
        Path("Data") / "Scripts" / "mods" / f"{NOM_MOD}.lua",
        Path("Data") / "scripts" / "mods" / f"{NOM_MOD}.lua",
    ):
        cible = jeu.cible_reelle(dossier / sous_chemin)
        cible.parent.mkdir(parents=True, exist_ok=True)
        cible.write_text(lua, encoding="utf-8")






    bloc_des_regles = reglages.bloc_cfg(dossier)
    (dossier / "mod.cfg").write_text(
        "-- Scriptorium : temoin de demarrage\n"
        "scriptorium_temoin_cfg = 1\n"
        "\n"
        "-- LE SON NE S'ARRETE PLUS QUAND ON QUITTE LA FENETRE.\n"
        "--\n"
        "-- JoVenGer : « si je vais sur le tableau, sur le deuxieme ecran, je vais\n"
        "-- perdre tout le son du jeu, et c'est chiant ».\n"
        "--\n"
        "-- Le jeu coupe tout sur `eAMRT_MUTE_ALL` des qu'il perd le focus. Ces\n"
        "-- deux variables sont les siennes, et leurs descriptions sont sans\n"
        "-- ambiguite :\n"
        "--\n"
        "--   wh_snd_ignore_focus   « If set to 1, OnLoseFocus and OnGetFocus\n"
        "--                           will not do anything »\n"
        "--   sys_SleepIfInactiveWH « When enabled and game window is inactive,\n"
        "--                           sleep the main thread for 25ms every frame »\n"
        "--\n"
        "-- `mod.cfg` est l'endroit prevu pour poser des variables de facon\n"
        "-- durable : elles survivent aux reapplications de CVarOverride, qui\n"
        "-- defont les changements faits a la console en cours de partie.\n"
        "wh_snd_ignore_focus = 1\n"
        "sys_SleepIfInactiveWH = 0\n"
        + (("\n" + bloc_des_regles + "\n") if bloc_des_regles else ""),
        encoding="utf-8",
    )

    manifeste = jeu.cible_reelle(dossier / "mod.manifest")
    manifeste.write_text(
        reglages.manifeste(
            NOM_MOD, version, "Panneau de controle Scriptorium -- agent embarque"
        ),
        encoding="utf-8",
    )

    ordres = jeu.cible_reelle(dossier / "local" / "ordres.txt")
    if not ordres.exists():
        ordres.write_text("# en attente du panneau\nlot 0\n", encoding="utf-8")





    inscrire_dans_ordre(inst, NOM_MOD)


    detail_merc = "monde du socle"



    from . import lumiere as _lumiere
    detail_regles = reglages.migrer(inst) or reglages.rafraichir(inst)
    detail_lumiere = _lumiere.migrer(inst.racine) or "lumiere inchangee"


    if socle_dedans:
        detail_socle = (f"socle dans le dossier unique : {compte_socle['a_lui']} fichiers dans {_socle.PAK}, "
                        f"{compte_socle['fusionnes']} tables fusionnees, ses quetes de {compte_socle['cartes']} carte(s) "
                        "dans notre projet ; " + _socle.preparer_ses_fichiers(inst, dossier)
                        + " ; " + _socle.retirer_l_ancien(inst))
    else:
        detail_socle = "socle a part"

    valide, detail = archives.verifier_pak(pak)
    if valide:
        contenu = archives.lire_texte(pak, CHEMIN_INTERNE_LUA)
        if contenu is None:
            valide, detail = False, "le script Lua est absent de l'archive"
        elif "OnGameplayStarted" not in contenu:
            valide, detail = False, "le script Lua ne s'accroche a aucun evenement"

    return ResultatInstallation(
        dossier=dossier, pak=pak, ordres=ordres, verifie=valide,
        detail=detail + " ; " + detail_merc + " ; " + detail_regles + " ; " + detail_lumiere + " ; " + detail_socle
    )


def inscrire_dans_ordre(inst: jeu.Installation, nom: str = NOM_MOD) -> bool:
    ""








    fichier = jeu.cible_reelle(inst.mods / "mod_order.txt")
    lignes = []
    if fichier.exists():
        lignes = fichier.read_text(encoding="utf-8", errors="replace").splitlines()
    if any(l.strip() == nom for l in lignes):
        return False
    lignes = [l for l in lignes if l.strip()]
    lignes.append(nom)
    fichier.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return True


def desinstaller(inst: jeu.Installation) -> bool:
    ""
    dossier = jeu.cible_reelle(dossier_mod(inst))
    if not dossier.exists():
        return False
    shutil.rmtree(dossier)

    fichier = jeu.cible_reelle(inst.mods / "mod_order.txt")
    if fichier.exists():
        lignes = [
            l for l in fichier.read_text(encoding="utf-8", errors="replace").splitlines()
            if l.strip() and l.strip() != NOM_MOD
        ]
        fichier.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return True
