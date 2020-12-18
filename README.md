# T2C Harvester - v0.1

**Mise à jour: Ce projet a été abandonné car l'ensemble des données de transport de la T2C sont désormais disponibles sous licence ODBL sur [transport.data.gouv](https://transport.data.gouv.fr/datasets/aom/34) et directement exploitables via l'api de [navitia.io](https://navitia.opendatasoft.com/explore/dataset/fr-se/table/). Dans ces conditions, un tel script basé sur du web scraping n'a donc plus vraiment de raison d'être.**

## Description

Ce script récupère et enregistre dans une base de donnée le nom ainsi que l'identifiant technique de chaque ligne et les directions/arrêts associés du réseau de transport T2C. Il est ensuite possible d'utiliser ces identifiants pour obtenir les horaires de passage en temps réel à un arrêt donné à l'aide du service [qr.t2c.fr](qr.t2c.fr).

## Motivation

A l'origine, et en l'absence de sources ouvertes, ce script me servait à générer automatiquement une base de donnée pour l'application web [Bus'O'Matic](https://github.com/Oxmel/busomatic). Appli web que j'avais créé à l'époque pour un usage perso car les solutions déjà existantes ne me convenaient pas. 

Aujourd'hui la situation est assez différente, et l'offre est pléthorique en matière de services et d'applications. Avec notamment les appli android [Oùra](https://play.google.com/store/apps/details?id=fr.cityway.maas.oura&hl=fr_FR), mais également l'arrivée plus récente de [MyBus](https://play.google.com/store/apps/details?id=fr.monkeyfactory.mybusclermontferrand&hl=fr) ou encore l'appli web communautaire [t2c.app](https://twitter.com/ToshCamille/status/1244221407921389568). 
