""







from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

APPID_KCD2 = "1771300"
NOM_DOSSIER = "KingdomComeDeliverance2"


REL_EXE = Path("Bin/Win64MasterMasterSteamPGO/KingdomCome.exe")
REL_DLL = Path("Bin/Win64MasterMasterSteamPGO/WHGame.dll")
REL_JOURNAL = Path("kcd.log")
REL_MODS = Path("Mods")



RANGEMENT_DES_RETIRES = "_retires_par_scriptorium"
REL_DATA = Path("Data")

DOSSIER_SAUVEGARDES = Path.home() / "Saved Games" / "kingdomcome2"


@dataclass
class EtatMod:
    ""

    nom: str
    dossier: Path
    manifeste: dict = field(default_factory=dict)
    paks: list[Path] = field(default_factory=list)
    liens_morts: list[Path] = field(default_factory=list)
    a_config: bool = False

    @property
    def valide(self) -> bool:
        ""


        return not self.liens_morts and (bool(self.paks) or self.a_config)

    @property
    def etat(self) -> str:
        if self.valide:
            return "valide"
        if self.paks and self.liens_morts:
            return "partiel"
        return "casse"

    @property
    def detail(self) -> str:
        if self.valide:
            if self.paks:
                return f"{len(self.paks)} pak(s)"
            return "mod.cfg seul (sans archive)"
        if self.paks:
            return f"{len(self.paks)} pak(s) valides, {len(self.liens_morts)} lien(s) mort(s)"
        if self.liens_morts:
            return f"{len(self.liens_morts)} lien(s) mort(s) -- archive disparue"
        return "aucun contenu"

    @property
    def par_vortex(self) -> bool:
        return any(p.is_symlink() for p in self.paks) or bool(self.liens_morts)


@dataclass
class Installation:
    ""

    racine: Path
    version: str = "inconnue"

    @property
    def exe(self) -> Path:
        return self.racine / REL_EXE

    @property
    def dll(self) -> Path:
        return self.racine / REL_DLL

    @property
    def journal(self) -> Path:
        return self.racine / REL_JOURNAL

    @property
    def mods(self) -> Path:
        return self.racine / REL_MODS

    @property
    def data(self) -> Path:
        return self.racine / REL_DATA

    def pak(self, nom: str) -> Path:
        return self.data / nom


def _bibliotheques_steam() -> list[Path]:
    ""
    bases = [
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Steam",
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Steam",
    ]

    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as cle:
            bases.insert(0, Path(winreg.QueryValueEx(cle, "SteamPath")[0]))
    except (ImportError, OSError):
        pass
    trouvees: list[Path] = []
    for base in bases:
        vdf = base / "steamapps" / "libraryfolders.vdf"
        if not vdf.exists():
            continue
        try:
            texte = vdf.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for chemin in re.findall(r'"path"\s+"([^"]+)"', texte):
            trouvees.append(Path(chemin.replace("\\\\", "\\")))
    return trouvees


def trouver_jeu(chemin_force: str | os.PathLike | None = None) -> Installation | None:
    ""
    if chemin_force:
        racine = Path(chemin_force)
        if (racine / REL_EXE).exists():
            inst = Installation(racine=racine)
            inst.version = lire_version(inst)
            return inst
        return None

    candidats: list[Path] = []

    from . import chemins
    retenu = chemins.dossier_du_jeu_retenu()
    if retenu is not None:
        candidats.append(retenu)
    for biblio in _bibliotheques_steam():
        candidats.append(biblio / "steamapps" / "common" / NOM_DOSSIER)
    for lettre in "CDEFGHIJ":
        candidats.append(Path(f"{lettre}:/SteamLibrary/steamapps/common/{NOM_DOSSIER}"))

    for racine in candidats:
        if (racine / REL_EXE).exists():
            inst = Installation(racine=racine)
            inst.version = lire_version(inst)
            return inst
    return None


def lire_version(inst: Installation) -> str:
    ""
    journaux = [inst.journal]
    dossier_backups = inst.racine / "logbackups"
    if dossier_backups.is_dir():
        journaux += sorted(
            dossier_backups.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True
        )

    for chemin in journaux:
        if not chemin.exists():
            continue
        try:
            texte = chemin.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        m = re.search(r"Extended build info:\s+(\S+)", texte)
        if m:
            return m.group(1)
        m = re.search(r"\*\s*description:\s*(\S+)", texte)
        if m:
            return m.group(1)
    return "inconnue"


def ordre_des_mods(inst: Installation) -> list[str]:
    ""
    fichier = inst.mods / "mod_order.txt"
    if not fichier.exists():
        return []
    lignes = fichier.read_text(encoding="utf-8", errors="replace").splitlines()
    return [l.strip() for l in lignes if l.strip() and not l.strip().startswith("#")]


def mods_workshop(inst: Installation) -> list[EtatMod]:
    ""














    resultats: list[EtatMod] = []
    racine = inst.racine

    steamapps = racine.parent.parent
    dossier = steamapps / "workshop" / "content" / APPID_KCD2
    if not dossier.is_dir():
        return resultats
    for sous in sorted(p for p in dossier.iterdir() if p.is_dir()):
        manifeste = _lire_manifeste(sous / "mod.manifest")
        etat = EtatMod(nom=manifeste.get("modid") or sous.name, dossier=sous)
        etat.manifeste = manifeste
        etat.a_config = (sous / "mod.cfg").exists()
        for rep in (sous / "Data", sous / "localization"):
            if rep.is_dir():
                etat.paks += sorted(rep.glob("*.pak"))
        resultats.append(etat)
    return resultats


def _lire_manifeste(chemin: Path) -> dict:
    ""
    if not chemin.exists():
        return {}
    try:
        import xml.etree.ElementTree as ET

        racine = ET.fromstring(chemin.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {}
    info = racine.find("info")
    if info is None:
        return {}
    return {enfant.tag: (enfant.text or "").strip() for enfant in info}


def inventorier_mods(inst: Installation) -> list[EtatMod]:
    ""




    resultats: list[EtatMod] = []
    if not inst.mods.is_dir():
        return resultats

    for dossier in sorted(p for p in inst.mods.iterdir() if p.is_dir()):










        if dossier.name == RANGEMENT_DES_RETIRES:
            continue
        etat = EtatMod(nom=dossier.name, dossier=dossier)
        etat.manifeste = _lire_manifeste(dossier / "mod.manifest")
        etat.a_config = (dossier / "mod.cfg").exists()



        deja_vus: set[str] = set()
        for sous in ("Data", "Localization"):
            rep = dossier / sous
            if not rep.is_dir():
                continue
            for fichier in rep.rglob("*.pak"):
                cle = str(fichier).casefold()
                if cle in deja_vus:
                    continue
                deja_vus.add(cle)

                if fichier.exists():
                    etat.paks.append(fichier)
                else:
                    etat.liens_morts.append(fichier)

        resultats.append(etat)
    return resultats


def cible_reelle(chemin: Path) -> Path:
    ""




    try:
        if chemin.is_symlink():
            return Path(os.path.realpath(chemin))
    except OSError:
        pass
    return chemin
