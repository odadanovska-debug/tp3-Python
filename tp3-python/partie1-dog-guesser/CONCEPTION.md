# Conception

# comment j'ai travaillé avec IA

J'ai utilisé Claude. Tout d'abord, j'ai utilisé mes connaissances pour coder ce que je savais faire, puis j'ai corrigé et ajouté ce que je ne connaissais pas avec Claude, en lui donnant l'architecture et le design que je voulais, le type de code et la structure, et en lui demandant de m'expliquer les lignes que je ne comprenais pas. Après avoir assemblé ma partie avec celle de Claude, je suis repassée sur l'ensemble pour corriger tous les bugs restants, en plus de les avoir réglés petit à petit au fur et à mesure.

# mes choix

## Mes choix

### L'interface en tkinter
Le sujet demandait de tout faire en Python, donc pas de site web. J'ai pris tkinter parce qu'il est déjà installé avec Python. Il m'a juste fallu ajouter Pillow, sinon les photos en .jpg ne s'affichaient pas.

### Trois fichiers au lieu d'un seul
J'ai séparé l'api (`dog_api.py`), le jeu (`game.py`) et les records (`server.py`). Je trouvais ça plus clair, et quand quelque chose bugait, je savais directement où chercher.

### Retrouver la race du chien
L'api donne seulement le lien de la photo, pas la race. En regardant les liens, j'ai vu que la race était écrite dedans (`/breeds/hound-afghan/`), donc je la récupère à partir de là. Les trois mauvaises réponses sont tirées au hasard dans la liste des races.

### Deux endroits pour les scores
Un fichier `mes_scores.txt` sur l'ordi du joueur pour son record perso (avec le même format qu'au TP2), et un fichier `records.json` sur le serveur pour le classement de tout le monde.

### Le classement en direct
J'ai utilisé les WebSockets comme dans la partie 0. Le serveur reste connecté à tous les joueurs, et dès que quelqu'un finit une partie, le nouveau classement s'affiche chez tout le monde.

### Un thread pour le serveur
Au début, la fenêtre risquait de se figer en attendant les messages du serveur. Le thread écoute en arrière-plan, et le jeu reste fluide.

### Le calcul du score
Je ne voulais pas que seule la bonne réponse compte. On gagne 100 points par bonne réponse, plus un bonus si on répond vite et un bonus si on enchaîne plusieurs bonnes réponses d'affilée. Ça donne envie de rejouer pour battre son record.

### Si internet coupe
Je ne voulais pas que le jeu plante. Si l'api ne répond pas, une fenêtre propose de réessayer. Si le serveur des records est éteint, on peut quand même jouer, et le score est gardé en local.