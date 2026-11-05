
""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from essais.cycle_en_jeu import Jeu

def parler(g, code, secondes=40):
    hexa = code.encode("ascii", "replace").hex()
    g.recepteur.aller_a_la_fin()
    fin = time.time() + secondes
    while time.time() < fin:
        g.emetteur.envoyer(["hex " + hexa])
        sous = time.time() + 4
        while time.time() < sous:
            for m in (g.recepteur.lire() or []):
                if m.texte.startswith(("hex", "eval")):




                    g.emetteur.envoyer([])
                    return m.texte
            time.sleep(0.3)
    return None

if __name__ == "__main__":
    if sys.argv[1] == "-f":
        code = open(sys.argv[2], encoding="utf-8").read()
    else:
        code = sys.argv[1]
    code = " ".join(l.split("--")[0].strip() for l in code.splitlines() if l.strip() and not l.strip().startswith("--"))
    g = Jeu()
    print(parler(g, code), flush=True)
