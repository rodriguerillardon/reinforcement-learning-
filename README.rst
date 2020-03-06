Connect4 Zeo: Reinforcement learning and Connect4
=================================================


Introduction
------------

Dans le cadre du projet de reinforcement learning, nous avons
cherché à reproduire les résultats de Alpha Zero adapté
aux échecs pour le puissance4 et le morpion.


Nous nous sommes inspirés du repository suivant  - https://github.com/Zeta36/chess-alpha-zero

Installation
------------

Il vous faudra dans un premier temps installer le module de puissance 4 que nous avons créé ainsi que les autres modules
requis à l'aide de la commande

::

    pip install -r requirements.txt


Organisation
------------
Notre repo est organisé en deux parties distinctes, la première est le fichier morpion et la deuxième est celle dédiée au
puissance 4.

Les deux fichiers sont assez semblables.

Entrainement
------------

Du fait des temps d'entrainements trop longs pour le puissance 4, nous avons donc décidé de tester les résultats obtenus sur
Alpha Chess Zero sur un jeu beaucoup plus simple, le morpion.

L'utilisateur du repo peut entrainer le modèle à l'aide des fichiers pipeline en les executant comme commande.

Test
------

L'utilisateur est libre de jouer contre l'IA en executant le fichier play_against_ai. Il y a une interface basique.

Rapport
-------

Un léger rapport sur notre travail est disponible dans le `fichier reinforcement_learning_master.pdf`.