""


















from __future__ import annotations

import ctypes
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from noyau import constructeur, jeu, pont

JEU = "KingdomCome.exe"
APPID = "1771300"


SANS_FENETRE = getattr(subprocess, "CREATE_NO_WINDOW", 0)







CALME_LUA = (
    'local r = {} '
    'local ok = pcall(function() local s = scriptorium '
    'local h = tonumber(s.hostiles_vivants) or 0 if h > 0 then r[#r + 1] = h .. " ennemis debout" end '


    'local c = compagnie and compagnie.CentreDuCamp '
    'if c and System and System.GetEntitiesInSphere then local n = 0 '
    'for _, e in pairs(System.GetEntitiesInSphere(c, 200) or {}) do local nm = "" pcall(function() nm = e:GetName() end) '
    'local mort = false pcall(function() mort = e.actor:IsDead() end) '
    'if string.find(tostring(nm), "scriptorium_ennemi_", 1, true) and not mort then n = n + 1 end end '
    'if n > 0 then r[#r + 1] = n .. " ennemis approchent" end end '
    'local ex = s.expedition if type(ex) == "table" and ex.sortie ~= nil then r[#r + 1] = "une troupe en mission" end '
    'if type(ex) == "table" and ex.retour ~= nil then r[#r + 1] = "une troupe sur le retour" end '
    'local mi = s.missions if type(mi) == "table" and type(mi.m) == "table" and mi.m.apparus '
    'then r[#r + 1] = "la bande d une mission posee pres d Henry" end '
    'local mp = s.missions_en_parallele if type(mp) == "table" and type(mp.dehors) == "function" '
    'and mp.dehors() > 0 then r[#r + 1] = mp.dehors() .. " troupes du Directeur dehors" end '
    'local n = 0 for _ in pairs((s.metiers or {}).sortis or {}) do n = n + 1 end '
    'if n > 0 then r[#r + 1] = n .. " hommes dehors aux metiers" end '



    'local ed, pc = s.editeur, s.plan_du_camp '
    'if type(ed) == "table" and type(ed.objets) == "table" and type(pc) == "table" and compagnie and compagnie.CampActif then '
    'local rp = nil pcall(function() rp = pc.repere(compagnie) end) '
    'if rp then local k = 0 for o in pairs(ed.objets) do local ps = (ed.poses or {})[o] '
    'if (ed._rate or {})[o] == nil and (ps == nil or (ps.x - rp.x) ^ 2 + (ps.y - rp.y) ^ 2 > 0.25 '
    'or math.abs((ps.cap or 0) - rp.cap) > 0.01) then k = k + 1 end end '
    'if k > 0 then r[#r + 1] = k .. " objets du camp encore a poser" end end end end) '
    'if not ok then return "INCONNU" end '
    'if #r == 0 then return "CALME" end '
    'return "AGITE " .. table.concat(r, " et ")'
)







NUIT = (20.0, 6.0)
HEURE_LUA = 'return string.format("HEURE %.2f", (Calendar.GetWorldTime() % 86400) / 3600)'


def lire_l_heure(reponse: str | None) -> float | None:
    ""
    mots = (reponse or "").split()
    for i, m in enumerate(mots[:-1]):
        if m == "HEURE":
            try:
                return float(mots[i + 1].replace(",", "."))
            except ValueError:
                return None
    return None


def de_nuit(heure: float | None) -> bool:
    ""
    return heure is not None and (heure >= NUIT[0] or heure < NUIT[1])


def lire_le_calme(reponse: str | None) -> str | None:
    ""
    if reponse is None:
        return "le jeu ne repond pas"
    mots = reponse.split()
    if mots and mots[0] == "hex":
        mots = mots[1:]
    if mots == ["CALME"]:
        return None
    if mots and mots[0] == "AGITE":
        return " ".join(mots[1:]) or "agite"
    return "reponse inattendue : " + " ".join(mots)[:120]





def seulement_des_metiers(raison: str | None) -> bool:
    if not raison:
        return False
    return all(p.strip().endswith("hommes dehors aux metiers") for p in raison.split(" et "))





def malgre_la_troupe(raison: str | None) -> bool:
    if not raison:
        return False
    return all(p.strip().endswith(("hommes dehors aux metiers", "troupes du Directeur dehors", "une troupe en mission",
                                   "une troupe sur le retour")) for p in raison.split(" et "))


class Jeu:
    ""

    def __init__(self) -> None:
        self.inst = jeu.trouver_jeu()
        if self.inst is None:
            raise RuntimeError("installation du jeu introuvable")
        dossier = jeu.cible_reelle(constructeur.dossier_mod(self.inst))







        self.emetteur = pont.Emetteur(dossier / "local" / "ordres.txt",
                                      racine_jeu=self.inst.racine)
        self.recepteur = pont.Recepteur(self.inst.racine / "kcd.log")

        self.noter = None



    def ecouter(self, prefixes: tuple[str, ...], secondes: float) -> str | None:
        fini = time.time() + secondes
        while time.time() < fini:
            for m in self.recepteur.lire():
                for p in prefixes:
                    if m.texte.startswith(p):
                        return m.texte
            time.sleep(0.3)
        return None

    def demander(self, ordres: list[str], attend: tuple[str, ...],
                 secondes: float = 20) -> str | None:
        ""













        self.emetteur.vider()
        fin = time.time() + secondes
        while time.time() < fin:
            self.emetteur.envoyer(ordres)
            r = self.ecouter(attend, min(3.0, max(0.5, fin - time.time())))
            if r is not None:
                return r
        return None

    def hex(self, code: str, secondes: float = 40, formes: tuple[str, ...] = ()) -> str | None:
        ""


        hexa = code.encode("ascii", "replace").hex()
        self.recepteur.aller_a_la_fin()
        fin = time.time() + secondes
        while time.time() < fin:
            self.emetteur.envoyer(["hex " + hexa])
            sous = time.time() + 4
            while time.time() < sous:
                for m in (self.recepteur.lire() or []):
                    if m.texte.startswith("hex") and (not formes or m.texte[3:].strip().startswith(formes)):


                        self.emetteur.envoyer([])
                        return m.texte
                time.sleep(0.3)
        return None

    def verifier_le_calme(self, accord: bool = False, troupe: bool = False) -> str | None:
        raison = lire_le_calme(self.hex(CALME_LUA, formes=("CALME", "AGITE", "INCONNU")))
        if raison is not None and accord and troupe and malgre_la_troupe(raison):
            return raison
        if raison is not None and accord and seulement_des_metiers(raison):
            return raison
        if raison is not None:
            raise RuntimeError(f"le camp n'est pas calme ({raison}) : je n'installe pas -- attendre, ou demander au joueur")
        return None



    @staticmethod
    def tourne() -> bool:
        r = subprocess.run(["tasklist", "/NH"], capture_output=True, text=True, creationflags=SANS_FENETRE)
        return JEU in r.stdout

    def heure(self) -> float | None:
        ""
        return lire_l_heure(self.hex(HEURE_LUA, 20, formes=("HEURE",)))

    def sauver(self, malgre_la_nuit: bool = False) -> bool:
        ""
        h = self.heure()
        if de_nuit(h) and not malgre_la_nuit:
            raise RuntimeError(
                f"il est {h:.1f} h dans le jeu : sauvegarder ferait dormir Henry jusqu'au matin (mesure du 5/10) -- "
                "attendre le jour (6 h), ou --malgre-la-nuit avec l'accord du joueur")
        self.recepteur.aller_a_la_fin()
        r = self.demander(["sauver"], ("sauve ok", "sauve echec"), 60)
        return r is not None and "ok" in r

    def fermer(self) -> bool:
        subprocess.run(["taskkill", "/IM", JEU, "/T"],
                       capture_output=True, text=True, creationflags=SANS_FENETRE)
        fini = time.time() + 90
        while time.time() < fini:
            if not self.tourne():
                return True
            time.sleep(2)
        subprocess.run(["taskkill", "/F", "/IM", JEU, "/T"],
                       capture_output=True, text=True, creationflags=SANS_FENETRE)
        time.sleep(6)
        return not self.tourne()

    def ouvrir(self) -> bool:
        subprocess.run(["cmd", "/c", "start", "",
                        f"steam://rungameid/{APPID}"], capture_output=True, creationflags=SANS_FENETRE)
        fini = time.time() + 120
        while time.time() < fini:
            if self.tourne():
                return True
            time.sleep(3)
        return False



    def reprendre(self, patience: int = 300) -> str | None:
        ""




        attendu = time.time() + 60
        while time.time() < attendu:
            if self._menu_pret():
                break
            time.sleep(5)

        self.recepteur.aller_a_la_fin()
        depuis = self.recepteur.position
        fini = time.time() + patience
        dernier_refus = None
        while time.time() < fini:
            for frappe in self._chemin_du_menu():



                if self._chargement_commence(depuis):
                    self._noter("le chargement de la partie a commence")
                    return self.demander(["ping", "position"], ("pong", "position "), max(10, fini - time.time()))
                refus = frappe()
                if refus != dernier_refus:
                    self._noter("touches du menu : " + (refus or "elles partent dans le jeu"))
                    dernier_refus = refus
                r = self.demander(["ping", "position"],
                                  ("pong", "position "), 10)
                if r is not None:
                    return r
        return None

    def _noter(self, texte: str) -> None:
        if self.noter is not None:
            try:
                self.noter(texte)
            except Exception:
                pass

    def _chargement_commence(self, depuis: int) -> bool:
        ""
        try:
            with open(self.recepteur.journal, "rb") as f:
                f.seek(depuis)
                return b"Loading saved game" in f.read()
        except OSError:
            return False

    def donnees_de_la_partie(self) -> str | None:
        ""

        r = self.hex('local c=nil pcall(function() c=_G.compagnie:Relire("IntendanceCaisse") end) '
                     'local j=-1 pcall(function() j=Calendar.GetWorldDay() end) '
                     'return "donnees " .. tostring(c) .. " " .. tostring(j)', 30, ("donnees",))
        return r


    def _chemin_du_menu(self):
        ""

























        return [
            lambda: self._frapper(0x0D, 0x1C, 1),
            lambda: self._frapper(0x28, 0x50, 1),
            lambda: self._frapper(0x0D, 0x1C, 1),
            lambda: self._frapper(0x46, 0x21, 1),
            lambda: self._frapper(0x0D, 0x1C, 1),
        ]

    @staticmethod
    def _frapper(code: int, balayage: int, combien: int = 1) -> str:
        ""


        u32 = ctypes.windll.user32
        fen = _fenetre_du_jeu()
        if not fen or not fen[0]:
            return "pas de fenetre du jeu"
        if not mettre_devant(fen[0]):
            return f"le jeu n'est pas devant (devant : {fenetre_de_devant()})"
        time.sleep(0.7)
        for _ in range(combien):
            u32.keybd_event(code, balayage, 0x08, 0)
            time.sleep(0.09)
            u32.keybd_event(code, balayage, 0x08 | 0x02, 0)
            time.sleep(1.2)
        return ""

    def _menu_pret(self) -> bool:
        try:
            t = self.recepteur.journal.read_text(encoding="utf-8",
                                                 errors="replace")
        except OSError:
            return False
        return "main_menu" in t[-40000:]

    @staticmethod
    def _frapper_entree(combien: int = 3) -> None:
        ""
        u32 = ctypes.windll.user32
        for proc in _fenetre_du_jeu():
            u32.ShowWindow(proc, 9)
            u32.SetForegroundWindow(proc)
            break
        time.sleep(2)
        for _ in range(combien):
            u32.keybd_event(0x0D, 0x1C, 0x08, 0)
            time.sleep(0.08)
            u32.keybd_event(0x0D, 0x1C, 0x08 | 0x02, 0)
            time.sleep(1.5)


def jeu_devant(devant: int, jeu_fenetre: int) -> bool:
    ""
    return bool(jeu_fenetre) and devant == jeu_fenetre


def fenetre_de_devant() -> str:
    ""
    u32 = ctypes.windll.user32
    u32.GetForegroundWindow.restype = ctypes.c_void_p
    d = u32.GetForegroundWindow()
    titre = ctypes.create_unicode_buffer(200)
    u32.GetWindowTextW(ctypes.c_void_p(d), titre, 200)
    return f"{int(d or 0)} '{titre.value}'"


def mettre_devant(fenetre: int) -> bool:
    ""



    u32, k32 = ctypes.windll.user32, ctypes.windll.kernel32
    u32.GetForegroundWindow.restype = ctypes.c_void_p
    h = ctypes.c_void_p(fenetre)

    def devant() -> bool:
        time.sleep(0.3)
        return jeu_devant(int(u32.GetForegroundWindow() or 0), fenetre)

    u32.ShowWindow(h, 9)
    u32.SetForegroundWindow(h)
    if devant():
        return True
    fil = u32.GetWindowThreadProcessId(ctypes.c_void_p(u32.GetForegroundWindow()), None)
    moi = k32.GetCurrentThreadId()
    if fil and fil != moi and u32.AttachThreadInput(moi, fil, True):
        u32.BringWindowToTop(h)
        u32.SetForegroundWindow(h)
        u32.AttachThreadInput(moi, fil, False)
        if devant():
            return True
    u32.keybd_event(0x12, 0, 0, 0)
    u32.keybd_event(0x12, 0, 0x02, 0)
    u32.SetForegroundWindow(h)
    return devant()


def _fenetre_du_jeu() -> list[int]:
    ""
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-Process -Name KingdomCome -ErrorAction SilentlyContinue)"
         ".MainWindowHandle"],
        capture_output=True, text=True, creationflags=SANS_FENETRE)
    return [int(l) for l in r.stdout.split() if l.strip().isdigit()]


SAUVEGARDES = Path.home() / "Saved Games" / "kingdomcome2" / "saves"


def derniere_sauvegarde():
    ""
    try:
        f = [(p.stat().st_mtime, p) for p in SAUVEGARDES.rglob("*.whs")]
    except OSError:
        return None
    return max(f, key=lambda x: x[0]) if f else None


def _coffre_et_jour(r: str | None) -> tuple[float | None, int | None]:
    ""
    try:
        _, _, c, j = (r or "").split()
    except ValueError:
        return None, None
    try:
        coffre = float(c)
    except ValueError:
        coffre = None
    try:
        jour = int(float(j))
    except ValueError:
        jour = None
    return coffre, jour


def partie_bien_revenue(avant: str | None, apres: str | None) -> bool:
    ""


    c2, j2 = _coffre_et_jour(apres)
    if c2 is None or j2 is None or j2 <= 1:
        return False
    c1, j1 = _coffre_et_jour(avant)
    if j1 is not None and not (j1 <= j2 <= j1 + 1):
        return False
    if c1 is not None and c1 > 0 and c2 <= 0:
        return False
    return True


def cycle(verbeux: bool = True, accord: bool = False, troupe: bool = False, malgre_la_nuit: bool = False) -> Jeu:
    ""
    g = Jeu()

    def dire(quoi: str) -> None:
        if verbeux:
            print(quoi, flush=True)

    if g.tourne():
        dire("0. je demande au jeu si le camp est calme (ni ennemi, ni troupe dehors)")
        accepte = g.verifier_le_calme(accord, troupe)
        if accepte:
            dire(f"   avec l'accord du joueur, malgre : {accepte}")
        donnees_avant = g.donnees_de_la_partie()
        dire("1. je sauvegarde sa partie")
        avant = derniere_sauvegarde()
        depart = time.time()
        if not g.sauver(malgre_la_nuit):
            raise RuntimeError(
                "l'agent n'a pas confirme la sauvegarde : je ne ferme pas")
        dire("   sauve. j'attends le fichier sur le disque.")


        neuve = None
        while time.time() - depart < 60:
            d = derniere_sauvegarde()
            if d is not None and (avant is None or d[0] > avant[0]) and d[0] >= depart - 5:
                neuve = d
                break
            time.sleep(2)
        if neuve is None:
            raise RuntimeError("aucun fichier de sauvegarde n'est apparu sur le disque : je ne ferme pas le jeu")
        dire(f"   fichier ecrit : {neuve[1].name}. quinze secondes pour le disque.")
        time.sleep(15)


        dire("2. je ferme le jeu")
        if not g.fermer():
            raise RuntimeError("le jeu ne se ferme pas")
        dire("   ferme.")
    else:
        donnees_avant = None
        dire("1-2. le jeu est deja ferme")

    dire("3. j'installe le mod")
    r = constructeur.installer(g.inst)
    dire(f"   {r.detail}")


    from noyau import application_des_bascules
    fait = application_des_bascules.appliquer_en_attente(g.inst)
    if fait:
        dire(f"   reglages du jeu : {fait}")

    dire("4. je relance le jeu")
    if not g.ouvrir():
        raise RuntimeError("le jeu ne demarre pas")

    dire("5. je reprends la partie")
    ou = g.reprendre()
    if ou is None:
        raise RuntimeError("la partie ne reprend pas")
    dire(f"   {ou}")

    apres = g.donnees_de_la_partie()
    dire(f"   avant : {donnees_avant} ; apres : {apres}")
    if not partie_bien_revenue(donnees_avant, apres):
        raise RuntimeError("LA PARTIE REPRISE N'EST PAS LA BONNE (coffre ou jour different) : ne rien sauvegarder ; "
                           "le joueur doit recharger lui-meme la derniere sauvegarde")
    return g


if __name__ == "__main__":
    cycle(accord="--accord-du-joueur" in sys.argv, troupe="--malgre-la-troupe" in sys.argv,
          malgre_la_nuit="--malgre-la-nuit" in sys.argv)
    print("\nla partie tourne, avec le mod a jour.")
