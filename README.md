# **Job Market Project**

Ce projet a pour objectif de créer un outil pour aider les étudiants et personnes en reconversion professionelle à s'orienter dans la recherche d'emploi et de formations dans le monde de la data. L'output consiste en un dashboard intéractif dans lequel l'utilisateur peut filtrer des offres d'emploi en ligne et analyser la demande pour certaines technologies sur le marché du travail. 

Les données sont collectées régulièrement (grace à l'usage de cron) en utilisant l'API d'Adzuna pour les offres d'emploi en France, complété par du web-scraping. Elles sont ensuite nettoyées et stockées dans une base de données ElasticSearch, d'où les données sont ensuite lues par un dashboard construit avec Plotly Dash. Le projet est structuré à l'aide de Docker, avec chaque partie containerisée séparément mais connectés à travers un réseau.

Pour lancer le projet, il suffit d'aller dans le terminal et de lancer `docker-compose up -d`, attendre quelques minutes, puis se rendre à `0:0:0:0/8050` dans le navigateur web.

Les sections suivantes expliquent chaque partie du projet.

## Collecte des données

Le dossier `App/src/Modules` contient le code nécessaire à la collecte des données. Il est organisé dans un conteneur Docker (voir le `Dockerfile`) basé sur une image `python:3.12-slim`, avec l'installation via pip de librairies contenues dans le fichier `requirements.txt`. Les fichiers `GenAdzunaJobs.py` et `GenAllJobs.py` sont lancés dans le Dockerfile via cron 1 et 2 fois par jour respectivement. Des logs des processus sont sauvegardés dans le fichier `App/src/Modules/LOGS/cron.log`.

**`GenAdzunaJobs.py`**: En premier lieu, les données d'offre d'emploi sont collectées à l'aide de l'API d'[Adzuna](https://www.adzuna.com), un aggrégateur d'offres d'emploi en ligne. Le fichier contient plusieurs fonctions: `get_adzuna_ads_page()`, qui collecte les données par page (vu qu'il y a une limite sur le nombre d'observation par page dans l'API) et `get_adzuna_ads()`, qui collecte les données pour toutes les pages. Ensuite `create_dump()` sauvegarde les données dans le dossier `App/data/adzuna_jobs`. La version actuelle cherche les offres d'emploi qui mentionnent le mot "data" dans le titre - les fonctions peuvent également chercher les offres d'emploi par catégorie, mais ça n'est pas utilisé dans la version actuelle. Le processus prend en compte les limites des demandent de l'API et optimise les pauses pour collecter le maximum d'offres d'emploi.

**`GenAllJobs.py`**: En deuxième lieu, ce fichier lance du web-scraping pour complèter l'information obtenue par l'API. Dans le cas où l'offre d'emploi vient à l'origine du site [HelloWork](https://www.hellowork.com), ce fichier (qui utilise des fonctions du fichier `GenHWJobs.py`) obtient un URL et scrape de l'information supplémentaire à partir du site. La fonction `gen_jobs()` vérifie si un URL de redirection existe dans les données collectées via l'API, et si oui, scrape HelloWork. Ensuite, elle combine les données de l'API et du scraping et les sauvegarde dans le dossier `App/data/all_jobs`.

**`GenHWJobs.py`**: Contient des fonctions nécessaires au scraping du site [HelloWork](https://www.hellowork.com). Il fait usage de la librairie BeautifulSoup pour le scraping, et procède à un nettoyage léger de certaines variables, comme le salaire, la duration du contrat ou si l'emploi permet le télétravail.

## Stockage des données

Le dossier `App/src/db` contient le code pour lancer le processus de stockage des données collectées dans la phase précédente dans une base de données ElasticSearch (un serveur ElasticSearch est déjà lancé via un ficher `docker-compose.yml`, comme expliqué ci-dessous). Cette partie est organisée dans un conteneur Docker basé sur une image `python:3.12-slim`, avec l'installation via pip de librairies contenues dans le fichier `requirements.txt`. Un cron job lancé dans le Dockerfile éxecute le fichier `GenEsData.py` régulièrement afin de d'uploader les dernières données à la base de données. Des logs des processus sont sauvegardés dans le fichier `App/src/db/LOGS/cron.log`.

**`GenEsData.py`**: ce fichier se connecte au serveur ElasticSearch et créer un nouvel index `adzuna_jobs` si il n'existe pas encore. Ensuite, il upload les données contenues dans le dossier `App/data/all_jobs` sur la base de données si elles n'y sont pas déjà.

## Collecte de technologies 

Le dossier `App/src/Technos` contient un fichier `Technos.py` qui collecte de l'information sur les technologies les plus utilisées dans le monde de la data. La fonction `get_db_engines_ranking()` scrape le site [db-engines.com](https://db-engines.com/en/ranking) qui contient une liste de technologies de bases de données les plus populaires; la fonction `get_tiobe_top50()` scrape l'index [TIOBE](https://www.tiobe.com/tiobe-index/) des languages de programmation les plus populaires; la fonction `get_github_frameworks()` scrape une liste des [frameworks les plus populaires sur Github](https://insights.stackoverflow.com/survey/2021#technology-most-popular-technologies).

Les données sont stockées dans le dossier `App/data/Technos` pour utilisation dans la section suivante.

## Visualisation des données

Le dossier `App/src/Dashboard` contient les fichier nécessaire à la création du dashboard. Les données contenues dans la base de donnée ElasticSearch `adzuna_jobs` sont visualisées dans un dashboard Plotly Dash qui permet une intéraction avec les données. Il est organisé dans un conteneur Docker (voir le `Dockerfile`) basé sur une image `python:3.12-slim`, avec l'installation via pip de librairies contenues dans le fichier `requirements.txt`. Un cron job lancé dans le Dockerfile éxecute le fichier `app.py` régulièrement. Des logs des processus sont sauvegardés dans le fichier `App/src/Dashboard/LOGS/cron.log`.

**`app.py`**: Ce fichier contient le code pour créer un dashboard Plotly Dash, avec les charactéristiques suivantes:

* Les technologies collectées dans le dossier `App/src/Technos` (voir section précédente) sont utilisées pour filtrer les offres d'emploi stockées sur la base de données `adzuna_jobs` qui sont importées et converties dans un DataFrame. Pour chaque offre d'emploi, les technologies sont incluses dans la colonne `technologies` du DataFrame. De plus, une nouvelle colonne `clean_title` est créée, qui nettoie le titre de l'offre d'emploi pour standardiser un peu plus leur format (par exemple, retirer la mention "H/F" ou "F/H"), les convertit en minuscules avec une majuscule pour seulement la première lettre.

* La liste de technologies est aussi utilisée pour calculer leur fréquence, ainsi que la moyenne des fourchettes de salaire mentionnant ces technologies.

* Le dashboard Plotly dash est créé dans l'objet `app`, et le layout de l'application est créé dans une fonction `generate_layout()`. L'application contient les fonctionalités suivantes:

    * Un filtre permet à l'utilisateur de sélectionner un type d'offre d'emploi. La fonction réactive `update_data_table()` permet ensuite de visualiser les offres d'emploi correspondantes dans une table.
    * Pour chaque offre d'emploi dans la table ci-dessus, l'utilisateur peut cocher une case qui affiche une carte de France avec la localisation de l'offre d'emploi. Cette carte est créée par la fonction réactive `update_graphs()` qui utilise la librairie `folium`.
    * Un onglet `Compétences` qui permet à l'utilisateur de visualiser des charactéristiques de technologies dans les offres d'emploi. Un filtre permet à l'utilisateur de selectionner plusieurs technologies à la fois. La fonction réactive `update_frequency_barchart()` montre ensuite la fréquence de mention de ces technologies dans les offres d'emploi à travers un histogramme. La fonction réactive `update_dumbbell_chart()` visualise la fourchette moyenne de salaires pour ces technologies à travers un dumbbell chart, avec les points montrant la moyenne des salaires minimum et maximum.

## Docker

Un fichier `docker-compose.yml` créé un réseau avec les conteneurs docker ci-dessus. En plus des conteneurs créés avec les Dockerfiles mentionnés ci-dessus, le docker-compose créé des conteneurs pour `elasticsearch` et `kibana`.


