""



























from __future__ import annotations

import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

PREFIXE_JOURNAL = "scriptorium_"






MOTIF_LIGNE = re.compile(
    r"Unknown command:\s*scriptorium_(?P<message>\S+)"
)










COMMANDES_AGENT = ("scr", "scrl")


def traduire(commande: str) -> list[str]:
    ""












    commande = commande.strip()
    if not commande:
        return []

    mot = commande.split()[0].lower()










    if mot in ("eval", "lua"):
        morceaux = commande.split(maxsplit=1)
        if len(morceaux) < 2:
            return []
        hexa = morceaux[1].encode("utf-8").hex()
        return [f"{nom} hex {hexa}" for nom in COMMANDES_AGENT]

    if mot == "console":

        return [commande.split(maxsplit=1)[1]] if len(commande.split()) > 1 else []

    return [f"{nom} {commande}" for nom in COMMANDES_AGENT]


class Emetteur:
    ""








    def __init__(self, fichier: Path, racine_jeu: Path | None = None) -> None:
        self.fichier = Path(fichier)
        self.fichier.parent.mkdir(parents=True, exist_ok=True)
        self.racine_jeu = Path(racine_jeu) if racine_jeu is not None else None
        self.lot = self._dernier_lot_connu()
        self.cfg = self.fichier.with_suffix(".cfg")



        self.copies: list[Path] = []
        if racine_jeu is not None and not getattr(sys, "frozen", False):
            racine = Path(racine_jeu)
            for relatif in (
                "Data/ordres_scriptorium.txt",
                "ordres_scriptorium.txt",
            ):
                chemin = racine / relatif
                try:
                    chemin.parent.mkdir(parents=True, exist_ok=True)
                    self.copies.append(chemin)
                except OSError:
                    pass

    def _dernier_lot_connu(self) -> int:
        ""









        lot = 0
        if self.fichier.exists():
            for ligne in self.fichier.read_text(encoding="utf-8", errors="replace").splitlines():
                if ligne.lower().startswith("lot "):
                    try:
                        lot = int(ligne.split()[1])
                    except (IndexError, ValueError):
                        pass
                    break
        journal = self.racine_jeu / "kcd.log" if self.racine_jeu else None
        if journal and journal.exists():
            try:
                texte = journal.read_text(encoding="utf-8", errors="replace")
                accuses = re.findall(r"scriptorium_recu_(\d+)", texte)
                if accuses:
                    lot = max(lot, max(int(a) for a in accuses))
            except OSError:
                pass
        return lot

    def envoyer(self, commandes: list[str]) -> int:
        ""



















        try:
            for ligne in self.fichier.read_text(
                    encoding="utf-8", errors="replace").splitlines():
                if ligne.lower().startswith("lot "):
                    self.lot = max(self.lot, int(ligne.split()[1]))
                    break
        except (OSError, IndexError, ValueError):
            pass
        self.lot += 1
        lignes = [f"# Scriptorium -- {time.strftime('%Y-%m-%d %H:%M:%S')}", f"lot {self.lot}"]
        lignes += [c.strip() for c in commandes if c.strip()]
        texte = "\n".join(lignes) + "\n"




        temporaire = self.fichier.with_suffix(f".{os.getpid()}.tmp")
        temporaire.write_text(texte, encoding="utf-8", newline="\n")
        for essai in range(20):
            try:
                temporaire.replace(self.fichier)
                break
            except PermissionError:
                if essai == 19:
                    raise
                time.sleep(0.1)






















        for copie in self.copies:
            try:
                temporaire = copie.with_suffix(copie.suffix + ".tmp")
                temporaire.write_text(texte, encoding="utf-8", newline="\n")
                temporaire.replace(copie)
            except OSError:
                pass










        lignes_cfg = list(traduire(f"lot {self.lot}"))
        for commande in commandes:
            lignes_cfg += traduire(commande)
        try:
            self.cfg.write_text(
                "\n".join(lignes_cfg) + "\n", encoding="utf-8", newline="\n"
            )
        except OSError:
            pass

        return self.lot

    def vider(self) -> None:
        ""




        try:
            self.cfg.write_text("", encoding="utf-8", newline="\n")
        except OSError:
            pass

    def ping(self) -> int:
        return self.envoyer(["ping"])


@dataclass
class Message:
    ""

    niveau: str
    texte: str


class Recepteur:
    ""





    def __init__(self, journal: Path) -> None:
        self.journal = Path(journal)
        self.position = 0
        self.inode = None

    def rembobiner(self) -> None:
        ""
        self.position = 0

    def aller_a_la_fin(self) -> None:
        ""
        try:
            self.position = self.journal.stat().st_size
        except OSError:
            self.position = 0

    def _redemarrage_detecte(self) -> bool:
        ""
        try:
            taille = self.journal.stat().st_size
        except OSError:
            return False
        if taille < self.position:
            self.position = 0
            return True
        return False

    def lire(self) -> list[Message]:
        ""
        if not self.journal.exists():
            return []
        self._redemarrage_detecte()

        try:
            with open(self.journal, "r", encoding="utf-8", errors="replace") as f:
                f.seek(self.position)
                brut = f.read()
                self.position = f.tell()
        except OSError:
            return []

        messages: list[Message] = []
        for ligne in brut.splitlines():
            trouve = MOTIF_LIGNE.search(ligne)
            if trouve:
                brut_message = trouve.group("message").strip()


                niveau = "ERREUR" if "echec" in brut_message else "INFO"
                messages.append(
                    Message(niveau=niveau, texte=brut_message.replace("_", " "))
                )
        return messages


def analyser_accuse(message: Message) -> dict | None:
    ""
    trouve = re.match(r"lot (?P<lot>\S+) applique (?P<ok>\d+)", message.texte)
    if not trouve:
        return None
    return {"lot": trouve.group("lot"), "appliquees": int(trouve.group("ok"))}
