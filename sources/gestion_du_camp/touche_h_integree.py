
""












from __future__ import annotations

import re
from pathlib import Path

VERROU = "ScriptoriumVeilleurToucheH"
TETE = 256
PAS_MS = 250
MOTIFS = {"basculer": re.compile(rb"Unknown command:\s*scriptorium_gestion_basculer_\d+"),

          "amenagement": re.compile(rb"Unknown command:\s*scriptorium_amenagement_ouvrir")}


class GuetteurDeH:
    ""


    def __init__(self, journal: Path) -> None:
        self.journal = Path(journal)
        self.pos: int | None = None
        self.tete = b""
        self.reste = b""

    def _lire_la_tete(self) -> bytes:
        try:
            with open(self.journal, "rb") as f:
                return f.read(TETE)
        except OSError:
            return b""

    def relever(self) -> list[str]:
        ""
        try:
            taille = self.journal.stat().st_size
        except OSError:
            if self.pos is None:
                self.pos = 0
            return []
        if self.pos is None:
            self.pos, self.tete = taille, self._lire_la_tete()
            return []
        if taille == self.pos:
            return []
        tete = self._lire_la_tete()
        commun = min(len(tete), len(self.tete))
        if taille < self.pos or (commun and tete[:commun] != self.tete[:commun]):
            self.pos, self.reste = 0, b""
        self.tete = tete
        try:
            with open(self.journal, "rb") as f:
                f.seek(self.pos)
                brut = f.read(taille - self.pos)
        except OSError:
            return []
        self.pos = taille
        brut = self.reste + brut
        coupe = brut.rfind(b"\n")
        if coupe < 0:
            self.reste = brut
            return []
        self.reste = brut[coupe + 1:]
        out: list[str] = []
        for ligne in brut[:coupe].splitlines():
            for nom, motif in MOTIFS.items():
                if motif.search(ligne):
                    out.append(nom)
        return out


def prendre_le_relais(nom: str = VERROU) -> object | None:
    ""
    try:
        import ctypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CreateMutexW.restype = ctypes.c_void_p
        k32.CloseHandle.argtypes = [ctypes.c_void_p]
        h = k32.CreateMutexW(None, False, nom)
        if ctypes.get_last_error() == 183:
            k32.CloseHandle(h)
            return None
        return h or True
    except Exception:
        return True
