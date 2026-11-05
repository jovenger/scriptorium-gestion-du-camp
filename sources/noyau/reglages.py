""













from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import quoteattr

from . import archives

ENTETE_RPG = (
    '<?xml version="1.0" encoding="us-ascii"?>\n'
    '<database xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
    'name="barbora" xsi:noNamespaceSchemaLocation="../database.xsd">\n'
)
ENTETE_ITEM = (
    '<?xml version="1.0" encoding="us-ascii"?>\n'
    '<database xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
    'name="barbora" xsi:noNamespaceSchemaLocation="item.xsd">\n'
)


@dataclass(frozen=True)
class Reglage:
    ""

    cle: str
    libelle: str
    defaut: float
    mini: float
    maxi: float
    note: str = ""


@dataclass(frozen=True)
class Variable:
    ""

    nom: str
    libelle: str
    defaut: str
    note: str = ""





PROGRESSION = [
    Reglage("SkillXPHit", "XP par coup porte", 1, 0, 100),
    Reglage("SkillXPKill", "XP par ennemi tue", 18, 0, 500),
    Reglage("SkillXPBlock", "XP par parade", 0.5, 0, 50),
    Reglage("SkillXPPerfectBlock", "XP par parade parfaite", 2.5, 0, 100),
    Reglage("SkillXPRiposte", "XP par riposte", 3, 0, 100),
    Reglage("SkillXPComboHit", "XP par enchainement", 3, 0, 100),
    Reglage("StatXPKill", "XP de statistique par mise a mort", 12, 0, 300),
    Reglage("StealthSneakBaseXp", "XP de furtivite (deplacement)", 13, 0, 300),
    Reglage("StealthAttackMinXp", "XP minimum d'attaque furtive", 30, 0, 500),
    Reglage("StatXpAgilityForStealth", "Agilite gagnee en furtivite", 8, 0, 200),
    Reglage("SpeechXPLevelBase", "Base d'XP d'eloquence", 25, 1, 200),
    Reglage("SpeechXPLevelDiff", "Ecart d'XP d'eloquence par niveau", 40, 1, 300),
    Reglage("ReadingXpPerHour", "XP de lecture par heure", 30, 0, 500),
    Reglage("ReadingSpeechXPBase", "Eloquence gagnee en lisant", 20, 0, 5000),
    Reglage("StatXPSpeechPersuadeCoerceSuccessMax",
            "Eloquence par persuasion reussie", 40, 0, 5000),
    Reglage("StatXPSpeechSkillCheckSuccessMax",
            "Eloquence par test reussi", 25, 0, 5000),
    Reglage("StatXPSpeechSkillCheckFailMax",
            "Eloquence par test rate", 12.5, 0, 5000),
    Reglage("StatXPSpeechSkillStatSkillCheckSuccessMax",
            "Eloquence par test de competence reussi", 18, 0, 5000),
    Reglage("StatXPSpeechSkillStatSkillCheckFailMax",
            "Eloquence par test de competence rate", 9, 0, 5000),
    Reglage("LockPickingToleranceDifficultyCoef",
            "Difficulte du crochetage", 0.48, 0.01, 2.0,
            "plus bas = les serrures cedent plus facilement"),
    Reglage("ControllerLockPickingToleranceDifficultyCoef",
            "Difficulte du crochetage (manette)", 0.46, 0.01, 2.0),
    Reglage("HunterXPKill", "XP de chasse par prise", 20, 0, 300),
    Reglage("HerbGatherXP", "XP par plante cueillie", 5, 0, 200),
    Reglage("HorseRidingXPPerDistance", "XP d'equitation par distance", 15, 0, 500),
    Reglage("PickpocketingXP", "XP de vol a la tire", 30, 0, 500),
    Reglage("LockPickingSuccessXPMulCoef", "Multiplicateur d'XP de crochetage",
            60, 0, 500),
    Reglage("StrengthXPLevelDiff", "Ecart d'XP de force par niveau", 40, 1, 300),
    Reglage("AgilityXPLevelDiff", "Ecart d'XP d'agilite par niveau", 35, 1, 300),
    Reglage("VitalityXPLevelDiff", "Ecart d'XP de vitalite par niveau", 35, 1, 300),
]




SURVIE = [
    Reglage("MetabolismDigestSpeed", "Vitesse de digestion (la faim vient)",
            0.0244, 0.0, 0.2, "plus bas = on a faim moins vite"),
    Reglage("MetabolismAbsorbSpeed", "Vitesse d'absorption", 0.003, 0.0, 0.05),
    Reglage("FoodOverEat", "Seuil de suralimentation", 150, 50, 1000),
    Reglage("FoodPoisoningDigestModifier", "Effet des aliments avaries",
            0.3, 0.0, 1.0),
    Reglage("FoodHealthThreshold", "Seuil de sante lie a la nourriture",
            0.2, 0.0, 1.0),
    Reglage("InjuryRegenInterval", "Intervalle de regeneration des blessures",
            20, 1, 200),
    Reglage("FullClothDirtyingOnFullSpeed", "Salissure en course",
            35000, 100, 999999),
    Reglage("FullClothDirtyingOnZeroSpeed", "Salissure a l'arret", 500, 10, 999999),
    Reglage("ClothesBloodSoakOnMaxBleeding", "Imbibition de sang", 240, 10, 999999),
]




ENDURANCE = [
    Reglage("BaseAttackStaminaCost", "Cout en endurance d'une attaque", 26, 0, 100),
    Reglage("StamRegenFromVit", "Regeneration d'endurance par vitalite",
            0.8, 0.0, 10.0, "plus haut = recuperation plus rapide"),
    Reglage("MinStaminaDamage", "Degats d'endurance minimum", 15, 0, 100),
    Reglage("MaxStaminaDmgR", "Degats d'endurance maximum", 80, 0, 300),
    Reglage("SprintStaminaSavingLowerBound", "Economie au sprint (borne basse)",
            10, 0, 100),
    Reglage("SprintStaminaSavingUpperBound", "Economie au sprint (borne haute)",
            80, 0, 100),
    Reglage("StaminaDeficitHealthDamageA", "Degats de sante par manque (A)",
            0.05, 0.0, 1.0),
    Reglage("StaminaDeficitHealthDamageB", "Degats de sante par manque (B)",
            0.075, 0.0, 1.0),
    Reglage("MaxStatToAttackStaminaCostStatDiff", "Ecart de stat sur le cout",
            10, 1, 60),
]




COMBAT = [
    Reglage("LethalDmgR", "Seuil de degats letaux", 300, 10, 2000,
            "plus haut = duels moins mortels"),
    Reglage("CombatHitUnconsciousDepth", "Seuil d'evanouissement", 480, 10, 3000),
    Reglage("GoodWeaponAttack", "Reference d'attaque d'une bonne arme", 90, 1, 500),
    Reglage("GoodArmorDefense", "Reference de defense d'une bonne armure",
            100, 1, 500),
    Reglage("WeaponStatusToAttackCoef", "Poids de l'usure de l'arme",
            0.6, 0.0, 2.0),
    Reglage("ArmorStatusToDefenseCoef", "Poids de l'usure de l'armure",
            0.6, 0.0, 2.0),
    Reglage("MaxAttackSpeedMod", "Bonus de vitesse d'attaque", 0.2, 0.0, 2.0),
    Reglage("AgiDiffToAttackSpeed", "Effet de l'agilite sur la vitesse",
            0.1, 0.0, 1.0),
    Reglage("CombatPerfectBlockProb1", "Chance de parade parfaite (IA)",
            2.5, 0.0, 20.0),
    Reglage("CombatNoBlockProb0", "Chance que l'IA ne pare pas", 0.3, 0.0, 1.0),
    Reglage("DamageToArmorStatus", "Usure de l'armure sous les coups",
            0.3, 0.0, 2.0),
    Reglage("MissileWeaponDamageStatus", "Usure des armes de jet", 0.3, 0.0, 2.0),
    Reglage("CombatLevelToRelativeAttackIncrease", "Effet du niveau sur l'attaque",
            0.5, 0.0, 3.0),
    Reglage("AdditionalAttackerCountForMaxFadingBuff",
            "Assaillants avant malus maximum", 1, 1, 10),
]




ENCOMBREMENT = [
    Reglage("BaseInventoryCapacity", "Poids transportable de base", 90, 10, 100000,
            "la vraie limite d'emport, avant le bonus de force"),
    Reglage("StrengthToInventoryCapacity", "Poids gagne par point de force",
            10, 0, 1000),
    Reglage("StrToEqwArmorLoad", "Force -> charge d'armure supportee", 40, 1, 300),
    Reglage("AgiToEqwArmorLoad", "Agilite -> charge d'armure supportee",
            40, 1, 300),
    Reglage("VitToEqwArmorLoad", "Vitalite -> charge d'armure supportee",
            0, 0, 300),
    Reglage("ArmorLoadDiffToMax", "Ecart de charge avant malus maximum",
            60, 1, 300),
    Reglage("ArmorLoadToJumpCost", "Cout du saut selon la charge", 1.8, 0.0, 10.0),
    Reglage("HeavyWeaponWeight", "Seuil d'arme lourde", 99, 1, 500),
]




FABRICATION = [
    Reglage("BlacksmithingEffectivityToXP", "XP de forge par coup efficace",
            0.75, 0.1, 20.0),
    Reglage("BlacksmithingFinishingXP", "XP a la fin d'une piece", 135, 10, 2000),
    Reglage("BlacksmithingMaxQualityLossFactor", "Perte de qualite en forge",
            0.017, 0.0, 0.1),
    Reglage("BlacksmithingOverheatQualityLossCoef", "Penalite de surchauffe",
            0.003, 0.0, 0.05),
    Reglage("AlchemyXPMultiplierSecondQualityPotion", "XP alchimie qualite 2",
            1.35, 1.0, 20.0),
    Reglage("AlchemyXPMultiplierThirdQualityPotion", "XP alchimie qualite 3",
            2.0, 1.0, 30.0),
    Reglage("AlchemyRecipeStepsTolerance", "Tolerance sur les recettes", 4, 0, 30),
    Reglage("AlchemyDryHerbQuality", "Qualite des herbes sechees", 0.3, 0.0, 1.0),
    Reglage("AlchemyDecayedHerbQuality", "Qualite des herbes fanees",
            0.01, 0.0, 1.0),
    Reglage("RepairKitCapacity", "Capacite d'un kit de reparation",
            600, 50, 10000),
    Reglage("RepairPriceModif", "Cout des reparations", 0.45, 0.0, 3.0),
    Reglage("SkillXPUseRepairKit", "XP par kit utilise", 1.5, 0.1, 50.0),
    Reglage("BlacksmithingMaxCompletionGainFactor",
            "Avancement gagne par coup de marteau", 0.02, 0.001, 1.0),
    Reglage("SurvivalXpRewardPerCookedItem", "XP par plat cuisine", 1, 0, 100),
    Reglage("SurvivalXpRewardPerSmokedItem", "XP par aliment fume", 3, 0, 100),
]




ECONOMIE = [
    Reglage("QuestMoneyRewardScaleConstant", "Echelle des recompenses de quete",
            1.025, 0.5, 20.0),
    Reglage("IndulgencePriceFactor", "Facteur du prix des indulgences",
            720, 1, 5000),
    Reglage("IndulgencePriceMax", "Prix maximum d'une indulgence",
            10000, 10, 100000),
    Reglage("IndulgencePriceMin", "Prix minimum d'une indulgence", 10, 1, 10000),
    Reglage("ItemOwnerFadePriceToHours", "Oubli des objets voles",
            0.015, 0.0, 5.0),
    Reglage("RepairShopSkillPriceMultiplier",
            "Prix de reparation selon la competence", 0.005, 0.0, 1.0),
    Reglage("PickpocketingTreasurePriceXP", "XP selon la valeur volee",
            110, 0, 1000),
]




CHEVAL = [
    Reglage("HorseStaminaDrainPerSpurLevel", "Endurance perdue par eperon",
            4, 0, 50),
    Reglage("HorseSpurDashIncrement", "Gain de vitesse par eperon", 7, 0, 50),
    Reglage("RiderHorseStaminaCoef", "Poids du cavalier", 0.75, 0.0, 3.0),
    Reglage("HorseRidingToHorseStamina", "Endurance du cheval a la monte",
            0.45, 0.0, 3.0),
    Reglage("HorseWithMaxStatsPrice", "Prix d'un cheval au maximum",
            6000, 100, 100000),
]












PERCEPTION_REGLES = [
    Reglage("PerceptionMaxFov", "Champ de vision des PNJ (degres)", 100, 5, 180,
            "abaisser rend les gardes myopes sur les cotes"),
    Reglage("VisionToViewRadius", "Portee de la vue", 1.35, 0.1, 5,
            "multiplie la distance a laquelle un PNJ vous distingue"),
    Reglage("HearingToFov", "Poids de l'ouie dans la detection", 1, 0, 5),
    Reglage("MaxHearingSoundAttenuationCoef",
            "Attenuation du bruit avec la distance", 0.02, 0.001, 1,
            "monter etouffe les bruits de pas plus vite"),
    Reglage("PerceptionBaseCha", "Attention de base d'un PNJ", 15, 0, 100,
            "plus bas, plus il faut de temps pour vous reconnaitre"),
    Reglage("PerceptionPriorBoostPlayer",
            "Attention portee au joueur", 20, 0, 200,
            "c'est ce qui fait qu'on vous remarque avant les autres"),
    Reglage("PerceptionPriorBoostRangedWeapon",
            "Attention si vous tenez une arme de jet", 4.2, 0, 50),
    Reglage("PerceptionPriorWeapon", "Attention si vous etes arme", 6, 0, 50),
    Reglage("PerceptionPriorConsp", "Poids de votre allure voyante", 6, 0, 50),
    Reglage("PerceptionPriorCha", "Poids de votre charisme", 0.15, 0, 5),
    Reglage("PerceptionPriorVisPeople", "Attention en foule", 3, 0, 50),
    Reglage("PerceptionPriorEnemyRelationship",
            "Attention d'un ennemi declare", -15, -100, 100),
    Reglage("PerceptionInnerConeMaxRelSize",
            "Largeur du cone de vision precise", 1, 0.1, 3),
    Reglage("ItemOwnerIsShopkeeperToSuspiciency",
            "Soupcon d'un marchand pour ses propres biens", 10, 0, 100,
            "abaisser facilite le recel chez celui qu'on a vole"),
    Reglage("ItemOwnerFactionDistanceToSuspiciencyMin",
            "Soupcon selon la distance au proprietaire", 0.15, 0, 5),
]





REPUTATION_REGLES = [
    Reglage("ReputationSpatialPrapagation",
            "Propagation de la reputation aux alentours", 0.25, 0, 2,
            "0 = ce que vous faites ici ne se sait pas ailleurs"),
    Reglage("ReputationSpatialPropagationDistance",
            "Distance de propagation (metres)", 400, 0, 5000),
    Reglage("ReputationPropagationCoefCap",
            "Plafond de propagation", 0.15, 0, 2),
]










USURE = [
    Reglage("DamageToArmorStatusHigherLayers",
            "Usure de la couche exterieure", 0.375, 0, 2,
            "0 = plaques et mailles ne s'abiment plus au combat"),
    Reglage("DamageToArmorStatusLowerLayers",
            "Usure des couches interieures", 0.0075, 0, 1),
    Reglage("ArmorStatusToCharismaCoef",
            "Effet d'un equipement abime sur le charisme", 0.6, 0, 3,
            "0 = une armure cabossee n'inspire plus le mepris"),
    Reglage("ItemHealthPriceStatusWeight",
            "Effet de l'usure sur le prix de revente", 0.99, 0, 2),
    Reglage("RepairKitMinSkillForQuality2",
            "Entretien requis pour une reparation correcte", 5, 0, 30),
    Reglage("RepairKitMinSkillForQuality3",
            "Entretien requis pour une bonne reparation", 12, 0, 30),
    Reglage("RepairKitMinSkillForQuality4",
            "Entretien requis pour une reparation parfaite", 16, 0, 30),
]








MINIJEUX = [
    Reglage("LockPickingAppropriateTolerance",
            "Largeur de la zone d'accroche", 0.048, 0.001, 1,
            "monter elargit la zone : le crochetage devient aise"),
    Reglage("LockPickingToleranceBaseCoef",
            "Tolerance de base du crochetage", 0.64, 0, 5),
    Reglage("LockPickingToleranceSkillCoef",
            "Part du talent dans la tolerance", 0.48, 0, 5),
    Reglage("LockPickingCursorShakeRangeMax",
            "Tremblement du curseur (maximum)", 0.34, 0, 2,
            "0 = la main ne tremble plus du tout"),
    Reglage("LockPickingCursorShakeRangeMin",
            "Tremblement du curseur (minimum)", 0.08, 0, 2),
    Reglage("LockPickingCursorShakeSpeed",
            "Vitesse du tremblement", 5.32, 0, 20),
    Reglage("LockPickingSkillToShakeRel",
            "Effet du talent sur le tremblement", 0.028, 0, 1),
    Reglage("LockPickingAgilityXP",
            "Agilite gagnee par serrure", 8, 0, 200),
]





PROPRETE = [
    Reglage("ArmorDirtToCharismaCoef",
            "Effet de la crasse sur le charisme", 0.8, 0, 3,
            "0 = on vous parle aussi bien couvert de boue"),
    Reglage("ClothDirtyingOnHorseModifier",
            "Salissure a cheval", 0.5, 0, 3),
    Reglage("DreadSkillcheckBloodinessWeight",
            "Effet du sang sur la crainte inspiree", 0.15, 0, 2),
    Reglage("DreadSkillcheckDirtinessWeight",
            "Effet de la crasse sur la crainte inspiree", 0.1, 0, 2),
    Reglage("HoleDiggingDirtiness",
            "Salissure en creusant une tombe", 0.45, 0, 2),
    Reglage("TransferedBloodToAttackerMax",
            "Sang recu en frappant (maximum)", 0.1, 0, 1),
    Reglage("TransferedBloodToVictimMax",
            "Sang recu en etant frappe (maximum)", 0.5, 0, 1),
]





MONTURE = [
    Reglage("HorseDashBufferLength",
            "Reserve de sprint du cheval", 21, 0, 1000),
    Reglage("HorseSlowdownTimeSprintIfDashed",
            "Temps de recuperation apres un sprint", 2, 0, 30),
    Reglage("HorseSlowdownTimeSlowSpeed",
            "Temps de ralentissement au pas", 0.5, 0, 30),
    Reglage("HorseSlowSpeedStaminaRegen",
            "Recuperation du cheval au pas", 1, 0, 20),
    Reglage("HorseJumpHeightModifier",
            "Hauteur des sauts", 0, 0, 5),
    Reglage("HorseMoraleToThrowOffRider",
            "Moral sous lequel le cheval vous desarconne", 0.01, 0, 1,
            "PLUS BAS = il desarconne moins ; 0 = jamais, 1 = tout le temps"),
    Reglage("HorseRidingToHorseCourage",
            "Courage gagne par l'equitation", 0.01, 0, 1),
    Reglage("HorseridingSkillXPForKillFromHorseback",
            "Equitation gagnee en tuant a cheval", 30, 0, 500),
]





DUELS = [
    Reglage("CombatDodgeProb1", "Frequence des esquives adverses", 0.3, 0, 1,
            "0 = les adversaires n'esquivent plus"),
    Reglage("CombatPerfectBlockPowTo",
            "Puissance rendue par une parade parfaite", 1.5, 0, 10),
    Reglage("CombatPerfectBlockZoneDistanceCoef",
            "Fenetre de la parade parfaite", 0.45, 0, 3,
            "monter donne plus de temps pour parer juste"),
    Reglage("CombatPerfectBlockNPCvsNPCCoef",
            "Parades parfaites entre PNJ", 1.5, 0, 10),
    Reglage("MinStaminaDmgR", "Plancher de degats d'endurance", -50, -500, 0),
    Reglage("StatXPAgilityPerDodge", "Agilite gagnee par esquive", 10, 0, 200),
    Reglage("StatXPVitalityPerDodge", "Vitalite gagnee par esquive", 3, 0, 200),
    Reglage("RespawnPeriod", "Delai de reapparition des PNJ (jours)", 7, 0, 60,
            "monter espace les patrouilles et les bandits sur les routes"),
    Reglage("CombatDangerCooldown", "Repit apres un combat", 0.5, 0, 30,
            "temps avant que le jeu vous considere de nouveau tranquille"),
]






NATURE = [
    Reglage("HerbGatherSkillToRadius", "Rayon de cueillette", 0.04, 0, 5,
            "monter permet de moissonner un carre d'herbes en passant"),
    Reglage("HerbGatherSkillToRadiusAdd", "Rayon de cueillette (ajout)",
            0.4, 0, 10),
    Reglage("HerbGatherSkillToCount", "Plantes ramassees d'un geste",
            0.25, 0, 10),
    Reglage("HuntingAlarmSoundMinimalMultiplier",
            "Seuil d'alarme du gibier (minimum)", 0.6, 0, 3,
            "abaisser rend les betes bien moins farouches"),
    Reglage("HuntingAlarmSoundMaximalMultiplier",
            "Seuil d'alarme du gibier (maximum)", 0.9, 0, 3),
    Reglage("HunterLootAmountAddCoef", "Butin de chasse supplementaire",
            0.1, 0, 5),
    Reglage("HunterXPLoot", "XP par depecage", 8, 0, 300),
    Reglage("DogDistractBarkTime", "Duree des aboiements de diversion",
            25, 0, 120),
    Reglage("DogDistractInitialWaitTime", "Attente avant que le chien aboie",
            3, 0, 60),
    Reglage("DogPOISearchRadiusMin", "Rayon de fouille du chien (minimum)",
            10, 0, 200),
    Reglage("DogPOISearchRadiusMax", "Rayon de fouille du chien (maximum)",
            35, 0, 300),
]





LARCIN = [
    Reglage("PickpocketingDistance", "Portee du vol a la tire", 2.4, 0.5, 15),
    Reglage("PickpocketingMisstargetingTolerance",
            "Tolerance de visee", 2250, 100, 20000,
            "monter pardonne une main qui derape"),
    Reglage("PickpocketingItemUncoverTimePerWeight",
            "Temps de degagement par kilo", 0.021, 0, 1,
            "abaisser accelere la sortie des objets lourds"),
    Reglage("StealthBackoffMinTime", "Repli furtif (minimum)", 0.1, 0, 10),
    Reglage("StealthBackoffMaxTime", "Repli furtif (maximum)", 1.5, 0, 20),
]





ARTISANAT = [
    Reglage("BlacksmithingRhythmicBonus", "Prime au rythme a la forge",
            8, 0, 100, "monter recompense un martelage regulier"),
    Reglage("BlacksmithingMinIntensity", "Intensite minimale du coup",
            0.5, 0, 3),
    Reglage("BlacksmithingAlmostCriticalQualityOffset",
            "Marge avant la faute critique", 0.1, 0, 2,
            "monter pardonne les coups presque rates"),
    Reglage("BlacksmithingIntensityToStamina",
            "Endurance depensee a la forge", 16, 0, 100),
    Reglage("SharpeningMaxDestructionAngle",
            "Angle avant d'abimer la lame a la meule", 0.99, 0, 5),
    Reglage("SharpeningFullPositiveHealthXP",
            "XP d'un affutage reussi", 125, 0, 1000),
    Reglage("SharpeningFullNegativeHealthXP",
            "XP d'un affutage rate", 15, 0, 1000),
    Reglage("AlchemyResultCoefToFirstQuality",
            "Chance d'atteindre la premiere qualite", 0.9, 0, 2),
    Reglage("AlchemyResultCoefToSecondQuality",
            "Chance d'atteindre la seconde qualite", 0.7, 0, 2),
    Reglage("AlchemyResourcesQualityWeight",
            "Poids de la qualite des ingredients", 0.2, 0, 3),
    Reglage("AlchemyPotionBaseQualityWeight",
            "Qualite de base d'une potion", 0, 0, 3),
]






CHUTES = [
    Reglage("HarmlessFallHeight", "Hauteur de chute sans dommage (m)",
            1.5, 0, 100, "monter a 50 supprime les morts absurdes en pente"),
    Reglage("InjuringFallHeight", "Hauteur de chute qui blesse (m)",
            2.2, 0, 100),
]





BOISSON = [
    Reglage("AlcoholDrunkThreshold", "Seuil d'ivresse", 0.32, 0, 5,
            "monter permet de boire davantage avant de tituber"),
    Reglage("AlcoholBlackoutThresholdBase", "Seuil du trou noir", 32, 0, 500),
    Reglage("AlcoholBlackoutThresholdSkillMultiplier",
            "Effet du talent sur le trou noir", 2, 0, 20),
    Reglage("AlcoholBaseHangoverDuration", "Duree de la gueule de bois",
            80000, 0, 500000, "abaisser raccourcit le lendemain difficile"),
    Reglage("AlcoholMaxDrinkingSkillHangoverDurationModifier",
            "Reduction de la gueule de bois par le talent", 0.05, 0, 2),
    Reglage("AlcoholismLevel1", "Premier palier d'accoutumance", 300, 0, 5000),
    Reglage("AlcoholismLevel2", "Second palier d'accoutumance", 450, 0, 5000),
    Reglage("AlcoholDrunkThresholdNPC", "Seuil d'ivresse des PNJ", 0.6, 0, 5),
]





DISCRETION = [
    Reglage("StealthSkillToFootstepSoundMult",
            "Bruit des pas selon le talent", 0.6, 0, 3,
            "abaisser rend la demarche sourde meme en armure"),
    Reglage("StealthSkillToRecogTime",
            "Temps avant d'etre reconnu", 0.6, 0, 5),
    Reglage("StealthSkillToViewRadiusDecr",
            "Reduction du rayon de vue adverse", 0.3, 0, 3),
    Reglage("CrimeDoorSoundMod", "Bruit d'une porte forcee", 0.5, 0, 3),
    Reglage("LockpickingFailSoundIntensity",
            "Bruit d'un crochetage rate", 1, 0, 5),
    Reglage("StealthToUnconsciousDepth",
            "Profondeur d'un assommage furtif", 600, 0, 5000),
    Reglage("StealthKnockOutUnconsciousDepthBase",
            "Base d'assommage", 400, 0, 5000),
]

GROUPES: dict[str, list[Reglage]] = {
    "Progression et experience": PROGRESSION,
    "Survie et metabolisme": SURVIE,
    "Endurance": ENDURANCE,
    "Combat et letalite": COMBAT,
    "Encombrement": ENCOMBREMENT,
    "Fabrication et reparation": FABRICATION,
    "Economie": ECONOMIE,
    "Cheval": CHEVAL,
    "Perception de l'IA": PERCEPTION_REGLES,
    "Reputation": REPUTATION_REGLES,
    "Usure de l'equipement": USURE,
    "Mini-jeux": MINIJEUX,
    "Proprete": PROPRETE,
    "Monture": MONTURE,
    "Duels": DUELS,
    "Cueillette et chasse": NATURE,
    "Vol a la tire": LARCIN,
    "Artisanat": ARTISANAT,
    "Chutes": CHUTES,
    "Boisson": BOISSON,
    "Empreinte sonore": DISCRETION,
}

TOUS: dict[str, Reglage] = {r.cle: r for g in GROUPES.values() for r in g}


























HORS_TABLE: dict[str, Reglage] = {
    r.cle: r for r in [
        Reglage("HorseMountMaxRelativeEncumberance",
                "Monter en selle malgre la charge", 1.0, 1.0, 1000.0,
                "Part de ta capacite au-dela de laquelle le jeu refuse la "
                "selle. 1 = pas un gramme de trop. Mesure en partie : 1."),
        Reglage("MaxBaseInventoryCapacity",
                "Plafond de la capacite de base", 600.0, 600.0, 100000.0,
                "Rabote BaseInventoryCapacity avant usage. Mesure en "
                "partie : 600 -- c'est lui qui annulait le sac sans fond."),
    ]
}



ECRIVABLES: dict[str, Reglage] = {**TOUS, **HORS_TABLE}








PERCEPTION = [
    Variable("wh_ai_perception_enabled", "Perception des PNJ active", "1",
             "0 rend les gardes aveugles"),
    Variable("wh_ai_hearing_enabled", "Ouie des PNJ active", "1"),
    Variable("wh_ai_hearing_distance_attenuation_power",
             "Attenuation du son avec la distance", "2.1",
             "plus haut = les PNJ entendent moins loin"),
    Variable("wh_ai_perception_recognizing_threshold",
             "Seuil de reconnaissance", "0.05",
             "plus haut = ils mettent plus longtemps a vous identifier"),
    Variable("wh_ai_perception_ignore_fov_radius",
             "Rayon ou le champ de vision est ignore", "1.5"),





    Variable("wh_sh_HearingWeightShouts", "Poids sonore des cris", "0.5"),
    Variable("wh_sh_HearingWeightScreams", "Poids sonore des hurlements", "0.7"),
    Variable("wh_sh_HearingWeightMaxHit", "Poids sonore d'un coup fort", "1"),
    Variable("wh_cs_StealthActionDistance", "Portee des attaques furtives", "2"),
    Variable("wh_cs_StealthActionAngle", "Angle des attaques furtives", "135"),
    Variable("wh_cs_EnableStealthActions", "Attaques furtives autorisees", "1"),
    Variable("wh_pl_FOWVisibilityRadius", "Rayon de decouverte de la carte", "100"),
]

SESSION = [
    Variable("wh_sys_NoSavePotion", "Sauvegarde libre sans schnaps", "0",
             "1 supprime l'obligation de boire pour sauvegarder"),
    Variable("wh_sys_AutoLoadLastSave", "Recharger la derniere sauvegarde", "0"),
    Variable("wh_pl_SkipTimeStep", "Pas de temps lors d'une attente", "1"),




    Variable("wh_actor_MovementSpeedMultEnabled",
             "Multiplicateur de vitesse actif", "1"),
    Variable("wh_actor_MovementSpeedMultDefault", "Multiplicateur de vitesse",
             "0.9", "le jeu demarre a 0.9 : monter accelere Henry"),
]








INTERFACE = [
    Variable("wh_ui_ShowHud", "Afficher l'interface", "1",
             "0 = plus aucun element a l'ecran, pour la capture d'images"),
    Variable("wh_ui_EnableAdaptiveHud", "Interface qui s'efface d'elle-meme", "1",
             "elle reapparait au combat ou quand la sante baisse"),
    Variable("wh_ui_AdaptiveHudFadeOutDelay",
             "Delai avant que l'interface s'efface (s)", "3"),
    Variable("wh_ui_AdaptiveHudHealthThreshold",
             "Seuil de sante qui rappelle l'interface", "0.5"),
    Variable("wh_ui_AdaptiveHudStaminaThreshold",
             "Seuil d'endurance qui rappelle l'interface", "0.5"),
    Variable("wh_ui_CompassNearThreshold", "Portee proche de la boussole", "20"),
    Variable("wh_ui_CompassFarThreshold", "Portee lointaine de la boussole", "200"),
    Variable("wh_ui_TutorialsEnabled", "Fenetres de didacticiel", "1",
             "0 = plus d'encart explicatif en cours de partie"),
    Variable("wh_ui_TutorialOverlayEnabled", "Incrustations de didacticiel", "1"),
    Variable("wh_ui_SubtitlesEnabled", "Sous-titres", "1"),
    Variable("wh_ui_SubtitleSize", "Taille des sous-titres", "1"),
    Variable("wh_ui_EnableSubtitleSpeakerName",
             "Nom du personnage dans les sous-titres", "1"),
    Variable("wh_ui_HDRHealthEffect", "Effet d'ecran quand la sante baisse", "1",
             "0 = plus de rougeoiement au bord de l'ecran"),
    Variable("wh_ui_HDRStaminaEffect", "Effet d'ecran a bout de souffle", "1"),
    Variable("wh_ui_PauseGameOnFocusLoss",
             "Mettre en pause si la fenetre perd le focus", "1"),
]









DEMARRAGE = [
    Variable("wh_sys_HideIntroVideo", "Masquer la video d'introduction", "0"),
    Variable("wh_sys_SkipStartupVideoWhenPossible",
             "Passer les logos au demarrage", "0"),












    Variable("sys_MaxFPS", "Limite d'images par seconde", "120",
             "0 = aucune limite"),
    Variable("sys_MaxFPSThrotteled",
             "Limite quand la fenetre n'est pas devant", "60",
             "0 = pleine vitesse meme sur le deuxieme ecran"),
    Variable("r_VSync", "Synchronisation verticale", "1"),
    Variable("r_Gamma", "Gamma de l'image", "1",
             "monter eclaircit les nuits sans toucher au jeu"),
    Variable("r_Brightness", "Luminosite de l'image", "1"),
]

GROUPES_VARIABLES: dict[str, list[Variable]] = {
    "Perception de l'IA": PERCEPTION,
    "Session et deplacement": SESSION,
    "Interface": INTERFACE,
    "Demarrage et affichage": DEMARRAGE,
}

TOUTES_VARIABLES: dict[str, Variable] = {
    v.nom: v for g in GROUPES_VARIABLES.values() for v in g
}






def _formater(valeur: float) -> str:
    if isinstance(valeur, float) and valeur.is_integer():
        return str(int(valeur))
    return f"{valeur:g}"


def construire_ptf_rpg_param(valeurs: dict[str, float]) -> tuple[str, int]:
    ""
    lignes = []
    for cle, valeur in sorted(valeurs.items()):
        reglage = ECRIVABLES.get(cle)
        if reglage is None or float(valeur) == float(reglage.defaut):
            continue
        lignes.append(
            f'\t\t<rpg_param rpg_param_key={quoteattr(cle)} '
            f'rpg_param_value={quoteattr(_formater(valeur))} />'
        )
    xml = (
        f'{ENTETE_RPG}\t<rpg_params version="1">\n' + "\n".join(lignes) +
        "\n\t</rpg_params>\n</database>\n"
    )
    return xml, len(lignes)


def construire_cfg(variables: dict[str, str]) -> tuple[str, int]:
    ""
    lignes = ["-- genere par Scriptorium"]
    nombre = 0
    for nom, valeur in sorted(variables.items()):
        connue = TOUTES_VARIABLES.get(nom)
        if connue is None or str(valeur) == str(connue.defaut):
            continue
        lignes.append(f"{nom} = {valeur}")
        nombre += 1
    return "\n".join(lignes) + "\n", nombre




FAMILLES_CIBLABLES = {
    "Ammo": "Munitions (fleches, carreaux)",
    "MeleeWeapon": "Armes de melee",
    "MissileWeapon": "Arcs et arbaletes",
    "Armor": "Armures",
    "Helmet": "Casques",
    "Hood": "Capuches et chaperons",
    "Food": "Vivres",
    "Ointment": "Onguents et potions",
    "CraftingMaterial": "Materiaux",
    "MiscItem": "Objets divers",
    "Document": "Livres et documents",
    "Herb": "Herbes",
}


def construire_ptf_objets(
    pak_tables: Path,
    facteur_poids: float = 1.0,
    facteur_prix: float = 1.0,
    facteur_durabilite: float = 1.0,
    vivres_imperissables: bool = False,
    vivres_sans_poids: bool = False,
    poids_par_famille: dict[str, float] | None = None,
) -> tuple[str, int]:
    ""













    poids_par_famille = {f: v for f, v in (poids_par_famille or {}).items()
                         if v != 1.0}
    if (facteur_poids == 1.0 and facteur_prix == 1.0
            and facteur_durabilite == 1.0 and not poids_par_famille
            and not vivres_imperissables and not vivres_sans_poids):
        return "", 0




    from . import archives as _a
    with zipfile.ZipFile(pak_tables) as z:
        racines = [ET.fromstring(z.read(s)) for s in _a.sources_objets(pak_tables)]

    lignes: list[str] = []
    for groupe in (g for r in racines for g in r):
        for objet in groupe:
            remplace: dict[str, str] = {}

            poids_ici = poids_par_famille.get(objet.tag, facteur_poids)
            for attribut, facteur, plancher in (
                ("Weight", poids_ici, 0.0),
                ("Price", facteur_prix, 0.0),
                ("MaxStatus", facteur_durabilite, 0.0),
            ):
                if facteur == 1.0:
                    continue
                brut = objet.get(attribut)
                if brut is None:
                    continue
                try:
                    valeur = float(brut)
                except ValueError:
                    continue
                if valeur <= 0:
                    continue
                remplace[attribut] = f"{max(plancher, round(valeur * facteur, 4)):g}"



            if objet.tag == "Food":
                if vivres_imperissables and objet.get("DecayTime") not in (None, "0"):
                    remplace["DecayTime"] = "99999"
                if vivres_sans_poids:
                    remplace["Weight"] = "0"

            if not remplace:
                continue
            attributs = dict(objet.attrib)
            attributs.update(remplace)
            corps = " ".join(
                f"{nom}={quoteattr(val)}" for nom, val in attributs.items()
            )
            lignes.append(f"\t\t<{objet.tag} {corps} />")

    xml = (
        f'{ENTETE_ITEM}\t<ItemClasses version="8">\n' + "\n".join(lignes) +
        "\n\t</ItemClasses>\n</database>\n"
    )
    return xml, len(lignes)











def _patcher_table(
    pak_tables: Path,
    chemin: str,
    groupe: str,
    version: str,
    schema: str,
    cible: str,
    modifications: dict[str, dict[str, str]],
    ajouts: list[dict[str, str]] | None = None,
) -> tuple[str, int]:
    ""










    if not modifications and not ajouts:
        return "", 0

    with zipfile.ZipFile(pak_tables) as z:
        racine = ET.fromstring(z.read(chemin))

    lignes: list[str] = []
    for bloc in racine:
        for ligne in bloc:
            identifiant = ligne.get(cible)
            if identifiant not in modifications:
                continue
            attributs = dict(ligne.attrib)
            change = False
            for nom, valeur in modifications[identifiant].items():
                if attributs.get(nom) != valeur:
                    attributs[nom] = valeur
                    change = True
            if not change:
                continue
            corps = " ".join(
                f"{nom}={quoteattr(val)}" for nom, val in attributs.items()
            )
            lignes.append(f"		<{ligne.tag} {corps} />")

    for ajout in ajouts or []:
        balise = ajout.get("_balise") or groupe.rstrip("s")
        corps = " ".join(f"{nom}={quoteattr(val)}"
                         for nom, val in ajout.items() if nom != "_balise")
        lignes.append(f"		<{balise} {corps} />")

    if not lignes:
        return "", 0
    xml = (
        '<?xml version="1.0" encoding="us-ascii"?>\n'
        '<database xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        f'name="barbora" xsi:noNamespaceSchemaLocation="{schema}">\n'
        f'\t<{groupe} version="{version}">\n' + "\n".join(lignes) +
        f"\n\t</{groupe}>\n</database>\n"
    )
    return xml, len(lignes)


def construire_ptf_mouvement(
    pak_tables: Path,
    sprint_sans_fin: bool = False,
    armure_sans_frein: bool = False,
) -> tuple[str, int]:
    ""























    changements: dict[str, dict[str, str]] = {}

    def poser(ident: str, attribut: str, valeur: str) -> None:
        changements.setdefault(ident, {})[attribut] = valeur

    if sprint_sans_fin:
        poser("3", "stamina_regen", "0")
        poser("5", "stamina_regen", "0")
    if armure_sans_frein:
        poser("2", "armor_load_to_speed", "0")
        poser("3", "armor_load_to_speed", "0")

    if not changements:
        return "", 0
    return _patcher_table(
        pak_tables, "Libs/Tables/rpg/rpg_movement_type.xml",
        "rpg_movement_types", "1", "../database.xsd",
        "rpg_movement_type_id",
        changements,
    )





















CVARS_VERROUILLEES: dict[str, str] = {
    "wh_actor_MovementSpeedMultDefault":
        "en lecture seule (le jeu la garde a 0.9) -- remplacee par l'effet "
        "« scriptorium_marche_rapide », qui, lui, fonctionne",
    "wh_pl_FOWVisibilityRadius":
        "en lecture seule (le jeu la garde a 100)",
    "wh_sys_NoSavePotion":
        "en lecture seule (le jeu la garde a 0) -- mais Scriptorium sait "
        "sauvegarder sans schnaps a la demande, depuis la page d'accueil",
    "wh_ui_AdaptiveHudFadeOutDelay":
        "en lecture seule (le jeu la garde a 3 secondes)",
}





GUID_MARCHE_RAPIDE = "5c7148ea-9b3f-4d21-8e6a-0f2a17b4c930"


def construire_ptf_surcharge(
    pak_tables: Path, surcharge_sans_malus: bool = False,
    marche_rapide: float = 1.0,
) -> tuple[str, int]:
    ""































    if not surcharge_sans_malus and not marche_rapide:
        return "", 0

    modifications = {}
    if surcharge_sans_malus:
        modifications["encumbered"] = {"buff_params": "rms*1;rms*1"}

    ajouts = []
    if marche_rapide and float(marche_rapide) != 1.0:
















        ajouts.append({
            "_balise": "buff",
            "buff_class_id": "0",
            "buff_exclusivity_id": "1",
            "buff_id": GUID_MARCHE_RAPIDE,
            "buff_lifetime_id": "0",
            "buff_name": "scriptorium_marche_rapide",
            "buff_params": f"rms*{_formater(marche_rapide)}",
            "duration": "-1",
            "icon_id": "0",
            "implementation": "Cpp:Constant",
            "is_persistent": "true",
        })

    return _patcher_table(
        pak_tables, "Libs/Tables/rpg/buff.xml",
        "buffs", "1", "../database.xsd", "buff_name",
        modifications, ajouts,
    )


def construire_ptf_monture(
    pak_tables: Path, cheval_sans_limite: bool = False
) -> tuple[str, int]:
    ""

























    if not cheval_sans_limite:
        return "", 0
    return _patcher_table(
        pak_tables, "Libs/Tables/rpg/soul_archetype.xml",
        "soul_archetypes", "1", "../database.xsd", "soul_archetype_name",
        {"Horse": {"inventory_capacity_multiplier": "40"}},
    )


def construire_ptf_talismans(
    pak_tables: Path, puissance: str = ""
) -> tuple[str, int]:
    ""




    if not puissance:
        return "", 0
    return _patcher_table(
        pak_tables, "Libs/Tables/rpg/buff__perk.xml",
        "buffs", "1", "../database.xsd", "buff_name",
        {
            "perk_good_old_pebbles": {"buff_params": puissance},
            "perk_red_herring": {"buff_params": puissance},
        },
    )



def construire_ptf_reputation(
    pak_tables: Path,
    annuler_malus: bool = False,
    facteur_gains: float = 1.0,
) -> tuple[str, int]:
    ""





    if not annuler_malus and facteur_gains == 1.0:
        return "", 0

    with zipfile.ZipFile(pak_tables) as z:
        brut = z.read("Libs/Tables/rpg/reputation_change.xml")
    import re as _re
    racine = ET.fromstring(
        _re.sub(r"<\?xml[^>]*\?>", "", brut.decode("utf-8", "replace"), count=1).lstrip()
    )

    lignes: list[str] = []
    for bloc in racine:
        for entree in bloc:
            brut_valeur = entree.get("change")
            if brut_valeur is None:
                continue
            try:
                valeur = float(brut_valeur)
            except ValueError:
                continue

            nouvelle = valeur
            if valeur < 0 and annuler_malus:
                nouvelle = 0.0
            elif valeur > 0 and facteur_gains != 1.0:
                nouvelle = round(valeur * facteur_gains, 4)
            if abs(nouvelle - valeur) < 1e-9:
                continue

            attributs = dict(entree.attrib)
            attributs["change"] = f"{nouvelle:g}"
            corps = " ".join(f"{n}={quoteattr(v)}" for n, v in attributs.items())
            lignes.append(f"		<{entree.tag} {corps} />")

    if not lignes:
        return "", 0
    xml = (
        f'{ENTETE_RPG}\t<reputation_changes version="1">\n'
        + "\n".join(lignes)
        + "\n\t</reputation_changes>\n</database>\n"
    )
    return xml, len(lignes)


def modid(nom: str) -> str:
    ""







    return re.sub(r"[^a-z_]", "", nom.lower()) or "scriptorium"


def construire_ptf_bourses(pak_tables: Path, facteur: float = 1.0
                           ) -> tuple[str, int]:
    ""







    if facteur == 1.0:
        return "", 0
    chemin = "Libs/Tables/item/InventoryPreset__shops.xml"
    with zipfile.ZipFile(pak_tables) as z:
        if chemin not in z.namelist():
            return "", 0
        brut = z.read(chemin).decode("utf-8", errors="replace")
    racine = ET.fromstring(re.sub(r"<\?xml[^>]*\?>", "", brut, count=1).lstrip())



    blocs: list[str] = []
    touches = 0
    for preset in racine.iter("InventoryPreset"):
        lignes_preset = []
        change = False
        for item in preset:
            attributs = dict(item.attrib)
            if attributs.get("Name") == "money" and attributs.get("Amount"):
                try:
                    attributs["Amount"] = str(int(float(attributs["Amount"]) * facteur))
                    change = True
                    touches += 1
                except ValueError:
                    pass
            lignes_preset.append(
                "        <{} {} />".format(
                    item.tag,
                    " ".join(f"{n}={quoteattr(v)}" for n, v in attributs.items()),
                )
            )
        if change:
            entete = " ".join(f"{n}={quoteattr(v)}" for n, v in preset.attrib.items())
            blocs.append(f"    <InventoryPreset {entete}>\n"
                         + "\n".join(lignes_preset)
                         + "\n    </InventoryPreset>")
    if not blocs:
        return "", 0
    return (
        '<?xml version="1.0" encoding="us-ascii"?>\n'
        '<database xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'name="barbora" xsi:noNamespaceSchemaLocation="InventoryPreset.xsd">\n'
        '  <InventoryPresets version="2">\n'
        + "\n".join(blocs)
        + "\n  </InventoryPresets>\n</database>\n"
    ), touches


def construire_ptf_capuches(pak_tables: Path, toujours: bool = False
                            ) -> tuple[str, int]:
    ""




    if not toujours:
        return "", 0
    chemin = "Libs/Tables/item/clothing_preset.xml"
    with zipfile.ZipFile(pak_tables) as z:
        brut = z.read(chemin).decode("utf-8", errors="replace")
    racine = ET.fromstring(re.sub(r"<\?xml[^>]*\?>", "", brut, count=1).lstrip())

    blocs: list[str] = []
    for preset in racine.iter("clothing_preset"):
        if preset.get("prefers_hood_on") == "true":
            continue
        attributs = dict(preset.attrib)
        attributs["prefers_hood_on"] = "true"


        enfants = []
        for groupe in preset:
            interieur = "".join(
                f"<{e.tag}>{e.text or ''}</{e.tag}>" for e in groupe
            )
            enfants.append(f"<{groupe.tag}>{interieur}</{groupe.tag}>")
        entete = " ".join(f"{n}={quoteattr(v)}" for n, v in attributs.items())
        blocs.append(f"    <clothing_preset {entete}>"
                     + "".join(enfants) + "</clothing_preset>")
    if not blocs:
        return "", 0
    return (
        '<?xml version="1.0" encoding="us-ascii"?>\n'
        '<database xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'name="barbora" xsi:noNamespaceSchemaLocation="../database.xsd">\n'
        '  <clothing_presets version="1">\n'
        + "\n".join(blocs)
        + "\n  </clothing_presets>\n</database>\n"
    ), len(blocs)


def manifeste(nom: str, version: str, description: str) -> str:
    ""









    identifiant = modid(nom)
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<kcd_mod>\n"
        "  <info>\n"
        f"    <name>{nom}</name>\n"
        f"    <modid>{identifiant}</modid>\n"
        f"    <description>{description}</description>\n"
        "    <author>Scriptorium</author>\n"
        f"    <version>{version}</version>\n"
        "    <created_on></created_on>\n"
        "    <dependencies></dependencies>\n"
        "  </info>\n"
        "</kcd_mod>\n"
    )


@dataclass
class ResultatReglages:
    dossier: Path
    pak: Path
    contenus: dict[str, int]
    verifie: bool = False
    detail: str = ""

    @property
    def total(self) -> int:
        return sum(self.contenus.values())


def ecrire_mod(
    inst,
    valeurs: dict[str, float],
    variables: dict[str, str] | None = None,
    facteur_poids: float = 1.0,
    facteur_prix: float = 1.0,
    facteur_durabilite: float = 1.0,
    vivres_imperissables: bool = False,
    vivres_sans_poids: bool = False,
    poids_par_famille: dict[str, float] | None = None,
    bourses_marchands: float = 1.0,
    capuche_relevee: bool = False,
    sprint_sans_fin: bool = False,
    armure_sans_frein: bool = False,
    surcharge_sans_malus: bool = False,
    cheval_sans_limite: bool = False,
    marche_rapide: float = 1.0,
    talismans: str = "",
    marchands_achat: float = 1.0,
    marchands_vente: float = 1.0,
    marchands_reassort: int | None = None,
    reputation_sans_malus: bool = False,
    reputation_gains: float = 1.0,
    reforge: int = 0,
    nom_mod: str = "scriptorium",
) -> ResultatReglages:
    ""








    from . import jeu

    contenu: dict[str, str] = {}
    compte: dict[str, int] = {}
    suffixe = modid(nom_mod)

    xml, nombre = construire_ptf_rpg_param(valeurs)
    if nombre:
        contenu[f"Libs/Tables/rpg/rpg_param__{suffixe}.xml"] = xml
        compte["regles"] = nombre

    xml, nombre = construire_ptf_objets(
        inst.pak("Tables.pak"), facteur_poids, facteur_prix, facteur_durabilite,
        vivres_imperissables, vivres_sans_poids, poids_par_famille,
    )
    if nombre:
        contenu[f"Libs/Tables/item/item__{suffixe}.xml"] = xml
        compte["objets"] = nombre

    xml, nombre = construire_ptf_bourses(inst.pak("Tables.pak"), bourses_marchands)
    if nombre:
        contenu[f"Libs/Tables/item/InventoryPreset__shops__{suffixe}.xml"] = xml
        compte["bourses"] = nombre

    xml, nombre = construire_ptf_capuches(inst.pak("Tables.pak"), capuche_relevee)
    if nombre:
        contenu[f"Libs/Tables/item/clothing_preset__{suffixe}.xml"] = xml
        compte["capuches"] = nombre

    xml, nombre = construire_ptf_mouvement(
        inst.pak("Tables.pak"), sprint_sans_fin, armure_sans_frein
    )
    if nombre:
        contenu[f"Libs/Tables/rpg/rpg_movement_type__{suffixe}.xml"] = xml
        compte["deplacement"] = nombre















    lignes_buff: list[str] = []
    compte_buff = 0
    for construire, argument in (
            (lambda: construire_ptf_surcharge(
                inst.pak("Tables.pak"), surcharge_sans_malus, marche_rapide),
             "surcharge"),
            (lambda: construire_ptf_talismans(
                inst.pak("Tables.pak"), talismans), "talismans")):
        xml, nombre = construire()
        if not nombre:
            continue
        lignes_buff += [ligne for ligne in xml.split("\n")
                        if ligne.strip().startswith("<buff ")]
        compte[argument] = nombre
        compte_buff += nombre
    if lignes_buff:
        contenu[f"Libs/Tables/rpg/buff__{suffixe}.xml"] = (
            '<?xml version="1.0" encoding="us-ascii"?>\n'
            '<database xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'name="barbora" xsi:noNamespaceSchemaLocation="../database.xsd">\n'
            '\t<buffs version="1">\n' + "\n".join(lignes_buff) +
            "\n\t</buffs>\n</database>\n"
        )

    xml, nombre = construire_ptf_monture(
        inst.pak("Tables.pak"), cheval_sans_limite
    )
    if nombre:
        contenu[f"Libs/Tables/rpg/soul_archetype__{suffixe}.xml"] = xml
        compte["monture"] = nombre



























    consignes = []
    if cheval_sans_limite:
        consignes.append("SCRIPTORIUM_CHEVAL_LIBRE = true")
    if marche_rapide and float(marche_rapide) != 1.0:



        consignes.append(
            'SCRIPTORIUM_EFFETS = { "' + GUID_MARCHE_RAPIDE + '" }')
    if consignes:
        entete = "-- Ecrit par Scriptorium. Lu par l'agent au demarrage.\n"
        drapeau = entete + "\n".join(consignes) + "\n"


        contenu[CONSIGNES] = drapeau
        contenu[CONSIGNES.lower()] = drapeau
        compte["consignes"] = len(consignes)



    xml, nombre = construire_ptf_reputation(
        inst.pak("Tables.pak"), reputation_sans_malus, reputation_gains
    )
    if nombre:
        contenu[f"Libs/Tables/rpg/reputation_change__{suffixe}.xml"] = xml
        compte["reputation"] = nombre

    if reforge:
        from . import recettes

        candidates = recettes.armes_candidates(
            inst.pak("Tables.pak"),
            Path(__file__).resolve().parent.parent / "local" / "catalogue.sqlite",
        )
        libres = [a for a in candidates if not a.deja_forgeable][:reforge]
        xml, nombre = recettes.construire_ptf(libres)
        if nombre:
            contenu[f"Libs/Tables/minigame/BlacksmithRecipes__{suffixe}.xml"] = xml
            compte["recettes"] = nombre

    from . import economie

    xml, nombre = economie.construire_ptf(
        inst.pak("Tables.pak"), marchands_achat, marchands_vente, marchands_reassort
    )
    if nombre:
        contenu[f"Libs/Tables/shop/shop__{suffixe}.xml"] = xml
        compte["marchands"] = nombre

    dossier = jeu.cible_reelle(inst.mods / nom_mod)
    (dossier / "Data").mkdir(parents=True, exist_ok=True)
    pak = jeu.cible_reelle(dossier / PAK_DES_REGLES)
    resultat = ResultatReglages(dossier=dossier, pak=pak, contenus=compte)


    partagees = fusionner_avec_le_pak_principal(contenu, dossier)
    if partagees:
        compte["tables_partagees"] = partagees

    cfg, nombre_cfg = construire_cfg(variables or {})
    ecrire_le_bloc_cfg(dossier, cfg if nombre_cfg else "")
    if nombre_cfg:
        compte["variables"] = nombre_cfg







    if archives.deja_identique(pak, contenu):
        resultat.detail = (
            "deja en place, rien a reecrire" if contenu
            else ("aucune regle modifiee" if not nombre_cfg
                  else f"{nombre_cfg} variable(s) moteur seulement")
        )
        resultat.verifie = bool(contenu or nombre_cfg)
    elif not contenu:


        pak.unlink()
        resultat.detail = (
            "regles retirees" if not nombre_cfg
            else f"regles retirees, {nombre_cfg} variable(s) moteur"
        )
        resultat.verifie = True
    else:
        archives.ecrire_pak(pak, contenu)
        resultat.verifie, resultat.detail = archives.verifier_pak(pak)


    from . import constructeur
    if nom_mod == constructeur.NOM_MOD:
        if retirer_l_ancien_mod(inst):
            resultat.detail += " ; reglages a part (scriptorium_regles) retires"
    return resultat






ANCIEN_MOD = "scriptorium_regles"
PAK_DES_REGLES = Path("Data") / "30_regles.pak"

PAKS_PRINCIPAUX = (Path("Data") / "20_scriptorium.pak", Path("Data") / "scriptorium.pak")
CONSIGNES = "Scripts/scriptorium/regles.lua"


SOURCES = "Regles/sources/"
DEBUT_DU_BLOC = "-- [regles du jeu, ecrites par Scriptorium] debut"
FIN_DU_BLOC = "-- [regles du jeu, ecrites par Scriptorium] fin"


def _table_de(chemin: str):
    ""

    import re
    m = re.match(r"(?i)libs/tables/(.+)/([^/]+)[.]xml$", chemin)
    if not m or "__" not in m.group(2):
        return None
    return m.group(1).lower(), m.group(2).split("__", 1)[0].lower()


def fusionner_avec_le_pak_principal(contenu, dossier: Path) -> int:
    ""


    import zipfile
    from . import choses
    principal = next((dossier / p for p in PAKS_PRINCIPAUX if (dossier / p).exists()), None)
    if principal is None:
        return 0
    siennes = {}
    with zipfile.ZipFile(principal) as z:
        for nom in z.namelist():
            cle = _table_de(nom)
            if cle is not None:
                siennes[cle] = (nom, z.read(nom).decode("utf-8", "replace"))
    n = 0
    for chemin in [c for c in contenu if _table_de(c) is not None]:
        cle = _table_de(chemin)
        if cle not in siennes:
            continue
        nom, texte = siennes[cle]
        brut = contenu.pop(chemin)
        contenu[SOURCES + chemin] = brut
        contenu[nom] = choses.fusionner(texte, brut)
        n += 1
    return n


def _lire_le_pak(pak: Path) -> dict:
    import zipfile
    with zipfile.ZipFile(pak) as z:
        return {n: z.read(n).decode("utf-8", "replace") for n in z.namelist()}


def rafraichir(inst, nom_mod: str = "scriptorium") -> str:
    ""



    from . import jeu
    dossier = jeu.cible_reelle(inst.mods / nom_mod)
    pak = jeu.cible_reelle(dossier / PAK_DES_REGLES)
    if not pak.exists():
        return "pas de regles"
    avant = _lire_le_pak(pak)
    sources = {k[len(SOURCES):]: v for k, v in avant.items() if k.startswith(SOURCES)}
    cles = {_table_de(k) for k in sources}
    contenu = {k: v for k, v in avant.items()
               if not k.startswith(SOURCES) and (_table_de(k) is None or _table_de(k) not in cles)}
    contenu.update(sources)
    n = fusionner_avec_le_pak_principal(contenu, dossier)
    if archives.deja_identique(pak, contenu):
        return f"regles deja a jour ({n} table(s) fusionnee(s))"
    archives.ecrire_pak(pak, contenu)
    return f"regles refaites sur le pak neuf ({n} table(s) fusionnee(s))"


def migrer(inst, nom_mod: str = "scriptorium") -> str | None:
    ""


    import re
    from . import jeu
    vieux = inst.mods / ANCIEN_MOD
    if not vieux.exists():
        return None
    dossier = jeu.cible_reelle(inst.mods / nom_mod)
    (dossier / "Data").mkdir(parents=True, exist_ok=True)
    suffixe = modid(nom_mod)
    contenu = {}
    ancien_pak = vieux / "Data" / f"{ANCIEN_MOD}.pak"
    if ancien_pak.exists():
        for nom, texte in _lire_le_pak(ancien_pak).items():
            if nom.lower() == f"scripts/mods/{ANCIEN_MOD}.lua":
                contenu[CONSIGNES] = texte
                contenu[CONSIGNES.lower()] = texte
            else:
                contenu[re.sub(r"__" + ANCIEN_MOD + r"[.]xml$", "__" + suffixe + ".xml", nom)] = texte
    n = fusionner_avec_le_pak_principal(contenu, dossier)
    pak = jeu.cible_reelle(dossier / PAK_DES_REGLES)
    if contenu:
        archives.ecrire_pak(pak, contenu)
    cfg = (vieux / "mod.cfg").read_text(encoding="utf-8") if (vieux / "mod.cfg").exists() else ""
    ecrire_le_bloc_cfg(dossier, cfg)
    retirer_l_ancien_mod(inst)
    tables = len([k for k in contenu if _table_de(k) is not None])
    return (f"regles migrees dans le dossier unique : {tables} table(s), dont {n} fusionnee(s) avec Scriptorium, "
            f"{'des variables moteur' if cfg.strip() else 'aucune variable'} ; ancien dossier retire")


def ecrire_le_bloc_cfg(dossier: Path, cfg: str) -> None:
    ""

    nl = chr(10)
    f = dossier / "mod.cfg"
    avant = f.read_text(encoding="utf-8") if f.exists() else ""
    if DEBUT_DU_BLOC in avant and FIN_DU_BLOC in avant:
        i = avant.index(DEBUT_DU_BLOC)
        j = avant.index(FIN_DU_BLOC) + len(FIN_DU_BLOC)
        reste = (avant[:i].rstrip(nl) + nl + avant[j:].lstrip(nl)).strip(nl)
    else:
        reste = avant.strip(nl)
    bloc = (DEBUT_DU_BLOC + nl + cfg.strip(nl) + nl + FIN_DU_BLOC) if cfg.strip() else ""
    neuf = (nl + nl).join(x for x in (reste, bloc) if x)
    neuf = (neuf + nl) if neuf else ""
    if neuf == avant:
        return
    if neuf:
        f.write_text(neuf, encoding="utf-8")
    elif f.exists():
        f.unlink()


def bloc_cfg(dossier: Path) -> str:
    ""
    f = dossier / "mod.cfg"
    texte = f.read_text(encoding="utf-8") if f.exists() else ""
    if DEBUT_DU_BLOC not in texte or FIN_DU_BLOC not in texte:
        return ""
    return texte[texte.index(DEBUT_DU_BLOC):texte.index(FIN_DU_BLOC) + len(FIN_DU_BLOC)]


def retirer_l_ancien_mod(inst) -> bool:
    ""

    import shutil
    from . import jeu
    nl = chr(10)
    d = inst.mods / ANCIEN_MOD
    avait = d.exists()
    if avait:
        shutil.rmtree(jeu.cible_reelle(d), ignore_errors=True)
    f = jeu.cible_reelle(inst.mods / "mod_order.txt")
    if f.exists():
        lignes = [l for l in f.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
        gardees = [l for l in lignes if l.strip() != ANCIEN_MOD]
        if len(gardees) != len(lignes):
            f.write_text(nl.join(gardees) + nl, encoding="utf-8")
            avait = True
    return avait
