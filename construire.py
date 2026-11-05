# -*- coding: utf-8 -*-
"""Builds the "Gestion du camp" program from these sources.

    py -3.13 -m venv venv
    venv\\Scripts\\python -m pip install -r requirements.txt
    venv\\Scripts\\python construire.py

Result: dist\\Gestion du camp\\Gestion du camp.exe
"""
import ast
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ICI = Path(__file__).resolve().parent
SOURCES = ICI / "sources"
NOM = "Gestion du camp"
# (unused by the program: left out of the build)
INUTILES = ("opengl32sw.dll", "translations")
TOUJOURS = {"importlib.util", "xml.etree.ElementTree", "xml.sax.saxutils", "ctypes.wintypes"}


def modules_de_la_bibliotheque():
    """The sources are loaded from disk: PyInstaller must be told which standard modules they import."""
    vus = set(TOUJOURS)
    for f in SOURCES.rglob("*.py"):
        for n in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
            noms = [a.name for a in n.names] if isinstance(n, ast.Import) else (
                [n.module] if isinstance(n, ast.ImportFrom) and n.module and not n.level else [])
            vus.update(nom for nom in noms if nom.split(".")[0] in sys.stdlib_module_names)
    return sorted(vus)


def main():
    for vieux in ("build", "dist"):
        if (ICI / vieux).exists():
            shutil.rmtree(ICI / vieux)
    commande = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir", "--windowed", "--noupx",
                "--name", NOM, "--distpath", str(ICI / "dist"), "--workpath", str(ICI / "build"),
                "--specpath", str(ICI), "--exclude-module", "PyQt6", "--exclude-module", "tkinter"]
    for haut in sorted(p.name for p in SOURCES.iterdir() if p.is_dir()):
        commande += ["--add-data", f"{SOURCES / haut}{os.pathsep}{haut}"]
    for m in modules_de_la_bibliotheque():
        commande += ["--hidden-import", m]
    subprocess.run(commande + [str(ICI / "lancement_gele.py")], check=True, cwd=str(ICI))
    dossier = ICI / "dist" / NOM
    for inutile in INUTILES:
        for p in list(dossier.rglob(inutile)):
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    # (Nexus Mods rejects an upload with an archive inside it: PyInstaller's small one is unpacked next to itself)
    archive = dossier / "_internal" / "base_library.zip"
    with zipfile.ZipFile(archive) as z:
        z.extractall(archive.parent)
    archive.unlink()
    for texte in ("LISEZMOI.txt", "LICENCES_TIERCES.txt", "LICENCE.txt"):
        shutil.copyfile(ICI / texte, dossier / texte)
    print(dossier)


if __name__ == "__main__":
    main()
