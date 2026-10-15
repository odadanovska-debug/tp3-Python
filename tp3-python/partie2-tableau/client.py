# client du tableau interactif
# on choisit une forme dans le menu, on donne ses dimensions,
# et le client l'envoie au serveur avec une requête http
# lancer avec : python client.py   (le serveur doit tourner)

import random

import requests

SERVEUR = "http://localhost:8000"
LARGEUR = 900   # taille du tableau
HAUTEUR = 560


# ---------- petites fonctions pour demander des valeurs ----------

def demander_entier(question: str, mini: int = 0, maxi: int = 2000) -> int:
    # redemande tant que l'utilisateur ne tape pas un nombre correct
    while True:
        reponse = input(f"  {question} : ")
        try:
            valeur = int(reponse)
            if mini <= valeur <= maxi:
                return valeur
            print(f"  -> entre {mini} et {maxi} stp")
        except ValueError:
            print("  -> il faut un nombre entier")


def demander_couleur() -> list[int]:
    reponse = input("  couleur r g b (ex : 255 0 0, entrée = au hasard) : ").strip()
    if reponse == "":
        return [random.randint(80, 255) for _ in range(3)]
    try:
        couleur = [int(v) for v in reponse.split()]
        if len(couleur) == 3 and all(0 <= v <= 255 for v in couleur):
            return couleur
    except ValueError:
        pass
    print("  -> couleur pas valide, j'en prends une au hasard")
    return [random.randint(80, 255) for _ in range(3)]


# ---------- envoi au serveur ----------

def envoyer(forme: dict) -> None:
    try:
        reponse = requests.post(f"{SERVEUR}/draw", json=forme, timeout=5)
        if reponse.status_code == 200:
            print(f"  ok, envoyé à {reponse.json()['tableaux']} tableau(x)")
        else:
            print("  erreur du serveur :", reponse.json()["detail"])
    except requests.ConnectionError:
        print("  impossible de joindre le serveur, il est bien lancé ?")
    except requests.Timeout:
        print("  le serveur met trop de temps à répondre")


def effacer() -> None:
    try:
        requests.post(f"{SERVEUR}/clear", timeout=5)
        print("  tableau effacé")
    except requests.RequestException:
        print("  impossible de joindre le serveur, il est bien lancé ?")


# ---------- les formes ----------

def point() -> dict:
    return {"shape": "point",
            "x": demander_entier("x", 0, LARGEUR),
            "y": demander_entier("y", 0, HAUTEUR),
            "color": demander_couleur()}


def ligne() -> dict:
    return {"shape": "line",
            "x1": demander_entier("x de départ", 0, LARGEUR),
            "y1": demander_entier("y de départ", 0, HAUTEUR),
            "x2": demander_entier("x d'arrivée", 0, LARGEUR),
            "y2": demander_entier("y d'arrivée", 0, HAUTEUR),
            "color": demander_couleur()}


def cercle() -> dict:
    return {"shape": "circle",
            "x": demander_entier("x du centre", 0, LARGEUR),
            "y": demander_entier("y du centre", 0, HAUTEUR),
            "radius": demander_entier("rayon", 1, 300),
            "color": demander_couleur()}


def rectangle() -> dict:
    return {"shape": "rectangle",
            "x": demander_entier("x du coin haut gauche", 0, LARGEUR),
            "y": demander_entier("y du coin haut gauche", 0, HAUTEUR),
            "width": demander_entier("largeur", 1, LARGEUR),
            "height": demander_entier("hauteur", 1, HAUTEUR),
            "color": demander_couleur()}


def carre() -> dict:
    return {"shape": "square",
            "x": demander_entier("x du coin haut gauche", 0, LARGEUR),
            "y": demander_entier("y du coin haut gauche", 0, HAUTEUR),
            "cote": demander_entier("côté", 1, HAUTEUR),
            "color": demander_couleur()}


# formes composées : plusieurs formes simples envoyées l'une après l'autre

def maison() -> list[dict]:
    x = demander_entier("x de la maison", 0, LARGEUR - 160)
    y = demander_entier("y du sol", 160, HAUTEUR)
    return [
        {"shape": "square", "x": x, "y": y - 140, "cote": 140, "color": [230, 200, 150]},     # murs
        {"shape": "line", "x1": x - 10, "y1": y - 140, "x2": x + 70, "y2": y - 210,
         "color": [200, 70, 60]},                                                             # toit gauche
        {"shape": "line", "x1": x + 70, "y1": y - 210, "x2": x + 150, "y2": y - 140,
         "color": [200, 70, 60]},                                                             # toit droit
        {"shape": "rectangle", "x": x + 55, "y": y - 70, "width": 30, "height": 70,
         "color": [120, 80, 50]},                                                             # porte
        {"shape": "square", "x": x + 15, "y": y - 120, "cote": 30, "color": [150, 200, 230]},  # fenêtre
    ]


def smiley() -> list[dict]:
    x = demander_entier("x du centre", 60, LARGEUR - 60)
    y = demander_entier("y du centre", 60, HAUTEUR - 60)
    return [
        {"shape": "circle", "x": x, "y": y, "radius": 60, "color": [245, 210, 70]},         # tête
        {"shape": "circle", "x": x - 20, "y": y - 15, "radius": 7, "color": [40, 40, 40]},  # œil gauche
        {"shape": "circle", "x": x + 20, "y": y - 15, "radius": 7, "color": [40, 40, 40]},  # œil droit
        {"shape": "line", "x1": x - 25, "y1": y + 20, "x2": x, "y2": y + 32, "color": [40, 40, 40]},
        {"shape": "line", "x1": x, "y1": y + 32, "x2": x + 25, "y2": y + 20, "color": [40, 40, 40]},
    ]


MENU = """
--- tableau interactif ---
1. point        5. carré
2. ligne        6. maison
3. cercle       7. smiley
4. rectangle    8. effacer le tableau
0. quitter
"""

FORMES = {"1": point, "2": ligne, "3": cercle, "4": rectangle, "5": carre}


def main() -> None:
    print(f"le tableau fait {LARGEUR} x {HAUTEUR} pixels, (0, 0) = en haut à gauche")
    while True:
        print(MENU)
        choix = input("ton choix : ").strip()

        if choix == "0":
            print("à plus !")
            break
        elif choix in FORMES:
            envoyer(FORMES[choix]())
        elif choix == "6":
            for forme in maison():
                envoyer(forme)
        elif choix == "7":
            for forme in smiley():
                envoyer(forme)
        elif choix == "8":
            effacer()
        else:
            print("choix inconnu")


if __name__ == "__main__":
    main()
