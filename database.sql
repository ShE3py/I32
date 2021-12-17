--
-- Domaine représentant les pays que les utilisateurs peuvent renseigner comme adresse de domicile.
--
CREATE DOMAIN pays
    AS TEXT
    CHECK (
        value IN (
            'France'
        )
    );


--
-- Table représentant l'adresse des utilisateurs.
--
CREATE TABLE adresse (
    id SERIAL NOT NULL PRIMARY KEY, -- SERIAL <=> AUTOINCREMENT sur PostgreSQL
    pays pays NOT NULL,
    code_postal TEXT NOT NULL,
    rue TEXT NOT NULL,
    numero TEXT NOT NULL,
    complement TEXT
);

INSERT INTO adresse VALUES
    (DEFAULT, 'France', '93390', 'rue de Strasbourg', '46', NULL),
    (DEFAULT, 'France', '21000', 'rue des lieutenants Thomazo', '109', NULL),
    (DEFAULT, 'France', '57050', 'rue St Ferréol', '144b', NULL),
    (DEFAULT, 'France', '88630', 'rue de la Basilique', '2', NULL),
    (DEFAULT, 'France', '91600', 'rue du Président Roosevelt', '127', 'App. 7');


--
-- Table représentant les utilisateurs.
--
CREATE TABLE utilisateur (
    id SERIAL NOT NULL PRIMARY KEY, -- SERIAL <=> AUTOINCREMENT sur PostgreSQL
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    mail TEXT NOT NULL UNIQUE,
    tel TEXT NOT NULL,
    adresse INTEGER NOT NULL REFERENCES adresse(id)
);

INSERT INTO utilisateur VALUES
    (DEFAULT, 'Ferrau', 'Huppé', 'ferrau.huppe@yahoo.fr', '01.11.92.28', 1),
    (DEFAULT, 'Blanchefle', 'Robitaille', 'banchefle-robitaille@gmail.com', '03 36 16 24', 2),
    (DEFAULT, 'Ferrau', 'Patrice', 'patate482@yahoo.fr', '01.11.92.28', 1),
    (DEFAULT, 'Gradasso', 'Bilodeau', 'gradasso@google.com', '+33 3 35 61 28', 3),
    (DEFAULT, 'd''Arc', 'Jeanne', 'jeannedarc@vosges.fr', '0329069586', 4),
    (DEFAULT, 'Romée', 'Isabelle', 'isabelleromee@vosges.fr', '0329069586', 4),
    (DEFAULT, 'd''Arc', 'Jacques', 'jacquesdarc@vosges.fr', '03 29 06 95 86', 4),
    (DEFAULT, 'd''Arc', 'Catherine', 'catherine@vosges.fr', '0329 0695 86', 4),
    (DEFAULT, 'de Chateaub', 'Royce', 'royce@dechateaub.co.uk', '014932645', 5);


--
-- Table contenant les catégories disponibles pour les articles.
--
CREATE TABLE categorie (
    id INTEGER NOT NULL PRIMARY KEY,
    nom TEXT NOT NULL
);

INSERT INTO categorie VALUES
    (1, 'Smartphone'),
    (2, 'PC'),
    (3, 'Tablette'),
    (4, 'Audio'),
    (5, 'Caméra');


--
-- Table contenant tous les articles, même ceux achetés.
--
CREATE TABLE article (
    reference TEXT NOT NULL PRIMARY KEY,
    categorie INTEGER NOT NULL REFERENCES categorie(id),
    vendeur INTEGER NOT NULL REFERENCES utilisateur(id),
    prix REAL NOT NULL CHECK ( prix >= 0 AND prix <> 'NaN' AND prix <> 'Infinity' ),
    description TEXT,
    marque TEXT NOT NULL,
    serie TEXT NOT NULL,
    modele TEXT NOT NULL
);

INSERT INTO article VALUES
    ('abricot', 1, 1, 500, 'Un iPhone 13.', 'Apple', 'iPhone', 'iPhone 13'),
    ('banane', 1, 2, 620, 'iPhone 13, encore emballé.', 'Apple', 'iPhone', 'iPhone 13'),
    ('courgette', 1, 2, 15, 'Téléphone résistant aux chocs', 'Nokia', 'Nokia 105', 'Nokia 105'),
    ('datte', 2, 3, 4200, 'Écran 27 pouces, 8 coeurs, Intel Xeon W (3.2 GHz), Radeon Pro Vega 56, 1 To SDD', 'Apple', 'iMac', 'iMac Pro'),
    ('érable', 2, 4, 260, 'Beau comme un dindon sorti du four.', 'Lenovo', 'Lenovo', 'Lenovo L540'),
    ('figue', 3, 9, 700, 'Prix de Noël !', 'Apple', 'iPad', 'iPad Pro'),
    ('goyave', 4, 5, 830, 'Couleur: noyer', 'Focal', 'Aria', 'Aria 936'),
    ('haricot', 4, 6, 11490, NULL, 'Klipsch', 'Klipschorn', 'Klipschorn AK6'),
    ('icaque', 4, 1, 90, 'Haut-parleurs 5.1', 'Logitech', 'Logitech Z607', 'Logitech Z607'),
    ('jamalac', 5, 4, 400, '24.1 mégapixels', 'Canon', 'Canon EOS', 'Canon EOS 2000D');


--
-- Table contenant la référence des articles achetables
--
CREATE TABLE article_en_vente (
    article TEXT NOT NULL PRIMARY KEY REFERENCES article(reference) ON DELETE CASCADE
);

INSERT INTO article_en_vente (SELECT reference FROM article);


--
-- Vue équivalente à la table `article`, ne contenant que les articles présents dans la table `article_en_vente`.
--
CREATE VIEW articles_en_vente AS
    SELECT article.reference, article.categorie, article.vendeur, article.prix, article.description, article.marque, article.serie, article.modele
    FROM article
    WHERE (
        article.reference IN (
            SELECT article_en_vente.article
            FROM article_en_vente
        )
    );


--
-- Trigger: Après l'ajout d'un tuple dans la table `article`, le met directement en vente dans la table `article_en_vente`.
--
CREATE FUNCTION sync_articles_en_vente()
    RETURNS TRIGGER
    LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO article_en_vente VALUES (NEW.reference);

    RETURN NULL;
END;
$$;

CREATE TRIGGER sync_articles_en_vente_trigger
    AFTER INSERT
    ON article
    FOR EACH ROW
    EXECUTE FUNCTION sync_articles_en_vente();


--
-- Table représentant l'achat d'un article.
--
CREATE TABLE achat (
    acheteur INTEGER NOT NULL REFERENCES utilisateur(id),
    article TEXT NOT NULL PRIMARY KEY REFERENCES article(reference)
);


--
-- Table représentant la vente d'un article.
--
CREATE TABLE vente (
    vendeur INTEGER NOT NULL REFERENCES utilisateur(id),
    article TEXT NOT NULL PRIMARY KEY REFERENCES article(reference)
);


--
-- Trigger: Après l'ajout ou la suppresion d'un tuple dans la table `achat`, répercute le changement dans `vente`.
--
CREATE FUNCTION sync_achat_vente()
    RETURNS TRIGGER
    LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO vente (
            SELECT article.vendeur, article.reference FROM article
            WHERE article.reference = NEW.article -- jointure pour récupérer le vendeur à partir de la référence de l'article
        );

    ELSEIF TG_OP = 'DELETE' THEN
        DELETE FROM vente
        WHERE vente.article = OLD.article;

    ELSE
        RAISE EXCEPTION 'entered unreachable code: TG_OP = %', TG_OP;

    END IF;

    RETURN NULL;
END;
$$;

CREATE TRIGGER sync_achat_vente_trigger
    AFTER INSERT OR DELETE
    ON achat
    FOR EACH ROW
    EXECUTE FUNCTION sync_achat_vente();

--
-- Effectue une recherche à partir des filtres passés en paramètre.
--
CREATE FUNCTION recherche(search_input TEXT DEFAULT NULL, categorie_filter INTEGER DEFAULT NULL, price_min REAL DEFAULT 0, price_max REAL DEFAULT 'Infinity', ordering INTEGER DEFAULT 0)
    RETURNS TABLE(reference TEXT, modele TEXT, prix REAL, nom_vendeur TEXT, prenom_vendeur TEXT)
    LANGUAGE plpgsql
AS $$
BEGIN
    -- résultat de la recherche désordonnée
    CREATE TEMPORARY TABLE unordered(reference text, modele text, prix real, nom_vendeur text, prenom_vendeur text);

    INSERT INTO unordered (
        SELECT article.reference, article.modele, article.prix, utilisateur.nom, utilisateur.prenom FROM articles_en_vente article, utilisateur
            WHERE article.vendeur = utilisateur.id -- jointure pour réunir les articles et le nom du vendeur sur la même ligne
            AND (
                -- filtre avec les mots à rechercher, si existants
                search_input IS NULL
                OR LOWER(article.description) LIKE LOWER(search_input)
                OR LOWER(article.marque) LIKE LOWER(search_input)
                OR LOWER(article.serie) LIKE LOWER(search_input)
                OR LOWER(article.modele) LIKE LOWER(search_input)
            )
            AND (
                categorie_filter IS NULL
                OR article.categorie = categorie_filter
            )
            AND (
                article.prix >= price_min
                AND article.prix <= price_max
            )
    );

    IF ordering = 0 THEN
        RETURN QUERY SELECT * FROM unordered;

    ELSEIF ordering = 1 THEN
        RETURN QUERY SELECT * FROM unordered ORDER BY prix ASC;

    ELSEIF ordering = 2 THEN
        RETURN QUERY SELECT * FROM unordered ORDER BY prix DESC;

    ELSE
        RAISE EXCEPTION 'unknow ordering %', ordering;

    END IF;

    DROP TABLE unordered;
END
$$;


--
-- Renvoie l'historique d'achat de l'utilisateur `user_id`.
--
CREATE FUNCTION historique_achat(user_id INTEGER)
    RETURNS TABLE(reference TEXT, modele TEXT, prix REAL, nom_vendeur TEXT, prenom_vendeur TEXT)
    LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
        SELECT article.reference, article.modele, article.prix, utilisateur.nom, utilisateur.prenom FROM article, utilisateur
        WHERE article.vendeur = utilisateur.id -- jointure pour réunir les articles et le nom du vendeur sur la même ligne
        AND article.reference IN (
            SELECT article FROM achat
            WHERE achat.acheteur = user_id -- l'on ne prend que les articles qui ont étés achetés par `user_id`
        );
END;
$$;


--
-- Renvoie l'historique de vente de l'utilisateur `user_id`.
--
CREATE FUNCTION historique_vente(user_id INTEGER)
    RETURNS TABLE(reference TEXT, modele TEXT, prix REAL, nom_acheteur TEXT, prenom_acheteur TEXT)
    LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
        SELECT article.reference, article.modele, article.prix, utilisateur.nom, utilisateur.prenom FROM article, achat, utilisateur
            WHERE article.reference IN (
                SELECT vente.article FROM vente
                WHERE vente.vendeur = user_id -- l'on ne prend que les articles qui ont étés vendus par `user_id`
            )
            AND achat.article = article.reference -- jointure pour récupérer les details de l'achat depuis la table `article` à travers la table `achat`
            AND utilisateur.id = achat.acheteur; -- jointure pour réunir les articles et le nom de l'acheteur sur la même ligne
END;
$$;


--
-- Renvoie les articles actuellements vendus par l'utilisateur `user_id`.
--
CREATE FUNCTION articles_vendus_par(user_id INTEGER)
    RETURNS TABLE(reference TEXT, modele TEXT, prix REAL)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
        SELECT article.reference, article.modele, article.prix FROM articles_en_vente article
        WHERE article.vendeur = user_id;
END;
    $$;
