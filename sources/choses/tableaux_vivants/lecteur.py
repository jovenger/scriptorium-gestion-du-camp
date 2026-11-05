
""








from __future__ import annotations

from pathlib import Path

MARQUES = {"[ScriptoPersonnel] ": "P", "[ScriptoTir] ": "T", "[ScriptoProgression] ": "G"}
NOMS = {v: k for k, v in MARQUES.items()}
VIVANT = "[ScriptoVivant] "
TYPES = {"P": "h", "T": "t", "G": "p"}
PALIER = 10


def palier(v: float | None) -> int | None:
    ""
    return None if v is None else int(v // PALIER * PALIER)


class Suiveur:
    ""

    def __init__(self, chemin: Path, depuis_le_debut: bool = False) -> None:
        self.chemin = Path(chemin)
        self.pos: int | None = 0 if depuis_le_debut else None
        self.reste = b""
        self.recommence = False

    def nouvelles_lignes(self) -> list[str]:
        try:
            taille = self.chemin.stat().st_size
        except OSError:
            return []
        if self.pos is None:
            self.pos = taille
            return []
        if taille < self.pos:
            self.pos, self.reste, self.recommence = 0, b"", True
        if taille == self.pos:
            return []
        try:
            with open(self.chemin, "rb") as f:
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
        return brut[:coupe].decode("utf-8", "replace").splitlines()


class RegistreVivant:
    ""

    def __init__(self) -> None:
        self.lignes: dict[str, dict[str, list[str]]] = {"P": {}, "T": {}, "G": {}}
        self.entetes: dict[str, str] = {}
        self.heure: str = ""
        self.pret = False
        self._blocs: dict[str, list[str] | None] = {"P": None, "T": None, "G": None}
        self._maj: list[str] | None = None


    def lire(self, lignes: list[str]) -> bool:
        change = False
        for brute in lignes:
            if VIVANT in brute:
                change |= self._vivant(brute.split(VIVANT, 1)[1].rstrip())
                continue
            for marque, code in MARQUES.items():
                if marque in brute:
                    change |= self._bloc(code, brute.split(marque, 1)[1].rstrip())
                    break
        return change

    def _bloc(self, code: str, l: str) -> bool:
        if l.startswith("debut|"):
            self._blocs[code] = [l]
            return False
        cour = self._blocs.get(code)
        if cour is None:
            return False
        if l.startswith("fin|"):
            self._blocs[code] = None
            hommes = {}
            for x in cour[1:]:
                c = x.split("|")
                if len(c) > 1 and c[0] == TYPES[code] and c[1]:
                    hommes[c[1]] = c
            self.lignes[code] = hommes
            self.entetes[code] = cour[0]
            if code == "P":
                d = cour[0].split("|")
                self.heure = d[1] if len(d) > 1 else ""
                self.pret = True
            return True
        cour.append(l)
        return False

    def _vivant(self, l: str) -> bool:
        if l.startswith("maj|"):
            self._maj = [l]
            return False
        if self._maj is None:
            return False
        if not l.startswith("fin|"):
            self._maj.append(l)
            return False
        maj, self._maj = self._maj, None
        d = maj[0].split("|")
        if len(d) > 2 and d[1] == "personnel":
            self.heure = d[2]
        for x in maj[1:]:
            c = x.split("|")
            if c[0] == "l" and len(c) > 3 and c[1] in self.lignes:
                code, champs = c[1], c[2:]
                avant = self.lignes[code].get(champs[1])
                if avant is not None:
                    champs = [v if v != "" or i >= len(avant) or avant[i] == "" else avant[i]
                              for i, v in enumerate(champs)]
                self.lignes[code][champs[1]] = champs
            elif c[0] == "x" and len(c) > 2 and c[1] in self.lignes:
                self.lignes[c[1]].pop(c[2], None)
        return True


    def texte(self) -> str:
        out = []
        for code in ("P", "T", "G"):
            marque = NOMS[code]
            hommes = self.lignes[code]
            if code == "P":
                out.append(f"{marque}debut|{self.heure}|{len(hommes)}")
            else:
                out.append(self.entetes.get(code, "") and marque + self.entetes[code] or f"{marque}debut|")
            out.extend(marque + "|".join(c) for c in hommes.values())
            out.append(f"{marque}fin|")
        return "\n".join(out)
