






















scriptorium = scriptorium or {}
scriptorium.prix_du_camp = scriptorium.prix_du_camp or {}
do
	local pr = scriptorium.prix_du_camp
	if pr.ACTIF == nil then pr.ACTIF = true end
	pr.DECOR = 25

	pr.PRIX = {

		tente_henry = 0, tente_henry_vide = 0, intendant = 0, tente_intendant = 0, lit = 0, coffret_banque = 0,
		mini_tente = 0,

		lit_banc = 20, lit_haut = 60, lit_double = 120, tente_hommes = 300, cabane_henry = 1500, cabane_henry_vide = 1500,

		feu_camp = 20, mannequin_paille = 40, ratelier_camp = 60, bureau_directeur = 400, tour_de_guet = 800,

		rond_client = 50, abreuvoir = 60, poste_de_chasse = 80, etal_cueillette = 80, etal_jardiniers = 100,
		etal_bucheron = 100, etal_chasseurs = 100, pupitre_coursier = 120, rond_marchand = 150, etal_taverne = 250,
		comptoir_bains = 300, potager_petit = 80, potager_moyen = 160, potager_grand = 300,

		baquet = 30, point_d_eau = 40, prie_dieu = 60, sechoir = 100, meule = 120, fumoir = 150,

		tabouret = 5, chaise = 12, banc = 15, chaise_haute = 18, table_une_place = 20, petite_table = 25, banc_trois = 25,
		banc_haut = 25, table_un_banc = 45, table_bancs = 60,

		torche = 8, lampe_table = 12, lanterne = 15, foyer = 40, table_boisson = 60, table_vaisselle = 80,
		tonneau_biere = 100, tonneau_vin = 150, cuisine = 200, cuisine_etageres = 250,


		coffre = 50, caisse_atelier = 0, cible = 40, cible_pres = 40, cible_moyen = 40, cible_loin = 40,
		cible_tres_loin = 40, ratelier = 60, ratelier_garde = 120, haches = 120, hallebardes = 150, porte_armure = 150,
		pilori = 200, atelier_armurier = 600,

		abri_foret = 50, auvent_foret = 60, tente_usee = 80, tente_rustique = 100, tente_petite = 120,
		tente_petite_verte = 140, tente_petite_rouge = 140, tente_petite_b = 140, auvent_grand = 150, tente_foret_a = 180,
		tente_foret_b = 180, tente_foret_c = 180, tente_ronde = 250, tente_ronde_1 = 250, tente_ronde_2 = 250,
		tente_carree = 300, tente_carree_b = 320, tente_carree_c = 320, tente_carree_verte = 320, tente_couman = 400,
		tente_yourte = 600, tente_riche = 900, tente_riche_ouverte = 900, tente_royale = 2000, tente_royale_ouverte = 2000,

		palissade = 400, porte_palissade = 1000,
		decor_cart_with_water = 300, decor_cart_with_things = 300, decor_tent_with_goods_dealer = 300,
		decor_canopy_small_shop = 150, decor_stash_industriall_with_firewood = 150, decor_stash_industriall_with_crates = 150,
		decor_stash_industriall_with_sacks = 150, decor_stash_forest_with_barrels = 150,
		decor_stash_forest_with_sacks_and_barrel = 150, decor_stack_of_goods_big = 100, decor_stack_of_goods_big_v2 = 100,
		decor_cooking_station_3 = 200, decor_cooking_station_v1 = 200, decor_cooking_station_v2 = 200,
		decor_cooking_station_v3_shelves = 250, decor_beer_keg_on_stump_driping = 100, decor_table_drinking_station = 60,
		decor_cages_coveres_big = 80, decor_cages_with_sack_medium = 50, decor_stack_of_cages_small = 40,
	}


	pr.INSTALLATIONS = { arene = 1200, entrainement = 400, fleches = 300, cuisine = 200, tonneau = 150, banc = 60, baquets = 60,
		pisser = 40 }
	pr._payes = pr._payes or {}

	local function valeur(v) pcall(function() scriptorium.valeur("prix_du_camp", v) end) end

	function pr.prix(cle)
		cle = tostring(cle)
		if pr.PRIX[cle] ~= nil then return tonumber(pr.PRIX[cle]) or 0 end
		if string.sub(cle, 1, 6) == "decor_" then return pr.DECOR end
		return 0
	end
	function pr.coffre(m)
		local c = 0
		pcall(function() c = scriptorium.banque.coffre(m) end)
		return tonumber(c) or 0
	end

	function pr.payer(m, prix, cle)
		local ok = false
		pcall(function()
			local bq = scriptorium.banque
			bq.au_coffre_sans_journal(m, -prix, "amenagement")
			bq.mouvement(m, "amenagement", prix, 1, cle)
			bq.sauver(m)
			ok = true
		end)
		valeur(string.format("paye-%s-%d", tostring(cle), prix))
		return ok
	end


	function pr.rembourser(m, prix, cle)
		local ok = false
		pcall(function()
			local bq = scriptorium.banque
			bq.au_coffre_sans_journal(m, prix, "annulation")
			bq.mouvement(m, "annulation", prix, 1, cle)
			bq.sauver(m)
			ok = true
		end)
		valeur(string.format("rembourse-%s-%d", tostring(cle), prix))
		return ok
	end
	local function dire_le_refus(prix)
		pcall(function()
			Game.SendInfoText("@scriptorium_directeur_dit @scr_pr_coffre " .. tostring(math.floor(prix)) .. " @scr_mi_gros", false, 0, 10)
		end)
	end


	local function sans_patente(m)
		local manque = false
		pcall(function()


			local pn = scriptorium.patente
			manque = pn ~= nil and pn.ACTIF and not m.CampActif and not pn.achetee(m)
		end)
		return manque
	end

	local function payante(origine, fondation)
		return function(jeton, cle, ...)
			local m = _G.compagnie
			local prix = pr.ACTIF and pr.prix(cle) or 0
			local deja = jeton ~= nil and pr._payes[jeton] ~= nil
			if fondation and m ~= nil and sans_patente(m) then return origine(jeton, cle, ...) end
			if prix > 0 and not deja and m ~= nil and pr.coffre(m) < prix then
				valeur(string.format("refus-%s-%d", tostring(cle), prix))
				dire_le_refus(prix)
				return "coffre_" .. math.floor(prix)
			end
			local r = origine(jeton, cle, ...)


			if prix > 0 and not deja and type(r) == "number" and m ~= nil and not (jeton ~= nil and pr._payes[jeton]) then
				if jeton ~= nil then pr._payes[jeton] = true end
				pr.payer(m, prix, cle)
			end
			return r
		end
	end


	function pr.brancher()
		local ed = scriptorium.editeur
		if type(ed) ~= "table" then return end
		if type(ed.ajouter) == "function" and ed.ajouter ~= pr._ajouter then
			pr._ajouter = payante(ed.ajouter, false)
			ed.ajouter = pr._ajouter
		end
		if type(ed.fonder) == "function" and ed.fonder ~= pr._fonder then
			pr._fonder = payante(ed.fonder, true)
			ed.fonder = pr._fonder
		end
	end

	if type(scriptorium.reveiller_la_compagnie) == "function" then
		local origine = scriptorium.reveiller_la_compagnie
		scriptorium.reveiller_la_compagnie = function(p)
			local n = origine(p)
			pcall(pr.brancher)
			return n
		end
	end
	pcall(pr.brancher)
end
