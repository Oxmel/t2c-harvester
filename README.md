# T2C Harvester - v0.1.1

**Mise à jour du 29/08/2021** : Ce projet avait été archivé pendant un temps car l'ensemble des données de transport de la T2C étaient jusqu'à présent disponibles sous licence ODBL sur [transport.data.gouv.fr](https://transport.data.gouv.fr/datasets/aom/34) et directement exploitables via l'api de [navitia.io](https://navitia.opendatasoft.com/explore/dataset/fr-se/table/).

Cependant, ce [jeu de données](https://transport.data.gouv.fr/datasets/donnees-reseau-tc-t2c/#dataset-discussions) est périmé depuis le 04/07/2021 et malgré des demandes répétées émanant de plusieurs personnes, les data n'ont toujours pas été mises à jour. Raison pour laquelle ce projet va certainement reprendre du service pour palier l'inconstance de la T2C dans la mise à jour de leurs données de transport. 

A noter que ce script n'est pour l'instant plus fonctionnel en l'état (voir [cette issue](https://github.com/Oxmel/t2c-harvester/issues/1)) et je le corrigerai dès que j'aurai le temps de me pencher dessus à nouveau.

## Description

A l'origine, et en l'absence de sources ouvertes, ce script me servait à générer automatiquement une base de donnée pour l'application web [Bus'O'Matic](https://github.com/Oxmel/busomatic).

L'idée est d'enregistrer dans une bdd SQLite le nom ainsi que l'identifiant technique de chaque ligne et les directions / arrêts associés du réseau de transport T2C. Il est ensuite possible d'utiliser ces identifiants pour obtenir les horaires de passage en temps réel à un arrêt donné à l'aide du service [qr.t2c.fr](qr.t2c.fr).

## Alternatives

Il existe un certain nombre d'alternatives pour pouvoir récupérer les horaires à un arrêt donné, effectuer une recherche d'itinéraire, etc... Avec notamment l'appli android [Oùra](https://play.google.com/store/apps/details?id=fr.cityway.maas.oura&hl=fr_FR), mais également [MyBus](https://play.google.com/store/apps/details?id=fr.monkeyfactory.mybusclermontferrand&hl=fr), ou encore l'appli web communautaire [t2c.app](https://twitter.com/ToshCamille/status/1244221407921389568) créée par [CamTosh](https://github.com/CamTosh).

## Usage


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
