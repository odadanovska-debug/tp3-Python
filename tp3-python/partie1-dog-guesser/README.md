# Dog Guesser

Une photo de chien s'affiche, il faut trouver sa race parmi 4 propositions.
10 manches par partie, les records s'affichent en direct pour tous les joueurs.

## Installation

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Lancement

Dans un premier terminal, le serveur des records :

```
python server.py
```

Dans un deuxième terminal, le jeu :

```
python game.py
```

On peut lancer plusieurs `game.py` en même temps : quand un joueur fait un record, le classement se met à jour chez tous les autres.

## Score

- bonne réponse : 100 points
- bonus vitesse : jusqu'à +50 si on répond vite (0 au bout de 10 s)
- bonus série : +10 par bonne réponse d'affilée

## Fichiers

- `game.py` : le jeu (interface tkinter)
- `dog_api.py` : les appels à l'api dog.ceo
- `server.py` : serveur WebSocket qui garde les records
- `mes_scores.txt` : scores du joueur, en local (créé automatiquement)
- `records.json` : records de tous les joueurs, côté serveur (créé automatiquement)
