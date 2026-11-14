# Scriptorium: Gestion du camp

The source code of **Gestion du camp** (Camp Management) 2.3.0, the optional small Windows program of
[Scriptorium](https://www.nexusmods.com/kingdomcomedeliverance2/mods/3947), a mod by JoVenGer for Kingdom Come: Deliverance II.
With the mod installed, the H key opens the camp's management in a separate window: a parchment in seven sections, The camp
today, The chest, The men, The craftsmen, Build, The camp map and The objectives.

This repository holds what the published program is built from. The comments were removed from the code, in the same way as
in the published files. The mod itself is not here.

## Get the program

Download it from the [latest release](https://github.com/jovenger/scriptorium-gestion-du-camp/releases/latest): under "Assets",
click the file named `Scriptorium_Gestion_du_camp`, a `.zip`. Unzip it anywhere except "Program Files", run
`Gestion du camp.exe` before you play, then press H in the game. The mod must be installed. It follows the game's language
(French, English, German, Russian, Japanese, Simplified Chinese and Traditional Chinese), and the list at the top right of its
window chooses another one. It closes by itself when you close the game. It isn't signed, so Windows or an antivirus may warn
you.

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
- It talks to the mod through files in the mod's own folder (`noyau/pont.py`). Once the game has received an order, the order
  is replaced by an empty one, so that it is never played again at the next launch.
- It keeps its own data in `%LOCALAPPDATA%\Scriptorium\Gestion du camp`.
- It checks the H key, and no other key, every 50 ms, and acts on it only while its own window is in front, to close that
  window (`gestion_du_camp/programme.py`, `GetAsyncKeyState(0x48)`). It records nothing.
- Every 5 seconds it asks Windows whether the game (`KingdomCome.exe`) is running; once the game has closed, it closes itself
  (`gestion_du_camp/programme.py`, `noyau/lanceur.py`).
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

Le code source de **Gestion du camp** 2.3.0, le petit programme facultatif du mod
[Scriptorium](https://www.nexusmods.com/kingdomcomedeliverance2/mods/3947), de JoVenGer. La touche H ouvre la gestion du camp
dans une fenêtre à part : un parchemin en sept rubriques.

**Pour l'obtenir :** téléchargez-le sur la [dernière version publiée](https://github.com/jovenger/scriptorium-gestion-du-camp/releases/latest) :
sous « Assets », cliquez sur le fichier `Scriptorium_Gestion_du_camp`, un `.zip`. Dézippez-le où vous voulez, sauf dans « Program
Files », lancez `Gestion du camp.exe` avant de jouer, puis appuyez sur H en jeu. Le mod doit être installé. Il suit la langue du jeu
(français, anglais, allemand, russe, japonais, chinois simplifié et chinois traditionnel) ; la liste en haut à droite de sa fenêtre
en choisit une autre. Il se ferme tout seul quand vous fermez le jeu. Il n'est pas signé : Windows ou un antivirus peut vous avertir.

Pour le construire vous-même, suivez les trois commandes ci-dessus. Le programme ne va pas sur internet, ne demande pas les droits
d'administrateur et n'installe rien. La liste en anglais ci-dessus dit tout ce qu'il fait sur votre ordinateur. Tous droits
réservés : voir `LICENCE.txt`.

## Deutsch

Der Quellcode von **Gestion du camp** (Lagerverwaltung) 2.3.0, dem optionalen kleinen Programm der Mod
[Scriptorium](https://www.nexusmods.com/kingdomcomedeliverance2/mods/3947) von JoVenGer. Die Taste H öffnet die Lagerverwaltung
in einem eigenen Fenster: ein Pergament in sieben Rubriken.

**So bekommst du es:** Lade es von der [neuesten Version](https://github.com/jovenger/scriptorium-gestion-du-camp/releases/latest)
herunter: Unter „Assets“ auf die Datei `Scriptorium_Gestion_du_camp` klicken, eine `.zip`. Entpacke sie an einen beliebigen Ort
außer „Program Files“, starte `Gestion du camp.exe` vor dem Spielen und drücke im Spiel H. Die Mod muss installiert sein. Es folgt
der Sprache des Spiels, und die Liste oben rechts im Fenster wählt eine andere. Es schließt sich von selbst, wenn du das Spiel
schließt. Es ist nicht signiert: Windows oder ein Virenschutz können warnen.

Selbst bauen: die drei Befehle oben. Das Programm geht nicht ins Internet, braucht keine Administratorrechte und installiert
nichts. Die englische Liste oben sagt alles, was es auf deinem Computer tut. Alle Rechte vorbehalten: siehe `LICENCE.txt`.

## Русский

Исходный код **Gestion du camp** («Управление лагерем») 2.3.0, необязательной небольшой программы мода
[Scriptorium](https://www.nexusmods.com/kingdomcomedeliverance2/mods/3947) от JoVenGer. Клавиша H открывает управление лагерем
в отдельном окне: пергамент из семи разделов.

**Как получить:** скачайте ее со [страницы последней версии](https://github.com/jovenger/scriptorium-gestion-du-camp/releases/latest):
в разделе «Assets» нажмите на файл `Scriptorium_Gestion_du_camp`, это `.zip`. Распакуйте куда угодно, кроме «Program Files»,
запустите `Gestion du camp.exe` до игры, затем нажмите H в игре. Мод должен быть установлен. Программа следует языку игры, а список
вверху справа в ее окне выбирает другой. Она закрывается сама, когда вы закрываете игру. Она не подписана: Windows или антивирус
могут предупредить.

Собрать самому: три команды выше. Программа не выходит в интернет, не требует прав администратора и ничего не устанавливает.
Список на английском выше говорит обо всем, что она делает на вашем компьютере. Все права защищены: см. `LICENCE.txt`.

## 日本語

JoVenGer によるMod [Scriptorium](https://www.nexusmods.com/kingdomcomedeliverance2/mods/3947) の、任意で使える小さなプログラム
**Gestion du camp**（野営地の管理）2.3.0 のソースコードです。Hキーで野営地の管理が別ウィンドウで開きます。7つの項目の羊皮紙です。

**入手方法：** [最新版](https://github.com/jovenger/scriptorium-gestion-du-camp/releases/latest)からダウンロードします。「Assets」の
`Scriptorium_Gestion_du_camp`（`.zip` ファイル）をクリックしてください。「Program Files」以外の好きな場所に展開し、プレイの前に
`Gestion du camp.exe` を起動して、ゲーム中にHキーを押します。Modのインストールが必要です。ゲームの言語に従い、ウィンドウ右上の一覧で
別の言語を選べます。ゲームを閉じると自動で閉じます。署名がないため、Windowsやウイルス対策ソフトが警告することがあります。

自分でビルドするには、上の3つのコマンドを使います。インターネットには接続せず、管理者権限も不要で、何もインストールしません。
パソコン上で行うことは、上の英語の一覧にすべて書いてあります。著作権はすべて作者に帰属します：`LICENCE.txt` を参照。

## 简体中文

JoVenGer 的模组 [Scriptorium](https://www.nexusmods.com/kingdomcomedeliverance2/mods/3947) 的可选小程序
**Gestion du camp**（营地管理）2.3.0 的源代码。按 H 键，营地管理会在单独的窗口中打开：一张分七个栏目的羊皮纸。

**获取方式：** 从[最新版本](https://github.com/jovenger/scriptorium-gestion-du-camp/releases/latest)下载：在“Assets”下点击
`Scriptorium_Gestion_du_camp` 文件（一个 `.zip`）。解压到“Program Files”以外的任意位置，游戏前运行 `Gestion du camp.exe`，
然后在游戏中按 H。需要已安装模组。它跟随游戏的语言，窗口右上角的列表可以另选一种。关闭游戏时它会自动关闭。它没有签名，
Windows 或杀毒软件可能会发出警告。

自己构建：使用上面的三条命令。程序不联网，不需要管理员权限，也不安装任何东西。它在你电脑上做的所有事情都写在上面的英文列表里。
保留所有权利：见 `LICENCE.txt`。

## 繁體中文

JoVenGer 的模組 [Scriptorium](https://www.nexusmods.com/kingdomcomedeliverance2/mods/3947) 的可選小程式
**Gestion du camp**（營地管理）2.3.0 的原始碼。按 H 鍵，營地管理會在獨立的視窗中開啟：一張分七個欄目的羊皮紙。

**取得方式：** 從[最新版本](https://github.com/jovenger/scriptorium-gestion-du-camp/releases/latest)下載：在「Assets」下點擊
`Scriptorium_Gestion_du_camp` 檔案（一個 `.zip`）。解壓縮到「Program Files」以外的任意位置，遊戲前執行 `Gestion du camp.exe`，
然後在遊戲中按 H。需要已安裝模組。它跟隨遊戲的語言，視窗右上角的清單可以另選一種。關閉遊戲時它會自動關閉。它沒有簽章，
Windows 或防毒軟體可能會發出警告。

自行建置：使用上面的三條指令。程式不連網，不需要系統管理員權限，也不安裝任何東西。它在你電腦上做的所有事情都寫在上面的英文清單裡。
保留所有權利：見 `LICENCE.txt`。
