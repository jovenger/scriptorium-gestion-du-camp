""













from __future__ import annotations

import ctypes
import os
import subprocess
import threading
import time
from ctypes import wintypes
from dataclasses import dataclass, field
from pathlib import Path

from . import jeu

APPID = "1771300"
PROCESSUS = "KingdomCome.exe"


OPTIONS = {
    "console": (
        "-console",
        "Ouvre la console de developpement",
        "indispensable pour lire les retours a l'ecran ; sans effet sur le jeu",
    ),
    "devmode": (
        "-devmode",
        "Mode developpeur",
        "debloque des commandes ; peut modifier le comportement du jeu",
    ),
    "mandatoryPaks": (
        "-mandatoryPaks",
        "Refuser de demarrer si une archive obligatoire manque",
        "le jeu sort avec le code 238 plutot que de tourner incomplet",
    ),
}


@dataclass
class Demarrage:
    ""

    voie: str
    commande: str
    position_journal: int = 0
    horodatage: float = field(default_factory=time.time)
    erreur: str = ""

    @property
    def reussi(self) -> bool:
        return not self.erreur




















_MEMOIRE: dict = {"etat": None, "quand": 0.0}
_VERROU = threading.Lock()
_FRAICHEUR = 1.0
_fil_de_fond: threading.Thread | None = None


class _ENTREE(ctypes.Structure):
    ""

    _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                ("th32ProcessID", wintypes.DWORD),
                ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
                ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                ("th32ParentProcessID", wintypes.DWORD),
                ("pcPriClassBase", ctypes.c_long), ("dwFlags", wintypes.DWORD),
                ("szExeFile", wintypes.WCHAR * 260)]


def _demander_a_windows() -> bool | None:
    ""
    try:
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
        instantane = k32.CreateToolhelp32Snapshot(0x00000002, 0)
        if instantane in (None, -1, 0xFFFFFFFFFFFFFFFF):
            return None
        try:
            e = _ENTREE()
            e.dwSize = ctypes.sizeof(_ENTREE)
            k32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(_ENTREE)]
            k32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(_ENTREE)]
            vise = PROCESSUS.lower()
            trouve = k32.Process32FirstW(instantane, ctypes.byref(e))
            while trouve:
                if e.szExeFile.lower() == vise:
                    return True
                trouve = k32.Process32NextW(instantane, ctypes.byref(e))
            return False
        finally:
            k32.CloseHandle(instantane)
    except Exception:
        return None


def _par_tasklist() -> bool:
    ""
    try:
        sortie = subprocess.run(
            ["tasklist", "/NH"], capture_output=True, text=True, timeout=10,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    return PROCESSUS.lower() in sortie.lower()


def _mesurer() -> bool:
    reponse = _demander_a_windows()
    if reponse is None:
        reponse = _par_tasklist()
    with _VERROU:
        _MEMOIRE["etat"], _MEMOIRE["quand"] = reponse, time.time()
    return reponse


def en_cours(fraicheur: float = _FRAICHEUR) -> bool:
    ""




    with _VERROU:
        etat, quand = _MEMOIRE["etat"], _MEMOIRE["quand"]
    if etat is not None and time.time() - quand < fraicheur:
        return etat
    return _mesurer()


def suivre(periode: float = 1.0) -> None:
    ""

    global _fil_de_fond
    if _fil_de_fond is not None and _fil_de_fond.is_alive():
        return

    def boucle():
        while True:
            _mesurer()
            time.sleep(periode)

    _fil_de_fond = threading.Thread(target=boucle, name="veille-jeu", daemon=True)
    _fil_de_fond.start()


def oublier() -> None:
    ""

    with _VERROU:
        _MEMOIRE["etat"], _MEMOIRE["quand"] = None, 0.0


def taille_journal(inst: jeu.Installation) -> int:
    try:
        return inst.journal.stat().st_size
    except OSError:
        return 0


def arreter(delai: float = 20.0) -> bool:
    ""










    oublier()
    try:
        subprocess.run(
            ["taskkill", "/IM", PROCESSUS, "/F"],
            capture_output=True, text=True, timeout=delai,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    fin = time.time() + delai
    while time.time() < fin:
        if not en_cours():
            return True
        time.sleep(0.5)
    return False


def lancer(
    inst: jeu.Installation,
    options: list[str] | None = None,
    direct: bool = False,
) -> Demarrage:
    ""




    options = [o for o in (options or []) if o in {v[0] for v in OPTIONS.values()}]

    if en_cours():
        return Demarrage(
            voie="aucune", commande="",
            erreur="le jeu tourne deja (une seule instance est autorisee)",
        )

    position = taille_journal(inst)

    if options or direct:
        if not inst.exe.exists():
            return Demarrage(
                voie="direct", commande="",
                erreur=f"executable introuvable : {inst.exe}",
            )
        commande = [str(inst.exe), *options]
        try:
            subprocess.Popen(
                commande,
                cwd=str(inst.racine),
                creationflags=getattr(subprocess, "DETACHED_PROCESS", 0),
                close_fds=True,
            )
        except OSError as err:
            return Demarrage(
                voie="direct", commande=" ".join(commande),
                erreur=f"lancement impossible : {err}",
            )
        return Demarrage(
            voie="direct", commande=" ".join(commande), position_journal=position
        )

    url = f"steam://rungameid/{APPID}"
    try:
        os.startfile(url)
        oublier()
    except OSError as err:
        return Demarrage(
            voie="steam", commande=url,
            erreur=f"Steam n'a pas repondu : {err}",
        )
    return Demarrage(voie="steam", commande=url, position_journal=position)


def attendre_demarrage(delai_max: float = 90.0, pas: float = 1.0) -> bool:
    ""
    limite = time.time() + delai_max
    while time.time() < limite:
        if en_cours():
            return True
        time.sleep(pas)
    return False


@dataclass
class Preparation:
    ""

    agent_installe: bool = False
    agent_dans_ordre: bool = False
    mods_casses: int = 0

    lignes_orphelines: list[str] = field(default_factory=list)

    workshop_inactifs: list[str] = field(default_factory=list)
    details: list[str] = field(default_factory=list)

    @property
    def pret(self) -> bool:
        return self.agent_installe and self.agent_dans_ordre


def preparer(inst: jeu.Installation, installer_agent: bool = True) -> Preparation:
    ""
    from . import constructeur

    bilan = Preparation()

    dossier = constructeur.dossier_mod(inst)
    if installer_agent:
        resultat = constructeur.installer(inst)
        bilan.agent_installe = resultat.verifie
        bilan.details.append(
            f"agent : {resultat.detail}" if resultat.verifie
            else f"agent NON installe : {resultat.detail}"
        )
        constructeur.inscrire_dans_ordre(inst)
    else:
        bilan.agent_installe = dossier.exists()
        bilan.details.append(
            "agent deja en place" if bilan.agent_installe else "agent absent"
        )

    ordre = jeu.ordre_des_mods(inst)
    bilan.agent_dans_ordre = constructeur.NOM_MOD in ordre
    bilan.details.append(
        f"mod_order.txt : {len(ordre)} mods, agent "
        + ("present" if bilan.agent_dans_ordre else "ABSENT")
    )

    casses = [m for m in jeu.inventorier_mods(inst) if m.etat != "valide"]
    bilan.mods_casses = len(casses)
    if casses:
        bilan.details.append(
            f"{len(casses)} mod(s) casses : "
            + ", ".join(f"{m.nom} ({m.detail})" for m in casses[:4])
            + " -- ils seront ignores par le jeu"
        )













    abonnes = {m.nom for m in jeu.mods_workshop(inst)}
    bilan.lignes_orphelines = [
        nom for nom in ordre
        if nom and nom not in abonnes and not (inst.mods / nom).is_dir()
    ]









    bilan.workshop_inactifs = sorted(abonnes - set(ordre))
    if bilan.workshop_inactifs:
        bilan.details.append(
            f"{len(bilan.workshop_inactifs)} mod(s) du Workshop abonne(s) mais "
            "JAMAIS charge(s) faute d'etre dans l'ordre : "
            + ", ".join(bilan.workshop_inactifs[:4])
        )
    if bilan.lignes_orphelines:
        bilan.details.append(
            f"{len(bilan.lignes_orphelines)} ligne(s) de mod_order.txt "
            "nomment un mod qui n'est plus sur le disque : "
            + ", ".join(bilan.lignes_orphelines[:4])
            + ("..." if len(bilan.lignes_orphelines) > 4 else "")
            + " -- sans effet, mais ces mods ne tournent pas"
        )

    return bilan
