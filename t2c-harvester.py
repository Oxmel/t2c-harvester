#!/usr/bin/env python
# -*- coding: UTF-8 -*-


'''
                            T2C Harvester v0.1

Dans le cadre du fonctionnement de ses services de transport, la T2C a mis en
place un système de numérotation technique (ou ID) de chacune de ses lignes.
Chaque ligne dispose donc d'un nom (ex. 'Ligne B'), ainsi que d'un identifiant
technique (ex. '11821953316814897'). Même chose pour chaque direction ainsi que
chaque arrêt qui disposent eux aussi du même type d'identifiant.

Ce numéro permet d'obtenir les horaires de passage en temps réel grâce à la
page web 'qr.tc2.fr' qui est un service d'information par qrcode disponible à
chaque arrêt. Cependant, en temps normal pour pouvoir utiliser ce service, il
faut être physiquement présent à l'arrêt et flasher un qrcode avec son mobile
afin de pouvoir accéder aux horaires en question.

Ce script a pour but de récupérer les identifiants de chaque ligne régulière du
réseau T2C et chaque direction / arrêt associé et de les stocker dans un base
de donnée au format sqlite. Il est ensuite possible, à partir de cette bdd, de
construire un système de recherche et d'affichage des horaires en temps réel
pour n'importe quel arrêt. Pour un exemple d'application pratique, se référer
au projet 'Bus-O-Matic' (https://github.com/Oxmel/busomatic).

'''


import urllib
from bs4 import BeautifulSoup
from collections import OrderedDict
import sqlite3
import os
import time
import re


# Url base permettant de récupérer les numéros de lignes
line_url = 'http://auvergne-mobilite.fr/fr/schedule/line/?&lineSchedule[network]=network%3AT2C'
# Url base des directions
dir_url = 'http://www.t2c.fr/admin/synthese?SERVICE=page&p=17732927961956390&noline='
# Url base des arrêts
stop_url = 'http://www.t2c.fr/admin/synthese?SERVICE=page&p=17732927961956392&numeroroute='
# Enregistre la base de donnée dans le même dossier que ce script
db = os.path.abspath('t2c-database.sq3')
conn = sqlite3.connect(db)
# Curseur temporaire pour forger les requêtes SQL
# Utiliser 'commit()' pour écrire définitivement dans la bdd
cur = conn.cursor()


# Récupère le nom / numéro de chaque ligne du réseau
def get_lines():
    line_list = OrderedDict()
    req = urllib.urlopen(line_url)
    soup = BeautifulSoup(req, from_encoding='utf-8', features='html.parser')
    lines = soup.find('select', {'id': 'lineSchedule_line'}).find_all('option')[1:]

    for line in lines:
        try:
            line_name = re.search(r'(^[A-C]|[0-9]{1,2})', line.text).group(1)
            line_num = re.search(r'line:T2C:(.*)', line['value']).group(1)
        # Ignore les lignes 'spéciales' qui ne sont pas exploitables
        except AttributeError:
            pass

        line_list[line_name] = line_num

    return line_list


# Récupère chaque direction / arrêt pour une ligne donnée
def get_line_data(url):
    item_list = OrderedDict()
    req = urllib.urlopen(url)
    soup = BeautifulSoup(req, from_encoding='utf-8', features='html.parser')

    # Skip le 1er résultat qui est un placeholder
    for item in soup.find_all('option')[1:]:
        item_name = item.text.strip()
        item_num = item['value']
        item_list[item_name] = item_num

    return item_list


# Créé la bdd et les tables qui seront utilisées pour stocker les data
# On utilise un système de 'Foreign Key' pour lier les tables entre elles
# Ce système permet de rechercher facilement toutes les directions / arrêts
# pour une ligne donnée (voir le README pour des exemples)
def create_db():
    print ('Création de la base de donnée...')
    # Récupère l'état de l'option 'foreign_keys' (0 ou 1)
    foreign_key = conn.execute('PRAGMA foreign_keys')
    # La requête retourne un tuple donc on extrait la valeur
    foreign_state = foreign_key.fetchone()[0]
    if foreign_state == 0:
        cur.execute('PRAGMA foreign_keys=ON')

    # Table parent 'lignes'
    cur.execute('''CREATE TABLE lignes(
        id_ligne INTEGER PRIMARY KEY,
        nom VARCHAR(10),
        numero INTEGER)''')
    # Table enfant de 'lignes'
    cur.execute('''CREATE TABLE directions(
        id_ligne INTEGER NOT NULL,
        id_direction INTEGER PRIMARY KEY,
        nom VARCHAR(10),
        numero INTEGER,
        FOREIGN KEY (id_ligne) REFERENCES lignes(id_ligne))''')
    # Table enfant de 'directions' et petit enfant de 'lignes'
    cur.execute('''CREATE TABLE arrets(
        id_ligne INTEGER NOT NULL,
        id_direction INTEGER NOT NULL,
        id_arret INTEGER PRIMARY KEY,
        nom VARCHAR(10),
        numero INTEGER,
        FOREIGN KEY (id_ligne) REFERENCES lignes(id_ligne),
        FOREIGN KEY (id_direction) REFERENCES directions(id_direction))''')

    conn.commit()


# Scrap les infos des lignes / directions / arrêts et les stocke dans la bdd
def fill_db():
    line_list = get_lines()
    for line_name, line_num in line_list.items():
        print ('Traitement de la ligne %s' %line_name)
        cur.execute('''INSERT INTO lignes(
            nom, numero) VALUES(?, ?)''',
            (line_name, line_num))

        # ID sqlite de la ligne pour la relation parent/enfant
        line_row_id = cur.execute('SELECT last_insert_rowid()')
        line_key = line_row_id.fetchone()[0]
        # ID de ligne en paramètre pour récupérer chaque direction
        line_dir = get_line_data(dir_url + line_num)
        for dir_name, dir_num in line_dir.items():
            cur.execute('''INSERT INTO directions(
                id_ligne, nom, numero) VALUES(?, ?, ?)''',
                (line_key, dir_name, dir_num))

            # ID sqlite de la direction
            dir_row_id = cur.execute('SELECT last_insert_rowid()')
            dir_key = dir_row_id.fetchone()[0]
            # ID de direction en paramètre pour récupérer chaque arrêt
            line_stop = get_line_data(stop_url + dir_num)
            for stop_name, stop_num in line_stop.items():
                cur.execute('''INSERT INTO arrets(
                    id_ligne, id_direction, nom, numero) VALUES(?, ?, ?, ?)''',
                    (line_key, dir_key, stop_name, stop_num))

        # Pause entre chaque ligne pour éviter le spam de requêtes
        time.sleep(3)

    # Ecrit les infos dans la bdd
    conn.commit()
    cur.close()


if __name__ == '__main__':
    create_db()
    fill_db()

