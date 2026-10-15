# Tableau interactif

Un tableau partagé dans le navigateur. Le client Python envoie des formes au serveur, et elles apparaissent en direct sur tous les tableaux ouverts. On peut aussi dessiner à la souris : les autres le voient en même temps.

## Installation

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Lancement

1. Le serveur : `python server.py`
2. Le tableau : ouvrir http://localhost:8000 (plusieurs onglets possibles)
3. Le client, dans un autre terminal : `python client.py`

## API

`POST /draw` avec un body json, par exemple :

```json
{"shape": "circle", "x": 40, "y": 40, "radius": 20, "color": [220, 140, 210]}
```

Formes : `point`, `line`, `circle`, `rectangle`, `square` (champs selon la doc du sujet).
Si un champ manque, le serveur répond 400 avec le message d'erreur.

`POST /clear` efface le tableau pour tout le monde.

## En plus du sujet

- dessin à la souris partagé entre tous les tableaux
- un tableau ouvert en retard récupère tout ce qui a déjà été dessiné
- reconnexion automatique si le serveur redémarre
- formes composées dans le client : maison et smiley
- bouton pour enregistrer le tableau en image
