# Préambule

Ce dossier contient les fichiers exécutables et les ressources qui y sont associées pour le projet
de travaux pratiques du module I32 « Bases de données »,
enseigné au 3<sup>e</sup> semestre de la licence informatique à l'UFR Sciences et Techniques
de l'Université de Toulon, sur le campus de La Garde, durant
l'année scolaire 2021-2022.

Ce projet est un serveur web programmé en Python proposant un site fictif
d'achat et de vente d'articles entre particuliers ; toutes les données associées
au projet sont stockées dans une base de données PostgreSQL.

Les dossiers principaux sont :
- `src/website/`, contenant les fichiers associés au site web (`.html`, `.css`, etc.)
- `src/`, contenant les fichiers Python (`.py`) servant à exécuter le serveur web.

# Fonctionnement général

Lorsqu'un utilisateur demande une certaine page web au serveur,
- Si la page est [statique](https://fr.wikipedia.org/wiki/Page_web_statique), 
alors le programme envoie simplement le fichier contenu sur le disque.  
Par exemple, `http://localhost/accueil.html` enverra directement `src/website/accueil.html`.
<br /><br />
- Si la page est [dynamique](https://fr.wikipedia.org/wiki/Page_web_dynamique), alors le programme
lit un ou plusieurs fichiers HTML qu'il modifie pour afficher le résultat de la
requête SQL.  
Par exemple, pour afficher la page `http://localhost/search.html`, le serveur
lira deux fichiers :
<br /><br />
  - `src/website/search.item_card.in.html` :
    ```html
    <div class="card" style="width: 22em; margin: 4px;">
      <div class="card-body">
        <div class="row">
          <div class="col-12"><h5>{model}</h5></div>
          <p class="card-text">Vendeur: {seller_surname} {seller_name}</p>
        </div>
        <span>Prix: {price:.2f} €</span>
        <br />
        <ul class="buttons">
          <li class="shop_btn">
            <a href="/item.html?ref={ref}">Voir plus</a>
          </li>
        </ul>
      </div>
    </div>
    ```
    Dans lequel il remplacera les champs `{clef}` par les valeurs
    obtenues suites à la requête SQL effectuant la recherche ; le
    contenu du fichier sera copié-modifié-collé à raison d'une fois
    par ligne/article dans le résultat de la requête.
    <br /><br />
  - `src/website/search.in.html`, qui contient le code source de la page
    statique avec un conteneur spécial :
    ```html
    <div class="main">
      <div class="row" id="__python_generate"></div>
    </div>
    ```
    Le serveur Python remplacera simplement l'intérieur de l'unique
    élement tel que `id = "__python_generate"` par le code HTML généré
    à partir du fichier d'au-dessus.
    <br /><br />
- Enfin, certaines pages ne font qu'effectuer une opération ;
  `http://localhost/do_login.html` tente d'authentifier l'utilisateur,
  et redirige l'utilisateur vers une autre page en cas de succès ([`HTTP 303 See Other`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/303)),
  ou affiche un message d'erreur le cas échant.

L'authentification d'un utilisateur est très simpliste
(un simple cookie `userid` contenant l'ID de l'utilisateur) afin d'éviter
de complexifier inutiliment le projet.

Les paramètres des requêtes sont pasés à travers la [query string](https://en.wikipedia.org/wiki/Query_string) ;
`http://localhost/search.html?what=iPhone&price_max=600` affichera tous
les articles contenants « iPhone » dans leur description, modèle, série ou marque
coûtants moins de 600 €.

# Dépendances

Afin d'effectuer tout cela, le projet possède quelques dépendences :
- Python 3.9
- PostgreSQL 14.1
- Psycopg 2.9 &ndash; pour faire la liaison entre le serveur et la base de données.
- Beautiful Soup 4.10 &ndash; pour [parser](https://fr.wiktionary.org/wiki/parser#Verbe) et générer les pages web dynamiques.

Python Package Index:
```
pip install psycopg2
pip install beautifulsoup4
```

# Présentation des fichiers

Sans rentrer dans les détails, voici à quoi servent les fichiers Python
présents à la racine de `src/` :
- `main.py` &ndash; le fichier à exécuter pour lancer le serveur
- `database.py` &ndash; effectue la connexion à la base de données
- `webserver.py` &ndash; créer et traite les requêtes du serveur web

Tous les autres fichiers servent à traiter les requêtes dynamiques sur
la page du même nom ; `search.py` pour `search.html`.  

# Installation

Pour modifier la base de données que le serveur accède, il faut
simplement modifier directement le fichier `config.ini` qui se crée
au premier lancement.  
Vous obtiendrez une erreur dans `src/database.py` à la ligne 39 si le
serveur ne parvient pas à effectuer une connexion avec la base de données.

Pour copier la base de données initiale, il faut exécuter toutes les requêtes
SQL dans `database.sql`.

Pour modifier le port sur lequel le serveur web s'ouvre, il faut modifier
la ligne 24 de `src/webserver.py` :
```python
PORT = 80
SERVER_ADDRESS = ("127.0.0.1", PORT)
```

# Requêtes SQL dans le code

La plupart des requêtes SQL effectués dans Python sont basiques :
- Ajout d'un article : `src/add_item.py`, ligne 51 :
  ```sql
  INSERT INTO article VALUES (:reference, :categorie, :vendeur, :prix, :description, :marque, :serie, :modele);
  ```

- Achat d'un article : `src/buy_item.py`, lignes 26, 34 et 35 :
  ```sql
  -- Vérifie que l'article est bien achetable
  SELECT EXISTS(SELECT * FROM article_en_vente WHERE article = :reference);
  
  -- Effectue la transaction
  DELETE FROM article_en_vente WHERE article = :reference;
  INSERT INTO achat VALUES (:acheteur, :reference);
  ```

- Historique d'un utilisateur : `src/history.py`, lignes 43, 48 et 53 :
  ```sql
  SELECT * FROM historique_achat(:id_utilisateur);
  SELECT * FROM historique_vente(:id_utilisateur);
  SELECT * FROM articles_vendus_par(:id_utilisateur);
  ```

- Page de présentation d'un article : `src/item.py`, ligne 33 :
  ```sql
  SELECT prix, modele, description, nom, prenom, modele, serie, marque, code_postal
    FROM article, utilisateur, adresse
    WHERE article.vendeur = utilisateur.id
    AND utilisateur.adresse = adresse.id
    AND article.reference = :reference;
  ```

- Authentification d'un utilisateur : `src/login.py`, ligne 27 :
  ```sql
  SELECT id FROM utilisateur
    WHERE mail = LOWER(:mail);
  ```

- Affichage du profil d'un utilisateur : `src/profile.py`, lignes 53-55 :
  ```sql
  SELECT nom, prenom, mail, rue, numero, complement, code_postal, tel
    FROM utilisateur, adresse
    WHERE utilisateur.adresse = adresse.id
    AND utilisateur.id = :id_utilisateur;
  ```

- Création d'un nouveau compte utilisateur : `src/register.py`, lignes 46 et 49 :
  ```sql
  INSERT INTO adresse VALUES (DEFAULT, :pays, :code_postal, :rue, :numero, :complement) RETURNING id;
  INSERT INTO utilisateur VALUES (DEFAULT, :nom, :prenom, :mail, :tel, :id_adresse) RETURNING id;
  ```
  
  La clause `RETURNING` permet à la requête de renvoyer le nouvel identifiant
  généré par le type `SERIAL`/`AUTOINCREMENT`, sans à devoir refaire une 2<sup>e</sup>
  requête afin de le récupérer.
  <br /><br />
- Modification d'un compte utilisateur existant : `src/register.py`, lignes 73, 76 et 77 :
  ```sql
  SELECT adresse FROM utilisateur WHERE utilisateur.id = :id_utilisateur;
  
  UPDATE adresse
    SET rue = :rue, numero = :numero, complement = :complement, code_postal = :code_postal, pays = :pays
    WHERE id = :id_adresse;
  
  UPDATE utilisateur
    SET nom = :nom, prenom = :prenom, mail = :mail, tel = :tel
    WHERE id = :id_utilisateur;
  ```

- Recherche d'un article : `src/search.py`, ligne 67 :
  ```sql
  SELECT * FROM recherche(:saisie, :categorie, :prix_min, :prix_max, :ordonnancement);
  ```
