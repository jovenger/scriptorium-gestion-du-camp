""





from __future__ import annotations

import zipfile
from pathlib import Path

SIGNATURE_ZIP = b"PK\x03\x04"


def est_un_pak(chemin: Path) -> bool:
    ""
    try:
        with open(chemin, "rb") as f:
            return f.read(4) == SIGNATURE_ZIP
    except OSError:
        return False


def lister(chemin: Path) -> list[zipfile.ZipInfo]:
    ""
    try:
        with zipfile.ZipFile(chemin) as z:
            return z.infolist()
    except (OSError, zipfile.BadZipFile):
        return []


def lire(chemin: Path, interne: str) -> bytes | None:
    ""
    try:
        with zipfile.ZipFile(chemin) as z:
            return z.read(interne)
    except (OSError, KeyError, zipfile.BadZipFile):
        return None


def lire_texte(chemin: Path, interne: str) -> str | None:
    donnees = lire(chemin, interne)
    if donnees is None:
        return None
    return donnees.decode("utf-8", errors="replace")


def ecrire_pak(destination: Path, fichiers: dict[str, bytes | str]) -> Path:
    ""





    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporaire = destination.with_suffix(destination.suffix + ".tmp")

    with zipfile.ZipFile(temporaire, "w", zipfile.ZIP_DEFLATED) as z:
        for interne, contenu in sorted(fichiers.items()):
            donnees = contenu.encode("utf-8") if isinstance(contenu, str) else contenu
            z.writestr(interne.replace("\\", "/"), donnees)

    try:
        temporaire.replace(destination)
    except PermissionError as err:



        temporaire.unlink(missing_ok=True)
        raise PermissionError(
            f"impossible d'ecrire {destination.name} : le fichier est verrouille. "
            "Ferme le jeu avant d'appliquer des changements."
        ) from err
    return destination


def deja_identique(chemin: Path, fichiers: dict[str, bytes | str]) -> bool:
    ""







    if not chemin.exists():
        return not fichiers
    attendu = {
        nom: (valeur.encode("utf-8") if isinstance(valeur, str) else valeur)
        for nom, valeur in fichiers.items()
    }
    try:
        with zipfile.ZipFile(chemin) as archive:
            noms = set(archive.namelist())
            if noms != set(attendu):
                return False
            return all(archive.read(nom) == attendu[nom] for nom in noms)
    except (OSError, zipfile.BadZipFile):

        return False


def verifier_pak(chemin: Path) -> tuple[bool, str]:
    ""




    if not chemin.exists():
        return False, "le fichier n'existe pas"
    if not est_un_pak(chemin):
        return False, "signature ZIP absente"
    try:
        with zipfile.ZipFile(chemin) as z:
            abime = z.testzip()
            if abime is not None:
                return False, f"CRC invalide sur '{abime}'"
            nombre = len(z.infolist())
    except (OSError, zipfile.BadZipFile) as err:
        return False, f"archive illisible : {err}"
    return True, f"{nombre} fichier(s), CRC verifie"




_SOURCES_EXCLUES = ("autotests", "test", "deprecated", "reward")


def sources_table(pak_tables: Path, dossier: str, base: str) -> list[str]:
    ""






    with zipfile.ZipFile(pak_tables) as z:
        noms = z.namelist()
    racine = f"Libs/Tables/{dossier}/{base}"
    principal = f"{racine}.xml"
    patches = sorted(
        n for n in noms
        if n.startswith(f"{racine}__") and n.endswith(".xml")
        and not any(x in n.lower() for x in _SOURCES_EXCLUES)
    )
    return ([principal] if principal in noms else []) + patches


def sources_objets(pak_tables: Path) -> list[str]:
    ""









    with zipfile.ZipFile(pak_tables) as z:
        noms = z.namelist()
    base = "Libs/Tables/item/item.xml"
    patches = sorted(
        n for n in noms
        if n.startswith("Libs/Tables/item/item__") and n.endswith(".xml")
        and not any(x in n.lower() for x in _SOURCES_EXCLUES)
    )
    return ([base] if base in noms else []) + patches
