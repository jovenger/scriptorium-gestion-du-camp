


















scriptorium = scriptorium or {}
scriptorium.prix_d_embauche = scriptorium.prix_d_embauche or {}

do
	local pe = scriptorium.prix_d_embauche
	if pe.ACTIF == nil then pe.ACTIF = true end
	pe.RECRUE = 250
	pe.CONFIRME = 500
	pe.VETERAN = 1500





	pe.ARCHER = 450
	pe.ARBALETRIER = 570

	local function valeur(v) pcall(function() scriptorium.valeur("prix_d_embauche", v) end) end

	local GENRES = { faible = "RECRUE", moyen = "CONFIRME", fort = "VETERAN", archer = "ARCHER",
		arbaletrier = "ARBALETRIER" }

	function pe.prix_de(genre)
		local cle = GENRES[genre]
		return cle and tonumber(pe[cle]) or nil
	end



	function pe.brancher()
		local em = scriptorium.embauche
		if type(em) ~= "table" or type(em.prix) ~= "function" or em.prix == pe._enveloppe then return end
		local ancien = em.prix
		pe._enveloppe = function(m, genre, ...)
			if pe.ACTIF then
				local p = pe.prix_de(genre)
				if p ~= nil then return p end
			end
			return ancien(m, genre, ...)
		end
		em.prix = pe._enveloppe
		valeur("branche")
	end
	pcall(pe.brancher)


	if type(scriptorium.reveiller_la_compagnie) == "function" then
		local origine = scriptorium.reveiller_la_compagnie
		scriptorium.reveiller_la_compagnie = function(p)
			local n = origine(p)
			pcall(pe.brancher)
			return n
		end
	end
end
