
""



from __future__ import annotations


ORDRES = [
    ("entrainement", "À l'entraînement", "Il emmène au terrain ceux qui sont en retard d'entraînement.",
     "Le colonel emmènera les retardataires à l'entraînement."),
    ("moral", "Remonter le moral", "Il va parler aux hommes dont le moral est le plus bas.",
     "Le colonel fera le tour du camp pour remonter le moral."),
    ("repos", "Repos des épuisés", "Il envoie se reposer ceux qui tiennent à peine debout.",
     "Le colonel enverra les épuisés se reposer."),
    ("bains", "Blessés aux bains", "Il envoie aux bains les blessés qui ne se soignent pas d'eux-mêmes.",
     "Le colonel enverra les blessés aux bains."),
    ("equipement", "Inspecter l'équipement", "Il envoie à la forge ceux dont une pièce est usée ; la forge les sert en premier.",
     "Le colonel inspectera l'équipement et enverra à la forge ce qui est usé."),
    ("querelle", "Calmer une querelle", "Il va voir les deux pires ennemis du camp et les réconcilie.",
     "Le colonel ira calmer la pire querelle du camp."),
    ("revue", "Revue des troupes", "Il passe devant les plus mal en point et arrange ce qui ne va pas (bains, forge, repos, moral).",
     "Le colonel passera les troupes en revue."),
    ("exercice", "Exercice général", "Il emmène au terrain les moins aguerris des hommes libres, pas seulement les retardataires.",
     "Le colonel mènera l'exercice général."),
    ("garde", "Doubler la garde", "Pour cette nuit : deux fois plus de gardes à la ronde ; l'effectif d'avant revient à 6 h.",
     "Le colonel double la garde cette nuit."),
    ("elite", "Troupe d'élite", "Il rassemble les meilleurs du camp au terrain, prêts pour une mission difficile.",
     "Le colonel prépare la troupe d'élite."),
]
CLES = {o[0] for o in ORDRES}


def phrase(quoi: str) -> str:
    return next(o[3] for o in ORDRES if o[0] == quoi)
