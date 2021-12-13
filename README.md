# T2C Harvester - v0.1.1

## Description

A l'origine, et en l'absence de sources ouvertes, ce script me servait à générer une base de donnée pour l'application web [Bus'O'Matic](https://github.com/Oxmel/busomatic).

Aujourd'hui, il n'est normalement plus nécessaire d'utiliser cette méthode car l'ensemble des données de transport de la T2C sont disponibles sous licence ODBL sur [transport.data.gouv.fr](https://transport.data.gouv.fr/datasets/aom/34). Et directement exploitables via l'api de [navitia.io](https://navitia.opendatasoft.com/explore/dataset/fr-se/table/).

Le problème étant que ces données sont mises à jour de manière assez aléatoire. Et il arrive parfois qu'elles deviennent inexpoitables pendant plusieurs semaines / mois. Cette méthode peut alors servir de fallback le temps qu'un nouveau jeu de données à jour soit disponible.


## Alternatives

Il existe également un certain nombre d'alternatives pour pouvoir récupérer les horaires à un arrêt donné, effectuer une recherche d'itinéraire, etc... Avec notamment l'appli android [Oùra](https://play.google.com/store/apps/details?id=fr.cityway.maas.oura&hl=fr_FR), mais également [MyBus](https://play.google.com/store/apps/details?id=fr.monkeyfactory.mybusclermontferrand&hl=fr), ou encore l'appli web communautaire [t2c.app](https://twitter.com/ToshCamille/status/1244221407921389568) créée par [CamTosh](https://github.com/CamTosh).


## Usage

L'idée est d'enregistrer dans une bdd SQLite le nom ainsi que l'identifiant technique de chaque ligne, direction et arrêt du réseau. Ce qui permet ensuite de scrap les horaires des 10 prochains bus / tram à un arrêt donné en passant son identifiant en paramètre sur `qr.t2c.fr/qrcode?_stop_id=`

#### 1. Générer la base de donnée
Pour générer une base de donnée,  clonez ce repo, installez les dépendances, et lancez le script :

    $ git clone https://github.com/Oxmel/t2c-harvester
    $ pip install BeautifulSoup4
    $ python t2c-harvester.py

#### 2. Accéder aux données

Une fois la base de données générée, vous pouvez utiliser le language de votre choix pour vous connecter à la bdd et lancer des requêtes afin de récupérer les informations nécessaires.

Voici un exemple basique en python pour afficher l'ensemble des lignes disponibles :

    import sqlite3

    database = ('t2c-database.sq3')
    conn = sqlite3.connect(database)
    lines = conn.execute("""SELECT id_ligne, nom, numero FROM lignes""")

    for line in lines:
        print line

La référence `id_ligne` permet de récupérer les directions associées à une ligne spécifique :

    SELECT id_direction, nom, numero FROM lignes WHERE id_ligne=1

La référence `id_direction` permet de récupérer les arrêts correspondants à une direction :

    SELECT nom, numero FROM arrets WHERE id_direction=1

#### 3. Récupérer les horaires de passage en temps réel

Une fois que l'on connaît l'identifiant de l'arrêt basé sur la ligne et la direction, il suffit de passer cet identifiant en paramètre sur l'url [qr.t2c.fr](qr.t2c.fr) pour récupérer les horaires de passage des 10 prochains bus/tram à cet arrêt.
Voici un autre exemple en python permettant d'extraire les valeurs avec `BeautifulSoup4` :

    from bs4 import BeautifulSoup
    import urllib

    # Ligne A - Direction La Pardieu Gare - Arrêt Jaude
    stop_id = '3377704015495730'

    url = 'http://qr.t2c.fr/qrcode?_stop_id='
    conn = urllib.urlopen(url + stop_id)
    soup = BeautifulSoup(conn, from_encoding='utf-8')
    line_info = soup.find_all('td')[:3]

    print 'Ligne: ' + line_info[0].text.strip()
    print 'Direction: ' + line_info[1].text.strip()
    print 'Prochain passage: ' + line_info[2].text.strip()

A noter qu'ici, et pour simplifier l'exemple, ce snippet récupère seulement le 1er résultat. Mais si on veut récupérer l'ensemble des horaires, il suffit par exemple de créer une boucle et de stocker chaque résultat dans une liste.
