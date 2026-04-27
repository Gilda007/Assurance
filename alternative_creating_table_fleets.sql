-- ==========================================
-- CRÉATION DE LA TABLE fleets
-- ==========================================

CREATE TABLE IF NOT EXISTS fleets (
    -- Identifiant principal
    id SERIAL PRIMARY KEY,
    
    -- Identification de la Flotte
    nom_flotte VARCHAR(100) NOT NULL,
    code_flotte VARCHAR(50) NOT NULL UNIQUE,
    
    -- Gestion & Assureur
    assureur INTEGER,
    type_gestion VARCHAR(50),
    remise_flotte INTEGER DEFAULT 0,
    statut VARCHAR(50) DEFAULT 'Actif',
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Totaux
    total_rc INTEGER DEFAULT 0,
    total_dr INTEGER DEFAULT 0,
    total_vol INTEGER DEFAULT 0,
    total_vb INTEGER DEFAULT 0,
    total_in INTEGER DEFAULT 0,
    total_bris INTEGER DEFAULT 0,
    total_ar INTEGER DEFAULT 0,
    total_dta INTEGER DEFAULT 0,
    total_prime_nette INTEGER DEFAULT 0,
    
    -- Calendrier du contrat
    date_debut DATE,
    date_fin DATE,
    
    -- Notes
    observations TEXT,
    
    -- Relations
    owner_id INTEGER,
    
    -- Traçabilité
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    created_ip VARCHAR(45),
    last_ip VARCHAR(45),
    
    -- Contraintes de clés étrangères
    CONSTRAINT fk_fleets_assureur FOREIGN KEY (assureur) 
        REFERENCES automobile_compagnies(id) ON DELETE SET NULL,
    CONSTRAINT fk_fleets_owner FOREIGN KEY (owner_id) 
        REFERENCES contacts(id) ON DELETE SET NULL,
    CONSTRAINT fk_fleets_created_by FOREIGN KEY (created_by) 
        REFERENCES utilisateurs(id) ON DELETE SET NULL,
    CONSTRAINT fk_fleets_updated_by FOREIGN KEY (updated_by) 
        REFERENCES utilisateurs(id) ON DELETE SET NULL
);

-- ==========================================
-- CRÉATION DES INDEX
-- ==========================================

-- Index pour les recherches par propriétaire
CREATE INDEX IF NOT EXISTS idx_fleets_owner_id ON fleets(owner_id);

-- Index pour les recherches par assureur
CREATE INDEX IF NOT EXISTS idx_fleets_assureur ON fleets(assureur);

-- Index pour les recherches par code flotte
CREATE INDEX IF NOT EXISTS idx_fleets_code_flotte ON fleets(code_flotte);

-- Index pour les recherches par statut
CREATE INDEX IF NOT EXISTS idx_fleets_statut ON fleets(statut);

-- Index pour les recherches par dates
CREATE INDEX IF NOT EXISTS idx_fleets_date_debut ON fleets(date_debut);
CREATE INDEX IF NOT EXISTS idx_fleets_date_fin ON fleets(date_fin);

-- Index composite pour les recherches fréquentes (propriétaire + statut)
CREATE INDEX IF NOT EXISTS idx_fleets_owner_statut ON fleets(owner_id, statut);

-- ==========================================
-- COMMENTAIRES SUR LES COLONNES
-- ==========================================

COMMENT ON TABLE fleets IS 'Table des flottes de véhicules';
COMMENT ON COLUMN fleets.id IS 'Identifiant unique de la flotte';
COMMENT ON COLUMN fleets.nom_flotte IS 'Nom de la flotte';
COMMENT ON COLUMN fleets.code_flotte IS 'Code unique de la flotte';
COMMENT ON COLUMN fleets.assureur IS 'ID de la compagnie d''assurance';
COMMENT ON COLUMN fleets.type_gestion IS 'Type de gestion: GLOBAL ou PAR_VEHICULE';
COMMENT ON COLUMN fleets.remise_flotte IS 'Remise accordée sur la flotte (%)';
COMMENT ON COLUMN fleets.statut IS 'Statut: Actif, Bloqué, Résilié';
COMMENT ON COLUMN fleets.is_active IS 'Flag d''activation';
COMMENT ON COLUMN fleets.owner_id IS 'ID du propriétaire (contact)';