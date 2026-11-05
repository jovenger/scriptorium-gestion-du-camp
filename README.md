# Scriptorium: Gestion du camp

The source code of **Gestion du camp**, the optional small Windows program of
[Scriptorium](https://www.nexusmods.com/kingdomcomedeliverance2/mods/3947), a mod by JoVenGer for Kingdom Come: Deliverance II.
With the mod installed, the H key opens the camp's management in a separate window: bank, hiring, camp map, staff, trades,
objectives.

This repository holds what the published program is built from. The comments were removed from the code, in the same way as
in the published files. The mod itself is not here.

## Get the program

Download it from the [latest release](https://github.com/jovenger/scriptorium-gestion-du-camp/releases/latest): under "Assets",
click the file named `Scriptorium_Gestion_du_camp`, a `.zip`. Unzip it anywhere except "Program Files", run
`Gestion du camp.exe` before you play, then press H in the game. The mod must be installed. It follows the game's language
(French, English, German, Japanese, Chinese), and the list at the top right of its window chooses another one. It isn't signed,
so Windows or an antivirus may warn you.

## Build it

Windows, Python 3.13:

```
py -3.13 -m venv venv
venv\Scripts\python -m pip install -r requirements.txt
venv\Scripts\python construire.py
```

The result is `dist\Gestion du camp\Gestion du camp.exe`, built with PyInstaller in folder mode, with no compression
(`--onedir --noupx`). The Python sources are not compiled into the program: they are plain files in its `_internal` folder, the
same files as in `sources`, so anyone can read what it runs. PyInstaller's `base_library.zip` is unpacked into `_internal`, so
that the published zip holds no archive inside it.

## What it does on your computer

- It finds the game through the Steam path in the registry (`HKCU\Software\Valve\Steam`) and Steam's library folders, or asks
  for the game's folder (`noyau/jeu.py`).
- It reads the game's log, `kcd.log`, to follow the H key and the mod's answers (`gestion_du_camp/touche_h_integree.py`).
- It talks to the mod through files in the mod's own folder (`noyau/pont.py`).
- It keeps its own data in `%LOCALAPPDATA%\Scriptorium\Gestion du camp`.
- It checks the H key, and no other key, every 50 ms, and acts on it only while its own window is in front, to close that
  window (`gestion_du_camp/programme.py`, `GetAsyncKeyState(0x48)`). It records nothing.
- It simulates an Alt key press when Windows refuses to bring its window in front of the game (`noyau/premier_plan.py`).
- It uses a local named channel so that only one copy runs at a time (`QLocalServer`).
- It restarts itself when the language changes, and keeps the language you chose in a small file in that same folder
  (`gestion_du_camp/programme.py`, `noyau/langue_du_programme.py`).

It has no internet access: the sources use no network client. It needs no administrator rights and installs nothing.

The sources also contain helpers shared with the author's development tools, such as closing and restarting the game and
pressing keys in its menu (`essais/cycle_en_jeu.py`, `noyau/lanceur.py`). They appear in this list so that a reader is not
surprised by them.

The sources import `PyQt6`, but the program is built with PySide6 (LGPL): `lancement_gele.py` makes PySide6 answer to that name.
PyQt6 is never included.

## Licence

(c) 2026 JoVenGer, all rights reserved: see `LICENCE.txt`. Third-party software: see `LICENCES_TIERCES.txt`.

---

## En français

Le code source de **Gestion du camp**, le petit programme facultatif du mod
[Scriptorium](https://www.nexusmods.com/kingdomcomedeliverance2/mods/3947), de JoVenGer.

**Pour l'obtenir :** téléchargez-le sur la [dernière version publiée](https://github.com/jovenger/scriptorium-gestion-du-camp/releases/latest) :
sous « Assets », cliquez sur le fichier `Scriptorium_Gestion_du_camp`, un `.zip`. Dézippez-le où vous voulez, sauf dans « Program
Files », lancez `Gestion du camp.exe` avant de jouer, puis appuyez sur H en jeu. Le mod doit être installé. Il suit la langue du jeu
(français, anglais, allemand, japonais, chinois) ; la liste en haut à droite de sa fenêtre en choisit une autre. Il n'est pas signé :
Windows ou un antivirus peut vous avertir.

Pour le construire vous-même, suivez les trois commandes ci-dessus. Le programme ne va pas sur internet, ne demande pas les droits
d'administrateur et n'installe rien. La liste ci-dessus dit tout ce qu'il fait sur votre ordinateur. Tous droits réservés : voir
`LICENCE.txt`.
