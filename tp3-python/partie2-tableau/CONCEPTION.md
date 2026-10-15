# Conception

## Comment j'ai travaillé avec l'IA


Pour cette partie, l'IA était recommandée, donc j'ai travaillé avec Claude du début à la fin. Je lui ai donné la doc de l'API du sujet en lui demandant de respecter exactement les noms des champs (`shape`, `cote`, `radius`), apres j'ai voulu personaliser et je lui ai expliquer quelle l'architecture, quel le type de code et le design que je voulais : un code simple, des outils vus en cours (sinon je modifier). Il m'a surtout aidée sur la page HTML/JavaScript, que je ne maîtrise pas encore, et je lui ai demandé de m'expliquer les lignes que je ne comprenais pas. Ensuite, j'ai testé chaque partie moi-même sur VS Code, avec plusieurs onglets ouverts pour vérifier le temps réel, et j'ai corrigé les bugs petit à petit. Par exemple, j'ai remarqué que le toit de la maison sortait du tableau quand on la plaçait trop haut, et on a ajouté une limite dans le client.

## mes choix

### FastAPI pour le serveur
Il fallait à la fois une API HTTP pour le client et un WebSocket pour les tableaux. FastAPI fait les deux dans le même programme, sur le même port. Sans ça, il aurait fallu lancer deux serveurs différents.

### Le serveur vérifie les formes
Je ne voulais pas que n'importe quoi s'affiche sur les tableaux. Si un champ manque ou si la couleur n'est pas bonne, le serveur refuse la forme et renvoie une erreur 400 avec un message clair qui explique le problème.

### Garder un historique
Le serveur garde en mémoire toutes les formes déjà dessinées. Comme ça, si quelqu'un ouvre un tableau en retard, il voit tout le dessin au lieu d'une page vide.

### La couleur en liste
Dans la doc, la couleur est écrite `(120, 200, 102)`, mais le JSON ne connaît pas ce format. Elle est donc envoyée sous forme de liste : `[120, 200, 102]`.

### Un client qui ne plante pas
Si on tape une lettre au lieu d'un nombre, ou une valeur hors du tableau, le client repose simplement la question. Ça m'a d'ailleurs permis de corriger la maison, dont le toit sortait du tableau quand on la plaçait trop haut.

### Les formes composées
Pour la maison et le smiley, je n'ai pas eu besoin de modifier l'API. Ce sont juste plusieurs formes simples (carrés, cercles, lignes) envoyées l'une après l'autre.

### Dessiner à la souris
J'ai ajouté la possibilité de dessiner directement sur le tableau. La page envoie des petits bouts de ligne par le WebSocket, au même format que l'API, et le serveur les renvoie à tous les autres tableaux en temps réel.

### Le design
Je voulais que ça ressemble à un vrai tableau de classe, mais en version rose : un cadre rose, des boutons arrondis, et un fond prune foncé pour que les couleurs des formes ressortent bien.
