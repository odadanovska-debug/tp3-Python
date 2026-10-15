# dog guesser : le jeu
# on affiche un chien au hasard, le joueur doit trouver sa race parmi 4 choix
# lancer avec : python game.py (le serveur des records doit tourner à côté)

import json
import queue
import random
import threading
import time
from datetime import datetime
from io import BytesIO
import tkinter as tk
from tkinter import messagebox, simpledialog

import requests
from PIL import Image, ImageTk
from websockets.sync.client import connect

from dog_api import get_all_breeds, get_random_dog, download_image

SERVEUR = "ws://localhost:8765"
FICHIER_LOCAL = "mes_scores.txt"
NB_MANCHES = 10

# couleurs de l'interface (thème rose)
FOND = "#fde4ee"      # rose pâle
CARTE = "#ffffff"
ROSE = "#e84c8b"      # rose vif pour les titres
ROSE_CLAIR = "#f9c6da"
CADRE_PHOTO = "#fbd3e3"
VERT = "#4caf7a"
ROUGE = "#d94f6a"
TEXTE = "#4a2c3a"
GRIS = "#a07d8c"
POLICE = "Segoe UI"


# ---------- scores en local (comme au tp2) ----------

def sauver_score_local(pseudo: str, score: int) -> None:
    # on ajoute la partie à la fin du fichier : pseudo;score;date
    date = datetime.now().isoformat(timespec="seconds")
    with open(FICHIER_LOCAL, "a", encoding="utf-8") as f:
        f.write(f"{pseudo};{score};{date}\n")


def meilleur_score_local(pseudo: str) -> int:
    # meilleur score du joueur sur cet ordi (0 si jamais joué)
    meilleur = 0
    try:
        with open(FICHIER_LOCAL, "r", encoding="utf-8") as f:
            for ligne in f:
                nom, score, date = ligne.strip().split(";")
                if nom == pseudo and int(score) > meilleur:
                    meilleur = int(score)
    except FileNotFoundError:
        pass  # pas encore de fichier = première partie
    return meilleur


# ---------- le jeu ----------

class DogGuesser:

    def __init__(self, fenetre: tk.Tk, pseudo: str, races: list[str]):
        self.fenetre = fenetre
        self.pseudo = pseudo
        self.races = races

        self.score = 0
        self.manche = 0
        self.serie = 0            # nombre de bonnes réponses d'affilée
        self.bonne_reponse = ""
        self.debut = 0.0          # heure d'affichage de la photo (pour le chrono)
        self.photo = None         # on garde l'image sinon tkinter l'efface

        # boîte aux lettres entre le thread réseau et l'interface
        # (tkinter n'aime pas qu'un autre thread touche à la fenêtre)
        self.messages = queue.Queue()

        self.creer_interface()

        # un thread en fond qui écoute les records en direct
        threading.Thread(target=self.ecouter_records, daemon=True).start()
        self.verifier_messages()

        self.nouvelle_manche()

    # ----- interface -----

    def creer_interface(self) -> None:
        self.fenetre.title("Dog Guesser")
        self.fenetre.configure(bg=FOND)
        self.fenetre.resizable(False, False)

        # en haut : titre + infos de la partie
        haut = tk.Frame(self.fenetre, bg=FOND)
        haut.pack(fill="x", padx=20, pady=(15, 5))
        tk.Label(haut, text="Dog Guesser", font=(POLICE, 20, "bold"),
                 bg=FOND, fg=ROSE).pack(side="left")
        self.infos = tk.Label(haut, text="", font=(POLICE, 12), bg=FOND, fg=TEXTE)
        self.infos.pack(side="right")

        milieu = tk.Frame(self.fenetre, bg=FOND)
        milieu.pack(padx=20, pady=(5, 20))

        # à gauche : la photo, la question et les 4 boutons
        jeu = tk.Frame(milieu, bg=FOND)
        jeu.grid(row=0, column=0, sticky="n")

        cadre_image = tk.Frame(jeu, width=440, height=360, bg=CADRE_PHOTO)
        cadre_image.pack()
        cadre_image.pack_propagate(False)  # le cadre garde sa taille fixe
        self.image = tk.Label(cadre_image, text="chargement...", bg=CADRE_PHOTO,
                              fg=GRIS, font=(POLICE, 12))
        self.image.pack(expand=True)

        tk.Label(jeu, text="C'est quelle race ?", font=(POLICE, 14, "bold"),
                 bg=FOND, fg=ROSE).pack(pady=(12, 4))

        zone_boutons = tk.Frame(jeu, bg=FOND)
        zone_boutons.pack()
        self.boutons = []
        for i in range(4):
            bouton = tk.Button(zone_boutons, text="", width=24, height=2,
                               font=(POLICE, 11), bg=CARTE, fg=TEXTE,
                               activebackground=ROSE_CLAIR, relief="flat",
                               cursor="hand2")
            # le lambda permet de savoir quel bouton a été cliqué
            bouton.config(command=lambda b=bouton: self.repondre(b))
            bouton.grid(row=i // 2, column=i % 2, padx=5, pady=5)
            self.boutons.append(bouton)

        self.resultat = tk.Label(jeu, text="", font=(POLICE, 12, "bold"), bg=FOND)
        self.resultat.pack(pady=(8, 0))

        # à droite : les records en direct
        cote = tk.Frame(milieu, bg=CARTE, padx=18, pady=15,
                        highlightbackground=ROSE_CLAIR, highlightthickness=2)
        cote.grid(row=0, column=1, sticky="n", padx=(20, 0))
        tk.Label(cote, text="Records en direct", font=(POLICE, 13, "bold"),
                 bg=CARTE, fg=ROSE).pack(anchor="w")
        self.etat_serveur = tk.Label(cote, text="connexion au serveur...",
                                     font=(POLICE, 9), bg=CARTE, fg=GRIS)
        self.etat_serveur.pack(anchor="w", pady=(0, 10))
        self.liste_records = tk.Label(cote, text="", font=("Consolas", 11),
                                      justify="left", bg=CARTE, fg=TEXTE)
        self.liste_records.pack(anchor="w")
        self.annonce = tk.Label(cote, text="", font=(POLICE, 10, "bold"),
                                bg=CARTE, fg=ROSE, wraplength=200, justify="left")
        self.annonce.pack(anchor="w", pady=(12, 0))

        tk.Label(cote, text=f"\njoueur : {self.pseudo}\nrecord perso : "
                            f"{meilleur_score_local(self.pseudo)}",
                 font=(POLICE, 10), bg=CARTE, fg=GRIS, justify="left").pack(anchor="w")

    def maj_infos(self) -> None:
        self.infos.config(text=f"manche {self.manche}/{NB_MANCHES}    "
                               f"score {self.score}    série {self.serie}")

    # ----- déroulement d'une manche -----

    def nouvelle_manche(self) -> None:
        if self.manche == NB_MANCHES:
            self.fin_de_partie()
            return

        try:
            url, race = get_random_dog()
            image = Image.open(BytesIO(download_image(url)))
        except requests.RequestException:
            # pas d'internet ou api en panne : on propose de réessayer
            if messagebox.askretrycancel("Problème réseau",
                                         "Impossible de joindre l'api dog.ceo.\n"
                                         "Vérifie ta connexion."):
                self.nouvelle_manche()
            else:
                self.fenetre.destroy()
            return

        self.manche += 1
        self.bonne_reponse = race

        # on réduit la photo pour qu'elle rentre dans le cadre
        image.thumbnail((440, 360))
        self.photo = ImageTk.PhotoImage(image)
        self.image.config(image=self.photo, text="")

        # 1 bonne réponse + 3 mauvaises tirées au hasard, puis on mélange
        mauvaises = [r for r in self.races if r != race]
        choix = random.sample(mauvaises, 3) + [race]
        random.shuffle(choix)
        for bouton, nom in zip(self.boutons, choix):
            bouton.config(text=nom, bg=CARTE, fg=TEXTE, state="normal")

        self.resultat.config(text="")
        self.maj_infos()
        self.debut = time.time()  # top chrono

    def calculer_points(self, temps: float) -> int:
        # bonne réponse = 100
        # + bonus vitesse : 50 si réponse immédiate, 0 au bout de 10 s
        # + bonus série : 10 points par bonne réponse d'affilée
        bonus_vitesse = max(0, 50 - int(temps * 5))
        bonus_serie = (self.serie - 1) * 10
        return 100 + bonus_vitesse + bonus_serie

    def repondre(self, bouton: tk.Button) -> None:
        temps = time.time() - self.debut

        # on bloque les boutons et on montre la bonne réponse en vert
        for b in self.boutons:
            b.config(state="disabled", disabledforeground=GRIS)
            if b["text"] == self.bonne_reponse:
                b.config(bg=VERT, disabledforeground="white")

        if bouton["text"] == self.bonne_reponse:
            self.serie += 1
            points = self.calculer_points(temps)
            self.score += points
            self.resultat.config(text=f"Bravo ! +{points} points ({temps:.1f} s)", fg=VERT)
        else:
            self.serie = 0
            bouton.config(bg=ROUGE, disabledforeground="white")
            self.resultat.config(text=f"Raté, c'était un {self.bonne_reponse}", fg=ROUGE)

        self.maj_infos()
        self.fenetre.after(1500, self.nouvelle_manche)  # manche suivante dans 1,5 s

    def fin_de_partie(self) -> None:
        ancien_record = meilleur_score_local(self.pseudo)
        sauver_score_local(self.pseudo, self.score)
        envoye = self.envoyer_score()

        texte = f"Score final : {self.score}\n"
        if self.score > ancien_record:
            texte += "Nouveau record perso !\n"
        else:
            texte += f"Ton record perso : {ancien_record}\n"
        if not envoye:
            texte += "\n(serveur des records injoignable, score gardé en local)\n"

        if messagebox.askyesno("Partie terminée", texte + "\nRejouer ?"):
            self.score = 0
            self.manche = 0
            self.serie = 0
            self.nouvelle_manche()
        else:
            self.fenetre.destroy()

    # ----- réseau : records -----

    def envoyer_score(self) -> bool:
        # on envoie le score au serveur, renvoie True si ça a marché
        try:
            with connect(SERVEUR, open_timeout=3) as ws:
                ws.send(json.dumps({"pseudo": self.pseudo, "score": self.score}))
            return True
        except Exception:
            return False

    def ecouter_records(self) -> None:
        # tourne en fond : on reste connecté au serveur et on reçoit le top
        while True:
            try:
                with connect(SERVEUR) as ws:
                    self.messages.put({"etat": "connecté au serveur"})
                    for message in ws:
                        self.messages.put(json.loads(message))
            except Exception:
                self.messages.put({"etat": "serveur hors ligne"})
            time.sleep(3)  # on réessaie un peu plus tard

    def verifier_messages(self) -> None:
        # toutes les 200 ms on regarde si le thread réseau a déposé quelque chose
        while not self.messages.empty():
            msg = self.messages.get()
            if "etat" in msg:
                self.etat_serveur.config(text=msg["etat"])
            if "top" in msg:
                self.afficher_records(msg["top"])
            if msg.get("nouveau"):
                self.annonce.config(text=f"{msg['nouveau']} vient d'entrer dans le top !")
        self.fenetre.after(200, self.verifier_messages)

    def afficher_records(self, top: list[dict]) -> None:
        if len(top) == 0:
            self.liste_records.config(text="aucun record\npour l'instant")
            return
        lignes = []
        for i, record in enumerate(top, start=1):
            lignes.append(f"{i}. {record['pseudo']:<12}{record['score']:>5}")
        self.liste_records.config(text="\n".join(lignes))


def main() -> None:
    fenetre = tk.Tk()
    fenetre.withdraw()  # on cache la fenêtre le temps de demander le pseudo

    pseudo = simpledialog.askstring("Dog Guesser", "Ton pseudo :", parent=fenetre)
    if not pseudo:
        fenetre.destroy()
        return
    pseudo = pseudo.replace(";", "").strip()[:12]  # pas de ; (séparateur du fichier)

    try:
        races = get_all_breeds()
    except requests.RequestException:
        messagebox.showerror("Problème réseau",
                             "Impossible de récupérer la liste des races.\n"
                             "Vérifie ta connexion puis relance le jeu.")
        fenetre.destroy()
        return

    fenetre.deiconify()
    DogGuesser(fenetre, pseudo, races)
    fenetre.mainloop()


if __name__ == "__main__":
    main()
