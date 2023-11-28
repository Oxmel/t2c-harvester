# T2C Harvester - v0.1.1

## Description

A l'origine, et en l'absence de sources ouvertes, ce script me servait à générer une base de données pour l'application web [Bus'O'Matic](https://github.com/Oxmel/busomatic).

L'idée étant d'enregistrer dans une BDD SQLite le nom ainsi que l'identifiant technique de chaque ligne, direction et arrêt du réseau. Ce qui permet ensuite de construire un système de recherche et d'affichages des horaires pour un arrêt donné. En se basant sur le service d'information par [QRCode](https://www.t2c.fr/horaires-par-qrcode) proposé par la T2C.

Aujourd'hui, on peut normalement se passer de cette méthode car l'ensemble des données de transport de la T2C sont disponibles sous licence ODBL sur [transport.data.gouv.fr](https://transport.data.gouv.fr/datasets/aom/34). Et directement exploitables via l'api de [navitia.io](https://navitia.io/).

Le problème est qu'il s'agit ici d'horaires théoriques qui ne prennent pas en compte les éventuelles perturbations, grêves, retards liés à la circulation, etc... Et il peut donc arriver régulièrement que ces données ne correspondent pas à la réalité. Cette méthode peut alors permettre d'obtenir des plannings de passage plus précis. Car pour les horaires affichés sur [qr.t2c.fr](http://qr.t2c.fr) on est en général sur du (quasi) temps réel.

## Usage

#### 1. Générer la base de données

Pour générer une base de données, clonez ce repo, installez les dépendances, et lancez le script :

    $ git clone https://github.com/Oxmel/t2c-harvester
    $ pip3 install beautifulsoup4
    $ python3 t2c-harvester.py

#### 2. Accéder aux données

Voici un exemple basique en python pour afficher l'ensemble des lignes disponibles :

    import sqlite3

    database = ('t2c-database.sq3')
    conn = sqlite3.connect(database)
    lines = conn.execute("""SELECT id_ligne, nom, numero FROM lignes""")

    for line in lines:
        print (line)

La référence `id_ligne` permet de récupérer les directions associées à une ligne spécifique :

    SELECT id_direction, nom, numero FROM lignes WHERE id_ligne=X

La référence `id_direction` permet de récupérer les arrêts correspondants à une direction :

    SELECT nom, numero FROM arrets WHERE id_direction=X

#### 3. Récupérer les horaires de passage

Une fois qu'on connaît l'identifiant de l'arrêt basé sur la ligne et la direction, il suffit de le passer en paramètre de l'url `qr.t2c.fr/qrcode?_stop_id=` pour récupérer les horaires de passage des 10 prochains bus/tram à cet arrêt.

Voici un autre exemple en python permettant d'extraire les valeurs avec `BeautifulSoup4` :

    import urllib.request
    from bs4 import BeautifulSoup

    # Ligne A - Direction La Pardieu Gare - Arrêt Jaude
    stop_id = '3377704015495730'

    url = ('http://qr.t2c.fr/qrcode?_stop_id=' + stop_id)
    conn = urllib.request.urlopen(url)
    soup = BeautifulSoup(conn, from_encoding='utf-8', features='html.parser')

    for item in soup.find_all('tr')[1:]:
        line_info = item.find_all('td')[:3]
        try:
            print ('Ligne: ' + line_info[0].get_text().strip())
            print ('Direction: ' + line_info[1].get_text().strip())
            print ('Prochain passage: ' + line_info[2].get_text().strip())
        except IndexError:
            print ('Aucun passage prévu')

## Alternatives

Il existe également un certain nombre d'alternatives pour pouvoir récupérer les horaires à un arrêt donné, effectuer une recherche d'itinéraire, etc... Avec notamment l'appli android [Oùra](https://play.google.com/store/apps/details?id=fr.cityway.maas.oura&hl=fr_FR), mais également [MyBus](https://play.google.com/store/apps/details?id=fr.monkeystudio.mybusgeneric), ou encore l'appli web communautaire [t2c.app](https://twitter.com/ToshCamille/status/1244221407921389568).
