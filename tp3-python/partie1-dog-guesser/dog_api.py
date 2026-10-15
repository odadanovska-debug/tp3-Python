# tout ce qui parle avec l'api dog.ceo est ici
# comme ça le jeu ne s'occupe que de l'affichage

import requests

URL_RACES = "https://dog.ceo/api/breeds/list/all"
URL_HASARD = "https://dog.ceo/api/breeds/image/random"


def get_all_breeds() -> list[str]:
    # renvoie toutes les races sous forme de liste de noms
    # ex : "afghan hound", "beagle", "bernese mountain"
    reponse = requests.get(URL_RACES, timeout=5)
    reponse.raise_for_status()  # plante si le serveur répond une erreur (404, 500...)
    data = reponse.json()["message"]

    races = []
    for race, sous_races in data.items():
        if len(sous_races) == 0:
            races.append(race)
        else:
            # une race avec des sous-races : on fait un nom par sous-race
            for sous_race in sous_races:
                races.append(f"{sous_race} {race}")
    return races


def nom_race(url: str) -> str:
    # l'api ne donne pas la race, mais elle est cachée dans l'url de l'image
    # ex : https://images.dog.ceo/breeds/hound-afghan/n02088094_1003.jpg
    dossier = url.split("/")[4]       # -> "hound-afghan"
    morceaux = dossier.split("-")     # -> ["hound", "afghan"]
    morceaux.reverse()                # -> ["afghan", "hound"]
    return " ".join(morceaux)         # -> "afghan hound"


def get_random_dog() -> tuple[str, str]:
    # renvoie (url de l'image, nom de la race)
    reponse = requests.get(URL_HASARD, timeout=5)
    reponse.raise_for_status()
    url = reponse.json()["message"]
    return url, nom_race(url)


def download_image(url: str) -> bytes:
    # télécharge l'image et renvoie son contenu brut
    reponse = requests.get(url, timeout=10)
    reponse.raise_for_status()
    return reponse.content


if __name__ == "__main__":
    # petit test rapide : python dog_api.py
    print("nombre de races :", len(get_all_breeds()))
    print("chien au hasard :", get_random_dog())
