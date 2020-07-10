# T2C Harvester - v0.1

Ce script récupère et enregistre dans une base de donnée le nom ainsi que l'identifiant technique de chaque ligne et les directions/arrêts associés du réseau de transport T2C. Il est ensuite possible d'utiliser ces identifiants pour obtenir les horaires de passage en temps réel à un arrêt donné à l'aide du service [qr.t2c.fr](qr.t2c.fr).

## Motivation

A l'origine, ce script me servait à générer automatiquement une base de donnée pour l'application web [Bus'O'Matic](https://github.com/Oxmel/busomatic). Appli web que j'avais créé à l'époque pour un usage perso car les solutions déjà existantes ne me convenaient pas. 

Aujourd'hui la situation est assez différente, et l'offre est pléthorique en matière de services et d'applications. Avec notamment les appli android [Auvergne Mobilité](https://play.google.com/store/apps/details?id=fr.auvergne.mobilite.android), mais également l'arrivée plus récente de [MyBus](https://play.google.com/store/apps/details?id=fr.monkeyfactory.mybusclermontferrand&hl=fr) ou encore l'appli web communautaire [t2c.app](https://twitter.com/ToshCamille/status/1244221407921389568). 

En revanche, bien que le [SMTC](http://www.smtc-clermont-agglo.fr/) de Clermont ait récemment fait un premier pas en mettant en ligne un jeu de données sur [transport.data.gouv.fr](https://transport.data.gouv.fr/datasets/donnees-reseau-tc-t2c-ete-2020-gtfs/), il ne s'agit là que de données bruts et ne permettant d'obtenir que les horaires de passage théoriques. Alors même que les data présentes sur [navitia.io](https://navitia.io) sont déjà mises en forme et prêtes à l'emploi, en offrant en plus la possibilité d'obtenir les horaires en temps réel. 

Et, comme ils ne semblent pas particulièrement pressés d'ouvrir l'accès à cette api, ce script permet au moins d'offrir une solution alternative. En attendant qu'ils finissent, un jour peut-être, par se décider à permettre au grand public d'accéder à leur données de transport sur navitia (#IWantToBelieve).

## Exemples d'utilisation

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

Une fois que l'on connaît l'identifiant de l'arrêt basé sur la ligne et la direction, il suffit de passer cet identifiant en paramètre sur l'url qr.t2c.fr pour récupérer les horaires de passage des 10 prochains bus/tram à cet arrêt.

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

A noter qu'ici, et pour simplifier l'exemple, ce snippet récupère seulement le 1er résultat. Mais si on veut récupérer l'ensemble des horaires, il suffit dans ce cas de créer une boucle et de stocker chaque résultat dans une liste.

